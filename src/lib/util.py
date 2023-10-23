def with_defaults(*values):
    """
    Takes a list of values, returning the first one which is not None.
    """

    for value in values:
        if value is not None:
            return value

    return None


def index_default(list, index, default):
    """
    Get index, if oob then default
    """

    return list[index] if index >= 0 and index < len(list) else default
