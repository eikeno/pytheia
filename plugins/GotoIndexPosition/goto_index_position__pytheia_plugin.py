# -*- coding: utf-8 -*-
"""
Jump to another image by giving its index position

"""

import os

from gi.repository import (
    Gdk,  # pylint: disable=E0611,W0611
    GObject,  # pylint: disable=E0611,W0611
    Gtk,  # pylint: disable=E0611,W0611
)


class _PytheiaPlugin:
    """
    Mixin for PytheiaPlugin.

    Mandatory plugins methods are to be implemented by PytheiaPlugin subclass.

    """

    def __init__(self):
        self.index_dst = None
        self.index_dst_split = (None, None)

    def _get_index(self):
        """
        Obtain the destination index position

        """
        # t_msg => (primsg, secmsg, title, prefix)
        self.index_dst = self.pytheia.wid_get_text_input_simple(
            (
                "Please enter the position to jump to",
                "possible values are: 1 to %s" % len(self.pytheia.path_index.path_nodes_store.current_pathnode()),
                "Goto index...",
                "index: ",
            )
        )

        self._check_index()

        if self.index_dst_split[0] is None:
            return False

    def _jump_to_index(self, offset, whence):
        """
        Try to jump to 'index_dst' position

        """
        try:
            self.pytheia.cb_path_seek_generic(int(offset), whence)
        except Exception as ex:
            self.plugin_console_out(f"error calling cb_path_seek_generic. ex: {ex}")
            return False

    def _check_index(self):
        """
        Returns True if requested index syntax makes sense, False if it doesn't

        """
        _seek_mode = None
        _seek_num = None
        _seek_sign = None

        if not self.index_dst:
            self.plugin_console_out("error: index_dst is None")
            return False

        if "-" in self.index_dst:
            _seek_sign = "negative"

        if "+" in self.index_dst:
            if _seek_sign:
                # plus and minus given at the same time
                self.plugin_console_out("error: more than 1 sign given")
                return False
            _seek_sign = "positive"

        # make sure there's no extra allowed chars:
        _num = self.index_dst.replace("+", "", 1)
        _num = _num.replace("-", "", 1)
        _num = _num.replace(":", "", 1)

        try:
            _seek_num = int(_num)
        except ValueError as e:
            self.plugin_console_out("_seek_num can't be seen as an int: " + str(e))

        if self.index_dst.startswith(":"):
            # Relative to end
            _seek_mode = os.SEEK_END

        elif self.index_dst.endswith(":"):
            # Relative to start (1)
            _seek_mode = os.SEEK_SET

        else:
            # Relative to current position
            _seek_mode = os.SEEK_CUR

        self.plugin_console_out("_seek_mode = %s" % str(_seek_mode))
        self.index_dst_split = (_num, _seek_mode)

    def cb_action_request(self):
        """
        Initiate index query to the user

        """
        self._oncall_in()  # perst load
        self.plugin_console_out("goto_index_position cb_action_request")

        try:
            self._get_index()

        except Exception as ex:
            self.plugin_console_out(f"goto_index_position:cb_action_request, _get_index error. ex: {ex}")
            return False

        self.plugin_console_out("Got: %s" % str(self.index_dst))
        self._jump_to_index(self.index_dst_split[0], self.index_dst_split[1])

    def cb_toggled(self, cell_renderer_toggle, row_idx_zb, user_data):
        """
        Invert boolean status of the toggle

        """
        pass

    def cb_ok(self, widget, window):
        """
        Callback for the Ok button

        """
        self.plugin_console_out("cb_ok, entering")

        ## _*_ code here _*_

        self._oncall_out()
        self.plugin_console_out("cb_ok, leaving")
        return True

    def cb_cancel(self, widget, window):
        """
        Callback for the Cancel button

        """
        self.plugin_console_out("cb_cancel")
        # window.destroy()
        self._oncall_out()
        return True

    def cb_debug(self, *args):
        """
        Callback for debugging purpose

        """
        self.plugin_console_out(str(args))
        return True


class PytheiaPlugin(_PytheiaPlugin):
    """
    Mandatory plugin class

    """

    _plugin_longdesc = "Change current image to one given by its index position"

    def __init__(self):
        _PytheiaPlugin.__init__(self)
        self.pytheia = None

    def __del__(self):
        self.plugin_console_out("deller of goto_index_position called")
        self._oncall_out()

    def _oncall_in(self):
        """
        To be used each time plugin is explicitly called (vs imported or
        registered), by the plugin itself.

        """
        pass

    def _oncall_out(self):
        """
        To be called when a call is ending or plugin is destroyed

        """
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
            "name": "Goto Index Position,",
            "author": "Eikeno <eikenault@gmail.com>",
            "copyright": "GPL",
            "website": "https://eikeno.eu",
            "filename": "goto_index_position",
            "categories": "navigation, interactive",
            "shortdesc": "Navigate to an image by giving its index position",
            "longdesc": self._plugin_longdesc,
            "manageable": False,  # is needed to manage others
            "hooks": {
                # hook1
                "on_keybinding_slot0": (
                    ("Navigate to an image by its index position",),
                    # keymod, MUST exist in pytheia, or be "0" string:
                    "self.keybindings.keymods['CTRL']",
                    # keyval. Litteral (1st arg) must NOT exist in pytheia:
                    ("self.keybindings.keyvals['i']", Gdk.KEY_i),
                    # callback from this instance:
                    ("self.plugins.plugins_registry['goto_index_position']['instance']." + "cb_action_request"),
                    # callback args would be here as a tuple
                )
            },
        }
