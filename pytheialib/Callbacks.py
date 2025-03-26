# -*- coding: utf-8 -*-
"""
Callbacks
"""

import os
import sys
import time

import gi # pylint: disable=import-error

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.ThumbnailsView import ThumbnailsView
from pytheialib.Utils import Utils


class Callbacks:
    """Mixin of callback needed by other Mixins and objects"""

    def __init__(self):
        self.config = None  # <PytheiaGui.config>
        self.display_state = None  # <DisplayState>
        self.image_display = None  # <ImageDisplay>
        self.image_display_widget = None  # <ImageDisplayWidget>
        self.lock = None  # <threading.Lock>
        self.notifications = None  # <Notifications>
        self.path_index = None  # <PathIndex>
        self.persistence = None  # <Persistence>
        self.pbl = None  # <ProgressivePixbufLoader>
        self.platform = None  # <Platform>
        self.plugins = None  # <Plugins>
        self.screen = None  # <Screen>
        self.source_image = None  # <SourceImage>
        self.render_state = None  # int
        self.render_first_block_updated = None  # int
        self.thumbnails_view = None  # <ThumbnailsView>

    @staticmethod
    def cb_debug(*args):
        """debugging callback"""
        raise NotImplementedError

    # noinspection PyUnusedLocal
    def cb_fit_best(self, *args):
        """callback to toogle fit_best"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.display_state.do_fit_best()

    # noinspection PyUnusedLocal
    def cb_fit_width(self, *args):
        """callback to toggle fit_width"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.display_state.do_fit_width()

    # noinspection PyUnusedLocal
    def cb_fit_height(self, *args):
        """callback to toggle fit_height"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.display_state.do_fit_height()

    # noinspection PyUnusedLocal
    def cb_toggle_fullscreen(self, *args):
        """callback to toggle fit_fullscreen"""
        gdebug(f"# {self.__class__}:{callee()}")

        # DisplayState()
        self.display_state.toggle_fullscreen()

    @staticmethod
    def cb_toggle_slideshow(*args):
        """callback to toggle slideshow"""
        raise NotImplementedError

    # noinspection PyUnusedLocal
    def cb_zoom_in(self, *args):
        """callback to zoom in"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.lock.acquire()
        self.display_state.request_zoom_in()
        self.lock.release()

    # noinspection PyUnusedLocal
    def cb_zoom_out(self, *args):
        """callback to zoom out"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.lock.acquire()
        self.display_state.request_zoom_out()
        self.lock.release()

    @staticmethod
    def cb_toggle_zoom_lock(*args):
        """callback to toggle zoom_lock"""
        raise NotImplementedError

    # noinspection PyUnusedLocal
    def cb_original_resolution(self, *args):
        """cllback to switch to original resolution (1:1)"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.lock.acquire()
        self.display_state.request_zoom_original_resolution()
        self.lock.release()

    def _do_update_display(self):
        """Apply last change to update the display"""
        # register image for the update path:
        self.source_image.register_image(
            self.path_index.path_nodes_store.current_pathnode()  # current_path
        )

        # ProgressivePixbufLoader()
        self.pbl.pixbuf_loader_start()

    def cb_path_seek_generic(self, offset, whence):
        """callback to perform a path_seek offering different modes"""
        wdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), offset, whence))

        if offset is None:  # but int(zero) is OK
            raise TypeError("offset cannot be None")
        if whence is None:
            raise TypeError("whence cannot be None")

        # TODO: implement method to stop a render in progress without waiting
        if self.render_state not in (None, 2):
            debug("moving by %d position(s) rejected: render is in progress" % offset)
            # KeyBindings needs a boolean:
            return False

        # Since no render is in progress, clear possible previous render mess:
        self.image_display_widget.image_display_widget_free_all()

        # PathIndex()
        # Use pathIndex as a proxy to request seek() to the underlying Node type:
        self.path_index.seek(offset, whence)

        self._do_update_display()

    def cb_pathnode_seek_next(self):
        """Jump to the next pathnode, if any"""
        gdebug(f"# {self.__class__}:{callee()}")

        self.path_index.pathnode_seek_next()
        # Use 0 offset will just trigger display update, seeking being
        # already done;
        self.cb_path_seek_generic(0, os.SEEK_CUR)

        self.notifications.notification_push(
            2,  # context_id
            1000,  # context_id
            "Location: " + str(self.path_index.path_nodes_store.current_pathnode().start_uri),
        )

    def cb_pathnode_seek_previous(self):
        """Jump to the next pathnode, if any"""
        gdebug(f"# {self.__class__}:{callee()}")

        self.path_index.pathnode_seek_previous()

        # Use 0 offset will just trigger display update, seeking being
        # already done;
        self.cb_path_seek_generic(0, os.SEEK_CUR)

        self.notifications.notification_push(
            2,  # context_id
            1000,  # milliseconds
            "Location: " + str(self.path_index.path_nodes_store.current_pathnode().start_uri),
        )

    def cb_path_seek(self, delta):
        """callback to perform a path_seek"""
        wdebug("# %s:%s(%s)" % (self.__class__, callee(), delta))
        print("\n\n\n")
        if not delta:
            raise TypeError("delta cannot be None")

        self.cb_path_seek_generic(delta, os.SEEK_CUR)

    def cb_path_seek_stepped(self, delta):
        """
        If window is not scrolled, act as 'cb_path_seek'.
        In scrolled mode, scroll down by one vertical screen size if scrollbar
        is not currently already at it downest position. If scrollbar is already
        at its downest position, act as 'cb_path_seek'
        """
        wdebug("# %s:%s(%s)" % (self.__class__, callee(), delta))
        print("\n\n\n")  # FIXME: shouldn't this be debug statement ?

        _vsb = (
            self.image_display_widget.main_window.get_children(
                # main_vbox
            )[0]
            .get_children(
                # main_scroll
            )[0]
            .get_vscrollbar()
        )

        # if vertical scrollbar is not visible, forward to cb_path_seek():
        if not _vsb.get_visible():
            self.cb_path_seek(delta)
        else:
            # returns the value of the upper point of the slider
            _val = _vsb.get_adjustment().get_value()

            # vertical size of the slider
            _pgsz = _vsb.get_adjustment().get_page_size()

            # end of the slide rail
            _upper = _vsb.get_adjustment().get_upper()

            if _val + _pgsz >= _upper:
                # we're already at the end, forward to cb_path_seek():
                self.cb_path_seek(delta)
            else:
                # set new position start as current position stop
                _vsb.set_value(_val + _pgsz)

    def cb_thumbnails_navigate(self, *args):
        """Thumbnails navigator"""
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(args)))

        self.thumbnails_view = ThumbnailsView()
        self.thumbnails_view.path_index = self.path_index
        self.thumbnails_view.image_display_widget = self.image_display_widget
        self.thumbnails_view.cb_path_seek = self.cb_path_seek
        self.thumbnails_view.screen = self.screen
        self.thumbnails_view.platform = self.platform
        self.thumbnails_view.initialize()

    # noinspection PyUnusedLocal
    def cb_quit(self, reason=None, *args):
        """callback to quit the application"""
        gdebug(f"# {self.__class__}:{callee()}")
        # pylint: disable=bare-except

        if reason:
            debug("Pytheia is stopping: %s" % str(reason))

        self.lock.acquire()

        # Plugins()
        # noinspection PyBroadException
        try:
            self.plugins.plugins_hooks_on_event_generic("on_quit_application")
        except Exception as ex:
            debug("ERROR on calling plugins_hooks_on_event_generic(%s), %s" % ("on_quit_application", ex))

        # Have PluginsStore() backup its state for next run:
        self.plugins.plugins_store.__del__()

        # Call plugins dellers, and dereference them:
        self.plugins.destroy_plugins()

        # Backup core configuration:
        self.persistence.dump(self.config)

        self.path_index.__del__()
        Gtk.main_quit()
        self.lock.release()
        sys.exit(0)

    def cb_area_closed(self, pixbuf_loader):
        """callback triggered when PixbufLoader has finished reading its data stream"""
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), pixbuf_loader))

        # Update timer
        self.pbl.time_stop = time.time()

        self.pbl.time_load_average.add_value(self.pbl.time_stop - self.pbl.time_start)

        ydebug("Average Loading time = %s" % str(self.pbl.time_load_average.compute_average()))
        ydebug("Current Loading time = %s" % str(self.pbl.time_stop - self.pbl.time_start))

        # final commit
        self.display_state.state_commit()

        # DisplayState
        self.render_state = 2

        # Plugins()
        self.plugins.plugins_hooks_on_event_generic("on_image_load_complete")

        if self.display_state.zoom:
            self.plugins.plugins_hooks_on_event_generic("on_zoom_performed")

    def cb_area_updated(self, pixbuf_loader, x_ofst, y_ofst, width, heigth):
        """
        Triggered when PixbufLoader has gathered a new chunk of data

        Args:
            pixbuf_loader: <GdkPixbufLoader>
            x_ofst:  Int, X offset of upper-left corner of the updated area.
            y_ofst:  Int, Y offset of upper-left corner of the updated area.
            width:  Int, Width of updated area.
            heigth:  Int, Height of updated area.

        Returns:    Bool
        """

        if self.source_image.prominent_axis == "x":
            ref = x_ofst
        else:
            ref = y_ofst

        if ref in self.pbl.breakpoints_render_tuple or (ref + 1 in self.pbl.breakpoints_render_tuple):
            if not self.display_state.render_pass:
                self.lock.acquire()
                self.display_state.render_pass = 0
                self.lock.release()

            # Multiple passes detection:
            if ref <= self.pbl.breakpoints_render_tuple[0]:
                self.render_first_block_updated += 1

            if self.render_first_block_updated > 1 and (ref < self.pbl.breakpoints_render_tuple[-2:][0]):
                # Allow only last updates from progressive images updates seqs:
                self.display_state.render_pass += 1
                ydebug("N-1 first blocks of secondary prog. seq. " + "skipped (ref:%s)" % ref)
                return True

            elif 1 < self.display_state.render_pass <= 7:
                debug("progressive chunk accepted at pass, ref = %s, %s" % (self.display_state.render_pass, ref))

            elif self.display_state.render_pass > 7:
                rdebug(
                    "REJECT: render_pass %s is over "
                    % (str(self.display_state.render_pass) + "the 7 limit. Wait for last event")
                )
                return

            # Continue, normal or progressive images treated the same:
            if self.render_state not in (0, 1):
                wdebug("cb_area_updated received state: %s" % self.render_state)
                raise RuntimeError("render_state has unexpected value: %s" % str(self.render_state))

            # It's now useful to flag rendering as updated:
            # DisplayState()
            self.render_state = 1

            debug("render : committed")
            self.display_state.state_commit()

            self.pbl.breakpoint_pos += 1
            if Gtk.events_pending():
                Gtk.main_iteration()

            # Only debug on breakpoints, to avoid clutter output with hundreds
            # of lines:
            gdebug(
                "# %s:%s(%s,%s,%s,%s,%s)"
                % (
                    self.__class__,
                    callee(),
                    pixbuf_loader,
                    x_ofst,
                    y_ofst,
                    width,
                    heigth,
                )
            )

            return True

    def cb_area_prepared(self, pixbuf_loader):
        """
        Trigerred once PixbufLoader contains enough data to determine pixbuf
        size and type, allowing to prepare the display area.

        Args:
            pixbuf_loader: <GdkPixbufLoader>

        Returns:
            Bool
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), pixbuf_loader))
        # Note: using received pixbuf_loader instead of self.pixbuf_loader
        # helps reducing the coupling, a little.

        # Dimensions:
        self.source_image.width = pixbuf_loader.get_pixbuf().get_property("width")
        self.source_image.height = pixbuf_loader.get_pixbuf().get_property("height")

        # Orientation:
        self.source_image.orientation = Utils.orientation_from_sizes(self.source_image.width, self.source_image.height)

        if self.source_image.orientation == "landscape":
            self.source_image.prominent_axis = "x"

        elif self.source_image.orientation == "portrait":
            self.source_image.prominent_axis = "y"

        elif self.source_image.orientation == "square":
            self.source_image.prominent_axis = "x"
        else:
            raise RuntimeError("unhandled orientation")

        self.pbl.gen_render_breakpoints()

        # It's now useful to flag rendering as prepared:
        # DisplayState()
        self.lock.acquire()  # asynchronous ops. must make us careful

        self.render_state = 0
        self.render_first_block_updated = 0

        # And flag as first pass:
        if not self.display_state.render_pass:
            self.display_state.render_pass = 0
        else:
            self.display_state.render_pass += 1
        self.lock.release()
        debug("render_pass = %s" % self.display_state.render_pass)

        # Get main_window, scroll, image etc. resize/scale using the
        # DisplayState() front:
        self.display_state.state_commit()

        # ImageDisplay()
        # Override breakpoints system for this initial state only:
        self.image_display.update_raw_pixbuf(pixbuf_loader.get_pixbuf())

        return True
