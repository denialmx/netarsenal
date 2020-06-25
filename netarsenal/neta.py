# imports
import sys
import ruamel.yaml
import re
from copy import deepcopy, copy

from nornir import InitNornir
from nornir.core.filter import F

from netarsenal.cisco.ios import iosarsenal
from netarsenal.cisco.nxos import nxosarsenal
from netarsenal.cisco.wlc import wlcarsenal
from netarsenal.mock import Marsenal
import netarsenal.cons as cons
import netarsenal.exceptions as netex

# TO REMOVE
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result

# definitions

# class


class NetArsenal(object):
    # variables
    # objects
    nornir = object
    netmiko = object
    textfm = object

    arsenal = {
        "ios": iosarsenal.IOSArsenal(),
        "nxos": nxosarsenal.NXOSArsenal(),
        "mock": Marsenal.MockArsenal(),
        "wlc": wlcarsenal.WLCArsenal(),
        "viptela": object,
        "iosxe": object,
    }

    # init
    def __init__(self, configfile, num_workers, mock_path=None):
        if mock_path:
            self.arsenal["mock"].opendb(mock_path, True)
        self.nornir = InitNornir(
            config_file=configfile,
            core={"num_workers": num_workers},
            inventory={"plugin": "netarsenal.inventory.include.Includentory"},
        )

    def _mock_record(self, db_file=None):
        self.arsenal["mock"].record()

    def _mock_pause(self):
        self.arsenal["mock"].pause()

    def _mock_check(self):
        return self.arsenal["mock"].check()

    def _mock_start(self):
        return self.arsenal["mock"].start()

    def __execute_and_aggregate(
        self, nornir=object, divider="platform", *args, **kwargs
    ):
        # Currently only platform is supported as a divider
        # Need to put the logic inside to make [data] available as a divider as well (on top of platform)
        # in case someone wants to execute a command and divide it by site
        # I might remove entirely the feature as well and always leave it as platform independent only
        command_picker = sys._getframe(1).f_code.co_name
        functions_to_call = cons.return_platform_function(command_picker)
        # TODO validate nornir is object of InitNornir
        t_nornir = deepcopy(nornir)
        pop = dict(t_nornir.inventory.hosts)
        current_pop_filter = None
        results = []

        if self._mock_check():
            mock = copy(self.arsenal["mock"])
            if mock.use_mock:
                mock.change_platform(t_nornir)
                mock.mock_command = command_picker
        else:
            mock = None

        while len(pop) > 0:
            if len(pop) > 1:
                completed = []
                for host in list(t_nornir.inventory.hosts):
                    # Check platform of host
                    pop_filter = getattr(t_nornir.inventory.hosts[host], divider)
                    # split pop_filter with an -
                    # pop_filter[0] will always have the right platform, either
                    # ios, nxos, mock
                    pop_filter = pop_filter.split("-")[0]
                    if not current_pop_filter:
                        current_pop_filter = pop_filter
                    if pop_filter != current_pop_filter:
                        t_nornir.inventory.hosts.pop(host)
                    else:
                        completed.append(host)

                # TODO
                # Error handling if platform does not exist
                try:
                    N = getattr(
                        self.arsenal[current_pop_filter],
                        functions_to_call[current_pop_filter],
                    )
                    result = N(t_nornir, use_textfsm=True, mock=mock)
                    results.append(result)
                except KeyError as e:
                    print(e)
                if len(t_nornir.inventory.hosts) > 1:
                    t_nornir.inventory.hosts = dict(pop)
                    for index in range(0, len(completed), 1):
                        t_nornir.inventory.hosts.pop(completed[index])
                    pop = dict(t_nornir.inventory.hosts)
                    current_pop_filter = None
                    index = 0
            else:
                host = next(iter(t_nornir.inventory.hosts))
                # Check platform of host
                current_pop_filter = getattr(t_nornir.inventory.hosts[host], divider)
                current_pop_filter = current_pop_filter.split("-")[0]
                N = getattr(
                    self.arsenal[current_pop_filter],
                    functions_to_call[current_pop_filter],
                )
                result = N(t_nornir, use_textfsm=True, mock=mock)
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

        results = self.__execute_and_aggregate(
            nornir, divider="platform", use_textfsm=True
        )
        return results

    def discover_l2_devices(self, nornir=object, *args, **kwargs):
        devices = {}
        discovery = {}
        t_nornir = deepcopy(nornir)
        completed = []

        if t_nornir:
            new_host = deepcopy(self.nornir.inventory.hosts["NEWHOST"])
            results = self._get_l2_neighbors(t_nornir)
            for platform in results:
                for host in platform:
                    devices[host] = deepcopy(t_nornir.inventory.hosts[host])
                    # Build nornir object dynamically
                    for l2_device in platform[host].result:
                        # Eliminate duplicates by hasing perhaps?
                        new_host.name = l2_device["destination_host"]
                        new_host.hostname = l2_device["management_ip"]
                        # Probably a callable functions to get IOS, NXOS, IOS-XE, IOS-XR, JUNOS
                        # to detect which platform it should use for callable_functions
                        new_host.platform = "ios"
                        devices[new_host.name] = deepcopy(new_host)
                completed.append(host)
            t_nornir.inventory.hosts = devices
            # Enter loop to continue searching up to X level
            new_hosts = self._get_l2_neighbors(t_nornir)
        return devices
