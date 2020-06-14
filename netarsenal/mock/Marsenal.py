import logging
import json
import tinydb
import random
import base64
import os
import re
import exceptions as mockex
from datetime import datetime


# Find out how to import
################################################################################
platform_mapping_commands = {
    "functions": {
        "_get_l2_neighbors": {
            "ios": "show_cdp_neighbors,show cdp neighbors detail",
            "nxos": "get_show_cdp_neighbors,show cdp neighbors detail",
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
INIT_STATE = "@>"
END_STATE = "<#"

# definitions

# class


class MockArsenal(object):
    # Variables
    device_state = {}
    save_state = False
    state_id = None
    path = ""
    key = "0"
    valid_mock = False

    def __init__(self, path, key=0):
        print("Creating MockIOS Object")

        self.path = path
        if key:
            self.key = key
        # Read MockIOSdata.s state file, this s file, is to emulate state of device
        # Hopefully, you can run commands and get state for past events
        try:
            with open(self.path, "a+", encoding="utf-8") as mock_file:
                mock_file_size = mock_file.tell()
                mock_file.seek(0, os.SEEK_SET)
                if mock_file_size > 0:
                    version = mock_file.read(40)
                    if re.search(r"^__mockdv\d+.\d+-->", version):
                        self.valid_mock = True
                    else:
                        raise mockex.InvalidMockDataFile
                else:
                    mock_file.write("__mockdv0.1-->\n")
                    self.valid_mock = True
        except:
            logging.error("Could not open file {}".format(path))

    def __return_file_offset(self, mock_file, current_seek, offset_string):
        print(1)

    def __find_in_file(self, mock_file, start_offset=0, look_for="\n", chunk_size=4096):
        seek = -1
        mock_file.seek(0, os.SEEK_END)
        fsize = bsize = mock_file.tell()
        mock_file.seek(0, os.SEEK_SET)
        word_len = len(look_for)
        found = []
        if bsize > chunk_size:
            bsize = chunk_size
        if start_offset:
            mock_file.read(start_offset)
        while True:
            p = mock_file.read(chunk_size).find(look_for)
            if p > -1:
                pos_dec = mock_file.tell() - (bsize - p)
                mock_file.seek(pos_dec + word_len)
                bsize = fsize - mock_file.tell()
                found.append(pos_dec)
                if start_offset:
                    found[0] = found[0] - start_offset
                    return found
            if mock_file.tell() < fsize:
                seek = mock_file.tell() - word_len + 1
                mock_file.seek(seek)
            else:
                mock_file.seek(0, os.SEEK_SET)
                if not found:
                    return -1
                return found

    def record(self):
        if self.valid_mock:
            self.save_state = True
            if not self.state_id:
                self.state_id = random.randrange(1000, 10000)
        else:
            raise mockex.InvalidMockDataFile

    def pause(self):
        self.save_state = False
        self.state_id = None

    def check(self):
        return self.save_state

    def show_cdp_neighbors(self, nornir=object, use_textfsm=False):
        command = "show cdp neighbors detail"

        return command

    def save_state_of_device(self, device, mock_data, command, key=None):
        logging.warning("Saving state of {}".format(device))
        new_device_state = {}
        json_data = {}
        seek = 0

        # Connect to device and extract raw info
        json_data = {
            "state_id": self.state_id,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "command": command,
            "data": base64.encodestring(mock_data.encode()).decode(),
        }
        new_device_state[device] = json_data
        with open(self.path, "r+", encoding="utf-8") as mock_file:
            seek = self.__find_in_file(mock_file, 0, device)
            if seek == -1:
                # file has no mock data for the device
                # add it to the end of the file
                mock_file.seek(0, os.SEEK_END)

                # position into seek
                mock_file.seek(mock_file.tell() - 1)
                mock_file.write(
                    "{}{}{}".format(INIT_STATE, json.dumps(new_device_state), END_STATE)
                )
            else:
                # load json object initial position is seek[0]
                # __find_in_file with start_offset seek[0] and look_for <#
                seek_end = self.__find_in_file(mock_file, seek[0], END_STATE)
                mock_file.seek(seek[0] - 2)
                mock_device = mock_file.read(seek_end[0])
                mock_device_data = u"{}".format(
                    base64.b64decode(device[device]["data"].encode())
                )
                print(mock_device)
        return 1
