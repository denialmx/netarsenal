from ntc_templates.parse import parse_output
from nornir import InitNornir as Nornir
from netarsenal.mock import Marsenal
from nornir.core.task import AggregatedResult
from nornir.plugins.tasks.networking import netmiko_send_command


# definitions

# class


class IOSArsenal(object):
    def __init__(self):
        print("Creating IOS Object")

    def _send_command(
        self, devices: Nornir, mock: Marsenal = None, *args, **kwargs
    ) -> AggregatedResult:

        # Variables
        command = ""
        use_textfsm = False

        if "use_textfsm" in kwargs and "command_string" in kwargs:
            use_textfsm = kwargs["use_textfsm"]
            command = kwargs["command_string"]

        params = {
            "command_string": command,
            "use_textfsm": use_textfsm,
        }

        if mock.save_state:
            params["use_textfsm"] = False
        if devices:
            result = devices.run(task=netmiko_send_command, **params)
        if mock.save_state:
            for device in result:
                if not result[device].failed:
                    mock.save_state_of_device(device, result[device].result, command)
                    if use_textfsm:
                        result[device][0].result = parse_output(
                            platform="cisco_ios",
                            command=command,
                            data=result[device].result,
                        )
                else:
                    print(1)

        return result

    def show_cdp_neighbors(self, devices: Nornir, *args, **kwargs):
        return 1

