# -*- coding: utf-8 -*-
"""
Plugins manager

"""

from gi.repository import (
    Gdk,  # pylint: disable=E0611,W0611
    GObject,  # pylint: disable=E0611,W0611
    Gtk,  # pylint: disable=E0611,W0611
)


class _PytheiaPlugin:
    """
    Mixin for PytheiaPlugin.

    Mandatory plugins methods are to be implemented by PytheiaPlugin subclass.

    """

    def __init__(self):
        self.modified_model = None
        self.modified_states = None

    def _start_stop_plugins(self):
        """
        Start / stop plugins depending on user choices

        """
        self.plugin_console_out("_start_stop_plugins, entering")
        self.plugin_console_out("self.modified_states = %s" % str(self.modified_states))

        for plugin in self.modified_states:
            _enabled = self.modified_states[plugin]

            if _enabled and self.pytheia.plugins_store.is_enabled(plugin):
                self.plugin_console_out("%s already active, skipping" % plugin)
                pass  # Already started, possibly from another manager

            elif _enabled and self.pytheia.plugins_store.is_disabled(plugin):
                # Start logic here
                self.pytheia.plugins_store.enable(plugin)
                self.pytheia.plugin_install_keybindings(plugin)
                self.modified_states[plugin] = True
                self.plugin_console_out("enabled plugin %s" % plugin)

            elif not _enabled and self.pytheia.plugins_store.is_enabled(plugin):
                # Stop logic here
                self.plugin_console_out("disabled plugin %s" % plugin)
                self.pytheia.plugin_deller_call_silent(plugin)
                self.pytheia.unsetup_plugin(plugin)
                self.pytheia.plugins_store.disable(plugin)

                self.modified_states[plugin] = False

            elif not _enabled and self.pytheia.plugins_store.is_disabled(plugin):
                self.plugin_console_out("%s already disabled, nothing to do" % plugin)
                pass

            else:
                raise RuntimeError("modified_states is in unplanned state")

        self.modified_states = zip(self.modified_states.keys(), self.modified_states.values())
        return True

    def _plugins_manager_gui(self):
        """
        Plugins management window

        """
        re_enter = False
        rcount = 0

        if not self.w:
            self.w = Gtk.Window()
        else:
            re_enter = True

        if not self.v:
            self.v = Gtk.VBox()

        if not self.bb:
            self.bb = Gtk.ButtonBox()

        if not self.bok:
            self.bok = Gtk.Button(stock=Gtk.STOCK_OK)
            self.bok.connect("clicked", self.cb_ok, self.w)

        if not self.bko:
            self.bko = Gtk.Button(stock=Gtk.STOCK_CANCEL)
            self.bko.connect("clicked", self.cb_cancel, self.w)

        if not re_enter:
            self.bb.add(self.bko)
            self.bb.add(self.bok)

            self.w.set_size_request(500, 200)
            self.w.set_title("Plugins manager")
            self.w.set_parent(self.pytheia.main_window)
            self.w.set_modal(True)
            self.w.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        self.ts = None
        self.ts = self.pytheia.tree_store()

        # Create model:
        _model = {}
        _labels = []
        _descriptions = []
        _tooltips = []
        _states = []

        for plugin in self.pytheia.plugins_store.ls_all():
            self.plugin_console_out(">>>> %s" % plugin)

            if self.pytheia.plugins_store.is_enabled(plugin):
                _states.append(True)

            elif self.pytheia.plugins_store.is_enabled(plugin) is None:
                # None is not acceptable from here, pytheia core
                # must enable or disable explicitely before:
                raise RuntimeError("%s enabled is None" % plugin)

            elif not self.pytheia.plugins_store.is_enabled(plugin):
                _states.append(False)

            _labels.append(plugin)
            _descriptions.append(self.pytheia.plugins_registry[plugin]["registered"]["shortdesc"])

            _tooltips.append(self.pytheia.plugins_registry[plugin]["registered"]["longdesc"])

            rcount += 1

            # _ev_desc = Gtk.EventBox()
            # _ev_desc.add(_desc)
            # _ev_desc.modify_bg(
            # Gtk.StateType.NORMAL,
            # Gdk.color_parse("white")
            # )
            # _ev_desc.set_has_tooltip(True)
            # _ev_desc.set_tooltip_text(
            # self.pytheia.plugins_registry[plugin]['registered']['longdesc']
            # )
            # _desc.set_alignment(0, 500)

        # print('================= states = %s' % _states)

        # Enable/disable checkbox
        _model["Enable"] = {
            "uuid": "0",
            "type": GObject.TYPE_BOOLEAN,
            "child": None,
            "parent": None,
            "states": _states,
            "renderer": {
                "renderer_type": Gtk.CellRendererToggle(),
                "properties": {},
                "attributes": {"activatable": 1},
                "callbacks": (("toggled", self.cb_toggled),),
            },
            "attributes": (None,),
            "data": (tuple([None for i in range(rcount)])),
        }

        _model["Name"] = {
            "uuid": "1",
            "type": GObject.TYPE_STRING,
            "child": None,
            "parent": None,
            "renderer": {
                "renderer_type": Gtk.CellRendererText(),
                "properties": {"editable": False},
                "callbacks": ((None),),
            },
            "attributes": (None,),
            "data": tuple([i for i in _labels]),
        }

        _model["Description"] = {
            "uuid": "2",
            "type": GObject.TYPE_STRING,
            "child": None,
            "parent": None,
            "renderer": {
                "renderer_type": Gtk.CellRendererText(),
                "properties": {"editable": False},
                "callbacks": ((None),),
            },
            "attributes": (None,),
            "data": tuple([i for i in _descriptions]),
        }

        _model["Tooltips"] = {
            "uuid": "3",
            "type": GObject.TYPE_STRING,
            "child": None,
            "parent": None,
            "renderer": {
                "renderer_type": Gtk.CellRendererText(),
                "properties": {"editable": False},
                "callbacks": ((None),),
            },
            "attributes": (None,),
            "data": tuple([i for i in _tooltips]),
        }

        self.ts.model = _model
        tsw = self.ts.run_widget()

        if not re_enter:
            self.v.add(tsw)
            self.v.add(self.bb)
            self.w.add(self.v)

        self.w.show_all()
        return True

    def cb_action_request(self):
        """
        Initiate plugins manager main window

        """

        self._oncall_in()  # perst load

        # Manage plugins:
        self.plugin_console_out("plugins_manager cb_action_request")
        for plugin in self.pytheia.plugins_store.ls_all():
            self.plugin_console_out("%s => enabled? %s" % (plugin, str(self.pytheia.plugins_store.is_enabled(plugin))))
        self._plugins_manager_gui()
        return True

    def cb_toggled(self, cell_renderer_toggle, row_idx_zb, user_data):
        """
        Invert boolean status of the toggle

        """
        store, column, model, colname = user_data
        row_idx_zb = int(row_idx_zb)

        store[row_idx_zb][column] = not store[row_idx_zb][column]

        model[colname]["states"][row_idx_zb] = not (model[colname]["states"][row_idx_zb])

        self.plugin_console_out("toggled: %s to %s" % (colname, model[colname]["states"][row_idx_zb]))

        # Store this to allow treatment when 'ok' is clicked:
        self.modified_model = model
        return True

    def cb_ok(self, widget, window):
        """
        Callback for the Ok button

        """
        self.plugin_console_out("cb_ok, entering")

        if not self.modified_model:
            # cb_toggled() was not called before:
            self.plugin_console_out("self.modified_model doesn't exist yet")

        else:
            # Plugins enable/disable logic here
            self.plugin_console_out("self.modified_model exists")

            _states = self.modified_model["Enable"]["states"]
            _names = self.modified_model["Name"]["data"]

            self.modified_states = dict(zip(_names, _states))
            self.plugin_console_out("modified_states = %s" % str(self.modified_states))

            self.plugin_console_out("caling start_stop")
            self._start_stop_plugins()
            self.modified_states = None

        window.hide()

        self._oncall_out()
        self.plugin_console_out("cb_ok, leaving")
        return True

    def cb_cancel(self, widget, window):
        """
        Callback for the Cancel button

        """
        self.plugin_console_out("cb_cancel")
        window.destroy()
        self._oncall_out()
        return True

    def cb_debug(self, *args):
        """
        Callback for debugging purpose

        """
        self.plugin_console_out(str(args))
        return True


