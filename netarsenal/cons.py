# imports
import netarsenal.exceptions as netex
import re

# constants

platform_mapping = {
    "functions": {
        "_get_l2_neighbors": {
            "cisco_ios": "_send_command|show cdp neighbors detail",
            "nxos": "_send_command|show cdp neighbors detail",
            "mock": "_send_command|show cdp neighbors detail",
        },
        "_get_facts": {"cisco_ios": "_get_facts", "mock": "_get_facts",},
        "get_all_waps": {
            "cisco_wlc_ssh": "_send_command|show ap summary",
            "mock": "_send_command|show ap summary",
        },
    },
    "models": {
        "C2960": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
            "ios": "cat2960",
        },
        "C2970": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C9300": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C9500": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C3850": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C3650": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C3750": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C4500X": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C3560C": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "C3560": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        "BR1310G": {
            "type": "network_switch",
            "vendor": "cisco",
            "platform": "cisco_ios",
        },
        # "ISR4331": {
        #    "type": "network_router",
        #    "vendor": "cisco",
        #    "platform": "cisco_ios",
        # },
        # "C819G": {
        #    "type": "network_router",
        #    "vendor": "cisco",
        #    "platform": "cisco_ios",
        # },
        # "^Cisco IP Phone": {
        #    "type": "ip_phone",
        #    "vendor": "cisco",
        #    "platform": "cisco_ip_phone",
        # },
    },
}


def return_platform(name: str, types: str = "functions", *args, **kwargs) -> dict:
    """ Return platform specific data

    Args:
        name (str): pattern to look for
        types (str, optional): Type of data to look for. Defaults to "functions".

    Raises:
        netex.CallableFunctionUndefined: [description]

    Returns:
        dict: Dictionary of data
    """

    if types == "functions":
        if name in platform_mapping[types]:
            return platform_mapping[types][name]
    if types == "models":
        for model in platform_mapping["models"]:
            if re.search(model, name):
                return platform_mapping["models"][model]
    else:
        raise netex.CallableFunctionUndefined()
