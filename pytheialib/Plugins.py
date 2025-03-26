# -*- coding: utf-8 -*-
"""
Plugins
"""

import glob
import importlib
import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.IO import IO
from pytheialib.JsonDict import JsonDict
from pytheialib.Persistence import Persistence
from pytheialib.Platform import Platform
from pytheialib.PluginsStore import PluginsStore
from pytheialib.Utils import Utils


class Plugins:
    """
    Plugins management
    """

    def __init__(self):
        self.discovered_plugins = None  # Tuple
        self.discovered_plugins_paths = None  # Str
        self.registered_plugins = None  # Tuple
        self.path_index = None  # <PathIndex>
        self.plugins_registry = None  # Dict
        self.plugins_search_path = None  # Tuple
        self.plugins_store = None  # <PluginsStore>
        self.platform = None  # <Platform>
        self.keybindings = None  # <KeyBindings>
        self.notifications = None  # <Notifications>
        self.main_window = None  # <ImageDisplayWidget>
        self.screen = None  # <Screen>
        self.tree_store = None  # <TreeStore>
        self.lock = None  # threading.Lock() //injected
        self.pytheia_plugins = None  # <PytheiaPlugins> //injected by main()

    def set_plugins_search_path(self, paths_t):
        """Setter for `plugins_search_path`."""
        self.plugins_search_path = paths_t

    def set_pytheia_plugins(self, value):
        """Setter for `pytheia_plugins`."""
        self.pytheia_plugins = value

    def initialize(self):
        """
        Attach to a PluginsStore, if not done yet, else do nothing
        """
        if self.plugins_store is None:
            self.plugins_store = PluginsStore()

        if self.platform is None:
            self.platform = Platform()

        if not self.plugins_search_path:
            raise RuntimeError("plugins_search_path must be set")

    def discover_plugins(self):
        """
        Discover plugins files along search paths
        """
        gdebug(f"# {self.__class__}:{callee()}")

        # create user plugins if missing:
        if not os.path.exists(self.platform.pytheia_plugins_dir_user):
            IO().make_folder_with_parents(self.platform.pytheia_plugins_dir_user)
            bdebug("Created dir: %s" % self.platform.pytheia_plugins_dir_user)

        # FIXME: add checks / warning around missing or unreachable system dir
        # Add basic declaration in plugins_store:
        for plugindir in self.plugins_search_path:
            ydebug("Searching plugins along: " + plugindir)

            for path in glob.glob(plugindir + os.path.sep + "*" + os.path.sep + "*__pytheia_plugin.py"):
                mod_name, _ = os.path.splitext(os.path.split(path)[-1])
                plugin_name = mod_name.replace("__pytheia_plugin", "")

                self.plugins_store.add(
                    plugin=mod_name.replace("__pytheia_plugin", "", 1),
                    path=path,
                    # reuse enabled state - ff not set, will get None:
                    state=self.plugins_store.is_enabled(plugin_name),
                    registered=None,
                )
        debug("Discovered plugins are: %s" % self.plugins_store.ls_all())
        return True

    def register_plugin(self, plugin):
        """
        Register one plugin
        """
        ydebug("registering plugin: %s" % plugin)

        self.setup_plugin(plugin)
        self.plugins_store.register(plugin)

    def register_plugins(self):
        """
        Register discovered plugins in the plugins_registry
        """
        gdebug(f"# {self.__class__}:{callee()}")

        # Plugins():
        self.plugins_registry = {}

        # Initially don't start a plugin unless it has an enabled saved state,
        # or if it's the special "plugins_manager" plugin:

        for plugin in self.plugins_store.ls_all():
            self.register_plugin(plugin)

        debug("Registered plugins are: %s" % self.plugins_store.ls_registered())
        return True

    def setup_plugin(self, mod_name):
        """
        Setup one plugin

        - store registration values returned by the plugin
        - store instance of the plugin
        - inject helpers in the plugin instance
        - install plugin keybindings

        IN: mod_name: name of module as used in python
        """
        pytheia_plugins = self.pytheia_plugins()

        self.plugins_registry[mod_name] = {}
        _plugreg = self.plugins_registry[mod_name]

        # 2024: yeah, this is bas. This whole plugin discovery/loading thing was poorly conceived
        # to begin with, and should be redone:
        # FIXME: check this on non-linux ; expect "drive letter" situation to cause troubles
        _mod = (
            "plugins"
            + "."
            + self.plugins_store.plugins[mod_name]["path"].split("/plugins/")[1].replace(os.sep, ".").replace(".py", "")
        )

        py_mod = importlib.import_module(_mod)

        _plugreg["py_mod"] = py_mod  # ref. to loaded module
        _plugreg["instance"] = py_mod.PytheiaPlugin()  # get instance

        _plugreg["instance"].attach(self)  # bind Plugins instance

        # Store registration values from plugin:
        _plugreg["registered"] = (
            # FIXME: harden this and don't rely on register() success:
            _plugreg["instance"].register()
        )

        # Install keybinding(s), ony if True(enabled) or unset(None):
        # noinspection PySimplifyBooleanCheck
        if self.plugins_store.is_enabled(mod_name) is not False:
            self.plugin_install_keybindings(mod_name)

        # Add helper shortcuts, with idea to add some real proxying
        # instead in the future:
        _plugreg["instance"].plugin_console_out = pytheia_plugins.plugin_console_out

        _plugreg["instance"].notifications = self.notifications

        # Bind to Utils class, not instance, since mostly static methods in
        # there:
        _plugreg["instance"].utils = Utils

        self.plugin_init_persistence(mod_name)

        return True

    def plugin_init_persistence(self, mod_name):
        """
        Initialize Persistence() of a plugin
        """
        _plugin_instance = self.plugins_registry[mod_name]["instance"]
        # Persistence() pre-configuration and shortcuts. Don't want a plugin
        # to have to provide pickle file name or other details.

        # Attach a persistence() instance:
        _plugin_instance.persistence = Persistence()

        # storage location is pre-defined here:
        _plug_persist_file = os.path.join(
            self.platform.get_infos()["userdir"],
            ".config",
            "pytheia",
            "plugins",
            "%s.pickle" % self.plugins_registry[mod_name]["registered"]["filename"],
        )

        # Preset 'store_file' name:
        _plugin_instance.persistence.store_file = _plug_persist_file

        # shortcuts to load/dump:
        _plugin_instance.persistence_load = _plugin_instance.persistence.load

        _plugin_instance.persistence_dump = _plugin_instance.persistence.dump

    def enable_plugin(self, plugin):
        """
        Enable one plugin
        """

        self.plugins_store.enable(plugin)

    def disable_plugin(self, plugin):
        """
        disable one plugin
        """

        self.plugins_store.disable(plugin)

    def disable_undefined_plugins(self):
        """
        Disable plugins whose state is not explicitly enabled, ignore others
        """

        for plugin in self.plugins_store.ls_all():
            if self.plugins_store.is_enabled(plugin) is None:  # undefined
                self.plugins_store.disable(plugin)

    def unsetup_plugin(self, mod_name):
        """
        Unsetup one plugin:

        - uninstall all plugin keybindings

        IN: mod_name: name of module as used in python
        """
        # Uninstall keybinding(s):
        for _slotnum in range(0, 10):
            _slot = "on_keybinding_slot" + str(_slotnum)

            if _slot in self.plugins_registry[(mod_name)]["registered"]["hooks"]:
                ydebug(_slot)
                ydebug(JsonDict().print_dict(self.plugins_registry[mod_name]["registered"]["hooks"]))

                self.plugin_uninstall_keybinding(self.plugins_registry[(mod_name)]["registered"]["hooks"][_slot])

    def unregister_plugin(self, mod_name):
        """
        Unregister one plugin.

        This implies uninstalling its keybinding,
        IN: mod_name: str: module name of the plugin to unregister
        """

        self.lock.acquire()

        self.unsetup_plugin(mod_name)
        self.plugins_store.unregister(mod_name)

        self.lock.release()
        return True

    def destroy_plugins(self):
        """
        Run destroy procedure on all discovered plugins.

        This is to be done _ONLY_ when quitting the application.
        Not to be used in place of unregister_plugin or PluginsStore.disable()
        """

        for plugin in self.plugins_store.ls_all():
            self.destroy_plugin(plugin)

        return True

    def destroy_plugin(self, mod_name):
        """
        Destroy procedure for a plugin.

        IN: mod_name: str: plugin's module name
        OU: bool
        """

        # Catch all possible exceptions created by buggy dellers:
        self.plugin_deller_call_silent(mod_name)

        # Clear references to the plugin:
        self.plugins_registry[mod_name]["instance"] = None
        del self.plugins_registry[mod_name]["instance"]

        return True

    def plugin_deller_call_silent(self, mod_name):
        """
        Try to call the deller of a plugin, inhibiting any raised exceptions:

        """
        # Plugins should have an explicit __del__(), to be called here,
        # because del() offers no warranties at all:
        try:
            self.plugins_registry[mod_name]["instance"].__del__()

        except Exception as exc:  # pylint: disable=W0703
            # FIXME: exception handling
            debug(str(exc))

    def plugins_hooks_on_event_generic(self, eventname_s):
        """
        Trigger execution of plugin having a hook on 'eventname_s'
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(eventname_s)))

        for plugin in self.plugins_store.ls_enabled():
            # plugin_instance = self.plugins_registry[plugin]['instance']  # FFU
            plugin_hooks = self.plugins_registry[plugin]["registered"]["hooks"]
            # plugin_name = self.plugins_registry[plugin]['registered']['name']  # FFU

            if eventname_s in plugin_hooks:
                # FIXME: implement 'visual' exception report here:
                plugin_hooks[eventname_s][0](
                    # pass tuple content, not tuple itself:
                    *plugin_hooks[eventname_s][1:]
                )

    def plugin_install_keybindings(self, mod_name):
        """
        Install keybindings for all defined slot of a plugin
        """
        _plugreg = self.plugins_registry[mod_name]
        for _slotnum in range(0, 10):
            _slot = "on_keybinding_slot" + str(_slotnum)
            if _slot in _plugreg["registered"]["hooks"]:
                self.plugin_install_keybinding(_plugreg["registered"]["hooks"][_slot])

    def plugin_install_keybinding(self, t_keybinding):
        """
        IN: t_keybinding

        self.keybindings.bindings		((doc), mod, val, callback, callback_args)
        self.keybindings.keyvals		k: mnemonic, v: GdkKey str
        self.keybindings.keymods

        OU: (bool_status, str_comment)

        REM:
        'hooks': {
                    'on_keybinding_slot1':
                    (
                        ("short description on this keybinding")
                        "0",                              # keymod, MUST exist in pytheia
                        ("self.keybindings.keyvals['c']", Gdk.KEY_c), # keyval, must NOT exist in pytheia
                        'copy_request',                   # callback from this instance
                        None                              # callback args
                    )
            }
        """
        status = True
        comment = "KEYBINDING_INSTALLED_OK"
        callback = t_keybinding[3]

        if len(t_keybinding) > 4:
            callback_args = t_keybinding[4:]
        else:
            callback_args = None

        description = t_keybinding[0]

        # check keymod:
        keymod = t_keybinding[1]
        rdebug("keymod = %s" % keymod)

        if keymod != "0":
            if (
                keymod.replace("self.keybindings.keymods[", "").replace("]", "").replace('"', "").replace("'", "")
            ) not in self.keybindings.keymods:
                status = False
                comment = "Requested modifier is unknow to pytheia: %s" % keymod
                return status, comment

        # check keyval in bindings:
        keyval_litteral = t_keybinding[2][0]
        keyval_value = t_keybinding[2][1]

        # check keyval is not already in use:
        for known_keyval in self.keybindings.keyvals.values():
            if known_keyval == keyval_value:
                status = False
                return status, comment

        # sounds good, register it:
        litteral = (
            keyval_litteral.replace("self.keybindings.keyvals[", "").replace("]", "").replace('"', "").replace("'", "")
        )

        self.keybindings.keyvals[litteral] = keyval_value

        if callback_args:
            self.keybindings.bindings.append((description, keymod, keyval_litteral, callback, callback_args))
        else:
            self.keybindings.bindings.append((description, keymod, keyval_litteral, callback))

        debug("%s: %s, %s" % (keymod, status, comment))
        return status, comment

    def plugin_uninstall_keybinding(self, t_keybinding):
        """
        'hooks': {
            'on_keybinding_slot1':
            (
                ("short description on this keybinding")
                "0",                              # keymod, MUST exist in pytheia
                ("self.keybindings.keyvals['c']", Gdk.KEY_c), # keyval, must NOT exist in pytheia
                'copy_request',                   # callback from this instance
                None                              # callback args
            )
            }
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), t_keybinding))

        callback = t_keybinding[3]
        wdebug("callback => %s" % callback)
        if len(t_keybinding) > 4:
            callback_args = t_keybinding[4:]
        else:
            callback_args = None
        wdebug("callback_args => %s" % callback_args)
        description = t_keybinding[0]

        # check keymod:
        keymod = t_keybinding[1]
        wdebug("keymod => %s(%s)" % (keymod, type(keymod)))
        if keymod != "0":
            if (
                keymod.replace("self.keybindings.keymods[", "").replace("]", "").replace('"', "").replace("'", "")
            ) not in self.keybindings.keymods:
                status = False
                comment = "Requested modifier is unknown to pytheia: %s" % keymod
                return status, comment
        wdebug("sound almost good")
        # check keyval in bindings:
        keyval_litteral = t_keybinding[2][0]
        keyval_value = t_keybinding[2][1]
        wdebug("keyval_value => %s" % keyval_value)
        wdebug("self.keybindings.keyvals=> %s" % str(self.keybindings.keyvals))

        # check keyval is already in use:
        status = False
        comment = "Requested keyval doesn'keybinding_t exists in pytheia: %s" % keyval_litteral

        for known_keyval in self.keybindings.keyvals.values():
            wdebug("known_keyval => %s" % known_keyval)
            if known_keyval == keyval_value:
                status = True

        if not status:
            return status, comment

        # sounds good, unregister it:
        wdebug("sounds good")
        litteral = (
            keyval_litteral.replace("self.keybindings.keyvals[", "").replace("]", "").replace('"', "").replace("'", "")
        )
        self.keybindings.keyvals[litteral] = None
        self.keybindings.keyvals.pop(litteral)

        # KeyBindings():
        bindings_l = list(self.keybindings.bindings)  # pylint: disable=E0203
        # (Access to member 'bindings' before its definition)

        self._del_keybinding(bindings_l, callback, callback_args, description, keymod, keyval_litteral)

        # KeyBindings():
        self.keybindings.bindings = bindings_l  # pylint: disable=W0201
        # (defined outside __init__)
        del bindings_l

        debug("%s: %s, %s" % (keymod, status, comment))
        return status, comment

    @staticmethod
    def _del_keybinding(bindings_l, callback, callback_args, description, keymod, keyval_litteral):
        """
        Delete keybinding from `bindings_l` based on its given values.

        Args:
            bindings_l:       List of bindings tuples.
            callback:         Str. representation of the resolution string for the callbadck
                              I.e: "self.plugins.plugins_registry['my_plugin']['instance'].cb_action_request"
            callback_args:    XXX, Callback arguments
            description:      Tuple, containing description string(s)
            keymod:           Str. representation of keymod. I.e: "self.keybindings.keymods['CTRL']"
            keyval_litteral:  Str. representation of keyval. I.e: "self.keybindings.keyvals['i']"

        Returns:
            nothing
        """
        if callback_args:
            idx = 0
            for keybinding_t in bindings_l:
                if (
                    keybinding_t[0],
                    keybinding_t[1],
                    keybinding_t[2],
                    keybinding_t[3],
                ) == (
                    description,
                    keymod,
                    keyval_litteral,
                    callback,
                ):
                    del bindings_l[idx]
                idx += 1
        else:
            idx = 0
            bindings_l.append((description, keymod, keyval_litteral, callback))
            for keybinding_t in bindings_l:
                if (keybinding_t[0], keybinding_t[1], keybinding_t[2]) == (
                    description,
                    keymod,
                    keyval_litteral,
                ):
                    del bindings_l[idx]
                idx += 1
