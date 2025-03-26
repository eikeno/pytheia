# -*- coding: utf-8 -*-
"""
SourceImage
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class SourceImage:
    """
    Contains an image (pixbuf) in an unaltered state, for reference
    """

    def __init__(self):
        self.imagefile = None  # Str
        self.width = None  # Int
        self.height = None  # Int
        self.orientation = None  # Str
        self.prominent_axis = None  # Str

    def register_image(self, current_pathnode):
        """
        Store source image file name, and feed atrributes based on it.

        Must accept accept that 'image_path' doesn't exist yet - to allow
        additionnal support provider to create it later, and avoid forcing
        too much resources consumming action right on PathNode instanciation.

        to summarize: Things to be created are on access, not in instanciation.
        """
        gdebug("# %s:%s(current_pathnode=%s)" % (self.__class__, callee(), str(type(current_pathnode))))
        if self.imagefile and current_pathnode.current_path == self.imagefile:
            raise RuntimeError("image already registered")

        elif self.imagefile:
            raise RuntimeError("Use SourceImage.unregister() first")

        # Path
        current_pathnode.preaccess_current()
        self.imagefile = current_pathnode.current_path

    def unregister_image(self):
        """
        Unregister current source image and references to it
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.imagefile:
            raise TypeError("source_image_file cannot be None")

        self.width = None
        self.height = None
        self.orientation = None
        self.prominent_axis = None
        self.imagefile = None
