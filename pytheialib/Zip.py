# -*- coding: utf-8 -*-
"""
Zip format support
"""

import os
import shutil
import sys
import zipfile
from io import BytesIO

import pytheialib
from pytheialib import JsonDict


class Zip:
    """Zip archives manipulation"""

    def __init__(self):
        self.registered_zipfiles = {}

    def register(self, zip_dict):
        """
        Register zip archives for later treatment

        If equal to None, outdir will be automatically replaced by a directory
        in the current working directory, whith a name based on archive basename,
        without extension.

        For Example, the following zip_dict:
        {'/foo/bar/baz.zip': None}

        Will set an outdir of: '/foo/bar/baz'
        The creation of that directory is attempted when extracting files with
        extract_* family of methods.

        zip_dict example:
            {
                '/p/a/t/h/t/o/file1.zip':	'/p/a/t/h/t/o/outdirname1',
                '/p/a/t/h/t/o/file2.zip':	'/p/a/t/h/t/o/outdirname2',
            }

        internal view of registered_zipfiles:
            { '/p/a/t/h/t/o/file1.zip':
                {
                    'outdir': '/p/a/t/h/t/o/outdirname1',
                    'object': <zipfile.ZipFile objet>
                },
              '/p/a/t/h/t/o/file2.zip':
                {
                    'outdir': '/p/a/t/h/t/o/outdirname2',
                     object': <another zipfile.ZipFile objet>
                },
                ...
            }

        """
        for i in zip_dict:
            self.registered_zipfiles[i] = {}
            # noinspection PyUnusedLocal
            _outdir = None

            if zip_dict[i] is None:
                _outdir = os.path.join(os.getcwd(), os.path.basename(os.path.splitext(i)[0]))
            else:
                _outdir = zip_dict[i]

            self.registered_zipfiles[i]["outdir"] = _outdir
            self.registered_zipfiles[i]["object"] = self._get_handle(i)

    @staticmethod
    def _get_handle(zip_archive):
        """
        Open a Zip archive for reading and return a ZIP object

        """
        return zipfile.ZipFile(zip_archive, "r", zipfile.ZIP_DEFLATED, True)

    @staticmethod
    def _list_all_files(obj):
        """
        List files from a ZIP object

        """
        return pytheialib.ignore_patterns_on_filepath_list(obj.namelist())

    def list_all_files(self, archive=None):
        """
        List files from registered 'archive' (zip file path name, used as key
        in register's registered_zipfiles) or all registered zip files if
        omitted.

        Result is returned as a single list, with files from different archives.
        For splitted lists per archives, used list_all_files_split()

        """
        _out_l = []

        if not archive:
            _zips_l = [k for k in self.registered_zipfiles]
        else:
            _zips_l = [archive]

        if not isinstance(_zips_l, list):
            raise RuntimeError("got a _zips_l which is not a list")

        for _zip_fn in _zips_l:
            if _zip_fn not in self.registered_zipfiles:
                raise ValueError("%s must be registered first" % str(archive))

            _out_l.extend(Zip._list_all_files(self.registered_zipfiles[_zip_fn]["object"]))

        return _out_l

    def list_all_files_split(self):
        """
        List all files from registered archives.

        Returns a list of lists (one per archive)

        """
        _out_l = []
        _zips_l = self.registered_zipfiles

        for _zip_fn in _zips_l:
            _out_l.append(self.list_all_files(archive=_zip_fn))  # list
        return _out_l  # list of lists

    def extract_all_files(self, archives=None, flat=True):
        """
        Extract spcified registered ZIP archives in respectively registered
        places.

        If 'flat' is True, possibly existing subdirectories structure will be
        preserved. If set to False, all files will be extracted right under
        registered 'outdir', causing possible overwritting if several files
        have the same basename in the archive.

        If 'archives' is omitted, all registered archives will be processed.

        """
        # NOTE: highly dependant on zipfile module internal !

        if not archives:
            _zips_l = [k for k in self.registered_zipfiles]
        else:
            if not isinstance(archives, list):
                raise ValueError("archives must be a list")
            _zips_l = archives

        for zipkey in _zips_l:
            if not isinstance(zipkey, str):
                raise ValueError("key: %s in archives dict. must be a string" % str(zipkey))

            if zipkey not in self.registered_zipfiles:
                raise ValueError("%s must be registered first" % str(zipkey))

            _files_list = Zip._list_all_files(self.registered_zipfiles[zipkey]["object"])

            if not isinstance(_files_list, list):
                raise RuntimeError("got a _files_list which is not a list")

            # outdir must exists, whatever the context:
            if not os.path.exists(self.registered_zipfiles[zipkey]["outdir"]):
                os.makedirs(self.registered_zipfiles[zipkey]["outdir"])

            for _file in _files_list:
                if _file.endswith(os.path.sep) and flat is True:
                    # Is an internal dir:
                    os.makedirs(os.path.join(self.registered_zipfiles[zipkey]["outdir"], _file))

                else:
                    # Is a file:
                    # Create intermediate internal dirs as needed:
                    if (
                        not os.path.exists(
                            os.path.join(
                                self.registered_zipfiles[zipkey]["outdir"],
                                os.path.dirname(_file),
                            )
                        )
                        and not flat
                    ):
                        os.makedirs(
                            os.path.join(
                                self.registered_zipfiles[zipkey]["outdir"],
                                os.path.dirname(_file),
                            )
                        )

                    _src = self.registered_zipfiles[zipkey]["object"].open(_file, pwd=None)

                    if not flat:
                        _tgt = open(
                            os.path.join(self.registered_zipfiles[zipkey]["outdir"], _file),
                            "wb",
                        )
                    else:
                        _tgt = open(
                            os.path.join(
                                self.registered_zipfiles[zipkey]["outdir"],
                                os.path.basename(_file),
                            ),
                            "wb",
                        )

                    # warn and pass if target exist already
                    shutil.copyfileobj(_src, _tgt)

                    # error if writing failed
                    _src.close()
                    _tgt.close()

    def extract_file(self, archive, filepath, flat=False):
        """
        Extract specified 'filepath' from registered 'archive', preserving
        possibly existing subdirectories.

        """
        # NOTE: highly dependant on zipfile module internal !

        if not archive:
            raise ValueError("A valid registered archive name is needed")

        if archive not in self.registered_zipfiles:
            raise ValueError("%s must be registered first" % str(archive))

        if not isinstance(archive, str):
            raise ValueError("archive must be string")

        if not filepath:
            raise ValueError("A valid filepath name is needed")

        if not isinstance(filepath, str):
            raise ValueError("filepath must be string")

        if filepath.endswith(os.path.sep):
            # Is an internal dir:
            raise ValueError("filepath must be a file, not a directory")

        # outdir must exists, whatever the context:
        if not os.path.exists(self.registered_zipfiles[archive]["outdir"]):
            os.makedirs(self.registered_zipfiles[archive]["outdir"])

        # Create intermediate internal dirs as needed:
        if (
            not os.path.exists(
                os.path.join(
                    self.registered_zipfiles[archive]["outdir"],
                    os.path.dirname(filepath),
                )
            )
            and not flat
        ):
            os.makedirs(
                os.path.join(
                    self.registered_zipfiles[archive]["outdir"],
                    os.path.dirname(filepath),
                )
            )

        _src = self.registered_zipfiles[archive]["object"].open(filepath, pwd=None)

        if not flat:
            _tgt = open(
                os.path.join(self.registered_zipfiles[archive]["outdir"], filepath),
                "wb",
            )
        else:
            _tgt = open(
                os.path.join(
                    self.registered_zipfiles[archive]["outdir"],
                    os.path.basename(filepath),
                ),
                "wb",
            )

        # warn and pass if target exist already
        shutil.copyfileobj(_src, _tgt)

        # error if writing failed
        _src.close()
        _tgt.close()

    def extract_file_tobuffer(self, archive, filepath):
        """
        Extract specified 'filepath' from 'archive' to an in-memory buffer
        that is returned.

        """
        # NOTE: highly dependant on zipfile module internal !

        if not archive:
            raise ValueError("A valid registered archive name is needed")

        if archive not in self.registered_zipfiles:
            raise ValueError("%s must be registered first" % str(archive))

        if not isinstance(archive, str):
            raise ValueError("archive must be string")

        if not filepath:
            raise ValueError("A valid filepath name is needed")

        if not isinstance(filepath, str):
            raise ValueError("filepath must be string")

        if filepath.endswith(os.path.sep):
            # Is an internal dir:
            raise ValueError("filepath must be a file, not a directory")

        _src = self.registered_zipfiles[archive]["object"].open(filepath, pwd=None)

        _buffer = BytesIO(_src.read())

        _src.close()
        return _buffer


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__file__ + " ZIPFILE1 ZIPFILE2 ...")
        sys.exit(0)

    ZF = sys.argv[1]
    ZF2 = sys.argv[2]
    print("ZF : " + ZF)
    print("ZF2 : " + ZF2)

    ZINST = Zip()
    ZINST.register(
        {
            ZF: None,
            ZF2: "/tmp/FOOBAR",
        }
    )

    ZL = ZINST.list_all_files()
    print(ZL)
    print()
    print(ZINST.list_all_files_split())
    print()
    print(JsonDict.JsonDict().print_dict(ZINST.registered_zipfiles))
    ZINST.extract_file(ZF, "py3createtorrent-0.9.3/gpl-3.0.txt", flat=True)
