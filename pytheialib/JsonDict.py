# -*- coding: utf-8 -*-
"""
JsonDict
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class JsonDict:
    """
    Python dictionnary to Json output transformation.
    Useful for debugging mainly.
    """

    def __init__(self):
        self.print_dict_obuf = ""  # str
        self.last_was = None  # str
        pass

    def print_dict(self, dic, nes=1):
        """
        Outputs a pseudo JSON representation of given dictionnary
        """
        indent = ""
        dlmdic = ""

        if self.last_was is None:
            debug("# %s:%s()" % (self.__class__, callee()))

        if nes != 0:
            for _ in range(0, nes):
                indent += "\t"

        is_first_item = True

        for key in dic.keys():
            # sub DICT:
            if isinstance(dic[key], dict):
                if not is_first_item:
                    dlmdic = ",\n"
                self.last_was = "dict"
                self.print_dict_obuf += '%s%s"%s":{\n' % (dlmdic, indent, key)
                self.print_dict(dic[key], (nes + 1))
                self.print_dict_obuf += "\n%s}" % indent
                is_first_item = False
                continue

            # sub LIST:
            elif isinstance(dic[key], list):
                if not is_first_item:
                    dlmdic = ",\n"
                else:
                    dlmdic = ""
                self.last_was = "list"
                self.print_dict_obuf += '%s%s"%s":' % (dlmdic, indent, key)

                self.print_dict_obuf += "%s" % (str(dic[key])).replace("'", '"')
                is_first_item = False
                continue

            # string "value"
            else:
                if not is_first_item:
                    dlmstd_ = ",\n"
                else:
                    dlmstd_ = ""
                self.last_was = "value"
                self.print_dict_obuf += '%s%s"%s":"%s"' % (
                    dlmstd_,
                    indent,
                    str(key),
                    str(dic[key]),
                )
                is_first_item = False

        return "{\n" + self.print_dict_obuf + "\n}"
