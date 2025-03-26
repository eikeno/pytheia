# -*- coding: utf-8 -*-
"""
Notifications
"""

from gi.repository import GLib, Gtk # pylint: disable=import-error


class Notifications:
    """
    Notifications system
    """

    def __init__(self):
        self.status_bar = None  # <GtkStatusbar>
        self.notification_window = None  # <GtkWindow>
        self.notification_vbox = None  # <GtkVBox>
        self.main_window = None  # <ImageDisplayWidget.main_window>
        self.screen = None  # <Screen>

        # context_id <-> glib timer source / mapping
        self.context_id_sources = {}

    def context_id_sources_add(self, context_id, source_id):
        """
        Add a GLib source ID to a context_id mapping
        """
        if context_id not in self.context_id_sources:
            self.context_id_sources[context_id] = []
        self.context_id_sources[context_id].append(source_id)

    def notification_push(self, context_id, duration, notification_message):
        """
        Push a new notification message
        """

        self.status_bar_hide(context_id)
        self.status_bar.push(context_id, notification_message)
        self.notification_window.set_opacity(0.5)

        pos_x, pos_y = self.main_window.get_position()
        self.notification_window.move(pos_x + 15, pos_y + 35)
        self.notification_window.show_all()

        # Hide it after a given duration timeout (Async op):
        self.context_id_sources_add(
            context_id,
            # GLib source:
            GLib.timeout_add(duration, self.status_bar_hide, context_id),
        )

    def create_status_bar(self):
        """
        Creates a status bar notification
        """

        self.notification_window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.notification_window.set_size_request(self.screen.screen_width / 2, 25)

        self.status_bar = Gtk.Statusbar()

        self.notification_vbox = Gtk.VBox()
        self.notification_vbox.add(self.status_bar)

        self.notification_window.add(self.notification_vbox)
        self.notification_window.hide()

    def status_bar_hide(self, context_id):
        """
        Hide the status bar
        """

        self.notification_window.hide()
        self.status_bar.remove_all(context_id)

        for context_id in self.context_id_sources:
            for source_id in self.context_id_sources[context_id]:
                GLib.source_remove(source_id)
                self.context_id_sources[context_id].remove(source_id)
