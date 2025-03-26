# -*- coding: utf-8 -*-
"""
Widgets
"""

import math

import gi # pylint: disable=import-error
from gi.repository import GdkPixbuf, Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Utils import Utils

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")


class Widgets:
    """
    Different ready to use widgets
    """

    def __init__(self):
        self.main_window = None
        self.platform = None

    def wid_get_text_input_simple(self, t_msg):
        # returns str
        """
        Get text dada from user input

        t_msg => (primsg, secmsg, title, prefix)
        returns entered text, or None

        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), t_msg))

        primsg = t_msg[0]
        secmsg = t_msg[1]
        title = t_msg[2]
        prefix = t_msg[3]

        entry = Gtk.Entry()

        # REM: parent, flags, type, buttons, message_format
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.NONE,
            None,
        )

        # Add just what we need:
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dialog.set_markup(primsg)
        dialog.set_title(title)

        # Create a horizontal box to pack the entry and a label
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(prefix), False, 5, 5)
        hbox.pack_end(entry, True, True, 5)

        if secmsg:
            dialog.format_secondary_markup(secmsg)
            dialog.get_content_area().pack_end(hbox, True, True, 0)  # pylint: disable=E1101

        dialog.show_all()
        result = dialog.run()
        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return False

        text = entry.get_text()

        if text == "":
            dialog.destroy()
            return None

        dialog.destroy()
        return text

    def wid_combo_text_choice(self, combo_data):
        """
        Get a choice from a textual combo list

        IN:
        combo_data = {
            'widget_title':	str,
            'widget_width': int,
            'widget_height': int,
            'combo_title': str,
            'msg1': str,
            'msg2': str;
            'text_entries': (str1, ..., strN),
            'text_default': int,
            'ok': (callback_func, callback_args),
            'cancel': (calback_func, callback_args)
            'debault_button': str('button_ok' or 'button_cancel')
        }

        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), combo_data))

        # Visual elements
        win = Gtk.Window()
        win.set_title(combo_data["widget_title"])
        win.set_size_request(combo_data["widget_width"], combo_data["widget_height"])
        win.set_position(Gtk.WindowPosition.CENTER)

        label1 = Gtk.Label()
        label1.set_markup(combo_data["msg1"])

        label2 = Gtk.Label()
        label2.set_markup(combo_data["msg2"])

        hsep = Gtk.HSeparator()
        vbox = Gtk.VBox()

        combo = Gtk.ComboBoxText()
        combo.set_title(combo_data["combo_title"])

        for text in combo_data["text_entries"]:
            combo.append_text(text)
        combo.set_active(combo_data["text_default"])

        button_ok = Gtk.Button.new_from_stock(Gtk.STOCK_OK)
        button_cancel = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)

        # ease access from external callbacks:
        button_ok.pytheia_combo_obj = combo
        button_cancel.pytheia_combo_obj = combo
        button_ok.pytheia_win_obj = win
        button_cancel.pytheia_win_obj = win

        button_ok.connect("clicked", combo_data["ok"][0], combo_data["ok"][1])
        button_cancel.connect("clicked", combo_data["cancel"][0], combo_data["cancel"][1])

        button_box = Gtk.HButtonBox()
        button_box.add(button_cancel)
        button_box.add(button_ok)

        vbox.pack_start(label1, False, False, 5)
        vbox.pack_start(hsep, False, False, 5)

        if combo_data["extra_widget"]:
            vbox.pack_start(combo_data["extra_widget"], True, True, 5)
            vbox.pack_start(hsep, False, False, 5)

        vbox.pack_start(label2, False, False, 5)
        vbox.pack_start(combo, False, False, 5)
        vbox.pack_start(button_box, False, False, 5)

        win.add(vbox)
        win.set_focus(eval(combo_data["default_button"]))
        win.show_all()  # no return, callbacks will do the job.

    def wid_images_table(self, table_data):
        """
        Create an images table following given format/option

        table_data = {
            "max_per_row": int,
            "max_images_size": (int_w, int_h),
            'interpolation_type': <GdkPixbuf.InterpType>

            'data': {
                "path1" : {
                    'legend': (bool, str),
                    'tooltip': (bool, str)
                },
                [...]
                "pathN" : {
                    'legend': (bool, str),
                    'tooltip': (bool, str)
                }
            }
        }

        returns <Gtk.Table>
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), table_data))

        # find hwo many row to create:
        keys_num = len(table_data["data"].keys())
        max_per_row = table_data["max_per_row"]
        rows = 1

        if keys_num > table_data["max_per_row"]:
            rows = math.ceil(float(keys_num) / float(max_per_row))

        table = Gtk.Table(rows, max_per_row, False)

        left_attach = 0
        right_attach = 1
        top_attach = 0
        bottom_attach = 1

        for path in table_data["data"].keys():
            if right_attach > max_per_row:
                # end of row reached, start a new one:
                left_attach = 0
                right_attach = 1
                top_attach += 1
                bottom_attach += 1

            forced_size = Utils.get_fit_best_sizes(  # static method
                table_data["max_images_size"],  # fit_sizes_t
                GdkPixbuf.Pixbuf.new_from_file(path).get_properties("width", "height"),  # src_sizes_t
            )
            debug("forced_size = %s, %s" % forced_size)

            pxbf = Utils.scale_pixbuf(  # static method
                GdkPixbuf.Pixbuf.new_from_file(path),  # reference pixbuf
                forced_size,
                table_data["interpolation_type"],
            )

            img = Gtk.Image()
            img.set_from_pixbuf(pxbf)

            # Add an eventBox in case caller wants to bind callbacks:
            eventbox = Gtk.EventBox()
            eventbox.add(img)
            eventbox.pytheia_file_path = path  # ease external manipulation

            table.attach(
                eventbox,  # child
                left_attach,
                right_attach,
                top_attach,
                bottom_attach,
                Gtk.AttachOptions.EXPAND,  # xoptions
                Gtk.AttachOptions.EXPAND,  # yoptions
                3,  # xpadding
                3,  # ypadding
            )

            # increment to next one horizontally:
            left_attach += 1
            right_attach += 1

        table.show_all()
        return table

    def wid_filechooser_getdir(self, filechooser_data):
        """
        Select a directory and return its path

        IN: filechooser_data = {
            "widget_title": "Copy destination directory",
            "widget_width": int,
            "widget_height": int,
            "msg1": str,
            "msg2": str,
            "current_value": None,
            }

        OUT: str
        """
        gdebug(f"# {self.__class__}:{callee()}")
        destination = None

        dialog = Gtk.FileChooserDialog(
            filechooser_data["widget_title"],
            self.main_window,  # parent - FIXME: verify if needed, and should be set with setter
            Gtk.FileChooserAction.SELECT_FOLDER,  # ignore files
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )

        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_property("extra-widget", Gtk.Label(filechooser_data["msg1"]))
        dialog.set_property("show-hidden", False)

        # Where to start. Use last choice if provided:
        if filechooser_data["current_value"] is not None:
            debug("setting current folder to %s" % filechooser_data["current_value"])
            dialog.set_current_folder(filechooser_data["current_value"])
        else:
            # use home
            dialog.set_current_folder(self.platform.get_infos()["userdir"])

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            destination = dialog.get_uri().replace("file://", "")
            dialog.destroy()

        elif response == Gtk.ResponseType.CANCEL:
            debug("Directory selection aborted by user")
            dialog.destroy()
            return None

        debug("Selected directory: %s" % destination)
        return destination

    def wid_message_dialog_warn(self, warn_data):
        """
        Warning message dialog widget.

        IN: dict: warn_data

        warn_data = {
                'parent': None,
                'widget_title': str,
                'msg1': str
            }

        returns: bool
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), warn_data))

        # REM: parent, flags, type, buttons, message_format
        dialog = Gtk.MessageDialog(
            warn_data["parent"],
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.NONE,
            None,
        )

        # Add just what we need:
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_markup(warn_data["msg1"])
        dialog.set_title(warn_data["widget_title"])

        # since in modal mode, gtk main loop stays here until 'ok' clicked:
        result = dialog.run()

        if result != Gtk.ResponseType.OK:
            dialog.destroy()
            return False

        dialog.destroy()
        return True
