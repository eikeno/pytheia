# -*- coding: utf-8 -*-
"""
Events
"""

import gi # pylint: disable=import-error
from gi.repository import Gdk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class Events:
    """
    Events management
    """

    def __init__(self):
        self.keybindings = None

    def evt_handle_key_press(self, widget, event):
        """
        Make the decision to attach an event to a registered binding or ignore
        it
        """
        # pylint: disable=eval-used
        gdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), widget, event))

        if not hasattr(self, "keybindings"):
            raise RuntimeError("attach a <KeyBindings> object")

        if not self.keybindings.bindings:
            raise RuntimeError("<KeyBindings> seems uninitialized")

        # MOUSE BUTTON :
        if event.type.value_name == "GDK_BUTTON_PRESS":
            if self._mouse_button(event):
                return True

        # KEYBOARD : Ignore everything but shift, control, and alt modifiers
        state = event.state & (
            Gdk.ModifierType.SHIFT_MASK
            | Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.MOD1_MASK
            | Gdk.ModifierType.BUTTON2_MASK
        )

        try:
            keyval = event.keyval
        except AttributeError:
            # FIXME: Have to find a way to better filter too many events.
            return True

        for bind in self.keybindings.bindings:
            if state == eval(bind[1]) and keyval == eval(bind[2]):
                callback = eval(bind[3])  # callback

                # Callback args:
                if len(bind) >= 5:
                    args = bind[4:]
                else:
                    args = ()

                debug("callback -> %s" % str(callback))
                debug("args -> %s" % str(args))

                # Run callback:
                callback(*args)  # pylint: disable=bad-option-value

                return True

    def _mouse_button(self, event):
        """
        Deals with detecting mouse related events, and run respective callback
        if relevant.

        Args:
            event:  <Gdk.EventButton>

        Returns: Bool
        """
        keyval = None
        state = None

        # Run action(s) if registered mouse event:
        if int(event.button) == (1):
            state = event.state & Gdk.ModifierType.BUTTON1_MASK
            keyval = 1
        if int(event.button) == (3):
            state = event.state & Gdk.ModifierType.BUTTON3_MASK
            keyval = 3
        if int(event.button) == (2):
            state = event.state & Gdk.ModifierType.BUTTON2_MASK
            keyval = 2

        for bind in self.keybindings.bindings:
            if keyval == eval(bind[2]) and state == eval(bind[1]):
                funk = eval(bind[3])
                args = eval(bind[4:])
                funk(*args)  # pylint: disable=bad-option-value
                return True
        return True
