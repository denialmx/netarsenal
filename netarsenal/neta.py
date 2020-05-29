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

    def get_hosts_with_simple_filter(self, *args, **kwargs):
        attribute_list = ""
        filter_list = []

        for attribute in kwargs:
            initiator = True
            if "," in kwargs[attribute]:
                attribute_list = kwargs[attribute].split(",")
            else:
                attribute_list = kwargs[attribute].split()
            for value in attribute_list:
                if attribute == "site":
                    if initiator:
                        f = F(groups__contains=value)
                        initiator = False
                    else:
                        f = f | F(groups__contains=value)
                    continue
                if attribute == "role":
                    if initiator:
                        f = F(role=value)
                        initiator = False
                    else:
                        f = f | F(role=value)
                    continue
                if attribute == "platform":
                    if initiator:
                        f = F(platform=value)
                        initiator = False
                    else:
                        f = f | F(platform=value)
                    continue
            filter_list.append(f)

        for i in range(len(filter_list)):
            if i == 0:
                f = filter_list[i]
            else:
                f = f & filter_list[i]
        hosts = self.nornir.filter(f)
        return hosts
