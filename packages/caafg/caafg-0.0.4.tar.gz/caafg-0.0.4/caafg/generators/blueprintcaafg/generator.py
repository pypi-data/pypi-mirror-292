import logging
import re
import pandas as pd
from typing import Any

from remoteinference.interfaces import LLMInterface

from caafg.dataset import Dataset
from caafg.interfaces import AbstractGenerator
from caafg.generators.blueprintcaafg.core import build_assistant_prompt, \
    build_system_prompt, build_user_prompt, build_feature_from_string

logger = logging.getLogger(__name__)

allowed_operators = [
    "FrequencyEncoding",
    "Absolute",
    "Log",
    "SquareRoot",
    "Sigmoid",
    "Round",
    "Residual",
    "Min",
    "Max",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Combine",
    "CombineThenFrequencyEncoding",
    "GroupByThenMin",
    "GroupByThenMax",
    "GroupByThenMean",
    "GroupByThenStd",
    "GroupByThenRank",
]


class BlueprintGenerator(AbstractGenerator):
    """
    A simple class to generate features from a language model given a dataset
    input. The generator will have as options a list of possible applicable
    operators and will provide us with a blueprint on which operators to apply
    to which features. We will then manually create the proposed feature by
    applying the operator manually in the background.
    """

    model: LLMInterface
    context_size: int
    features: dict[str, dict[str, Any]]
    feedback: dict[str, str]

    def __init__(self,
                 model: LLMInterface,
                 context_size: int = 8192) -> None:
        """
        Parameters
        ----------
        model : LLMInterface
            The language model to query for generating features.
        context_size : int, optional
            The maximum context size of the language model, by default 8192.
            This is to check wether the prompt size exceeds the maximum
            context window of the model.
        """
        self.model = model
        self.context_size = context_size

        # the dict containing the proposed feature transformations
        self.features = {}
        self.feedback = {}

    def _fit(self,
             dataset: Dataset,
             temperature: float,
             max_tokens: int,
             feedback: dict[str, str],
             **kwargs) -> str:
        """
        Fit the LLM on the currently given training dataset and prompt a new
        feature. Note that this method should only be fitted on the training
        data. The transformation for the test dataset at a later point will be
        performed separately.
        """

        if feedback:
            assistant_prompt = build_assistant_prompt(feedback)
            logger.debug(f"Assistant prompt: {assistant_prompt}")
        else:
            logger.debug("No feedback provided, not using assistant prompt")
            assistant_prompt = None

        system_prompt = build_system_prompt()
        logger.debug(f"System prompt: {system_prompt}")

        user_prompt = build_user_prompt(dataset,
                                        feedback)

        logger.debug(f"User prompt: {user_prompt}")

        if assistant_prompt:
            messages = [system_prompt, user_prompt, assistant_prompt]
        else:
            messages = [system_prompt, user_prompt]

        response = self.model.chat_completion(messages,
                                              temperature,
                                              max_tokens,
                                              **kwargs)

        # quit when we have an empty response
        if not response:
            logger.error("Received an empty response from the model.")
            return None

        logger.debug(f"Response: {response}")
        logger.info(f"total request tokens: \
{response['usage']['total_tokens']}")

        # TODO: try to generalize this by reading out of the model what the
        # effective context window is
        if int(response["usage"]["prompt_tokens"]) > self.context_size:
            logger.warning(f"Prompt tokens exceeded maximum context window of \
{self.context_size} with a total of {response['usage']['prompt_tokens']} \
tokens. Results are probably useless.")

        # tranform the string representation that the LLM proposed into a real
        # feature
        feature_str = str(response["choices"][0]["message"]["content"])
        return feature_str

    def _build_feature(self,
                       X: pd.DataFrame,
                       operator: str,
                       mapping: Any,
                       features: list[str]) -> tuple[pd.Series, Any]:
        """
        Build a new feature from the exsiting features of a given dataset and
        the proposed instructions.

        :param X: the feature space to apply the transformation to
        :param operator: the operator to apply
        :param feature: the list of currently available features

        Returns
            The transformed dataset containing the new feature, the mapping
            applied to the new feature
        """
        new_feature, mapping = build_feature_from_string(X,
                                                         operator,
                                                         mapping,
                                                         features)

        logger.debug(f"Len of new feature: {len(new_feature)}")
        logger.debug(f"New feature has mapping: \
                     {True if mapping is not None else False}")
        if new_feature.empty:
            logger.error("Feature could not be generated")

        return new_feature, mapping

    def _validate_llm_output(self,
                             operator: str,
                             selected_features: list[str],
                             dataset_features: list[str]
                             ) -> bool:
        """
        Validate the output of the LLM to see if the feature can be created
        without actually having to create the feature.
        """
        ok = True
        if operator not in allowed_operators:
            logger.error(f"Operator {operator} not allowed")
            ok = False

        if len(selected_features) > 2:
            logger.error("No support to apply an operator to more than two \
features at once")
            ok = False

        for feature in selected_features:
            feature_idx = int(feature) - 1
            if feature_idx < 0 or feature_idx > len(dataset_features) - 1:
                logger.error(f"Feature {feature} not in list of existing \
dataset features")
                ok = False

        return ok

    def ask(self,
            dataset: Dataset,
            n_features: int = 1,
            max_retries: int = 5,
            temperature: float = 0.5,
            max_tokens: int = 300,
            **model_kwargs
            ) -> dict[str, dict[str, Any]]:
        """
        Ask the generator to generate a new sample.

        Parameters
        ----------
        dataset : Dataset
            The dataset to generate the features for.
        n_features : int, optional
            The number of features to generate, by default 1.
        max_retries : int, optional
            The maximum number of retries when prompting the LLM to generate a
            new feature. When the proposed feature is not parseable, the
            generator will retry to generate a new feature. Defaults to 5.
        temperature : float
            The temperature to run inference at.
        max_tokens : int
            The maximum number of tokens the model is allowed to generate.
        model_kwargs : dict
            Additional keyword arguments for further defining the inference at
            the model. These keywords will be passed to the model when the
            chat_completion endpoint is called. Should match OpenAI API specs.
            ref: https://platform.openai.com/docs/api-reference/chat/create

        Returns
        -------
        features : dict
            A dictionary containing the generated features. For each feature
            the dictionary contains an individual field for the name, operator,
            features, features_combination, description and reasoning.
        """

        feedback = {}

        for i in range(n_features):
            logger.info(f"Generating feature {i + 1} of {n_features}")
            name, operator, features, features_combination, description, \
                reasoning = self._generate(
                    dataset=dataset,
                    max_retries=max_retries,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    feedback=feedback,
                    **model_kwargs)

            self.features[f"blueprint_feature_{i}"] = {
                "name": name,
                "operator": operator,
                "features": features,
                "features_combination": features_combination,
                "description": description,
                "reasoning": reasoning
            }

        return self.features

    def tell(self):
        """
        Update the states of the generator based on the feedback.
        """
        raise NotImplementedError

    def transform(self,
                  train_X: pd.DataFrame,
                  test_X: pd.DataFrame,
                  features: dict[str, dict[str, Any]]
                  ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Transform the train and the test dataset by applying the generated
        feature transformation rules to the given data.

        Parameters
        ----------
        train_X : pd.DataFrame
            The training dataset to transform.
        test_X : pd.DataFrame
            The test dataset to transform.
        features : dict
            The features to apply to the dataset. This dictionary should be
            previously applied by calling the ask method from the generator.

        Returns
        -------
        train_X, test_X : tuple[pd.DataFrame, pd.DataFrame]
            The transformed training and test dataset.
        """

        for feature in features:
            operator = features[feature]["operator"]
            transform_features = features[feature]["features"]
            feature_name = features[feature]["name"]
            try:
                train_feature, mapping = self._build_feature(train_X,
                                                             operator,
                                                             None,
                                                             transform_features)
                train_feature.name = feature_name
            except Exception as e:
                logger.error(f"Error occured during transformation of the \
training dataset: {str(e)}")
                continue

            try:
                test_feature, mapping = self._build_feature(test_X,
                                                            operator,
                                                            mapping,
                                                            transform_features)
                test_feature.name = feature_name
            except Exception as e:
                logger.error(f"Error occured during transformation of the \
test dataset: {str(e)}")
                continue

            # check whether a feature with that name was already created and
            # added to the dataset
            if feature_name in train_X.columns:
                logger.info(f"Feature of name {feature_name} already exists \
in the training dataset. Checking whether the new feature and the existing \
feature are equal.")
                if train_X[feature_name].equals(train_feature):
                    logger.info(f"Feature of name {feature_name} is equal to \
the newly created feature. Skipping adding the new feature to the dataset.")
                    continue
                else:
                    # change name to placeholder name from generator
                    name = feature
                    logger.info(f"Feature of name {feature_name} is not equal \
to the existing feaure. Adding the new feature to the dataset under name \
{name}.")
            train_X = pd.concat([train_X, train_feature], axis=1)
            test_X = pd.concat([test_X, test_feature], axis=1)

        return train_X, test_X

    def _generate(self,
                  dataset: Dataset,
                  max_retries: int = 5,
                  temperature: float = 0.5,
                  max_tokens: int = 300,
                  feedback: dict[str, str] = {},
                  **kwargs
                  ) -> tuple[str, str, list[str], str, str]:
        """
        Generate a singular feature from a dataset.

        Parameters
        ----------
        dataset : Dataset
            The dataset to generate the feature for.
        max_retries : int
            The maximum number of retries to generate a feature, whenever the
            LLM generates a non-parseable output. Default is 5.
        temperature : float
            The temperature to run inference at.
        max_tokens : int
            The maximum number of tokens the model is allowed to generate.
        kwargs : dict
            Additional keyword arguments for further defining the inference at
            the model. These keywords will be passed to the model when the
            chat_completion endpoint is called. Should match OpenAI API specs.
            ref: https://platform.openai.com/docs/api-reference/chat/create

        Returns
        -------
        [name, operator, features, features_combination, description, reasoning] : tuple[str, str, list[str], str, str, str]
            A tuple containing:
                name: the name of the new feature,
                operator: the operator to apply,
                features: the features to apply the operator to,
                features_combination: a unparsed string representation of the features,
                description: the description of the new feature,
                reasoning: the reasoning behind the new feature,
        """
        max_retries = max_retries
        retries = 0

        while retries < max_retries:
            feature_str = self._fit(dataset=dataset,
                                    temperature=temperature,
                                    max_tokens=max_tokens,
                                    feedback=feedback,
                                    **kwargs)

            if feature_str is None:
                logger.error("Received no instructions to generate the new \
    feature, quitting")
                return None, None, None, None, None, None

            # extract the feature, order is Feature, Name, Description, Reasoning
            pattern = r'([A-Z]+):\s*(.*?)\s*(?=(?:[A-Z]+:)|(?:\n\n)|$)'
            matches = re.findall(pattern, feature_str, re.DOTALL)
            infos = {key: value.strip() for key, value in matches}
            try:
                reasoning = infos["REASONING"]
                operator = re.findall(r'[A-Za-z]+', infos["FEATURE"])[0]
                features = re.findall(r'[0-9]+', infos["FEATURE"])

                features_combination = str(infos["FEATURE"])
                name = str(infos["NAME"]).strip(';')  # remove trailing ;
                description = str(infos["DESCRIPTION"])
            except Exception as e:
                logger.error(f"Received an error trying to extract the \
feature from the response: {str(e)}. Retrying for {retries +1} of \
{max_retries} retries.")
                retries += 1
                # TODO: return empty feedback for now if generated feature
                # breaks
                feedback = {}
                continue

            # check if the feature can be created
            ds_features = list(dataset.X.columns)
            ok = self._validate_llm_output(operator=operator,
                                           selected_features=features,
                                           dataset_features=ds_features)

            if not ok:
                logger.warn(f"Proposed feature could not be validated. \
Retrying {retries +1} of {max_retries} retries.")
                retries += 1
                # TODO: return empty feedback for now if generated feature breaks
                feedback = {}
                continue

            try:
                logger.info(f"Generated feature: {name}")
                logger.info(f"Operator: {operator}")
                logger.info(f"Features: {features}")
                logger.info(f"Reasoning: {reasoning}")
            except Exception as e:
                logger.error(f"Received an error trying to log the generated \
    feature: {str(e)}")

            break

        if name and operator and features and features_combination and description and reasoning:
            return name, operator, features, features_combination, description, reasoning

        return None, None, None, None, None, None
