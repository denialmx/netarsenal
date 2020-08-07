# imports
import netarsenal.exceptions as netex
import re

# constants
def check_regex_in_list(pattern: str, stringlist: list, *args, **kwargs) -> any:

    return_bool = True

    if "match" in kwargs:
        return_bool = False

    element = ""
    if pattern and stringlist:
        for element in stringlist:
            if re.search(r"^{}".format(pattern), element):
                if return_bool:
                    return True
                else:
                    return element
    if return_bool:
        return False
    else:
        return ""
