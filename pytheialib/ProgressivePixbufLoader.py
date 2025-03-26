# -*- coding: utf-8 -*-
"""
ProgressivePixbufLoader
"""

import os
import time

import gi # pylint: disable=import-error
from gi.repository import GdkPixbuf, GLib # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.SampleStats import SampleStats

# gi.require_version('Gdk', '3.0')


class ProgressivePixbufLoader:
    """
    Asynchronous image loading
    """

    def __init__(self):
        self.image_display = None  # <ImageDisplay>
        self.image_display_widget = None  # <ImageDisplayWidget>
        self.callbacks = None  # <Callbacks>
        self.source_image = None  # <SourceImage>
        self.platform = None  # <Platform>
        self.plugins = None  # <Plugins>

        self.lock = None  # <threading.Lock>
        self.time_start = None  # <Time.time>
        self.time_stop = None  # <Time.time>
        self.time_load_average = None  # <Float>

        self.errors = None  # Exception, or whatever
        self.output_image = None  # GtkImage
        self.pixbuf_loader_source_image_fd = None  # _fd
        self.pixbuf_loader = None  # <GdkPixbufLoader>
        self.max_render_breakpoints = 5  # int
        self.breakpoint_pos = 0  # int
        self.breakpoints_render_tuple = ()  # (ints)

    def pixbuf_loader_free(self):
        """
        Try to safely free open file descriptors and PixbufLoader
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.pixbuf_loader_source_image_fd.close()
        # TODO: Add smart exception handling here

        self.pixbuf_loader.close()
        del self.pixbuf_loader
        return True

    def _max_render_breakpoints(self):
        """Define value of `max_render_breakpoints` depending on `time_load_average.average`"""
        gdebug(f"# {self.__class__}:{callee()}")

        if self.time_load_average.average:
            if self.time_load_average.average < 0.5:
                self.max_render_breakpoints = 2
            elif 0.1 < self.time_load_average.average < 1:
                self.max_render_breakpoints = 3
            elif 0.5 < self.time_load_average.average < 2:
                self.max_render_breakpoints = 4
            else:
                self.max_render_breakpoints = 6

    def gen_render_breakpoints(self):
        """
        Determine which received data block should trigger a display update,
        to avoid taking too much resources updating for each one
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.max_render_breakpoints:
            raise TypeError("max_render_breakpoints should be defined")
        elif not self.source_image.orientation:
            raise TypeError("Use register_image() first")

        self._max_render_breakpoints()
        bdebug("max_render_breakpoints is now: %s" % self.max_render_breakpoints)

        _bpl = []
        idx = None
        chunks_idx = [i for i in range(self.max_render_breakpoints)[1:]]
        chunks_idx.reverse()
        bdebug("chunks_idx = %s" % chunks_idx)

        if self.source_image.orientation == "landscape":
            for idx in chunks_idx:
                _bpl.append(self.source_image.width / idx)

        elif self.source_image.orientation == "portrait":
            for idx in chunks_idx:
                _bpl.append(self.source_image.height / idx)

        else:
            for idx in chunks_idx:
                _bpl.append(self.source_image.width / idx)

        self.breakpoints_render_tuple = tuple(_bpl)
        bdebug("breakpoints_render_tuple = %s" % str(self.breakpoints_render_tuple))

        del idx
        del _bpl
        del chunks_idx

    def set_pixbufloader(self):
        """
        Attach a <GdkPixbufLoader> to the instance, if none already attached
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not hasattr(self, "pixbuf_loader"):
            # provision a blank pixbufloader, for reuse:
            self.pixbuf_loader = GdkPixbuf.PixbufLoader()
        elif not self.pixbuf_loader:
            self.pixbuf_loader = GdkPixbuf.PixbufLoader()
        # Allow detection of errors that triggers cb_area_closed first:
        self.errors = True

    def pixbuf_loader_start(self):
        """
        Actually start render of the pixbuf
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.time_load_average:
            self.time_load_average = SampleStats()
            self.time_load_average.set_maxvalues(5)
        debug("time_load_average_values =>" + str(self.time_load_average.values))
        self.time_start = time.time()  # stop set by DisplayState.state_commit()

        # SourceImage():
        if str(type(self.source_image.imagefile)).__contains__("pytheialib"):
            # Source image support is provided by additional support, and
            # is a File-Like Object - and it's already opened:
            self.pixbuf_loader_source_image_fd = self.source_image.imagefile

        else:
            # Regular file opening:
            try:
                self.pixbuf_loader_source_image_fd = open(self.source_image.imagefile, "rb")
            except IOError as exc:
                debug("IOError(%s): %s while opening: %s" % (exc.errno, exc.strerror, self.source_image.imagefile))
                return

        debug("file descriptor opened on %s" % self.source_image.imagefile)

        self.set_pixbufloader()

        # provide hook for plugins
        self.plugins.plugins_hooks_on_event_generic("on_image_load_start")

        # Attach to callbacks:
        self.pixbuf_loader.connect("area-prepared", self.callbacks.cb_area_prepared)
        self.pixbuf_loader.connect("area-updated", self.callbacks.cb_area_updated)
        self.pixbuf_loader.connect("closed", self.callbacks.cb_area_closed)

        # start chunks feeding:
        try:
            self.pixbuf_loader.write(self.pixbuf_loader_source_image_fd.read())

        except GLib.GError as exc:  # pylint: disable=catching-non-exception
            # to be treated by Callbacks.cb_area_closed()
            bdebug("Loading Error Detected: %s" % str(exc))
            _error_image = os.path.join(self.platform.pytheia_data_dir_system, "loading_error.svg")
            self.image_display.active_pixbuf = GdkPixbuf.Pixbuf.new_from_file(_error_image)
            self.image_display_widget.main_image.set_from_pixbuf(self.image_display.active_pixbuf)

        self.pixbuf_loader.close()
