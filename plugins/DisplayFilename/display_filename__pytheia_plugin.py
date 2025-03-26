# -*- coding: utf-8 -*-
"""
display current file name

"""

import os
import pdb

from gi.repository import Gtk  # pylint: disable=E0611,W0611


class _PytheiaPlugin:
    """
    Mixin for PytheiaPlugin.

    Mandatory plugins methods are to be implemented by PytheiaPlugin subclass.

    """

    def __init__(self):
        pass

    def cb_action_request(self, *args):
        _pn = self.pytheia.path_index.path_nodes_store.current_pathnode()

        self.pytheia.notifications.notification_push(
            10,  # context_id
            500,  # 1/2 second
            ">>> %s"
            % (
                os.path.basename(
                    repr(_pn.all_files[_pn.position])
                    # self.pytheia.path_index.path_nodes_store.current_pathnode()
                )
            ),
        )

    def say_goodbye(self, *args):
        self.plugin_console_out("DisplayFilename Bye !")


class PytheiaPlugin(_PytheiaPlugin):
    """
    Mandatory plugin class

    """

    _plugin_longdesc = """
	Display the filename of current image.

	Some parameters can be customized with plugins_manager.
	"""

    def __init__(self):
        _PytheiaPlugin.__init__(self)
        self.pytheia = None  # running pytheia instance object

    def __del__(self):
        self.plugin_console_out("deller of display_filename called")
        if hasattr(self, "config"):
            self.persistence.dump(source_object=self.config)

    def _oncall(self):
        self.config = {}
        self.config = self.persistence.load()

    def attach(self, pytheia):
        """
        Attach 'pytheia', an accessor to PytheiaGui.core.plugins

        """
        self.pytheia = pytheia

    def register(self):
        return {
            "name": "display_filename",
            "author": "Eikeno <eikenault@gmail.com>",
            "copyright": "GPL",
            "website": "N/A",
            "filename": "display_filename",
            "categories": "notifications",
            "shortdesc": "Display the filename of current image",
            "longdesc": self._plugin_longdesc,
            "hooks": {"on_image_load_complete": (self.cb_action_request,), "on_quit_application": self.say_goodbye},
        }
