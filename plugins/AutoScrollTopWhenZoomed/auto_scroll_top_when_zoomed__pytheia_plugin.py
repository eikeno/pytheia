# -*- coding: utf-8 -*-
"""
Automatically scroll to top when in zomm mode with vertical scrollbar

"""

__DONE__ = """

"""

# TODO: everything


import math
import os
import pdb
import shutil

from gi.repository import (
    Gdk,  # pylint: disable=E0611,W0611
    GdkPixbuf,  # pylint: disable=E0611,W0611
    Gtk,  # pylint: disable=E0611,W0611
)


class _PytheiaPlugin:
    """
    Mixin for PytheiaPlugin.

    Mandatory plugins methods are to be implemented by PytheiaPlugin subclass.

    """

    def __init__(self):
        pass

    def cb_action_request(self):
        """
        Initiate copying of current file when registered keybinding's triggered

        """
        self._oncall_in()  # perst load

        self.pytheia.main_window.get_children()[0].get_children()[0].get_vadjustment().set_value(0)

        self._oncall_out()

    def i_was_here(self, *args):
        self.plugin_console_out("auto_scroll_top_when_zoomed's in %s %s" % (args[0], args[1]))


class PytheiaPlugin(_PytheiaPlugin):
    """
    Mandatory plugin class

    """

    _plugin_longdesc = """
	Force display of the top part of new images when in zoom mode, with
	vertical scrollbar active.

	Probably what you want for comics, magazines and books reading.
	"""

    def __init__(self):
        self.pytheia = None  # <Pytheia>
        self.config = {}
        _PytheiaPlugin.__init__(self)

    def __del__(self):
        self.plugin_console_out("deller of auto_scroll_top_when_zoomed called")
        pass

    def _oncall_in(self):
        """
        To be used each time plugin is explicitly called (vs imported or
        registered), by the plugin itself.

        """
        # self.config = {}
        # self.config = self.persistence.load()

        # self._action_on_dup = None
        pass

    def _oncall_out(self):
        """
        To be called when a call is ending

        """
        # if not self.config:
        # self.plugin_console_out("'config' is None when _oncall_out reached")
        # return True

        # self.persistence.dump(source_object=self.config)
        pass

    def attach(self, pytheia):
        """
        Attach 'pytheia', an accessor to PytheiaGui.core.plugins

        """
        self.pytheia = pytheia

    def register(self):
        """
        Expose the plugin to pytheia

        """
        return {
            "name": "auto_scroll_top_when_zoomed",
            "author": "Eikeno <eikenault@gmail.com>",
            "copyright": "GPL",
            "website": "https://eikeno.eu",
            "filename": "auto_scroll_top_when_zoomed",
            "categories": "browsing, non-interactive",
            "shortdesc": "Scroll to top of new image when in zoom mode",
            "longdesc": self._plugin_longdesc,
            "hooks": {"on_zoom_performed": (self.cb_action_request,)},
        }
