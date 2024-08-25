"""
Common functions used in workflows
"""


def validate_type(type: str) -> str:
    if type == "timeseries":
        type = "indicator"

    return type
