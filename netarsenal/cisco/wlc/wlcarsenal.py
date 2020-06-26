from ntc_templates.parse import parse_output

from nornir.plugins.tasks.networking import netmiko_send_command

# definitions

# class


class WLCArsenal(object):
    def __init__(self):
        print("Creating WLC Object")

    def send_command(self, devices, mock, command: str, use_textfsm: str = True):
        """[summary]

        Args:
            devices ([type]): [description]
            mock ([type]): [description]
            command (str): [description]
            use_textfsm (str, optional): [description]. Defaults to True.
        """
        print(2)
