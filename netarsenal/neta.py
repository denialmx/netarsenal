# imports
import sys
import ruamel.yaml
import re
from copy import deepcopy, copy

from nornir import InitNornir as Nornir
from nornir.core.filter import F

from netarsenal.cisco.ios import iosarsenal
from netarsenal.cisco.nxos import nxosarsenal
from netarsenal.cisco.wlc import wlcarsenal
from netarsenal.mock import Marsenal
import netarsenal.cons as cons
import netarsenal.helpers as nethelpers
import netarsenal.exceptions as netex

# definitions

# class


class NetArsenal(object):
    # variables
    # objects
    nornir = object
    netmiko = object
    textfm = object

    arsenal = {
        "cisco_ios": iosarsenal.IOSArsenal(),
        "nxos": nxosarsenal.NXOSArsenal(),
        "mock": Marsenal.MockArsenal(),
        "cisco_wlc_ssh": wlcarsenal.WLCArsenal(),
        "viptela": object,
    }

    ios = arsenal["cisco_ios"]
    nxos = arsenal["nxos"]
    mock = arsenal["mock"]
    wlc = arsenal["cisco_wlc_ssh"]

    # init
    def __init__(self, configfile, num_workers, mock_path=None):
        if mock_path:
            self.mock.opendb(mock_path, True)
        self.nornir = Nornir(
            config_file=configfile,
            core={"num_workers": num_workers},
            inventory={"plugin": "netarsenal.inventory.include.Includentory"},
        )

    def mock_record(self, db_file=None) -> int:
        return self.mock.record()

    def _mock_pause(self):
        self.mock.pause()

    def mock_check(self):
        return self.mock.check()

    def mock_start(self):
        return self.mock.start()

    def _build_parameters(self, parameters):
        # Variables
        params = {}

        # Implementation
        if "use_textfsm" in parameters:
            params.update({"use_textfsm": parameters["use_textfsm"]})
        if "command" in parameters:
            params.update({"command_string": parameters["command"]})
        return params

    def __execute_and_aggregate(
        self, devices: Nornir, divider: str = "platform", *args, **kwargs
    ) -> list:

        # Variables
        results = []
        current_pop_filter = ""
        parameters = {}

        # Implementation
        # Check for kwargs and build parameters to send to function_to_call
        parameters = self._build_parameters(kwargs)
        source_function = sys._getframe(1).f_code.co_name
        function_to_call = cons.return_platform(source_function)
        # TODO validate nornir is object of Nornir
        t_devices = deepcopy(devices)
        pop = dict(t_devices.inventory.hosts)

        if self.mock_check():
            if self.mock.use_mock:
                self.mock.change_platform(t_devices)
                self.mock.mock_command = source_function

        while len(pop) > 0:
            if len(pop) > 1:
                completed = []
                for host in list(t_devices.inventory.hosts):
                    # Check platform of host
                    pop_filter = getattr(t_devices.inventory.hosts[host], divider)
                    # split pop_filter with an -
                    # pop_filter[0] will always have the right platform, either
                    # ios, nxos, mock
                    pop_filter = pop_filter.split("-")[0]
                    if not current_pop_filter:
                        current_pop_filter = pop_filter
                    if pop_filter != current_pop_filter:
                        t_devices.inventory.hosts.pop(host)
                    else:
                        completed.append(host)

                # TODO
                # Error handling if platform does not exist
                try:
                    if "|" in function_to_call[current_pop_filter]:
                        FN = function_to_call[current_pop_filter].split("|")
                        function_to_call = FN[0]
                        command = FN[1]
                        parameters.update({"command_string": command})
                    else:
                        function_to_call = function_to_call[current_pop_filter]
                    N = getattr(self.arsenal[current_pop_filter], function_to_call)
                    result = N(t_devices, self.mock, **parameters)
                    results.append(result)
                except KeyError as e:
                    print(e)
                if len(t_devices.inventory.hosts) > 1:
                    t_devices.inventory.hosts = dict(pop)
                    for index in range(0, len(completed), 1):
                        t_devices.inventory.hosts.pop(completed[index])
                    pop = dict(t_devices.inventory.hosts)
                    current_pop_filter = None
                    index = 0
            else:
                host = next(iter(t_devices.inventory.hosts))
                # Check platform of host
                current_pop_filter = getattr(t_devices.inventory.hosts[host], divider)
                current_pop_filter = current_pop_filter.split("-")[0]
                if "|" in function_to_call[current_pop_filter]:
                    FN = function_to_call[current_pop_filter].split("|")
                    function_to_call = FN[0]
                    command = FN[1]
                    parameters.update({"command_string": command})
                N = getattr(self.arsenal[current_pop_filter], function_to_call)
                result = N(t_devices, self.mock, **parameters)
                results.append(result)
                pop.pop(host)
        return results

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
                value = value.strip()
                if value:
                    # TODO input a Dict to avoid if cases
                    # For example f = F(**{'site':'value'})
                    if attribute == "site":
                        if initiator:
                            f = F(site=value)
                            initiator = False
                        else:
                            f = f | F(site=value)
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

        result = self.nornir.filter(f)
        return result

    def _get_l2_neighbors(self, nornir=object, *args, **kwargs):

        # Variables
        use_textfsm = False

        # Implementation
        if "use_textfsm" in kwargs:
            use_textfsm = kwargs["use_textfsm"]

        results = self.__execute_and_aggregate(nornir, use_textfsm=use_textfsm)
        return results

    def discover_l2_devices(self, devices: Nornir, *args, **kwargs):

        # Variables
        l2_neighbors = {}
        t_nornir = deepcopy(devices)
        completed = []
        use_textfsm = False

        # Implementation
        if "structured" in kwargs:
            use_textfsm = kwargs["structured"]
        if "ignorelist" in kwargs:
            completed = kwargs["ignorelist"]

        if t_nornir:
            new_host = deepcopy(self.nornir.inventory.hosts["NEWHOST"])
            results = self._get_l2_neighbors(t_nornir, use_textfsm=use_textfsm)
            for platform in results:
                for host in platform:
                    # l2_neighbors[host] = deepcopy(t_nornir.inventory.hosts[host])
                    groups = devices.inventory.hosts[host].groups.data
                    # Build nornir object dynamically
                    for l2_device in platform[host].result:
                        root_exists = nethelpers.check_regex_in_list(host, completed)
                        if not root_exists:
                            if not nethelpers.check_regex_in_list(
                                l2_device["destination_host"], completed
                            ) and not nethelpers.check_regex_in_list(
                                l2_device["destination_host"], host
                            ):
                                platform_values = cons.return_platform(
                                    l2_device["platform"], "models"
                                )
                                # We are not interested in devices with no model defined in cons.py
                                if platform_values:
                                    new_host.name = l2_device["destination_host"]
                                    new_host.hostname = l2_device["management_ip"]
                                    new_host.platform = platform_values["platform"]
                                    new_host.data["type"] = platform_values["type"]
                                    new_host.data["vendor"] = platform_values["vendor"]
                                    new_host.groups = groups
                                    l2_neighbors[new_host.name] = deepcopy(new_host)
                                    completed.append(new_host.name)
                        else:
                            root_name = nethelpers.check_regex_in_list(
                                host, completed, match=True
                            )
                            l2_neighbors.pop(root_name)
                            completed.remove(root_name)
        return devices

    # ----------------- #
    # CISCO WLC METHODS #
    # ----------------- #

    def get_all_waps(self, devices: Nornir, *args, **kwargs):

        # Variables
        result = {}
        use_textfsm = False

        # Implementation
        if "use_textfsm" in kwargs:
            use_textfsm = kwargs["use_textfsm"]

        result = self.__execute_and_aggregate(devices, use_textfsm=use_textfsm)
        return result

