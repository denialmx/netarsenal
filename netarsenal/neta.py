# imports
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F

# definitions

# class


class NetArsenal(object):
    # variables
    nornir = object
    netmiko = object
    textfm = object

    # security definitions
    # list of safe functions to be called by eval()
    eval_safe_list = [
        "F",
    ]
    # use the list to filter the local namespace
    eval_safe_dict = dict([(k, locals().get(k, None)) for k in eval_safe_list])
    # add any needed builtins back in.
    eval_safe_dict["print_result"] = print_result

    # init
    def __init__(self, config_file, num_workers):
        self.nornir = InitNornir(
            core={"num_workers": num_workers},
            inventory={"plugin": "netarsenal.inventory.include.Includentory"},
        )

    def show_command(self, command):
        # variables
        result = ""

        if "show" in command:
            try:
                result = self.nornir.run(
                    task=netmiko_send_command, command_string=command
                )
            except:
                result = {"status": 500}
        return result

    def get_hosts_with(self, *args, **kwargs):
        attribute_list = ""
        f = F()
        for attribute in kwargs:
            if "," in kwargs[attribute]:
                attribute_list = kwargs[attribute].split(",")
                site_filter = "F(groups__contains='{}') | F(groups__contains='gor')".format(
                    attribute_list
                )
        hosts = self.nornir.filter(
            (F(groups__contains=attribute_list)) & (F(role="core") | F(role="dist"))
        )

        hosts = self.nornir.filter(site="ssp", role="core")

        # THIS IS VERY DANGEROUS
        hosts = self.nornir.filter(eval(site_filter))

        return hosts

    def get_hosts_from_groups(self, *args, **kwargs):
        hosts = {}
        for site in kwargs:
            if site == "site":
                site_list = kwargs["site"]
        hosts = self.nornir.filter(F(groups__contains=site_list))

        return hosts
