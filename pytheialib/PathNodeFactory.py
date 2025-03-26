# -*- coding: utf-8 -*-
"""
PathNodeFactory
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class PathNodeFactory:
    """
    Path Node object represents a toplevel object for a path location of a
    given type, as a directory, a Zip archive, a protocol URI etc...

    """

    def __init__(self):
        self.platform = None  # <Platform>
        self.current_pathnode_index = None  # int
        self.supporting_pool = None  # <SupportingPool>
        self.cli_parse = None  # <CliParse>

        if not hasattr(self, "factory_types"):
            self.factory_types = {}

    def add_to_supporting_pool(self, pool_data):
        """
        Merge additional support providers in the Factory

        """
        gdebug(f"# {self.__class__}:{callee()}")

        for supporter in pool_data:
            _name = pool_data[supporter]["factory"]["name"]
            _mimes = pool_data[supporter]["mimes"]
            _origin = pool_data[supporter]["factory"]["origin"]
            _recursive = pool_data[supporter]["factory"]["recursive"]
            _uri = pool_data[supporter]["factory"]["uri"]
            _provider = pool_data[supporter]["factory"]["provider"]

            wdebug("found supporter: %s, with name: %s, for mime(s): %s" % (supporter, _name, str(_mimes)))

            self.factory_types[_name] = {
                "origin": _origin,
                "recursive": _recursive,
                "uri": _uri,
                "provider": _provider,
            }

    def create_node(
        self,
        ntype=None,
        uri=None,
        # recursive is for future use:
        recursive=False,  # pylint: disable=W0613
        start_uri=None,
    ):
        """
        Str ntype =>
            'directory',
            'archive',
            'compressed_file',
            'http',
            'ftp',
            'ssh',
            ...

        ndata = {
            'uri'
        }

        """
        gdebug(
            "# %s:%s(ntype=%s, uri=%s, recursive=%s, start_uri=%s)"
            % (
                self.__class__,
                callee(),
                str(ntype),
                str(uri),
                str(recursive),
                str(start_uri),
            )
        )

        # Dynamically create an instance of the requested PathNode type and
        # return it:
        new_node = self.factory_types[ntype]["provider"]()

        new_node.platform = self.platform
        new_node.cli_parse = self.cli_parse
        new_node.recursive = recursive
        new_node.supporting_pool = self.supporting_pool

        # start uri allow to specify a more detailed resource to start with,
        # withing a given node, to it overrides 'uri' for the starter election:
        if uri and not start_uri:
            # debug('uri: %s -> start_uri' % str(uri))
            new_node.set_start_uri(uri)

        elif uri and start_uri:
            # debug('uri: %s, start_uri: %s -> start_uri: %s' % (uri, start_uri, start_uri))
            new_node.set_start_uri(start_uri)

        else:
            raise RuntimeError("uri/start_uri unexpected combination")

        return new_node
