# -*- coding: utf-8 -*-
"""
Screen
"""

import gi # pylint: disable=import-error
from gi.repository import Gdk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class Screen:
    """
    Represents the physical screen attributes and features.
    """

    def __init__(self):
        self.screen_width = None  # int
        self.screen_height = None  # int
        self.screen_ratio = None  # float
        self.screen_simulation = False  # bool
        self.fit_fullscreen = None  # bool
        self.fit_best = None  # bool

        self.config = None  # <PytheiaGui.config>

    def set_config(self, value):
        """Setter for `config`."""
        self.config = value

    def screen_initialize(self):
        """Compute startup values for:
        - `screen_width`
        - `screen_height`
        - `screen_ratio`
        """
        gdebug(f"# {self.__class__}:{callee()}")

        screen = Gdk.Screen().get_default()
        geometry = screen.get_monitor_geometry(
            # screen.get_monitor_at_window worked only on xorg.
            # To accomodate wayland, let's use 0 instead:
            0
        )  # <CairoRectangleInt>
        # FIXME: turn screen_width and screen_height into properties, to be able to remain correct should the user move
        # FIXME: the window across multiple monitors.
        self.screen_width = geometry.width
        self.screen_height = geometry.height
        debug("found geometry for active monitor: %dx%d" % (geometry.width, geometry.height))

        # While we're at it, define some fallback values:
        # Default window size to 50% of the Screen:
        self.config["main_window_fallback_width"] = self.screen_width / 2
        self.config["main_window_fallback_height"] = self.screen_height / 2

        # To avoid hasattr() calls later:
        self.config["main_window_width"] = None
        self.config["main_window_height"] = None

        # set in __main__() from CLI:
        if hasattr(self, "screen_simulation"):
            # Vertical screen simulation
            if self.screen_simulation == "sim_vertical_screen":
                # These attributes held by DisplayState():
                self.fit_fullscreen = False
                self.fit_best = True

                self.screen_width, self.screen_height = (
                    self.config["main_window_fallback_height"],  # swap values
                    self.config["main_window_fallback_width"],
                )

                # 50% of the Screen:
                self.config["main_window_fallback_width"] = self.screen_width
                self.config["main_window_fallback_height"] = self.screen_height

                rdebug("screen simulation mode at w,h = %s, %s" % (self.screen_width, self.screen_height))

            # Square screen simulation
            if self.screen_simulation == "sim_square_screen":
                self.fit_fullscreen = False
                self.fit_best = True

                self.screen_width, self.screen_height = (
                    self.config["main_window_fallback_height"],  # scale to min
                    self.config["main_window_fallback_height"],
                )

                # 50% of the Screen:
                self.config["main_window_fallback_width"] = self.screen_height
                self.config["main_window_fallback_height"] = self.screen_height

                rdebug("screen simulation mode at w,h = %s, %s" % (self.screen_width, self.screen_height))

        self.screen_ratio = float(float(self.screen_width) / float(self.screen_height))
