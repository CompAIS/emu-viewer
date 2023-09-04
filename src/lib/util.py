def with_defaults(*values):
    """
    Takes a list of values, returning the first one which is not None.
    """

    for value in values:
        if value is not None:
            return value

    return None
