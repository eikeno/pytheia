# -*- coding: utf-8 -*-
"""
ThumbnailsView
"""

import math
import os

from gi.repository import Gdk, GdkPixbuf, Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Utils import Utils
from pytheialib.widgets.ImagesGrid import ImagesGrid


class ThumbnailsView:
    """Display images in a thumbnails window"""

    def __init__(self):
        gdebug(f"# {self.__class__}:{callee()}")
        self.window = None  # <GtkWindow>
        self.images_grid = None  # <ImagesGrid>
        self.path_index = None  # <PathIndex>
        self.callbacks = None  # <Callbacks>
        self.screen = None  # <Screen>
        self.image_display_widget = None  # <ImageDisplayWidget>
        self.platform = None  # <Platform>
        self.display_orientation = None  # Str (landscape, square, ...)

    def initialize(self):
        """post-creation initialization"""
        gdebug("# %scrwin:%scrwin()" % (self.__class__, callee()))

        # Later base calculation of thumbs sizes and density on the display type
        self.display_orientation = Utils.orientation_from_sizes(self.screen.screen_width, self.screen.screen_height)

        # Prepare data to be passed to the grid:
        data = {}
        for i in self.path_index.path_nodes_store.current_pathnode().all_files:
            data[os.path.basename(str(i))] = {
                "pathnodeitem": i,
                "legend_type": "auto",  # None, 'auto', 'text'
                "legend_text": None,  # 'text' or None
                # FIXME: display of the tooltip started influencing the scroll in recent gtk version: find workaround
                "tooltip_type": None,  # 'auto', # None, 'auto', 'text',
                "tooltip_text": None,  # 'text' or None
            }

        # Place above main window, and be borderless:
        self.window = Gtk.Window(type=Gtk.WindowType.POPUP)

        self.window.set_size_request(*self.image_display_widget.main_window.get_size())
        self.window.move(*self.image_display_widget.main_window.get_position())
        self.window.set_parent(self.image_display_widget.main_window)
        self.window.set_transient_for(self.image_display_widget.main_window)

        self.images_grid = ImagesGrid(
            self.window,  # parent
            self.path_index,  # index
            os.path.join(  # loading_icon_file
                self.platform.pytheia_data_dir_system, "imgloading.svg"
            ),
            self.cb_clicked,  # on_click
        )

        # Allow resizing with grid refreshing:
        self.window.connect("check-resize", self.cb_window_state_event, self.images_grid, self.window)

        # Allow closing:
        self.window.connect("destroy", self.destroy)

        # Feed the grid:
        xpadding = 3  # FIXME: xpadding and ypadding shouldn't be hardcoded
        ypadding = 3

        if self.display_orientation in ("landscape", "square"):
            items_per_row = 5
            width = height = math.trunc(self.image_display_widget.main_window.get_size()[0] / items_per_row)

        else:
            items_per_row = 3
            width = height = math.trunc(self.image_display_widget.main_window.get_size()[0] / items_per_row)
        self.images_grid.initialize(
            {
                "keep_ratio": True,
                "max_per_row": -1,  # -1 = auto
                "max_images_size": (width, height),  # -1 = unscaled
                # One of: BILINEAR, HYPER, NEAREST, TILES
                "interpolation_type": GdkPixbuf.InterpType.HYPER,
                "xoptions": Gtk.AttachOptions.EXPAND,  # EXPAND, FILL, SHRINK
                "yoptions": Gtk.AttachOptions.EXPAND,  # EXPAND, FILL, SHRINK
                "xpadding": xpadding,
                "ypadding": ypadding,
                "col_spacing": 5,
                "row_spacing": 5,
                "data": data,
            }
        )

        self.images_grid.update_grid(initial=True)

        vbx = Gtk.VBox(True, spacing=5)
        vport = Gtk.Viewport()
        scrwin = Gtk.ScrolledWindow()

        scrwin.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)

        # Pack widgets:
        vport.add(self.images_grid.grid)
        vbx.pack_end(scrwin, True, True, 10)
        scrwin.add(vport)
        self.window.add(vbx)
        self.images_grid.set_scrollbar_position()

        # Let receive needed events:
        self.window.add_events(Gdk.EventMask.PROPERTY_CHANGE_MASK)
        # display:
        self.window.show_all()

    # noinspection PyUnusedLocal
    def cb_window_state_event(self, widget, image_grid=None, win=None):
        """callback, to allow resizing"""
        gdebug(f"# {self.__class__}:{callee()}")

        if image_grid.last_w is not None and image_grid.last_h is not None:
            if (
                image_grid.last_w,
                image_grid.last_h,
            ) != win.get_size():
                image_grid.update_grid()

    @staticmethod
    def hide():
        """Unused for now"""
        # FIXME: __CODEME__

        pass

    @staticmethod
    def show():
        """Unused for now"""
        # FIXME: __CODEME__

        pass

    def destroy(self, *args):
        """Destroys this widget's main window"""
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(args)))

        self.window.destroy()

    # noinspection PyUnusedLocal
    def cb_clicked(self, eventbox, *args):
        """Callback, action to run when a thumb is clicked"""

        cur_idx = self.path_index.path_nodes_store.current_pathnode().position
        goto_idx = self.path_index.path_nodes_store.current_pathnode().all_files.index(eventbox.pytheia_imageobj)
        offset = goto_idx - cur_idx
        self.callbacks.cb_path_seek(offset)
        self.destroy()

    def __del__(self):
        """Deletter"""

        self.destroy()
