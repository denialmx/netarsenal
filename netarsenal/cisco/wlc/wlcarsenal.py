from ntc_templates.parse import parse_output
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir import InitNornir as Nornir
from nornir.core.task import AggregatedResult
from netarsenal.mock import Marsenal
import netarsenal.cisco.wlc.wlcex as wlcex
from easysnmp import Session

# definitions

# class


class WLCArsenal(object):
    def __init__(self):
        print("Creating WLC Object")

    def _send_command(
        self, devices: Nornir, mock: Marsenal = None, *args, **kwargs
    ) -> AggregatedResult:

        # Variables
        command = ""
        use_textfsm = True

        if "use_textfsm" in kwargs:
            use_textfsm = kwargs["use_textfsm"]
        if "command_string" in kwargs:
            command = kwargs["command_string"]

        params = {
            "command_string": command,
            "use_textfsm": use_textfsm,
        }

        if mock != None and mock.save_state:
            params["use_textfsm"] = False
        if devices:
            result = devices.run(task=netmiko_send_command, **params)
        if mock != None and mock.save_state:
            for device in result:
                mock.save_state_of_device(device, result[device].result, command)
                if use_textfsm:
                    result[device][0].result = parse_output(
                        platform="cisco_wlc_ssh",
                        command=command,
                        data=result[device].result,
                    )

        return result

    def ap_exists(self, devices: Nornir, *args, **kwargs) -> dict:
        """Check if an AP (name) exists in a WLC

        Args:
            devices (Nornir): WLCs to check if AP exists
            args (optional): Not in use
            kwargs (Dict):
              ap_name (str): Name of the AP to look for.

        Returns:
            dict: {WLCNAME:True} if found, {WLCNAME:False} if not found
        """
        # Variables
        ap_name = ""
        result = {}

        # Implementation
        if "ap_name" in kwargs:
            ap_name = kwargs["ap_name"]
            command = "show ap config general {}".format(ap_name)
        else:
            raise wlcex.RequiredParameterMissing

        data = self._send_command(devices, command_string=command, use_textfsm=True)

        for device in data:
            if "name" in data[device].result[0]:
                if data[device].result[0]["name"] == ap_name:
                    result.update({device: True})
                else:
                    result.update({device: False})
            else:
                result.update({device: False})

        return result
