# -*- coding: utf-8 -*-
"""
CliParse
"""

import argparse

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class CliParse:
    """
    Command Line Arguments parser

    Object is constructed expecting a named 'command_line' argument, a list of
    provided command line arguments.

    Supported options:

    --help          Print this help
    --debug         Enable debugging messages

    --loop          Loop over directories, files, URIs etc.
    --recursive     Scan directories recursively for supported files
    --no-recursive  (default)

    --fullscreen    Enable fullscreen display
    --window        Force windowed mode, overrides saved state

    --fit-best      Force fitting the whole image in the window
    --fit-height    force fitting image based on its height
    --fit-width     Force fitting image based on its width

    --slideshow     Display as a slide-show
    --selector      Start with a simple file selector
    --welcome       Display welcome screen with some basic tips

    --no-plugins    Disable loading of plugins

    """

    def __init__(self, command_line=None):
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(command_line)))

        self.command_line = None  # List
        self.parsed_command_line = None  # dict

        # provided by creator:
        self.config = None  # <Persistence>dict

        # argparse backend specifics:
        self.parser = None
        self.args = None

    def set_config(self, value):
        """Setter for `config`."""
        self.config = value

    def initialize(self, desc):
        """
        Create and initialize the argument parser

        """
        if not self.parser:
            self.parser = argparse.ArgumentParser(description=desc)
            self._add_default_args()

        else:
            raise RuntimeError("parser already initialized")

    def _add_default_args(self):
        """
        Feed the parser with default values

        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="Enable console debugging output",
        )

        self.parser.add_argument(
            "--loop",
            action="store_true",
            default=False,
            help="Loop over path/files lists",
        )

        self.parser.add_argument(
            "--fullscreen",
            action="store_true",
            default=None,
            help="force fullscreen display, overrides saved state",
        )

        self.parser.add_argument(
            "--recursive",
            action="store_true",
            default=False,
            help="Recurse into directories",
        )

        # Deal with the remaining. Expecting start path/file/archive:
        self.parser.add_argument("remainders", nargs=argparse.REMAINDER)

    def parse(self, cli_args_l):
        """
        Parsed provided command line List with the backend argument parser

        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.command_line:
            self.command_line = cli_args_l  # can be useful later
        else:
            # If already exist, append given item instead:
            self.command_line.extend(cli_args_l)

        self.args = self.parser.parse_args(self.command_line)
        self.post_initialize()

    def post_initialize(self):
        """
        perform post initializations mappings on 'args' and
        startup 'config' state.

        """
        # initialize self.config['fullscreen'], leaving a chance to have it
        # done before/externally is that would become needed:
        if "fullscreen" not in self.config.keys():
            self.config["fullscreen"] = False

        # None indicates a bool value was not explicited on CLI:
        if self.args.fullscreen is not None:
            self.config["fullscreen"] = self.args.fullscreen

    def get(self, item):
        """
        Accessor to the parsed arguments

        """
        return vars(self.args)[item]
