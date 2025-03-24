def is_true(value):
    if type(value) == str:
        return bool(value.lower() not in ("0", "false", ""))

    return bool(value)
