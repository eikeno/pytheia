# -*- coding: utf-8 -*-
"""
ImagesGrid
"""

import math
import os
import queue
import syslog
import threading

import gi # pylint: disable=import-error
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango  # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Utils import Utils

gi.require_version("Pango", "1.0")

# Make sure GLib won't conflict with threading:
GLib.threads_init()


class ImagesGrid:
    """
    Image grid based on GtkGrid, with extras features.

    Can be placed in a ScolledWindow and will display only the visible sub
    widgets, based on scroll events, allowing dealing with relatively large
    images list.
    """

    def __init__(
        self,
        parent,
        index,  # <PathIndex>
        loading_icon_file,
        on_click=None,
        num_worker_threads=12,
        queue_maxsize=0,
    ):
        self.grid_data = None  # Dict
        self.grid = None  # <GtkGrid>
        self.max_per_row = None  # Int
        self.items = None  # Dict
        self.platform = None  # <Platform>
        self.path_index = index

        self.last_w = None  # Int
        self.last_h = None  # Int
        self.scroll_upper = 0

        self.loading_icon_file = loading_icon_file
        self.loading_icon_pxbf = None
        self.loading_icon_pxbf_w, self.loading_icon_pxbf_h = None, None
        self.loading_image = None

        self.parent = parent  # <GtkWindow> or similar
        self.on_click = on_click  # Callable

        self.lock = threading.Lock()
        self.num_worker_threads = num_worker_threads
        self.queue = queue.Queue(maxsize=queue_maxsize)

        self._threads_pool_init()

    def __del__(self):
        self.queue.join()
        self.queue = None
        self.parent = None

    def _threads_pool_init(self):
        """
        Initialize a pool of 'num_worker_threads' daemon threads to treat data
        in the queue.
        """

        syslog.syslog("pytheia using %s threads workers" % str(self.num_worker_threads))
        for _ in range(self.num_worker_threads):
            _thread = threading.Thread(target=self._render_worker)
            _thread.daemon = True  # property since python3+
            _thread.start()

    def initialize(self, grid_data):
        """
        Initialization routine
        """

        self.grid_data = grid_data
        self.max_per_row = self.grid_data["max_per_row"]
        self.items = self.grid_data["data"]

        self.loading_icon_pxbf = Utils.scale_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file(self.loading_icon_file),  # ref. pixbuf
            self.grid_data["max_images_size"],  # t_sizes
            self.grid_data["interpolation_type"],  # interp_method
        )

        self.loading_icon_pxbf_w, self.loading_icon_pxbf_h = self.loading_icon_pxbf.get_properties("width", "height")

        self.loading_image = Gtk.Image()
        self.loading_image.set_from_pixbuf(self.loading_icon_pxbf)

    def set_max_per_row(self, max_i):
        """
        Sets a maximum items per row value
        """

        self.max_per_row = max_i

    def set_items(self, items_d):
        """
        Assigns a dictionnary to "grid_data['data']".
        """

        self.grid_data["data"] = items_d

    def set_scrollbar_position(self):
        """
        Set the position of the scrollbar, based on the current position in the
        provided 'index' (a <PathIndex> object).

        i.e: make the current picture visible in the current scroll view.
        """

        _va = self.grid.get_parent().get_parent().get_vscrollbar().get_adjustment()
        _vau = _va.get_upper()
        if _vau > self.scroll_upper:
            self.scroll_upper = _vau

        _idx_pos = self.path_index.path_nodes_store.current_pathnode().position
        _idx_len = len(self.path_index.path_nodes_store.current_pathnode().all_files)
        _row_scroll_height = _vau / _idx_len

        _idx_pos_pct = round((100 / _idx_len) * _idx_pos)
        _new_scroll_pos = float((self.scroll_upper / 100) * _idx_pos_pct)
        _va.set_value(_new_scroll_pos - (4 * _row_scroll_height))
        _va.value_changed()

    def update_grid(self, initial=False):
        """
        Creates an images self.grid_data['max_per_row'] following given
        format/option.

        Returns a <Gtk.self.grid_data['max_per_row']>

        'grid_data' description:
        self.grid_data = {

            "keep_ratio": bool,
            "max_per_row": int,                # -1 = auto
            "max_images_size": (int_w, int_h), # -1 = unscaled

            # one of: BILINEAR, HYPER, NEAREST, TILES
            'interpolation_type': <GdkPixbuf.InterpType>,

            'xoptions': <Gtk.AttachOptions> # EXPAND, FILL, SHRINK
            'yoptions': <Gtk.AttachOptions> # EXPAND, FILL, SHRINK
            'xpadding': int,
            'ypadding': int,

            'data': {

                "item1" {
                    "pathnodeitem" : <PathNodeItemCacheable>
                    'legend_type': Str
                    'legend_text': str,
                    'legend_wrap': Bool,
                    'legend_wrap_mode': Str # or None
                    'tooltip_type': Str # None, 'auto', 'text',
                    'tooltip_text': Str # or None
                },

                [...]

                "itemN" : {
                    [...]
                }
            }
        }
        """
        gdebug("# %s:%s(initial=%s)" % (self.__class__, callee(), str(initial)))

        tooltip_text = None
        # Find how many columns fit in one row if auto mode on:
        if self.grid_data["max_per_row"] == -1:
            self.max_per_row = math.ceil(
                self.parent.get_size()[0]
                / (
                    self.grid_data["max_images_size"][0]
                    + (2 * self.grid_data["xpadding"])
                    + (2 * self.grid_data["col_spacing"])
                )
            )
        else:
            self.max_per_row = self.grid_data["max_per_row"]
        debug("max_per_row = %s" % self.max_per_row)

        # Don't overwrite on ourselves:
        if self.grid is not None:
            _parent_vp = self.grid.get_parent()
            _parent_vp.remove(self.grid)
            self.grid = Gtk.Grid()
            _parent_vp.add(self.grid)
        else:
            self.grid = Gtk.Grid()

        self.grid.set_property("column-homogeneous", True)

        left_attach = 0
        right_attach = 1
        top_attach = 0
        bottom_attach = 1

        for item in sorted(self.items.keys()):
            if right_attach > self.max_per_row:
                # End of row reached, start a new one:
                left_attach = 0
                right_attach = 1
                top_attach += 1
                bottom_attach += 1

            # Use a placeholder 'loading' image first, to be replaced on any
            # visibility event reception:
            image = Gtk.Image()
            image.show()

            # Add a reference to the 'real' image to be rendered later:
            if not isinstance(self.items[item]["pathnodeitem"], str):
                image.pytheia_filename = str(self.items[item]["pathnodeitem"])
                image.pytheia_filepath = self.items[item]["pathnodeitem"].filepath_norm
                image.pytheia_imageobj = self.items[item]["pathnodeitem"]
            else:
                image.pytheia_filepath = str(self.items[item]["pathnodeitem"])
                image.pytheia_filename = image.pytheia_filepath
                image.pytheia_imageobj = self.items[item]["pathnodeitem"]

            # placeholder sizes, to be replaced by real images sizes later:
            image.pytheia_target_sizes = (
                self.loading_icon_pxbf_w,
                self.loading_icon_pxbf_h,
            )
            image.pytheia_target_sizes = self.grid_data["max_images_size"]

            # Tooltip:
            if self.items[item]["tooltip_type"]:
                if self.items[item]["tooltip_type"] == "auto":
                    tooltip_text = os.path.basename(image.pytheia_filename)

                elif self.items[item]["tooltip_type"] == "text":
                    if not self.items[item]["tooltip_text"]:
                        tooltip_text = "_ERROR_"
                    else:
                        tooltip_text = self.items[item]["tooltip_text"]
                image.set_has_tooltip(True)
                image.set_tooltip_text(tooltip_text)

            # Allow using callbacks with an eventbox:
            eventbox = Gtk.EventBox()

            if self.on_click:
                eventbox.connect_after("button-press-event", self.on_click)

            # Add reference to pathname and contained image to ease parsing:
            eventbox.pytheia_filename = image.pytheia_filename
            eventbox.pytheia_filepath = image.pytheia_filepath
            eventbox.pytheia_imageobj = image.pytheia_imageobj
            eventbox.pytheia_gtkimage = image
            eventbox.pytheia_is_rendered = False
            eventbox.pytheia_skip_render = True

            eventbox_vbox = Gtk.VBox(homogeneous=False, spacing=0)
            eventbox.add(eventbox_vbox)

            # React to visibility events
            eventbox.add_events(Gdk.EventMask.VISIBILITY_NOTIFY_MASK | Gdk.EventMask.EXPOSURE_MASK)

            # Legend:
            legend_text = " N/A "
            if self.items[item]["legend_type"]:
                if self.items[item]["legend_type"] == "auto":
                    legend_text = os.path.basename(eventbox.pytheia_filename)
                elif self.items[item]["legend_type"] == "text":
                    if not self.items[item]["legend_text"]:
                        legend_text = "_ERROR_"
                    else:
                        legend_text = self.items[item]["legend_text"]

            label = Gtk.Label(legend_text)
            label.set_justify(Gtk.Justification.CENTER)
            label.set_ellipsize(Pango.EllipsizeMode.START)
            label.set_property("wrap", True)
            label.set_property("wrap_mode", Pango.WrapMode.CHAR)
            label_hbox = Gtk.HBox()
            label_hbox.pack_start(label, True, False, 0)

            eventbox_vbox.pack_end(child=label_hbox, expand=False, fill=False, padding=0)
            eventbox_vbox.pack_start(child=image, expand=False, fill=False, padding=0)
            self.grid.attach(
                eventbox,  # child
                left_attach,  # pos
                top_attach,  # post
                1,  # width in cell
                1,  # height in cell
            )

            # Increment to next one horizontally:
            left_attach += 1
            right_attach += 1

            # costs a little initial latency, but avoids too many widgets
            # to be visible initially and being rendered
            self._unrender(eventbox)

            eventbox.connect_after("visibility-notify-event", self.cb_eventbox_visibility_notify_event)

        self.last_w, self.last_h = self.parent.get_size()
        self.grid.set_column_spacing(self.grid_data["col_spacing"])
        self.grid.set_row_spacing(self.grid_data["row_spacing"])
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(False)
        self.grid.show_all()

    def _images_objects_list(self):
        """
        Returns a list of images objects

        """
        return [im[0] for im in [e.get_child().get_children() for e in self.grid.get_children()]]

    def _eventboxes_objects_list(self):
        """
        Returns children list of 'grid'.

        """
        return self.grid.get_children()

    def _unrender(self, widget):
        """
        Reset image to generic loading style icon

        """
        widget.pytheia_gtkimage.set_from_pixbuf(self.loading_icon_pxbf)

        widget.pytheia_gtkimage.pytheia_target_sizes = (
            self.loading_icon_pxbf_w,
            self.loading_icon_pxbf_h,
        )
        widget.pytheia_is_rendered = False

    def _render_worker(self):
        """
        Render visible images

        """
        while True:
            qdata = self.queue.get()
            widget = qdata[1]

            self.lock.acquire()

            if not widget.pytheia_is_rendered and not widget.pytheia_skip_render:
                if not isinstance(widget.pytheia_imageobj, str):
                    widget.pytheia_imageobj.uncompress_file_if_needed()

                pixbuf = GdkPixbuf.Pixbuf.new_from_file(widget.pytheia_filepath)
                pixbuf_w, pixbuf_h = pixbuf.get_properties("width", "height")

                # Scale pixbuf or not depending on context:
                if pixbuf_w > self.grid_data["max_images_size"][0] or (
                    (pixbuf_h > self.grid_data["max_images_size"][1]) and (-1 not in self.grid_data["max_images_size"])
                ):
                    if self.grid_data["keep_ratio"]:
                        pixbuf = Utils.scale_pixbuf(
                            pixbuf,  # reference pixbuf
                            (
                                self.grid_data["max_images_size"][0],
                                self.grid_data["max_images_size"][0],
                            ),
                            self.grid_data["interpolation_type"],
                        )
                    else:
                        pixbuf = pixbuf.scale_simple(
                            self.grid_data["max_images_size"][0],
                            self.grid_data["max_images_size"][1],
                            self.grid_data["interpolation_type"],
                        )

                if (
                    pixbuf_w > self.grid_data["max_images_size"][0] or (pixbuf_h > self.grid_data["max_images_size"][1])
                ) and (
                    -1 in self.grid_data["max_images_size"]  # unscaled requested
                ):
                    raise RuntimeError("Image is bigger than allowed and scaling is disabled")

                widget.pytheia_gtkimage.set_from_pixbuf(pixbuf)
                widget.pytheia_is_rendered = True
            self.lock.release()
            self.queue.task_done()

    def cb_eventbox_visibility_notify_event(self, widget, data=None):
        """
        Callback. Gets notified of visibility changes of an image,
        starts render as needed.

        Widget expected to be <Gtk.EventBox>
        """
        if data.state.value_name in (
            "GDK_VISIBILITY_UNOBSCURED",
            "GDK_VISIBILITY_PARTIAL",
        ):
            self.queue.put(
                (
                    "render",
                    widget,
                ),
                block=False,
            )
            widget.pytheia_skip_render = False

        elif data.state.value_name in ("GDK_VISIBILITY_FULLY_OBSCURED",):
            widget.pytheia_skip_render = True
            self._unrender(widget)
            widget.pytheia_skip_render = False

        else:
            raise ValueError("value_name not supported: %s" % str(data.state.value_name))
