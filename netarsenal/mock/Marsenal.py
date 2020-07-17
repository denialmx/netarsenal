import logging
import json
from tinydb import TinyDB, Query
import random
import base64
import os
import re
from datetime import datetime

try:
    import mockex
except:
    import netarsenal.mock.mockex as mockex

from nornir.core.task import Task
from nornir import InitNornir as Nornir
from nornir.core.task import AggregatedResult
from netarsenal.mock import Marsenal
from ntc_templates.parse import parse_output


# Find out how to import
################################################################################
platform_mapping_commands = {
    "functions": {
        "_get_l2_neighbors": {
            "ios": "show cdp neighbors detail",
            "nxos": "show cdp neighbors detail",
        }
    },
    "commands": {"show version": {"ios": True, "nxos": True}},
}


def return_platform_function(name, type="functions"):
    if name in platform_mapping_commands["functions"]:
        return platform_mapping_commands["functions"][name]
    else:
        raise EnvironmentError


#################################################################################

from nornir.plugins.tasks.networking import netmiko_send_command

# cons

# definitions

# class


class MockArsenal(object):
    # Variables
    device_state = {}
    save_state = False
    state_id = None
    path = ""
    db = ""
    query = ""
    key = "0"
    valid_mock = False
    use_mock = False
    mock_command = ""

    def __init__(self, path=None, key=0):
        print("Creating Mock Object")
        logging.info("Creating MockIOS Object")
        logging.debug("Checking if {} is valid".format(path))
        self.opendb(path, True)

    def __extract_mock_data(self, task, **kwargs):

        # Variables
        real_command = False
        # Extract mock data from path.
        # validate errors
        if "mock" in task.host.platform:
            real_platform = task.host.platform.split("-")[1]
            if "command_string" in kwargs:
                command = kwargs["command_string"]
                real_command = True
            else:
                command = return_platform_function(kwargs["command_string"])

            table_devices = self.db.table("devices")
            device_exists = table_devices.search(
                self.query.device_name == task.host.name
            )
            # check states, return last state or return if state_id provided
            if len(device_exists) > 0:
                extract = device_exists[0][
                    "state{}".format(device_exists[0]["last_state_dict_id"])
                ]
                if real_command:
                    if command == extract["command"]:
                        data = base64.decodestring(extract["data"].encode()).decode(
                            "utf-8"
                        )
                        return data
                else:
                    if command[real_platform] == extract["command"]:
                        data = base64.decodestring(extract["data"].encode()).decode(
                            "utf-8"
                        )
                        return data
                    else:
                        raise mockex.MockSimulateFailure
            else:
                raise mockex.MockDeviceNotFound

    def opendb(self, path, create_on_open=False):
        if path:
            try:
                self.db = TinyDB(path)
                self.query = Query()
                table_devices = self.db.table("devices")
                if "devices" not in self.db.tables():
                    if create_on_open:
                        doc_id = table_devices.insert(
                            {
                                "creation_date": datetime.now().strftime(
                                    "%d/%m/%Y %H:%M:%S"
                                ),
                                "last_updated": datetime.now().strftime(
                                    "%d/%m/%Y %H:%M:%S"
                                ),
                            }
                        )
                    if doc_id:
                        self.valid_mock = True
                else:
                    if table_devices.contains(doc_id=1):
                        self.valid_mock = True
            except:
                self.valid_mock = False
                raise mockex.InvalidMockDataFile
        else:
            self.valid_mock = False
            self.save_state = False

    def record(self, db_file=None) -> int:
        if self.valid_mock:
            self.save_state = True
            self.use_mock = False
            if not self.state_id:
                self.state_id = random.randrange(1000, 10000)
                return self.state_id
        else:
            raise mockex.InvalidMockDataFile

    def pause(self):
        self.save_state = False

    def start(self):
        if self.valid_mock:
            self.save_state = False
            self.use_mock = True

    def stop(self):
        self.use_mock = False

    def check(self):
        if self.valid_mock and (self.use_mock or self.save_state):
            return True
        else:
            return False

    def _send_command(self, devices: Nornir, *args, **kwargs):

        # Variables
        use_textfsm = False
        command = ""

        # Implementation
        if "command_string" in kwargs:
            command = kwargs["command_string"]
        else:
            command = self.mock_command
        if "use_textfsm" in kwargs:
            use_textfsm = kwargs["use_textfsm"]

        params = {
            "command_string": command,
        }

        # result = devices.run(task=self.__extract_mock_data, **params)
        result = devices.run(task=self.__extract_mock_data, num_workers=1, **params)
        for device in result:
            if use_textfsm and result[device].result != "Timeout":
                result[device][0].result = parse_output(
                    platform=devices.inventory.hosts[device].platform.split("-")[1],
                    command=command,
                    data=result[device].result,
                )
        return result

    def change_platform(self, nornir):
        # grab the nornir object and change the platform to mock
        for device in nornir.inventory.hosts:
            nornir.inventory.hosts[device].platform = "mock-{}".format(
                nornir.inventory.hosts[device].platform
            )

    def save_state_of_device(self, device, mock_data, command, key=None):
        logging.info("Saving state of {}".format(device))
        json_data = {}
        last_state_dict_id = 0
        new_state_dict_id = last_state_dict_id + 1

        device_exists = None

        new_device_state = {
            "state_id": self.state_id,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "command": command,
            "data": base64.encodestring(mock_data.encode()).decode(),
        }

        table_devices = self.db.table("devices")
        # Check if the device already exists in the database
        device_exists = table_devices.search(self.query.device_name == device)
        if device_exists:
            last_state_dict_id = device_exists[0]["last_state_dict_id"]
            new_state_dict_id = last_state_dict_id + 1

        json_data = {
            "device_name": device,
            "last_state_dict_id": new_state_dict_id,
            "state{}".format(new_state_dict_id): new_device_state,
        }

        if device_exists:
            table_devices.upsert(json_data, self.query.device_name == device)
        else:
            # add new record
            table_devices.insert(json_data)
        return 1
