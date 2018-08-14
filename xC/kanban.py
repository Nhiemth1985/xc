"""
kanban.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2018-08-13
        * Version: 0.00b
        * Scrach version.
"""

import sys
import yaml
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class Kanban:
    """
    Methods:
    """
    def __init__(self, data):
        self.version = '0.10b'
        self.load(data)
        self.reset()

    def load(self, data):
        self.data = data

    def is_enable(self):
        enable = False
        try:
            enable = self.data["device"][self.id].get('enable', True)
        except BaseException:
            pass
        return enable

    def get_id(self):
        return self.id

    def set(self, id):
        """Set a device to be used.

        Used to set a device and import all elements.

        Attributes:
            element: An element name (like x1, x2, x6, etc.).
        """
        self.reset()
        self.id = id
        if not self.id:
            return
        # Is device present in configuration file?
        try:
            check_id = self.data["device"][self.id]
        except KeyError:
            erroln('Device is not present in configuration file.')
            sys.exit(True)
        # Check mandatory keys.
        try:
            self.system_plat = self.data["device"][self.id]["system"]["plat"]
            self.system_mark = self.data["device"][self.id]["system"]["mark"]
            self.system_desc = self.data["device"][self.id]["system"]["desc"]
            self.system_arch = self.data["device"][self.id]["system"]["arch"]
            self.system_path = self.data["device"][self.id]["system"]['path']
            self.system_logs = self.data["device"][self.id]["system"]['logs']
        except KeyError as err:
            erroln('Mandatory key is absent: %s' % (err))
            sys.exit(True)

    def list(self):
        """Fetches device IDs from a dictionary.

        Args:
            None

        Returns:
            A list of device IDs. For example:

            ['x1', 'x2', 'x3', 'x4']

        Raises:
            None
        """
        elements = []
        for i in self.data["device"]:
            elements.append(i)
        elements.sort()
        return elements

    def get_comm(self):
        try:
            return self.data["device"][self.id]["comm"]
        except BaseException:
            return []

    def get_objects(self):
        try:
            return self.data["device"][self.id]["object"]
        except BaseException:
            return []

    def get_endup(self):
        try:
            return self.data["device"][self.id]["endup"]
        except BaseException:
            return []

    def get_startup(self):
        try:
            return self.data["device"][self.id]["startup"]
        except BaseException:
            return []

    def get_control(self):
        try:
            return self.data["device"][self.id]["control"]
        except BaseException:
            return []

    def reset(self):
        """Reset device default properties"""
        self.id = None
        self.system_plat = ""
        self.system_mark = ""
        self.system_desc = ""
        self.system_arch = ""
        self.system_path = ""
        self.system_logs = ""

    def set_interface(self, interface):
        self.interface = interface

    def info(self):
        """ """
        infoln('ID: ' + str(self.id), 1)
        if not self.id:
            return
        infoln('Name: ' + str(self.system_plat) +
               ' Mark ' + str(self.system_mark), 1)
        infoln('Description: ' + str(self.system_desc), 1)

    def get_control_map(self):
        for i in self.objects():
            info(i)["command"]

    def detect(self):
        self.reset()
        ids = []
        for id in self.list():
            self.set(id)
            session = Session(self.get_comm())
            if not self.is_enable():
                continue
            if session.is_connected_serial():
                ids.append(str(id).encode("utf-8"))
            else:
                session.reset()
        if len(ids) == 1:
            self.set(ids[0])
        elif len(ids) < 1:
            self.set(None)
        elif len(ids) > 1:
            self.set(False)
        return ids
