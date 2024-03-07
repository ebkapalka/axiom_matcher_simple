import re


def contains_letters_and_numbers(s: str) -> bool:
    """
    Check if a string contains both letters and numbers
    :param s: string to check
    :return: whether the string contains both letters and numbers
    """
    contains_letters = any(c.isalpha() for c in s)
    contains_numbers = any(c.isdigit() for c in s)
    return contains_letters and contains_numbers


def split_into_parts(addr: str) -> list[str]:
    """
    Split the incoming string wherever a number and non-number are adjacent to each other,
    and then split the individual parts again by non-alphanumeric characters.  This will weed
    out any regular addresses and leave only return True for potential split Utah addresses.
    :param addr: address string to process initially
    :return: list of strings after initial processing
    """
    # Split where a number and non-number character are adjacent
    parts = re.split(r'(?<=\d)(?=\D)|(?<=\D)(?=\d)', addr)
    processed_parts = []
    for part in parts:
        # Further split by non-alphanumeric characters and filter empty strings
        sub_parts = [sub_part for sub_part in re.split(r'\W+', part) if sub_part]
        if len(sub_parts) > 2:
            return []  # Return an empty list to indicate a failure in the condition
        processed_parts.extend(sub_parts)
    return processed_parts


def process_addr(addr: str) -> list[str]:
    """
    Step 1, 2, and 3: Lowercase, replace non-alpha chars, and split by spaces
    :param addr: address string to process
    :return: list of strings after processing
    """
    return [s.strip() for s in ''.join(
        c if c.isalpha() else ' '
        for c in addr.lower()).split()]
