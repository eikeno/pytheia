# -*- coding: utf-8 -*-
"""Utils.
General purpose helpers
"""

import hashlib
import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class Utils:
    """Misc. helpers and utilities"""

    def __init__(self):
        pass

    @staticmethod
    def md5_by_path(path):
        """Return MD5 sum for provided file path"""
        try:
            digest = hashlib.md5(open(path, "rb").read()).hexdigest()

        except IOError as exc:
            debug("IOError(%s): %s while opening: %s" % (exc.errno, exc.strerror, path))
            return False

        return digest

    @staticmethod
    def md5_by_string(_string_bytes):
        """Returns MD5 sum of the given `_string_bytes`

        Args:
            _string_bytes:  Str, textual value to calculate md5 sum for.

        Returns:    Str, md5 sum of passed `_string`.
        """
        return hashlib.md5(_string_bytes.encode("utf-8")).hexdigest()

    @staticmethod
    def get_fit_width_sizes(fit_sizes_t, src_sizes_t):
        """
        Args:
            fit_sizes_t:    tuple of dimensions of target display area.
            src_sizes_t:    tuple of dimensions of the original image (width, height,).

        Returns:     tuple of dimensions: (w, h,) the image should have to fit `fit_sizes_t`
                     Preserving aspect ratio.
        """

        w = src_sizes_t[0]
        h = src_sizes_t[1]
        ret_w = float(fit_sizes_t[0])
        l_ratio = float(ret_w) / float(w)
        ret_h = float(h) * float(l_ratio)

        bdebug("returns %sx%s" % (round(ret_w), round(ret_h)))
        return (round(ret_w) - 5, round(ret_h) - 5)

    @staticmethod
    def get_fit_height_sizes(fit_sizes_t, src_sizes_t):
        """
        Return a tuple of size an image (of original sizes: 'src_sizes_t')
        should have to fit in the height of a target display
        area: 'fit_sizes_t'.
        """
        bdebug("# %s:%s(%s, %s)" % ("Utils", "get_fit_height_sizes", str(fit_sizes_t), str(src_sizes_t)))

        w = src_sizes_t[0]
        h = src_sizes_t[1]
        ret_h = float(fit_sizes_t[1])
        l_ratio = float(ret_h) / float(h)
        ret_w = float(w) * float(l_ratio)

        bdebug("returns %sx%s" % (round(ret_w), round(ret_h)))
        return (round(ret_w) - 5, round(ret_h) - 5)

    @staticmethod
    def get_fit_best_sizes(fit_sizes_t, src_sizes_t):
        """
        Calculates and returns as a tuple the size an image
        of original dimensions given by `src_sizes_t` should have to
        fit in the dimentions of a target display area: 'fit_sizes_t'.

        Args:
            fit_sizes_t:    (Int width, Int height)
            src_sizes_t:    (Int width, Int height)

        Returns:
            (Int width, Int height)
        """
        bdebug("# %s:%s(%s, %s)" % ("Utils", "get_fit_height_sizes", str(fit_sizes_t), str(src_sizes_t)))

        # Not needed, but easier to read:
        src_img_w = src_sizes_t[0]
        src_img_h = src_sizes_t[1]
        dst_area_w = fit_sizes_t[0]
        dst_area_h = fit_sizes_t[1]

        # Add abstraction over the Screen aspect ratio for later comparisons:
        # noinspection PyPep8
        l_ratio = lambda a, b: float(a) / float(b)
        # noinspection PyPep8
        l_apply_ratio = lambda a, b, r: ((float(a) * r), (float(b) * r))

        fraction = float(src_img_w) / float(dst_area_w)
        ret_w = dst_area_w
        ret_h = float(src_img_h) / float(fraction)

        # detect out-of-boundaries dimension, and reduce accordingly, keeping aspect ratio:
        if ret_h > dst_area_h:
            ret_w, ret_h = l_apply_ratio(ret_w, ret_h, l_ratio(dst_area_h, ret_h))

        if ret_w > dst_area_w:
            ret_w, ret_h = l_apply_ratio(ret_w, ret_h, l_ratio(dst_area_w, ret_w))

        debug("ret_w:%s, ret_h: %s" % (round(ret_w), round(ret_h)))
        return round(ret_w) - 5, round(ret_h) - 5

    @staticmethod
    def orientation_from_sizes(width, height):
        """Return natural language orientation of provided image WxH sizes"""
        if width > height:
            orientation = "landscape"

        elif width < height:
            orientation = "portrait"

        elif width == height:
            orientation = "square"
        else:
            raise RuntimeError("couldn't determine orientation of image")

        return orientation

    @staticmethod
    def scale_pixbuf(reference_pixbuf, sizes_t, interp_method):
        """
        Returns scaled version of `reference_pixbuf` based on provided
        `sizes_t` values.

        Args:
            reference_pixbuf: <GdkPixbuf>
            sizes_t:          (width, heigth) Dimension to scale the image to
            interp_method:    Str, a valid GdkPixbuf interpolation method
                              (nearest, tiles etc.)

        Returns: <GdkPixbuf>, scaled to required dimensions
        """
        ref_pxbf_w, ref_pxbf_h = reference_pixbuf.get_properties("width", "height")
        dst_w, dst_h = sizes_t[0], sizes_t[1]

        orient = Utils.orientation_from_sizes(ref_pxbf_w, ref_pxbf_h)  # static method

        if orient in ("portrait", "square"):
            fraction = float(ref_pxbf_h) / float(dst_h)
            ret_w, ret_h = (int(ref_pxbf_w / fraction), int(ref_pxbf_h / fraction))

        elif orient == "landscape":
            fraction = float(ref_pxbf_w) / float(dst_w)
            ret_w, ret_h = (int(ref_pxbf_w / fraction), int(ref_pxbf_h / fraction))

        else:
            raise RuntimeError("Orientation incorrect: %s" % orient)

        return reference_pixbuf.scale_simple(ret_w, ret_h, interp_method)

    @staticmethod
    def containing_directory(path=None):
        """Returns containing directory of a file or directory"""

        if not path:
            raise TypeError("path must be specified")

        return os.path.dirname(os.path.abspath(path))

    @staticmethod
    def str_reduced(limit=None, data=None):
        """
        A derivation of 'str()' that truncate output at 'limit' characters.

        @param limit Int
        @param data Str
        """
        if not limit:
            raise TypeError("limit must be specified")

        if not data:
            return

        _str = str(data)

        if len(_str) <= limit:
            return data

        # Truncation splitter, before/after -> 80/20 ratio:
        _pre = round(float(limit * 80) / 100)
        _post = limit - _pre

        return _str[: int(_pre)] + "[]" + _str[-int(_post) :]
