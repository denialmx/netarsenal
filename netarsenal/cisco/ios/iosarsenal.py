from ntc_templates.parse import parse_output

from nornir.plugins.tasks.networking import netmiko_send_command

# definitions

# class


class IOSArsenal(object):
    def __init__(self):
        print("Creating IOS Object")

    def show_cdp_neighbors(self, nornir=object, use_textfsm=False, mock=None):
        command = "show cdp neighbors detail"
        params = {
            "command_string": command,
            "use_textfsm": use_textfsm,
        }

        if mock:
            params["use_textfsm"] = False

        # Need to fix this, as sometimes mock = None and this fails
        if nornir and not mock.use_mock:
            result = nornir.run(task=netmiko_send_command, **params)
        else:
            result = nornir.run(task=netmiko_send_command, **params)
        if mock:
            for device in result:
                mock.save_state_of_device(device, result[device].result, command)
                if use_textfsm:
                    result[device].result = parse_output(
                        platform="cisco_ios",
                        command=command,
                        data=result[device].result,
                    )

        return result
