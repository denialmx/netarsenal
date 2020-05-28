import logging
from typing import Any, Optional

from nornir.core.deserializer.inventory import (
    HostsDict,
    GroupsDict,
    Inventory,
    VarsDict,
)

import ruamel.yaml
import json


class Includentory(Inventory):
    def __init__(
        self, config_file="netarsenal/config/config.yml", *args: Any, **kwargs: Any
    ):

        # Define variables
        hosts = {}
        yml = ruamel.yaml.YAML(typ="safe")

        # TODO error handling and logging
        with open(config_file, "r") as config_file:
            config = yml.load(config_file)
            if isinstance(config, dict):
                # TODO maybe put it in a loop to retrieve files dynamically?
                # Open the host file
                if config["inventory"]["options"]["host_file"]:
                    host_file_path = config["inventory"]["options"]["host_file"]
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

                # Open the group file
                if config["inventory"]["options"]["group_file"]:
                    group_file_path = config["inventory"]["options"]["group_file"]
                    with open(group_file_path, "r") as group_file:
                        groups = yml.load(group_file)

                # Open defaults file
                if config["inventory"]["options"]["defaults_file"]:
                    defaults_file_path = config["inventory"]["options"]["defaults_file"]
                    with open(defaults_file_path, "r") as defaults_file:
                        defaults = yml.load(defaults_file)

            super().__init__(
                hosts=hosts, groups=groups, defaults=defaults, *args, **kwargs
            )


# temp = Includentory()
