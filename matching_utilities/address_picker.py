def select_address(addr1: str, addr2: str) -> str:
    """
    Select the best address from two addresses
    :param addr1: first address
    :param addr2: second address
    :return: ideal address
    """
    addr1_stripped = addr1.lower().strip()
    addr2_stripped = addr2.lower().strip()
    addr1_stripped = addr1_stripped if addr1_stripped != "null" else ""
    addr2_stripped = addr2_stripped if addr2_stripped != "null" else ""

    if not addr1_stripped and not addr2_stripped:
        return ''
    elif addr1_stripped == addr2_stripped:
        return addr1
    else:
        addr1_has_alnum = contains_letters_and_numbers(addr1_stripped)
        addr2_has_alnum = contains_letters_and_numbers(addr2_stripped)
        if not addr1_has_alnum and not addr2_has_alnum:
            return ''
        if addr1_has_alnum and not addr2_has_alnum:
            return addr1
        elif addr2_has_alnum and not addr1_has_alnum:
            return addr2
        elif addr1_has_alnum and addr2_has_alnum:
            if "box" in addr1_stripped:
                return addr1
            if "box" in addr2_stripped:
                return addr2
        return addr1
        # TODO: add case for those weird Utah addresses, e.g. 1234 N 5678 W


def contains_letters_and_numbers(s) -> bool:
    """
    Check if a string contains both letters and numbers
    :param s: string to check
    :return: whether the string contains both letters and numbers
    """
    contains_letters = any(c.isalpha() for c in s)
    contains_numbers = any(c.isdigit() for c in s)
    return contains_letters and contains_numbers
