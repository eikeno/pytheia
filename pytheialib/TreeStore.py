# -*- coding: utf-8 -*-
"""
TreeStore
"""

import gi # pylint: disable=import-error
from gi.repository import GObject, Gtk # pylint: disable=import-error

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class TreeStore:
    """
    TreeStore abstraction
    """

    def __init__(self):
        self.__model = None  # dict
        self.widget = None  # GtkTreeView
        self.tree_store = None  # <GtkTreeStore>

    def _import_model(self):
        """Import_model"""
        _cols = list(self.model.keys())  # pylint: disable=no-member
        _types = []

        # Declare columns with their types:
        for _col in _cols:
            _types.append(self.model[_col]["type"])

        self.tree_store = Gtk.TreeStore(*_types)  # pylint: disable=bad-option-value
        # (Used * or ** magic)

        # We enforce declaring 'None' in 'data' tuple of model dictionary
        # for empty cell, to have the same number of row for each column.
        # Thus we can here get this count from col0, always:
        _data_l = len(
            self.model[list(self.model.keys())[0]]["data"]  # pylint: disable=no-member
        )

        for _row_idx in range(_data_l):
            debug("_row_idx: %d" % _row_idx)
            _row_idx_vals = []

            for _col in _cols:
                # Fetch values from each column this row is part of:
                _row_idx_vals.append(self.model[_col]["data"][_row_idx])
                debug("appended: %s to idx_vals" % (self.model[_col]["data"][_row_idx]))

            # Append the row with values:
            self.tree_store.append(
                parent=None,  # parent
                row=_row_idx_vals,  # iter (col. values for that row)
            )

    def _set_gtk_tv_col(self, col, col_idx_zb, renderer):
        if self.model[col]["type"] == GObject.TYPE_BOOLEAN:
            print("gtk_tv_col %s has type %s" % (col_idx_zb, type(self.model[col]["type"])))

            gtk_tv_col = Gtk.TreeViewColumn(title=col, cell_renderer=renderer)
        else:
            print("gtk_tv_col %s has text based on %s" % (col_idx_zb, col_idx_zb))

            gtk_tv_col = Gtk.TreeViewColumn(title=col, cell_renderer=renderer, text=col_idx_zb)
        return gtk_tv_col

    def _set_treemodel_row_state(self, col, col_idx_zb, gtk_tm_row):
        for _ in self.model[col]["states"]:
            self.tree_store[gtk_tm_row][col_idx_zb] = self.model[col]["states"][gtk_tm_row]  # bool
            gtk_tm_row += 1
            # FIXME: add more attr. support here, or best: generic support.

    def _signals_to_callbacks(self, callbacks_t, col, col_idx_zb, renderer, tooltips_col):
        if self.model[col]["type"] != GObject.TYPE_BOOLEAN:
            if col == "Tooltips":
                if tooltips_col:
                    raise RuntimeError("Only one 'Tooltips' column allowed")
                tooltips_col = col_idx_zb

            # Skip special column types:
            if col not in ("Tooltips",):
                # Connect signals to callbacks:
                for _callback_t in callbacks_t:
                    if _callback_t is None:
                        continue
                    _signal = _callback_t[0]
                    _cb = _callback_t[1]
                    _cbargs = _callback_t[2:]
                    print("signal: %s" % _signal)

                    renderer.connect(
                        _signal,
                        _cb,
                        # Can be used from callback, if needed:
                        self.tree_store,
                        _cbargs,
                    )
        elif self.model[col]["type"] == GObject.TYPE_BOOLEAN:
            # Connect signals to callbacks:
            for _callback_t in callbacks_t:
                if _callback_t is None:
                    continue
                _signal = _callback_t[0]
                _cb = _callback_t[1]

                renderer.connect(_signal, _cb, (self.tree_store, col_idx_zb, self.model, col))
        return tooltips_col

    def _make_view(self):
        """_make_view"""  # FIXME : better comment
        self.widget = Gtk.TreeView(self.tree_store)
        cols = self.model.keys()  # pylint: disable=no-member
        tooltips_col = None

        # Counter 'one' and 'zero' based - iter on cols count:
        col_idx_ob = 1
        col_idx_zb = 0

        for col in cols:
            renderer = self.model[col]["renderer"]["renderer_type"]

            for prop in self.model[col]["renderer"]["properties"].keys():
                if not prop:
                    continue

                renderer.set_property(prop, self.model[col]["renderer"]["properties"][prop])

            gtk_tv_col = self._set_gtk_tv_col(col, col_idx_zb, renderer)
            callbacks_t = self.model[col]["renderer"]["callbacks"]

            if "attributes" in self.model[col]["renderer"]:
                for attr in self.model[col]["renderer"]["attributes"].keys():
                    if attr == "activatable":
                        gtk_tv_col.add_attribute(renderer, "activatable", col_idx_ob)
                        gtk_tv_col.add_attribute(renderer, "active", col_idx_zb)

                        # Active / inactive initial state:
                        gtk_tm_row = 0  # <Gtk.TreeModelRow>
                        self._set_treemodel_row_state(col, col_idx_zb, gtk_tm_row)

            tooltips_col = self._signals_to_callbacks(callbacks_t, col, col_idx_zb, renderer, tooltips_col)
            self.widget.append_column(gtk_tv_col)

            if col == "Tooltips":
                gtk_tv_col.set_visible(False)
                self.widget.set_tooltip_column(tooltips_col)

            col_idx_ob += 1
            col_idx_zb += 1

    # noinspection PyMethodParameters
    @property
    def model(self):
        """ "
        Property holding the <GtkTreeStore> model template.
        It must be assigned (not passed) a model dictionnary.

        @IN: dict: model dictionnary

        Model dictionnary format:

        TreeStore().model = {
        'column0_title': {
            'uuid': uuid,
            'type':	GObject.TYPE_(INT|BOOLEAN|STRING),
            'child': uuid, # __NOT_IMPLEMENTED_YET
            'parent': uuid, # __NOT_IMPLEMENTED_YET
            'renderer':
                'renderer_type',
                'properties': {
                    'editable': bool
                    'activatable': bool
                    ...
                },
                'callbacks': (
                    ('signal1', cb_meth1, *args),
                    ...,
                    ('signaln', cb_methn, *args)
                )
            'attributes':()  # __NOT_IMPLEMENTED_YET__
            'data': (col0_data, ..., coln_data)
            },

            'column1_title' {
                ...
            }
        }
        """
        return self.__model

    @model.setter
    def model(self, model_d):
        """IN: model_d: dictionnary. See __doc__"""
        self.__model = model_d

    @model.deleter
    def model(self):
        self.__model = None

    def run_widget(self):
        """
        Run widget
        """

        # returns <GtkTreeView>
        self._import_model()
        self._make_view()
        return self.widget