class PytheiaPlugin(_PytheiaPlugin):
    """
    Mandatory plugin class

    """

    _plugin_longdesc = "Manage other plugins. Cannot be disabled"

    def __init__(self):
        _PytheiaPlugin.__init__(self)
        self.pytheia = None
        self.ts = None
        self.w = None
        self.v = None
        self.bb = None
        self.bok = None
        self.bko = None

    def __del__(self):
        self.plugin_console_out("deller of plugins_manager called")
        self._oncall_out()

    def _oncall_in(self):
        """
        To be used each time plugin is explicitly called (vs imported or
        registered), by the plugin itself.

        """
        pass

    def _oncall_out(self):
        """
        To be called when a call is ending or plugin is destroyed

        """
        pass

    def attach(self, pytheia):
        """
        Attach 'pytheia', an accessor to PytheiaGui.core.plugins

        """

        self.pytheia = pytheia
        return True

    def register(self):
        """
        Expose the plugin to pytheia

        """

        return {
            "name": "Plugins Manager",
            "author": "Eikeno <eikenault@gmail.com>",
            "copyright": "GPL",
            "website": "https://eikeno.eu",
            "filename": "plugins_manager",
            "categories": "plugins_management, interactive",
            "shortdesc": "Manage other plugins",
            "longdesc": self._plugin_longdesc,
            "manageable": False,  # is needed to manage others
            "hooks": {
                # hook1
                "on_keybinding_slot0": (
                    ("Start the plugins manager",),
                    # keymod, MUST exist in pytheia, or be "0" string:
                    "0",
                    # keyval. Litteral (1st arg) must NOT exist in pytheia:
                    ("self.keybindings.keyvals['p']", Gdk.KEY_p),
                    # callback from this instance:
                    ("self.plugins.plugins_registry['plugins_manager']['instance']." + "cb_action_request"),
                    # callback args would be here as a tuple
                )
            },
        }
