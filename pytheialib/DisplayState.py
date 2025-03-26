# -*- coding: utf-8 -*-
"""
DisplayState
"""

import gi # pylint: disable=import-error
from gi.repository import GdkPixbuf, Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Utils import Utils

# gi.require_version('Gdk', '3.0')
# gi.require_version('Gtk', '3.0')


class DisplayState:
    """Manipulate display modes state"""

    def __init__(self):
        self.config = None  # Dict
        self.lock = None  # <threading.Lock>
        self.image_display = None  # <ImageDisplay>
        self.image_display_widget = None  # <ImageDisplayWidget>
        self.pbl = None  # <ProgressivePixbufLoader>
        self.plugins = None  # <Plugins>
        self.screen = None  # <Screen>
        self.source_image = None  # <SourceImage>
        self._fit_modes = ("height", "width", "best", "zoom")
        self._fit_mode = None  # Str
        self.fullscreen = False  # Bool
        self.render_state = None  # Int
        self.render_pass = None  # Int
        self.render_first_block_updated = None  # Int
        self.zoom = None  # Float

    def set_config(self, value):
        """Setter for `config`."""
        self.config = value

    @property
    def fit_mode(self):
        """`fit_mode` getter"""
        if not self._fit_mode:
            self._fit_mode = "best"  # default setting
        return self._fit_mode

    @fit_mode.setter
    def fit_mode(self, mode):
        """`fit_mode` setter"""
        if mode not in self._fit_modes:
            raise RuntimeError("%s is not valid mode" % str(mode))
        self._fit_mode = mode

    @fit_mode.deleter
    def fit_mode(self):
        """'fit_mode' deleter"""
        self._fit_mode = None

    def toggle_fullscreen(self, commit=True):
        """toogle boolean value of fit_fullscreen

        Values for commit:
            0: area_prepared
            1: area_updated
            2: closed
            None: the initial state
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.lock.acquire()
        self.config["fullscreen"] = not self.config["fullscreen"]
        self.fullscreen = self.config["fullscreen"]
        self.lock.release()

        if commit:
            if self.render_state not in (0, 1):
                self.state_commit()
            # else, a state_commit will soon be performed, so do nothing

    def do_fit_width(self, commit=True):
        """have the image fit the display area width.

        Values for commit:
            0: area_prepared
            1: area_updated
            2: closed
            None: the initial state
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.fit_mode = "width"
        if commit:
            if self.render_state not in (0, 1):
                self.state_commit()
            # else, a state_commit will soon be performed, so do nothing

    def do_fit_height(self, commit=True):
        """have the image fit the display area height

        Values for commit:
            0: area_prepared
            1: area_updated
            2: closed
            None: the initial state
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.fit_mode = "height"

        if commit:
            if self.render_state not in (0, 1):
                self.state_commit()
            # else, a state_commit will soon be performed, so do nothing

    def do_fit_best(self, commit=True):
        """have the image fit the display area completely

        Values for commit:
            0: area_prepared
            1: area_updated
            2: closed
            None: the initial state
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.fit_mode = "best"

        if commit:
            if self.render_state not in (0, 1):
                self.state_commit()
            # else, a state_commit will soon be performed, so do nothing

    def _fullscreen_scaled(self, target_sizes_meth):
        """FIXME: docstring required here"""
        self.image_display.update_active_pixbuf(
            Utils.scale_pixbuf(
                # reference pixbuf:
                self.image_display.raw_pixbuf,
                # target sizes:
                target_sizes_meth(
                    (
                        self.screen.screen_width,
                        self.screen.screen_height,
                    ),  # fit_sizes_t
                    (self.source_image.width, self.source_image.height),  # src_sizes_t
                ),
                # interpolation method:
                GdkPixbuf.InterpType.BILINEAR,
            ),
            comment="isFullscreen",
        )
        debug("updating active pixbuf to size: ")
        debug("WxH: %sx%s" % (self.screen.screen_width, self.screen.screen_height))
        bdebug("***** DisplayState, _fullscreen_scaled, mode == best / DONE")

    def _fullscreen(self, mode):
        """
        Update active pixbuf, in fullscreen mode, with the given 'mode'
        dependent behaviour.
        """
        # depending on the running environment, calling fullscreen() on the
        # window is necessary or not - but it sounds like a logic thing to
        # to, so let's do it:

        if mode == "best":
            self._fullscreen_scaled(Utils.get_fit_best_sizes)
            bdebug("***** DisplayState, _fullscreen, mode == best")

        if mode == "width":
            self._fullscreen_scaled(Utils.get_fit_width_sizes)

        if mode == "height":
            self._fullscreen_scaled(Utils.get_fit_height_sizes)

        if mode == "zoom":
            self._zoom()

    def _windowed_scale(self, target_sizes_meth):
        """
        FIXME: missing doc for DisplayState._windowed_scale()
        """
        self.image_display.update_active_pixbuf(
            Utils.scale_pixbuf(
                # reference pixbuf:
                self.image_display.raw_pixbuf,
                # target sizes:
                target_sizes_meth(
                    self.image_display_widget.main_window_size,  # fit_sizes_t
                    self.image_display.raw_pixbuf.get_properties("width", "height"),  # src_sizes_t
                ),
                # interpolation method:
                GdkPixbuf.InterpType.BILINEAR,
            ),
            comment="isWindowedScaled",
        )

    def _zoom(self):
        """
        FIXME: needed description
        """
        if not self.zoom:
            debug("Warning: zoom is None")
            self.zoom = 1  # better do nothing than guessing

        _zoom_factor = self.zoom  # 10% steps
        # noinspection PyPep8
        _apply_factor = lambda t: (t[0] * _zoom_factor, t[1] * _zoom_factor)

        if not self.image_display.active_pixbuf:
            self.image_display.active_pixbuf = self.image_display.raw_pixbuf.copy()

        target_sizes_t = _apply_factor(self.image_display.active_pixbuf.get_properties("width", "height"))

        self.image_display.update_active_pixbuf(
            Utils.scale_pixbuf(
                self.image_display.raw_pixbuf,  # reference pixbuf
                target_sizes_t,
                GdkPixbuf.InterpType.BILINEAR,
            ),
            comment="isZoomed",
        )

    def _windowed(self, mode):
        """
        Update active pixbuf, in windowed mode, with the given 'mode'
        dependent behaviour.
        """
        if mode == "best":
            self._windowed_scale(Utils.get_fit_best_sizes)  # callable

        if mode == "width":
            self._windowed_scale(Utils.get_fit_width_sizes)  # callable

        if mode == "height":
            self._windowed_scale(Utils.get_fit_height_sizes)  # callable

        if mode == "zoom":
            self._zoom()

    def state_commit(self):
        """commit pending changes to the display"""
        gdebug(f"# {self.__class__}:{callee()}")

        # Sanity checks:
        if not (self.config["main_window_width"]) and not (self.config["main_window_height"]):
            self.config["main_window_width"] = self.config["main_window_fallback_width"]
            self.config["main_window_height"] = self.config["main_window_fallback_height"]

        if self.config["fullscreen"] and not self.fullscreen:
            # Just in case sync was omitted:
            self.fullscreen = True

        # first group actions based on the fullscreen criteria:
        if self.fullscreen:
            rdebug("fullscreen requested")
            self._state_commit_fullscreen()

        else:  # Windowed mode:
            rdebug("windowed mode requested")
            self._state_commit_windowed()

        # Finally, apply changes on pixbuf to the visible image:
        self.image_display_widget.main_image.set_from_pixbuf(self.image_display.active_pixbuf)

    def _state_commit_windowed(self):
        """
        Actions required when comit_state() called in windowed mode.
        """
        # Make sure to un-fullscreen only when needed, to avoid visual
        # weirdness, using custom attribute pytheia_fullscreen`:
        if self.image_display_widget.main_window.pytheia_fullscreen:
            width, height = self.image_display_widget.main_window_size
            rdebug("restoring window size: %sx%s" % (width, height))
            self.image_display_widget.main_window.unfullscreen()
            self.image_display_widget.main_window.pytheia_fullscreen = False
            self.image_display_widget.main_window.resize(width, height)
            del width
            del height
        else:
            # FIXME: Poor man's way to update manually resized window
            # FIXME: without listening to window's event:
            self.image_display_widget.get_main_window_size()
        if self.image_display.raw_pixbuf and self.fit_mode == "best":
            self._windowed("best")

        elif self.image_display.raw_pixbuf and self.fit_mode == "width":
            self._windowed("width")

        elif self.image_display.raw_pixbuf and self.fit_mode == "height":
            self._windowed("height")

        elif self.image_display.raw_pixbuf and self.fit_mode == "zoom":
            self._windowed("zoom")
        self.image_display_widget.main_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,  # horiz
            Gtk.PolicyType.AUTOMATIC,  # vert
        )

    def _state_commit_fullscreen(self):
        """
        Actions required when comit_state() called in fullscreen mode.
        """
        if not self.image_display_widget.main_window.pytheia_fullscreen:
            rdebug("performing a fullscreen() on main window")
            self.image_display_widget.main_window.fullscreen()
            self.image_display_widget.main_window.pytheia_fullscreen = True

        scroll_policy_h = Gtk.PolicyType.AUTOMATIC
        scroll_policy_v = Gtk.PolicyType.AUTOMATIC

        if self.image_display.raw_pixbuf and self.fit_mode == "best":
            self._fullscreen("best")
            scroll_policy_h = Gtk.PolicyType.NEVER
            scroll_policy_v = Gtk.PolicyType.NEVER

        elif self.image_display.raw_pixbuf and self.fit_mode == "width":
            self._fullscreen("width")
            scroll_policy_h = Gtk.PolicyType.NEVER

        elif self.image_display.raw_pixbuf and self.fit_mode == "height":
            self._fullscreen("height")
            scroll_policy_v = Gtk.PolicyType.NEVER

        elif self.image_display.raw_pixbuf and self.fit_mode == "zoom":
            self._fullscreen("zoom")

        # Reposition scrollbars to start, to avoid missing zones
        # when disabling them below:
        self.image_display_widget.main_scroll_emit_event(Gtk.ScrollType.START, "vertical")
        self.image_display_widget.main_scroll_emit_event(Gtk.ScrollType.START, "horizontal")
        # Remove scrollbars: FIXME: check if always needed
        self.image_display_widget.main_scroll.set_policy(scroll_policy_h, scroll_policy_v)

    def state_free(self):
        """free resources set by display state"""
        gdebug(f"# {self.__class__}:{callee()}")

        self.render_pass = None
        self.render_first_block_updated = None

    def request_zoom_in(self):
        """request for a zoom-in on next commit"""
        gdebug(f"# {self.__class__}:{callee()}")

        self.zoom = 1.1
        self.fit_mode = "zoom"
        self.state_commit()

    def request_zoom_out(self):
        """request for a zoom-out on next commit"""
        gdebug(f"# {self.__class__}:{callee()}")

        self.zoom = 0.9
        self.fit_mode = "zoom"
        self.state_commit()

    def request_zoom_original_resolution(self):
        """request to zoom up/down to original resolution on next commit"""
        gdebug(f"# {self.__class__}:{callee()}")
        self.image_display.active_pixbuf = self.image_display.raw_pixbuf.copy()
        self.zoom = 1
        self.fit_mode = "zoom"
        self.state_commit()
