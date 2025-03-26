# -*- coding: utf-8 -*-
"""
Mime
"""

import mimetypes

# import gi
# gi.require_version('GdkPixbuf', '3.0')
from gi.repository import GdkPixbuf

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class Mime:
    """
    Mime type support
    """

    def __init__(self):
        self.supported_types = None  # <Str>List
        self.supported_extensions = None  # <Str>List

    def get_supported_mimetypes(self):
        """Return default supported mimetypes"""
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.supported_types:
            self.supported_types = []

            # Add default types:
            for pixbuf_format in GdkPixbuf.Pixbuf.get_formats():
                self.supported_types.extend(pixbuf_format.get_mime_types())

        return self.supported_types

    def get_supported_extensions(self):
        """Return default supported files extensions"""
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.supported_extensions:
            self.supported_extensions = []

        # inverted types_map:
        # noinspection PyUnresolvedReferences
        ivd = dict([(v, k) for (k, v) in mimetypes.types_map.items()])

        for supported_type in self.get_supported_mimetypes():
            # noinspection PyUnresolvedReferences
            if supported_type in mimetypes.types_map.values():
                self.supported_extensions.append(ivd[supported_type])

        # until something more reliable than mimetypes is used, let's tweak
        # variants as possible:
        if ".jpeg" in self.supported_extensions:
            self.supported_extensions.append(".jpg")

        return self.supported_extensions
