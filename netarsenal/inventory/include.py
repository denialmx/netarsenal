import logging
from typing import Any, Optional

from nornir.core.deserializer.inventory import (
    HostsDict,
    GroupsDict,
    Inventory,
    VarsDict,
)

# Find a way to import the exceptions
# from netarsenal.exceptions import ConfigFileNotFound

import ruamel.yaml
import json


class Includentory(Inventory):
    def __init__(self, config_file="config.yml", *args: Any, **kwargs: Any):

        # Define variables
        hosts = {}
        yml = ruamel.yaml.YAML(typ="safe")

        # TODO error handling and logging
        try:
            if "hosts.yml" in kwargs["host_file"]:
                host_file_path = kwargs["host_file"]
                # Open the host file
                with open(host_file_path, "r") as host_file:
                    hosts_include = yml.load(host_file)
                    #
                    for i in range(len(hosts_include["config"]["include"])):
                        # validate file actually exists
                        # put a flag to continue?
                        with open(
                            hosts_include["config"]["include"][i]
                        ) as include_host_file:
                            if isinstance(hosts, dict):
                                hosts.update(yml.load(include_host_file))

            # Open the groups file
            if "groups.yml" in kwargs["group_file"]:
                group_file_path = kwargs["group_file"]
                with open(group_file_path, "r") as group_file:
                    groups = yml.load(group_file)

            # Open the defaults file
            if "defaults.yml" in kwargs["defaults_file"]:
                defaults_file_path = kwargs["defaults_file"]
                with open(defaults_file_path, "r") as defaults_file:
                    defaults = yml.load(defaults_file)

            # Call the base inventory nornir object
            super().__init__(
                hosts=hosts, groups=groups, defaults=defaults, *args, **kwargs
            )
        except:
            raise EnvironmentError


# temp = Includentory()
