from ntc_templates.parse import parse_output
from nornir import InitNornir as Nornir
from netarsenal.mock import Marsenal
from nornir.core.task import AggregatedResult
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.networking import netmiko_send_config


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
        use_textfsm = True
        commands = False
        enable = False
        result_list = {}

        # TODO Finish implementing 'always send templated data'

        if "use_textfsm" in kwargs:
            use_textfsm = kwargs["use_textfsm"]
        if "command_string" in kwargs:
            command = kwargs["command_string"]
        if "command" in kwargs:
            command = kwargs["command"]
            if not isinstance(command, str):
                # This is a list of commands
                commands = True
        if "enable" in kwargs:
            enable = kwargs["enable"]

        params = {
            "command_string": command,
            "use_textfsm": use_textfsm,
            "enable": enable,
        }

        if mock != None:
            if mock.save_state:
                params["use_textfsm"] = False
        if devices:
            if commands:
                for current_command in command:
                    params.update(
                        {
                            "command_string": current_command,
                            "delay_factor": 10,
                            "max_loops": 500,
                        }
                    )
                    # When sockets are closed, this fails
                    # Need to find a way to reopen the socket
                    result_list[current_command] = devices.run(
                        task=netmiko_send_command, **params
                    )
                result = result_list
            else:
                result = devices.run(task=netmiko_send_command, **params)
        if mock != None:
            if mock.save_state:
                for device in result:
                    if not result[device].failed:
                        mock.save_state_of_device(
                            device, result[device].result, command
                        )
                        if use_textfsm:
                            result[device][0].result = parse_output(
                                platform="cisco_ios",
                                command=command,
                                data=result[device].result,
                            )
                    else:
                        print(1)

        return result

    def _get_facts(self, devices: Nornir, mock: Marsenal = None, *args, **kwargs):
        # Get serial number model and current IOS

        # Variables

        result = self._send_command(
            devices, mock, command="show version", use_textfsm=True
        )

        for device in result:
            if len(result[device].result[0]["hardware"]) > 1:
                result[device].result[0].update({"stack": True})
            else:
                result[device].result[0].update({"stack": False})
        return result
