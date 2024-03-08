import time

from matching_utilities.address_utils import (split_into_parts,
                                              process_addr,
                                              contains_letters_and_numbers)

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

    city = addr_dict['City'].lower().strip()
    state = addr_dict['State'].lower().strip()
    zip_code = addr_dict['Zip'].strip()

    if not addr1_stripped and not addr2_stripped:
        return ''
    elif addr1_stripped == addr2_stripped:
        if street_contains_csz(addr1_stripped, city, state, zip_code):
            return "skip"
        return addr_dict['Address 1']
    else:
        addr1_stripped = '' if street_contains_csz(addr1_stripped, city, state, zip_code) else addr1_stripped
        addr2_stripped = '' if street_contains_csz(addr2_stripped, city, state, zip_code) else addr2_stripped
        if state == "ut":
            old_addr1_stripped = addr1_stripped[:]
            addr1_stripped, addr2_stripped = (
                is_split_utah_address(addr1_stripped, addr2_stripped))
            # if the address changed, update the address that will be returned
            if addr1_stripped != old_addr1_stripped:
                addr_dict['Address 1'] = addr1_stripped
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


def is_split_utah_address(addr1, addr2) -> tuple[str, str]:
    """
    Check if two addresses are actually a split Utah address
    :param addr1: address 1
    :param addr2: address 2
    :return: True if it meets the specific conditions for a split Utah address, False otherwise
    """
    # Initial processing to check if the address is too complex to be a Utah address
    if not split_into_parts(addr1) or not split_into_parts(addr2):
        return addr1, addr2

    # try to isolate cardinal directions from the address parts
    addr1_parts = process_addr(addr1)
    addr2_parts = process_addr(addr2)
    addr1_dirs = [DIRECTIONS[part] for part in addr1_parts if part in DIRECTIONS]
    addr2_dirs = [DIRECTIONS[part] for part in addr2_parts if part in DIRECTIONS]

    # Check if there is exactly one unique direction in each part and they are not the same
    if (len(addr1_dirs) == 1
            and len(addr2_dirs) == 1
            and set(addr1_dirs) != set(addr2_dirs)):
        return f"{addr1} {addr2}", ""
    return addr1, addr2


def street_contains_csz(addr: str, city: str, state: str, zip_code: str) -> bool:
    """
    Check if the street address (address1 or address2) contains the city, state, or zip
    :param addr: address to check
    :param city: city to check for in the address
    :param state: state to check for in the address
    :param zip_code: zip code to check for in the address
    :return: boolean
    """
    if city and city in addr:
        return True
    if state and state in split_into_parts(addr):
        return True
    if zip_code and zip_code.split('-')[0] in addr:
        return True
    return False
