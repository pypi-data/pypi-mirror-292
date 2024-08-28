import logging
import pandas as pd

from remoteinference.util import system_prompt, user_prompt, assistant_prompt
from caafg.dataset import Dataset
from caafg.generators.blueprintcaafg.consts import SHORT_OPERATOR_STRING, \
    BLIND_OPERATOR_STRING
logger = logging.getLogger(__name__)

# TODO: maybe transform the get_XX_prompt functions into internal helper
# functions of the build_XX_prompt functions


def get_dataset_prompt(dataset_description: str,
                       dataset_name: str) -> str:
    return f"""Dataset Name: {dataset_name}
    Dataset Description: {dataset_description}
    """


def get_operator_prompt() -> str:
    """
    Pass a list of all possible operators. We use the operators used in
    the OpenFE paper only.
    """
    operators = SHORT_OPERATOR_STRING

    return operators


def get_stats_prompt(X: pd.DataFrame) -> str:
    """
    Generate the statistics prompt.
    """

    features = list(X.columns)
    stats_prompt = ""
    for i, feature in enumerate(features):
        f_type = X[feature].dtype
        f_size = X[feature].size
        f_vals = X[feature].count()
        f_distinct = X[feature].nunique()

        if f_type == "object" or f_type == "category":
            f_max = "EMPTY"
            f_min = "EMPTY"
            f_mean = "EMPTY"
            f_var = "EMPTY"
        else:
            f_max = X[feature].max()
            f_min = X[feature].min()
            f_mean = X[feature].mean()
            f_var = X[feature].var()

        f_missing = X[feature].isnull().sum()
        f_name = feature

        stats_template = f"Feature {i+1}: Type: {f_type}, \
Feature size: {f_size}, Number of values: {f_vals}, \
Number of distinct values: {f_distinct}, \
Number of missing values: {f_missing}, Max: {f_max}, Min: {f_min}, \
Mean: {f_mean}, Variance: {f_var}, Name: {f_name}"
        stats_prompt += ("\n"+stats_template)
    return stats_prompt


def build_system_prompt() -> dict[str, str]:
    """
    Generate the system prompt.

    Returns the system prompt as a dictionary in correct OpenAI format.
    """

    operator_description = "Operator: Add, Description: Binary."

    content = f"""You are an expert data scientist performing effective \
feature engineering on a dataset. You will get a short description of every \
feature in the dataset. This description will contain some statistical \
information about each feature.

Example of the information you will get about a feature:
Feature 1: Type: int64, Feature size: 100, Number of values: 100, Number of \
distinct values: 100, Number of missing values: 0, Max: 100, Min: 0, \
Mean: 50, Variance: 100, Name: name. Sample: First couple of rows of the \
dataset.

If some value carries the value EMPTY, it means that this value is not \
applicable for this feature.

You will also be provided a set of operators with a short description of what \
each operator does. There are unary and binary operators. Unary operators \
take one feature as input and binary operators take two features as input.

Example of the information you will get about an operator:
{operator_description}

You are now asked to generate a new feature using the information from the \
features and the information from the operators as well as your own \
understanding of the dataset and the given domain. There will be an example \
of how your response should look like. You will only answer following this \
example. Your response will containg nothing else. You are only allowed to \
select operators from the list of operators and features from the list of \
features. Your are only allowed to generate one new feature.
Your newly generated feature will then be added to the dataset."""

    return system_prompt(content)


def build_user_prompt(dataset: Dataset,
                      feedback: dict[str, str]) -> dict[str, str]:
    """
    Generate the user prompt.

    :param dataset: The dataset to generate features from.

    Returns the user prompt as a dictionary in correct OpenAI format.
    """
    dataset_template = get_dataset_prompt(
        dataset.dataset_description,
        dataset.dataset_name)

    sample_template = f"Sample: {dataset.X.head()}"

    stats_template = get_stats_prompt(dataset.X)

    operator_template = get_operator_prompt()

    instructions = """
Here is an example of how your return will look like. Suppose you want to \
apply operator A to Feature X and Feature Y. Even if you know the \
names of features X and Y you will only call them by their indices provided \
to you. You will not call them by their actual names. You will return the \
following and nothing else: \
REASONING: Your reasoning why you generated that feature.; FEATURE: A(X, Y); \
NAME: name; DESCRIPTION: This is the feature called name.    \
This feature represents ... information.
"""
    if feedback:
        logger.info(f"Got the following feedback: {feedback}")
        if "difference" in feedback and "feature" in feedback:
            if feedback["difference"] > 0:
                improvement_key = "improved"
            elif feedback["difference"] < 0:
                improvement_key = "decreased"
            else:
                improvement_key = "did not change"
            feedback = f"""
Your last generated feature was: {feedback['feature']}. This feature \
{improvement_key} the performance of the model."
"""
        else:
            feedback = ""
    else:
        feedback = ""

    content = f"""
{dataset_template}

{sample_template}

{stats_template}

{operator_template}

{instructions}

{feedback}
    """

    prompt = user_prompt(content)
    return prompt


