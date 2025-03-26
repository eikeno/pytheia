# -*- coding: utf-8 -*-
"""
ImageDisplay
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class ImageDisplay:
    """
    Manage image display internal details
    """

    def __init__(self):
        self.raw_pixbuf = None  # GdkPixbuf
        self.active_pixbuf = None  # GdkPixbuf

        self.display_state = None  # <DisplayState>
        self.image_display_widget = None  # <ImageDisplayWidget>
        self.pbl = None  # <ProgressivePixbufLoader>
        self.screen = None  # <Screen>
        self.source_image = None  # <SourceImage>

    def update_active_pixbuf(self, _pixbuf, comment=None):
        """Update active pixbuf, with complete or partial pixbuf"""
        # returns bool
        gdebug("# %s:%s(%s, comment=%s)" % (self.__class__, callee(), str(_pixbuf), str(comment)))

        if not _pixbuf:
            self.pbl.error = 1
            # Don't raise an error here but flag the error state to
            # be used by error manager later (i.e: display a 'broken image'
            # symbol, etc.
        self.active_pixbuf = _pixbuf

    def get_active_pixbuf_size(self):
        """get active pixbuf sizes tuple: (widht, height)"""
        # returns (ints)
        gdebug(f"# {self.__class__}:{callee()}")

        return self.active_pixbuf.get_width(), self.active_pixbuf.get_height()

    def update_raw_pixbuf(self, _pixbuf):
        """update raw_pixbuf with given Pixbuf object"""
        # returns bool
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(_pixbuf)))

        if not _pixbuf:
            self.pbl.error = 2
        # raise TypeError('_pixbuf cannot be none')

        self.raw_pixbuf = _pixbuf

    def clear_pixbufs(self):
        """try to safely clear references to Pixbuf objects"""
        # returns bool
        gdebug(f"# {self.__class__}:{callee()}")

        if self.raw_pixbuf:
            self.raw_pixbuf = None

        if self.active_pixbuf:
            self.active_pixbuf = None
