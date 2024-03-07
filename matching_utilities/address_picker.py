import re


# Define cardinal directions and their abbreviations
DIRECTIONS = {
    'n': 'north',
    's': 'south',
    'e': 'east',
    'w': 'west',
    'north': 'north',
    'south': 'south',
    'east': 'east',
    'west': 'west'
}


def select_address(addr_dict: dict) -> str:
    """
    Select the best address from two addresses
    :param addr_dict: dictionary of address components
    :return: ideal address
    """
    addr2 = addr_dict['Address 2'].rstrip(". Please review. Address Line 2 is not blank.")
    addr1_stripped = addr_dict['Address 1'].lower().strip()
    addr2_stripped = addr2.lower().strip()
    addr1_stripped = addr1_stripped if addr1_stripped != "null" else ""
    addr2_stripped = addr2_stripped if addr2_stripped != "null" else ""

    if not addr1_stripped and not addr2_stripped:
        return ''
    elif addr1_stripped == addr2_stripped:
        return addr_dict['Address 1']
    else:
        addr1_has_alnum = contains_letters_and_numbers(addr1_stripped)
        addr2_has_alnum = contains_letters_and_numbers(addr2_stripped)
        if not addr1_has_alnum and not addr2_has_alnum:
            return ''
        if addr1_has_alnum and not addr2_has_alnum:
            return addr_dict['Address 1']
        elif addr2_has_alnum and not addr1_has_alnum:
            return addr2
        elif addr1_has_alnum and addr2_has_alnum:
            if "box" in addr1_stripped:
                return addr_dict['Address 1']
            if "box" in addr2_stripped:
                return addr2
        return addr_dict['Address 1']
        # TODO: add case for those weird Utah addresses, e.g. 1234 N 5678 W
        # TODO: add check for city or state in the address1 field
        # TODO: refactor this function to take a dict with address1, address2, city, state, and zip


def contains_letters_and_numbers(s: str) -> bool:
    """
    Check if a string contains both letters and numbers
    :param s: string to check
    :return: whether the string contains both letters and numbers
    """
    contains_letters = any(c.isalpha() for c in s)
    contains_numbers = any(c.isdigit() for c in s)
    return contains_letters and contains_numbers


def is_split_utah_address(addr1, addr2):
    """
    Check if two addresses are actually a split Utah address
    :param addr1: address 1
    :param addr2: address 2
    :return: True if it meets the specific conditions for a split Utah address, False otherwise
    """
    def _process_initial(addr: str) -> list[str]:
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

    def _process_addr(addr: str) -> list[str]:
        """
        Step 1, 2, and 3: Lowercase, replace non-alpha chars, and split by spaces
        :param addr: address string to process
        :return: list of strings after processing
        """
        return [s.strip() for s in ''.join(
            c if c.isalpha() else ' '
            for c in addr.lower()).split()]

    # Initial processing to check the new condition
    if not _process_initial(addr1) or not _process_initial(addr2):
        return False  # Early return if the new condition fails

    addr1_parts = _process_addr(addr1)
    addr2_parts = _process_addr(addr2)
    addr1_dirs = [DIRECTIONS[part] for part in addr1_parts if part in DIRECTIONS]
    addr2_dirs = [DIRECTIONS[part] for part in addr2_parts if part in DIRECTIONS]

    # Check if there is exactly one unique direction in each part and they are not the same
    if (len(addr1_dirs) == 1
            and len(addr2_dirs) == 1
            and set(addr1_dirs) != set(addr2_dirs)):
        return True
    return False
