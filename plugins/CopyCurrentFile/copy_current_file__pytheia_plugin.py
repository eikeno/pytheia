# -*- coding: utf-8 -*-
"""
Copy current file

"""

__DONE__ = """
	- implement at keybinding level a docstring for each keybinding:

"""

# TODO:- fixed (short) duration copy notification, windowed mode AND fullscreen
# TODO:	- have self.pytheia.create_main_window() embed a notification widget
# TODO:		stacked aside image... lot of fun :-) < DONE
# TODO:- try to implement inherited variant of this class as base of:
# TODO:	current_file_move
# TODO:- implement plugin "information" system,
# TODO:	based partially on info provided on register()
# TODO:+
# TODO:	'help' feature, base don THIS docstring, exposed though some entry
# TODO:	in register() (to allow dynamic tweaks, templating...)
# TODO:+ 'apidoc' feature, wrapper around pydoc.
# TODO:- > in register_plugins, add support of 'enabled' field, for this.
# TODO:
# TODO: catch the special case of an image already saved to 'save location'
# TODO; being opened, and 'copy' requested; thus, copy requested onto itself:
# TODO: message should tell it is the SAME PHYSICAL FILE


import math
import os
import pdb
import shutil

from gi.repository import (
    Gdk,  # pylint: disable=E0611,W0611
    GdkPixbuf,  # pylint: disable=E0611,W0611
    Gtk,  # pylint: disable=E0611,W0611
)


class _ImagesInfos:
    """
    Manipulate informations about current image

    """

    def __init__(self, pyinstance):
        self.cpn = pyinstance.path_index.path_nodes_store.current_pathnode()
        self.position = self.cpn.position
        self.clear = str(self.cpn.all_files[self.position])
        self.real = str(self.cpn.current_path)

    def current_clear(self):
        """clear text path of the current image"""
        return self.clear

    def current_real(self):
        """real path of the current image"""
        return self.real

    def current_clear_bn(self):
        """clear basename of the current image"""
        return os.path.basename(self.clear)

    def current_real_bn(self):
        """real basename of tge current image"""
        return os.path.basename(self.real)


