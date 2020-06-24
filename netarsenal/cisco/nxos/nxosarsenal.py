from nornir.plugins.tasks.networking import netmiko_send_command

# definitions

# class


class NXOSArsenal(object):
    def __init__(self):
        print("Creating NXOS Object")

    def show_cdp_neighbors(self, nornir_object=None, use_textfsm=False):
        command = "show cdp neighbors detail"
        params = {
            "command_string": command,
            "use_textfsm": use_textfsm,
        }

        if nornir_object:
            result = nornir_object.run(task=netmiko_send_command, **params)
        return result
