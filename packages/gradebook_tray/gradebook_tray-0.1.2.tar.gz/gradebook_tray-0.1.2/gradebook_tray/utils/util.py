from datetime import datetime


def tolerant_float(value: str) -> float:
    """Convert a string to a float, returning nan if the conversion fails

    Args:
        value (str): The string to convert

    Returns:
        float: The converted value
    """

    if value is None:
        return float("nan")

    try:
        return float(value)
    except ValueError:
        return float("nan")


def tolerant_datetime(value: str, fmt: str = "%m/%d/%Y") -> datetime:
    """Convert a string to a datetime, returning None if the conversion fails

    Args:
        value (str): The string to convert
        fmt (str, optional): The format of the string. Defaults to "%m/%d/%Y".

    Returns:
        datetime: The converted value
    """

    if value is None:
        return datetime.min

    try:
        if fmt == "iso":
            return datetime.fromisoformat(value)
        else:
            return datetime.strptime(value, fmt)
    except ValueError:
        return datetime.min
