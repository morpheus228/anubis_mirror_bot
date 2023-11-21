def number_validation(string: str) -> int|float|None:
    try:
        return int(string)
    except:
        pass

    try:
        return float(string)
    except:
        return None
            