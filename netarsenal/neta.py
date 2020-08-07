# imports
import sys
import ruamel.yaml
import re
from copy import deepcopy, copy
import logging
from datetime import datetime
import inspect

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
            configure_logging=False,
        )

    ##############
    # MOCK STUFF #
    ##############

    def mock_record(self, db_file=None) -> int:
        return self.mock.record()

    def _mock_pause(self):
        self.mock.pause()

    def mock_check(self):
        return self.mock.check()

    def mock_start(self):
        return self.mock.start()

    ##############
    #  L  O   G  #
    ##############

    def log(self, debug_level: str, debug_msg: str, e: Exception = None):
        # Variables
        timestamp = datetime.now()
        source_function = sys._getframe(1).f_code.co_name

        if debug_level == "debug":
            logging.debug(
                "[{}] ({}) -> {}: {}".format(
                    timestamp, debug_level, source_function, debug_msg
                )
            )
        if debug_level == "warn":
            logging.warn(
                "[{}] ({}) -> f({}): {}".format(
                    timestamp, debug_level, source_function, debug_msg
                )
            )

    ##############
    # B  A  S  E #
    ##############

    def _build_parameters(self, parameters):
        # Variables
        params = {}

        # Implementation
        if "use_textfsm" in parameters:
            params.update({"use_textfsm": parameters["use_textfsm"]})
        if "command" in parameters:
            params.update({"command_string": parameters["command"]})
        return params

    def filter(self, *args, **kwargs):
        # TODO implement attr name
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
                    if attribute == "name":
                        if initiator:
                            f = F(name=value)
                            initiator = False
                        else:
                            f = f | F(name=value)
                        continue
                    if attribute == "type":
                        if initiator:
                            f = F(type=value)
                            initiator = False
                        else:
                            f = f | F(type=value)
                        continue
            filter_list.append(f)

        for i in range(len(filter_list)):
            if i == 0:
                f = filter_list[i]
            else:
                f = f & filter_list[i]

        result = self.nornir.filter(f)
        return result

    #############
    # INTERNALS #
    #############

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

    def __get_site(self, device: list) -> str:

        try:
            if isinstance(device[0].host.groups[0], str):
                return device[0].host.groups[0]
        except:
            return ""

    # ----------------- #
    # CISCO SW METHODS  #
    # ----------------- #

    def _get_l2_neighbors(self, devices, *args, **kwargs):
        # Variables

        structured = False
        downlink = False
        discovered_sites = []
        l2_neighbors = {}

        # Implementation
        if "structured" in kwargs:
            structured = kwargs["structured"]
        if "include_downlink" in kwargs:
            downlink = True

        # Results will start with the platform
        results = self.__execute_and_aggregate(devices, use_textfsm=structured)
        # We can only return objects if we use structured data
        if not structured:
            self.log("debug", "Data is unstructured !!!")
        else:

            for platforms in results:
                for host_name in platforms:
                    self.log("warn", "Processing data for {}".format(host_name))
                    current_host = platforms[host_name]
                    site = self.__get_site(current_host)
                    if site not in discovered_sites:
                        discovered_sites.append(site)
                        l2_neighbors[site] = {}
                    # Add downlink
                    if downlink:
                        for each in current_host.result:
                            each["local_host"] = current_host.host.name
                    # l2_neighbors[site][current_host.host.name] = current_host.result
                    l2_neighbors[site][current_host.host.name] = current_host
        return l2_neighbors

    def _get_facts(self, devices: Nornir, *args, **kwargs):
        # Get some facts from devices like, model, vendor, os version, serial numbers, stacks?
        # Possibly others in the future
        result = self.__execute_and_aggregate(devices)
        return result

    def discover_l2_devices(self, devices: Nornir, *args, **kwargs):

        # Variables
        split_hostname = False
        l2_neighbors = {}
        t_devices = deepcopy(devices)
        r_devices = deepcopy(t_devices)
        sites = {}
        visited = []
        failed = False
        failed_hosts = {}
        # Implementation
        if "raw" in kwargs:
            raw = kwargs["raw"]
        if "split_hostname" in kwargs:
            split_hostname = kwargs["split_hostname"]

        if t_devices:
            # new_host = deepcopy(self.nornir.inventory.hosts["NEWHOST"])
            new_host = self.nornir.inventory.hosts["NEWHOST"]
            while len(t_devices.inventory.hosts) > 0:
                results = self._get_l2_neighbors(t_devices, structured=True,)
                # Dirty hack, but canot doing the scan in serial mode
                # because nornir sends threads to do more than one neighbor at a time
                for site in results:
                    if site not in sites:
                        sites.update({site: {}})
                        failed_hosts.update({site: {}})
                    for device in results[site]:
                        self.log("warn", "Looking for neighbors in {}".format(device))
                        t_devices.inventory.hosts.pop(device)
                        group = site
                        if results[site][device].failed:
                            # TODO If failed is true, tell which device it failed and why
                            failed = True
                            failed_hosts[site].update(
                                {device: results[site][device].exception}
                            )
                            self.log(
                                "warn",
                                "Could not process {}".format(device),
                                results[site][device].exception,
                            )
                        visited.append(device)
                        for seen_neighbor in results[site][device].result:
                            if not results[site][device].failed:
                                if split_hostname:
                                    current_neighbor = seen_neighbor[
                                        "destination_host"
                                    ].split(".")[0]
                                if not nethelpers.check_regex_in_list(
                                    current_neighbor, visited
                                ):
                                    valid_platform = cons.return_platform(
                                        seen_neighbor["platform"], "models"
                                    )
                                    if valid_platform:
                                        new_host.name = current_neighbor
                                        new_host.hostname = seen_neighbor[
                                            "management_ip"
                                        ]
                                        new_host.platform = valid_platform["platform"]
                                        new_host.data["type"] = valid_platform["type"]
                                        new_host.data["vendor"] = valid_platform[
                                            "vendor"
                                        ]
                                        new_host.groups.data[0] = group
                                        l2_neighbors[new_host.name] = deepcopy(new_host)
                                    else:
                                        print()
                        t_devices.inventory.hosts.update(l2_neighbors)
                        r_devices.inventory.hosts.update(l2_neighbors)
                        l2_neighbors = {}
                # sites[site] = r_devices
            return r_devices

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

