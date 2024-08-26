"""text_utils

Text utility functions
"""


def str2bool(string: str) -> bool:
    """str2bool Converts strings to booleans

    Function to convert strings to booleans.
    Any of `yes`, `y`, `true`, `t`, `1` return as true

    :param v: String to convert
    :type v: str
    :return: if converted
    :rtype: bool
    """
    return string.lower() in {"yes", "y", "true", "t", "1"}