class _PytheiaPlugin:
    """
    Mixin for PytheiaPlugin.

    Mandatory plugins methods are to be implemented by PytheiaPlugin subclass.

    """

    def __init__(self):
        self.images = None  # <ImagesInfos>

    def _src_dst_comparator(self):
        _mis = math.trunc((float(self.pytheia.screen.screen_height) / 100) * float(35))

        _table_data = {
            "max_per_row": 2,
            "max_images_size": (_mis, _mis),
            "interpolation_type": GdkPixbuf.InterpType.BILINEAR,
            "data": {},
        }

        for path in (self.images.current_real(), self.destination_path):
            _table_data["data"][path] = {"legend": (True, "foo legend "), "tooltip": (True, "foo tooltip")}

        return self.pytheia.wid_images_table(_table_data)

    def _get_destdir(self):
        # Open the widget at the last saved 'destdir' location, if any, and
        # still accessible:
        _destdir_current_value = None
        if "destdir" in self.config:
            if self.config["destdir"] and os.path.isdir(self.config["destdir"]):
                _destdir_current_value = self.config["destdir"]

        print("_destdir_current_value =========> %s" % _destdir_current_value)
        return self.pytheia.wid_filechooser_getdir(
            {
                "widget_title": "Copy destination directory",
                "widget_width": math.trunc(self.pytheia.screen.screen_width / 2),
                "widget_height": math.trunc(self.pytheia.screen.screen_height / 2),
                "msg1": "Please select a directory in which to store copied files: ",
                "msg2": "plop",
                "current_value": _destdir_current_value,
            }
        )

    def _get_action_on_dup(self, _bn, _dup_reason):
        _alike_warn = ""
        _text_default = 1  #
        _default_button = "button_ok"

        md5_src = self.utils.md5_by_path(self.images.current_real())
        md5_dst = self.utils.md5_by_path(self.destination_path)

        if md5_src == md5_dst:
            _text_default = 2  #
            _alike_warn = "<b>Note</b>: the two files have the same content !"
            _default_button = "button_cancel"

        _message1 = "It appears that:\n"
        _message1 += "<b>%s</b>\n\n%s: \n" % (_bn, _dup_reason)
        _message1 += "<i>%s</i>" % self.config["destdir"]

        _message2 = "%s\nPlease select an action:" % _alike_warn

        _ac_rensrc = "Choose another name to save file to"  # 0
        _ac_renaut = "Automatically save under an unused name"  # 1
        _ac_ovwt = "Overwrite target file"  # 2

        _scroll = Gtk.ScrolledWindow()
        _scroll.add_with_viewport(self._src_dst_comparator())
        _scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.pytheia.wid_combo_text_choice(
            {
                "widget_title": "Destination file already exist...",
                "combo_title": "combo title",
                "widget_width": math.trunc(self.pytheia.screen.screen_width / 1.5),
                "widget_height": math.trunc(self.pytheia.screen.screen_height / 1.5),
                "msg1": _message1,
                "msg2": _message2,
                "text_entries": (_ac_rensrc, _ac_renaut, _ac_ovwt),
                "text_default": _text_default,
                "ok": (self.cb_get_action_on_dup_ok, "argsok1"),
                "cancel": (self.cb_get_action_on_dup_cancel, "argscancel1"),
                "default_button": _default_button,
                "extra_widget": _scroll,
            }
        )

    def _get_replacement_filename(self):
        """
        Prompt for replacement filename, taking care of extension

        """
        # give alternative name snipplet:

        _input = None
        while _input is None:
            _input = self.pytheia.wid_get_text_input_simple(
                (
                    "Please enter a replacement filename.\n",
                    "This will be saved under:\n\t<b>%s</b>" % self.config["destdir"],
                    "Filename",
                    "name: ",
                )
            )
            self.plugin_console_out("_input = %s" % str(_input))
            if not _input:  # cancelled or destroyed
                return False

        _src_ext = os.path.splitext(self.images.current_clear_bn())[1]
        _input_bn = os.path.splitext(_input)[0]
        _input_ext = os.path.splitext(_input)[1]

        # Difficult to decide if one must allow changing the extension. There
        # are a few reasonnable cases, so accept. But, refuse a target name
        # without extension if source had one:
        if _src_ext != "" and _input_ext == "":
            _input_ext = _src_ext
            self.plugin_console_out("Automatically appended %s extension" % _input_ext)

        _temp_name = os.path.join(self.config["destdir"], _input_bn + _input_ext)

        # provided replacement name also exists in destdir. Notify of this
        if os.path.exists(_temp_name):
            _msg = "<b>Entered name</b>:\n%s\n\n" % (_input_bn + _input_ext)
            _msg += "<b>already exists</b> under:\n%s\n\n" % (self.config["destdir"])
            _msg += "Please try again.\n"

            self.pytheia.wid_message_dialog_warn({"parent": None, "widget_title": "Warning", "msg1": _msg})
            return None

        self.plugin_console_out(_input_bn + _input_ext)
        return _input_bn + _input_ext

    def cb_get_action_on_dup_ok(self, *args):
        """
        Callback for OK click in 'wid_combo_text_choice' widget

        """

        self._action_on_dup = int(args[0].pytheia_combo_obj.get_active())
        args[0].pytheia_win_obj.destroy()

        # choose another name:
        if self._action_on_dup == 0:
            _replacement_name = None

            while _replacement_name is None:
                _replacement_name = self._get_replacement_filename()
                if not _replacement_name:
                    return False

            # FIXME: check new name doesn't exist, use method for this:
            self.copy(
                self.images.current_real(),  # src
                os.path.join(self.config["destdir"], _replacement_name),  # dst
            )

        # automatic renaming:
        elif self._action_on_dup == 1:
            pass  # FIXME: automatic renaming NotImplementedYet

        # overwrite:
        elif self._action_on_dup == 2:
            self.copy(
                self.images.current_real(),  # src
                self.destination_path,
            )

    def cb_get_action_on_dup_cancel(self, *args):
        """
        Callback for Cancel click in 'wid_combo_text_choice' widget

        """

        self._action_on_dup = None
        args[0].pytheia_win_obj.destroy()

    def cb_set_destdir(self):
        """
        keybinding wrapper around _get_destdir()

        """

        self.plugin_console_out(">>> cb_set_destdir")
        self._oncall_in()
        self.config["destdir"] = self._get_destdir()

        if not self.config["destdir"]:
            return

        self.persistence.dump(source_object=self.config)
        self._oncall_out()

    def cb_action_request(self):
        """
        Initiate copying of current file when registered keybinding's triggered

        """
        self.images = _ImagesInfos(self.pytheia)
        self._oncall_in()  # perst load

        # Iff copy_destination_dir not set, get it interactively:
        if "destdir" not in self.config:
            self.config["destdir"] = self._get_destdir()

        if not self.config["destdir"]:
            # Cancel was chosen. leave without updating configuration:
            return

        # get it too in case stored value is not pointing to a directory:
        elif not os.path.isdir(self.config["destdir"]):
            self.config["destdir"] = self._get_destdir()

        # Cancel was selected, leave now
        if not self.config["destdir"]:
            return True

        # Check if file already exist by the same name under destdir:
        _bn = self.images.current_clear_bn()

        self.destination_path = os.path.join(self.config["destdir"], _bn)
        _dup_reason = None

        if os.path.isfile(self.destination_path):
            _dup_reason = "Already exists as a file in"
        elif os.path.isdir(self.destination_path):
            _dup_reason = "Already exists ad a directory in"
        elif os.path.exists(self.destination_path):
            _dup_reason = "Already exist (but cannot be identified) in"

        if _dup_reason:
            # Ask action to be undertaken if destination already exist:
            self._get_action_on_dup(_bn, _dup_reason)
            # remaining actions will be started by _get_action_on_dup()
            # callbacks.
        else:
            # no duplicate, simply proceed with copy:
            self.copy(self.images.current_real(), self.destination_path)

        self._oncall_out()

    def handle_copy_error(self, excp):
        self.plugin_console_out("handle_copy_error: %s" % excp)
        pass

    def copy(self, src, dst):
        """
        Copy 'src' file to 'dst'

        """

        _status = "Success"
        try:
            shutil.copyfile(src, dst)

        except IOError as excp:
            self.handle_copy_error(excp)
            _status = "Error"

        self.pytheia.notifications.notification_push(
            12,  # context_id
            1550,  # 1/2 second
            "\tCopy of: %s to: %s, %s" % (self.images.current_clear_bn(), self.config["destdir"], _status),
        )
        return True

    def i_was_here(self, *args):
        self.plugin_console_out("copy_current_file's in %s %s" % (args[0], args[1]))


