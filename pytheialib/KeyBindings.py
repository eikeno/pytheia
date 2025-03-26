# -*- coding: utf-8 -*-
"""
KeyBindings
"""

import gi # pylint: disable=import-error

# this is being using indirectly, by reference, via eval(), in initialize():
# noinspection PyUnresolvedReferences
from gi.repository import Gdk  # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import

# gi.require_version('Gdk', '3.0')


class KeyBindings:
    """
    Represents and holds bindings for keyboard / mouse events and callback actions
    """

    def __init__(self):
        self.callbacks = None  # <Callbacks>
        self.config = None  # <PytheiaGui.config>
        self.bindings = None  # <List>Tuples
        self.keyvals = None  # Dict
        self.keymods = None  # Dict

    def set_config(self, value):
        """Setter for `config`."""
        self.config = value

    def initialize(self):
        """
        Defines current bindings model
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.config:
            raise RuntimeError("`config` attribute must be set before initialize()")
        # FIXME: modify as a plugin system < ???

        # FYI:
        # ctrl l = 65507
        # alt l  = 65513
        # alt r = 65027
        # cmd l = 65515
        # cmd r = 65516
        # fn = None
        # tab = 65289
        # shift l = 65505
        # shift r = 65506
        # esc = 65307

        # Other keys to left and right of Space bar

        # 65513 Alt (left)
        # 65312 Compose > unbound by default, on most linux

        # F1 = 65470
        # F2 = 65471
        # ..
        # F9 = 65478
        # F10 = 65479
        # F12 = 65481

        # KEY VALUES
        self.keyvals = {}
        if "keyvals" in self.config:
            _keyvals = self.config["keyvals"]

        else:  # set defaults
            _keyvals = {
                "F1": "Gdk.KEY_F1",
                "b": "Gdk.KEY_b",
                "d": "Gdk.KEY_d",
                "f": "Gdk.KEY_f",
                "n": "Gdk.KEY_n",
                "o": "Gdk.KEY_o",
                "q": "Gdk.KEY_q",
                "h": "Gdk.KEY_h",
                "t": "Gdk.KEY_t",
                "w": "Gdk.KEY_w",
                ">": "Gdk.KEY_greater",
                "<": "Gdk.KEY_less",
                # 'p': 'Gdk.KEY_p',
                "space": "Gdk.KEY_space",
                "backspace": "Gdk.KEY_BackSpace",
                "esc": "Gdk.KEY_Escape",
                "left": "Gdk.KEY_Left",
                "right": "Gdk.KEY_Right",
            }

            self.config["keybindings"] = _keyvals

        # Evaluate objects (non pickable):
        for k in _keyvals.keys():
            self.keyvals[k] = eval(_keyvals[k])
        del _keyvals

        # KEY MODIFIERS
        self.keymods = {}
        if "keymods" in self.config:
            _keymods = self.config["keymods"]

        else:  # set defaults
            _keymods = {
                "SHIFT": "Gdk.ModifierType.SHIFT_MASK",
                "CTRL": "Gdk.ModifierType.CONTROL_MASK",
                "SUPER": "Gdk.ModifierType.SUPER_MASK",
                "MOD1": "Gdk.ModifierType.MOD1_MASK",  # often alt on linux
            }
            self.config["keymods"] = _keymods

        # Evaluate objects (non pickable):
        for k in _keymods.keys():
            self.keymods[k] = eval(_keymods[k])
        del _keymods

        # KEY BINDINGS
        self.bindings = []
        if "keybinding" in self.config:
            self.bindings = eval(str(self.config["keybindings"]))

        else:  # set defaults
            self.bindings = [
                # (modifier, key, function, [args])
                (
                    """Safely quit pytheia""",
                    "0",
                    "self.keybindings.keyvals['q']",
                    "self.callbacks.cb_quit",
                ),
                (
                    """Thumbnails navigator""",
                    "0",
                    "self.keybindings.keyvals['t']",
                    "self.callbacks.cb_thumbnails_navigate",
                ),
                (
                    """Enter in console debug (pdb) mode""",
                    "0",
                    "self.keybindings.keyvals['d']",
                    "pdb.set_trace",
                ),
                (
                    """Toggle between fullscreen and windowed modes""",
                    "0",
                    "self.keybindings.keyvals['f']",
                    "self.callbacks.cb_toggle_fullscreen",
                ),
                (
                    """Zoom out""",
                    "0",
                    "self.keybindings.keyvals['<']",
                    "self.callbacks.cb_zoom_out",
                ),
                (
                    """Fit Width""",
                    "0",
                    "self.keybindings.keyvals['w']",
                    "self.callbacks.cb_fit_width",
                ),
                (
                    """Fit Height""",
                    "0",
                    "self.keybindings.keyvals['h']",
                    "self.callbacks.cb_fit_height",
                ),
                (
                    """Fit best""",
                    "0",
                    "self.keybindings.keyvals['b']",
                    "self.callbacks.cb_fit_best",
                ),
                (
                    """Original resolution""",
                    "0",
                    "self.keybindings.keyvals['o']",
                    "self.callbacks.cb_original_resolution",
                ),
                (
                    """Go or Step to next image""",
                    "0",
                    "self.keybindings.keyvals['space']",
                    "self.callbacks.cb_path_seek_stepped",
                    +1,
                ),
                (
                    """Go to previous image""",
                    "0",
                    "self.keybindings.keyvals['backspace']",
                    "self.callbacks.cb_path_seek",
                    -1,
                ),
                (
                    """Go to previous image""",
                    "0",
                    "self.keybindings.keyvals['left']",
                    "self.callbacks.cb_path_seek",
                    -1,
                ),
                (
                    """Go to next image""",
                    "0",
                    "self.keybindings.keyvals['right']",
                    "self.callbacks.cb_path_seek",
                    +1,
                ),
                (
                    """'Go to previous 'PathNode'""",
                    "self.keybindings.keymods['MOD1']",
                    "self.keybindings.keyvals['left']",
                    "self.callbacks.cb_pathnode_seek_previous",
                ),
                (
                    """Go to next 'PathNode'""",
                    "self.keybindings.keymods['MOD1']",
                    "self.keybindings.keyvals['right']",
                    "self.callbacks.cb_pathnode_seek_next",
                ),
                (
                    """Zoom in""",
                    "self.keybindings.keymods['SHIFT']",
                    "self.keybindings.keyvals['>']",
                    "self.callbacks.cb_zoom_in",
                ),
            ]
            self.config["keybindings"] = self.bindings

        return True
