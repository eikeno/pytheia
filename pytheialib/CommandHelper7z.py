# -*- coding: utf-8 -*-
"""
CommandHelper7z
"""

import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class CommandHelper7z:
    """
    Wrappers around external '7z' command invocation

    """

    def __init__(self, archive, command_path=None):
        gdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), archive, str(command_path)))

        if command_path:
            self.cmd_7z = command_path
        else:
            self.cmd_7z = "7z"

        if not os.path.exists(archive):
            raise ValueError("Archive: %s does not exist" % str(archive))

        self.archive = archive
        self.l_slt_out_l = None
        self.akeys = (
            "Path",
            "Type",
            "Solid",
            "Blocks",
            "Multivolume",
            "Volumes",
            "Method",
            "Physical Size",
            "Headers Size",
        )
        self.ikeys = (
            "Path",
            "Folder",
            "Size",
            "Solid",
            "Packed Size",
            "Attributes",
            "Encrypted",
        )
        self.meta = {}
        self.item = {}
        self.listing = []

    def _gen_meta(self):
        """Generate and store meta informations for the registered achive"""
        gdebug(f"# {self.__class__}:{callee()}")

        ret = os.popen('%s l -slt "%s"' % (self.cmd_7z, self.archive))

        self.l_slt_out_l = ret.readlines()
        ret.close()

    def extract_file_as(self, member, destination_file):
        """Extract 'member' file from archive to 'destination_file'"""
        gdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), member, destination_file))

        debug("os.popen() ->" + '%s e "%s" -so "%s" > "%s"' % (self.cmd_7z, self.archive, member, destination_file))
        ret = os.popen('%s e "%s" -so "%s" > "%s"' % (self.cmd_7z, self.archive, member, destination_file))

        ret.close()

    def _dump_item(self):
        """Extract informations from the item being parsed to self.listing"""
        if not self.item:
            return

        if "Folder" not in self.item:
            self.item["Folder"] = None

        if self.item["Folder"] == "+" or (self.item["Attributes"].startswith("D")):
            self.listing.append(self.item["Path"] + os.path.sep)

        else:
            self.listing.append(self.item["Path"])

    def parse_tech_listing(self):
        """
        Parse output of archive listing produced by 7z binary with -slt option
        to 'self.listing' - this also distinguish directories by appending
        an os.path.sep character to the end of their name.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self._gen_meta()
        context = None

        for line in self.l_slt_out_l:
            if line == "\n" and not context:
                continue

            if line == "\n" and context == "item":
                self._dump_item()
                self.item = {}

            if line.strip() == "--":
                context = "archive"

            if line.strip() == "----------":
                self._dump_item()
                context = "item"
                self.item = {}

            if str(line.strip().split(" = ")[0]) in self.akeys and (context == "archive"):
                self.meta[str(line.strip().split(" = ")[0])] = str("".join(line.strip().split(" = ")[1:]))

            elif str(line.strip().split(" = ")[0]) in self.ikeys and (context == "item"):
                self.item[str(line.strip().split(" = ")[0])] = str("".join(line.strip().split(" = ")[1:]))
        self._dump_item()