class PytheiaPlugin(_PytheiaPlugin):
    """
    Mandatory plugin class

    """

    _plugin_longdesc = """
	Allow copy of the currently displayed file.

	Destination folder is asked a first time, then sitlently used.
	It can be changed anytime by calling the installed keybinding.

	Copy support checking against doublons, and offers binary + visual
	comparison helper.
	"""

    def __init__(self):
        self.pytheia = None  # <Pytheia>
        self.config = {}
        self._action_on_dup = None
        self.destination_path = None
        _PytheiaPlugin.__init__(self)

    def __del__(self):
        self.plugin_console_out("deller of copy_current_file called")
        pass

    def _oncall_in(self):
        """
        To be used each time plugin is explicitly called (vs imported or
        registered), by the plugin itself.

        """

        self.config = {}
        self.config = self.persistence.load()

        self._action_on_dup = None
        self.destination_path = None

    def _oncall_out(self):
        """
        To be called when a call is ending

        """

        if not self.config:
            self.plugin_console_out("'config' is None when _oncall_out reached")
            return True

        self.persistence.dump(source_object=self.config)

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
            "name": "copy_current_file",
            "author": "Eikeno <eikenault@gmail.com>",
            "copyright": "GPL",
            "website": "https://eikeno.eu",
            "filename": "copy_current_file",
            "categories": "file_management, interactive",
            "shortdesc": "Copy current file to a directory of your choice",
            "longdesc": self._plugin_longdesc,
            "hooks": {
                # hook1
                "on_keybinding_slot0": (
                    ("Copy the current file to destination directory",),
                    # keymod, MUST exist in pytheia, or be "0" string:
                    "0",
                    # keyval. Litteral (1st arg) must NOT exist in pytheia:
                    ("self.keybindings.keyvals['c']", Gdk.KEY_c),
                    # callback from this instance:
                    "self.plugins.plugins_registry['copy_current_file']['instance'].cb_action_request",
                    # callback args would be here as a tuple
                ),
                # hook2
                "on_keybinding_slot1": (
                    ("Select a destination directory for copied files",),
                    "self.keybindings.keymods['SHIFT']",
                    ("self.keybindings.keyvals['C']", Gdk.KEY_C),
                    "self.plugins.plugins_registry['copy_current_file']['instance'].cb_set_destdir",
                    # callback args would be here as a tuple
                ),
                # hook3
                "on_image_load_complete": (self.i_was_here, "the", "place"),
            },
        }