def build_assistant_prompt(feedback: dict[str, str]) -> dict[str, str]:
    """
    Generate the assistant prompt.

    Returns the assistant prompt as a dictionary in correct OpenAI format.
    """
    content = ""
    if "feature" in feedback:
        content += f"Feature generated in last round: {feedback['feature']}"
    if "reasoning" in feedback:
        content += f"Reasoning for feature generation: {feedback['reasoning']}"
    return assistant_prompt(content)


def build_feature_from_string(X: pd.DataFrame,
                              operator: str,
                              mapping: pd.Series | None,
                              features: list[str]
                              ) -> tuple[pd.Series, pd.Series | None]:
    """
    Build a feature from a string returned by the llm.

    :param X: The dataset to generate features from.
    :param operator: The string representation of the operator that will be
        used to generate the feature.
    :param features: The indices of the features that will be used to generate
        the feature. Are one based currently.

    Return:
        [New Feature, possible mapping]
    """
    feature_num = int(features[0]) - 1
    feature_one = list(X.columns)[feature_num]

    # TODO: currently every operatoion that is executed on NaN will always
    # return also NaN. What do we want to do for binary operations?

    # only exists for binary operators
    if len(features) == 2:
        feature_num = int(features[1]) - 1
        feature_two = list(X.columns)[feature_num]

    if operator == "FrequencyEncoding":
        from .operators import frequency_encode
        new_feat, mapping = frequency_encode(X[feature_one], mapping)
    elif operator == "Absolute":
        from .operators import absolute
        new_feat = absolute(X[feature_one])
    elif operator == "Log":
        from .operators import log
        new_feat = log(X[feature_one])
    elif operator == "SquareRoot":
        from .operators import squareroot
        new_feat = squareroot(X[feature_one])
    elif operator == "Sigmoid":
        from .operators import sigmoid
        new_feat = sigmoid(X[feature_one])
    elif operator == "Round":
        from .operators import round
        new_feat = round(X[feature_one])
    elif operator == "Residual":
        from .operators import residual
        new_feat = residual(X[feature_one])
    elif operator == "Min":
        from .operators import min
        new_feat = min(X[feature_one], X[feature_two])
    elif operator == "Max":
        from .operators import max
        new_feat = max(X[feature_one], X[feature_two])
    elif operator == "Add":
        from .operators import add
        new_feat = add(X[feature_one], X[feature_two])
    elif operator == "Subtract":
        from .operators import subtract
        new_feat = subtract(X[feature_one], X[feature_two])
    elif operator == "Multiply":
        from .operators import multiply
        new_feat = multiply(X[feature_one], X[feature_two])
    elif operator == "Divide":
        from .operators import divide
        new_feat = divide(X[feature_one], X[feature_two])
    elif operator == "Combine":
        from .operators import combine
        new_feat, mapping = combine(X[feature_one], X[feature_two], mapping)
    elif operator == "CombineThenFrequencyEncoding":
        from .operators import combine_then_frequency_encode
        new_feat, mapping = combine_then_frequency_encode(X[feature_one],
                                                          X[feature_two],
                                                          mapping)
    elif operator == "GroupByThenMin":
        from .operators import group_by_then_min
        new_feat, mapping = group_by_then_min(X[feature_one],
                                              X[feature_two],
                                              mapping)
    elif operator == "GroupByThenMax":
        from .operators import group_by_then_max
        new_feat, mapping = group_by_then_max(X[feature_one],
                                              X[feature_two],
                                              mapping)
    elif operator == "GroupByThenMean":
        from .operators import group_by_then_mean
        new_feat, mapping = group_by_then_mean(X[feature_one],
                                               X[feature_two],
                                               mapping)
    elif operator == "GroupByThenMedian":
        from .operators import group_by_then_median
        new_feat, mapping = group_by_then_median(X[feature_one],
                                                 X[feature_two],
                                                 mapping)
    elif operator == "GroupByThenStd":
        from .operators import group_by_then_std
        new_feat, mapping = group_by_then_std(X[feature_one],
                                              X[feature_two],
                                              mapping)
    elif operator == "GroupByThenRank":
        from .operators import group_by_then_rank
        new_feat, mapping = group_by_then_rank(X[feature_one],
                                               X[feature_two],
                                               mapping)
    else:
        new_feat = None
        logger.error(f"Operator {operator} not found.")
    return new_feat, mapping if mapping else None
