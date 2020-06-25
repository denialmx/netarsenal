from ntc_templates.parse import parse_output

from nornir.plugins.tasks.networking import netmiko_send_command

# definitions

# class


class WLCArsenal(object):
    def __init__(self):
        print("Creating WLC Object")

    def send_command(self, nornir=object, use_textfsm=False, mock=None):
        print(1)
