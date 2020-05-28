# imports
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F

# definitions

# class


class NetArsenal(object):
    # variables
    neta = object
    netmiko = object
    textfm = object

    # init
    def __init__(self, config_file, num_workers):
        self.neta = InitNornir(
            core={"num_workers": num_workers},
            inventory={"plugin": "netarsenal.inventory.include.Includentory"},
        )

    def show_command(self, command):
        # variables
        result = ""

        if "show" in command:
            try:
                result = self.neta.run(
                    task=netmiko_send_command, command_string=command
                )
            except:
                result = {"status": 500}
        return result

    def get_hosts_from_sites(self, *args, **kwargs):
        for site in kwargs:
            if site == "site":
                site_list = kwargs["site"]
        sites = self.neta.filter(F(groups__contains=site_list))
        return sites
