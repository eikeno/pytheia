# -*- coding: utf-8 -*-
"""
ImageDisplayWidget
"""

import os

import gi # pylint: disable=import-error
from gi.repository import Gdk, GdkPixbuf, Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import

# gi.require_version('Gdk', '3.0')
# gi.require_version('Gtk', '3.0')


class ImageDisplayWidget:
    """
    Widgets and related operations for the display.
    """

    def __init__(self):
        self.pytheia_install_context = None  # system | sources_dir
        self.callbacks = None  # <Callbacks>
        self.display_state = None  # <DisplayState>
        self.image_display = None  # <ImageDisplay>
        self.source_image = None  # <SourceImage>
        self.pbl = None  # <ProgressivePixbufLoader>
        self.config = None  # <PytheiaGui.config>
        self.platform = None  # <Platform>
        self.app_name = None  # <PytheiaGui.PYTHEIA_APP_NAMES>
        self.main_window = None  # <gtk.Window>
        self.main_window_size = None  # (ints)
        self.main_scroll = None  # <gtk.ScrolledWindow>
        self.main_viewport = None  # <gtk.Viewport>
        self.main_window_bgcolor = "#555555"  # str
        self.main_image = None  # <gtk.Image>
        self.main_scroll_policy = None  # <GtkPolicyType>
        self.main_vbox = None  # <GtkVBox>
        # depends on:
        # self.display_state.fit_fullscreen <Screen>
        # self.config[*] <PytheiaGui.config>
        #
        # Thus, should be provided:
        # context dependant values for pytheia.png path:
        # self.app_icon_path
        # self.screen, reference to core's <Screen>

    def _create_main_scroll(self):
        """
        Creates main scroll widget
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.main_scroll = Gtk.ScrolledWindow()

    def _create_main_image(self):
        """
        Creates main image widget
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.main_image = Gtk.Image()

    def _create_main_viewport(self):
        """
        Creates main viewport widget
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.main_viewport = Gtk.Viewport()

    def set_app_name(self, value):
        """`app_name` setter."""
        self.app_name = value

    def set_config(self, value):
        """`config` setter."""
        self.config = value

    def set_pytheia_install_context(self, value):
        """
        Explicitly set value of `pytheia_install_context'

        :param value: Str, one of 'system', 'sources_dir'
        """
        self.pytheia_install_context = value

    def create_main_window(self):
        """
        Creates a main window widget
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.main_window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.main_window.connect("destroy", self.callbacks.cb_quit)
        self.main_window.connect("delete-event", self.callbacks.cb_quit)
        self.main_window.pytheia_fullscreen = None

        # Iconified window icon:
        if self.pytheia_install_context == "system":
            iconified_pxbf = GdkPixbuf.Pixbuf.new_from_file(
                os.path.join(self.platform.pytheia_data_dir_system, "pytheia.png")
            )
        else:
            iconified_pxbf = GdkPixbuf.Pixbuf.new_from_file(
                os.path.join(
                    os.path.dirname(self.platform.pytheia_exec_dir),
                    "data",
                    "icons",
                    "128x128",
                    "pytheia.png",
                )
            )

        self.main_window.set_icon_list([iconified_pxbf])
        del iconified_pxbf

        self.main_window.set_title(self.app_name[0] + ": " + self.app_name[1])

        if not self.display_state.fullscreen:
            self.main_window.set_size_request(
                self.config["main_window_fallback_width"],
                self.config["main_window_fallback_height"],
            )
            self.get_main_window_size()  # set self.main_window_size

        # Main VBox():
        self.main_vbox = Gtk.VBox()

        # Scroll
        self._create_main_scroll()
        self.main_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.main_vbox.pack_end(self.main_scroll, True, True, 0)
        self.main_window.add(self.main_vbox)

        # Viewport
        self._create_main_viewport()
        self.main_viewport.modify_bg(
            Gtk.StateType.NORMAL,
            Gdk.color_parse(self.main_window_bgcolor),  # [1]
        )
        self.main_viewport.set_shadow_type(Gtk.ShadowType.NONE)
        self.main_scroll.add(self.main_viewport)

        self._create_main_image()
        self.main_viewport.add(self.main_image)

    def get_main_window_size(self):
        """
        Get size of main window widget
        FIXME: this has to be a property. really
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not hasattr(self, "main_window"):
            raise RuntimeError("main_window not found in instance")

        if not self.main_window:
            raise TypeError("main_window cannot be None")

        w, h = self.main_window.get_size()

        if not w or not h:
            raise RuntimeError("incorrect size data from main_window")

        # Act like a setter/updated for the sake of convenience:
        self.main_window_size = (w, h)  # FIXME: implement set_main_window_size()

        # Back to be getter if needed:
        return w, h

    def set_main_scroll_policy(self, hscrollbar_policy, vscrollbar_policy):
        """
        Force main scroll widget policy
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not hscrollbar_policy or not vscrollbar_policy:
            raise TypeError("h/vscrollbar_policy cannot be None")

        self.main_scroll.set_policy(hscrollbar_policy, vscrollbar_policy)
        self.main_scroll_policy = (hscrollbar_policy, vscrollbar_policy)

    def unmap_main_image(self):
        """
        Unbound main image and its content
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not hasattr(self, "main_image"):
            raise RuntimeError("missing main_image attribute")

        if not self.main_image:
            raise TypeError("main_image cannot be None")

        if not isinstance(self.main_image, Gtk.Image):
            raise RuntimeError("main_image is a wrong type")

        # free image resources and get a new usable one:
        # noinspection PyUnresolvedReferences
        self.main_image.destroy()  # this is a Gtk.Image

        del self.main_image
        self._create_main_image()
        # noinspection PyUnresolvedReferences
        self.main_image.show()

        # but we need to reparent to the upper viewport:
        self.main_viewport.add(self.main_image)

    def image_display_widget_free_all(self):
        """
        Free all resources bound to the widge
        """
        gdebug(f"# {self.__class__}:{callee()}")

        # Free as much things as possible to avoid memory leaks:
        # ImageDisplayWidget
        self.unmap_main_image()  # self.main_image

        # ImageDisplay()
        self.image_display.clear_pixbufs()  # self.{active_pixbuf, raw_pixbuf}

        # SourceImage()
        self.source_image.unregister_image()  # self.source_image_*

        # ProgressivePixbufLoader()
        self.pbl.pixbuf_loader_free()

        # DisplayState()
        self.display_state.state_free()  # self.{render_pass, first_block_updated}

    def main_scroll_emit_event(self, scroll_type, axis):
        """
        Emit scroll event
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not scroll_type:
            raise TypeError("scroll_type cannot be None")

        if not axis:
            raise TypeError("axis cannot be None")

        if axis not in ("horizontal", "vertical"):
            raise RuntimeError("received an unsupported value for axis: %s" % str(axis))

        self.main_scroll.emit("scroll-child", scroll_type, axis)
