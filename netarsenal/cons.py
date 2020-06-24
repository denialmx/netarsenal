# imports
import netarsenal.exceptions as netex

# constants

platform_mapping_commands = {
    "functions": {
        "_get_l2_neighbors": {
            "ios": "show_cdp_neighbors",
            "nxos": "show_cdp_neighbors",
            "mock": "mock_send_command",
        }
    },
    "commands": {"show version": {"ios": True, "nxos": True}},
}


def return_platform_function(name, type="functions"):
    if name in platform_mapping_commands["functions"]:
        return platform_mapping_commands["functions"][name]
    else:
        raise netex.CallableFunctionUndefined()
