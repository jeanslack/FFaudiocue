# -*- coding: UTF-8 -*-
"""
Name: argparser.py
Porpose: FFcuesplitter-GUI Command line arguments
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.13.2025
Code checker: flake8, pylint .

This file is part of FFcuesplitter-GUI.

   FFcuesplitter-GUI is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FFcuesplitter-GUI is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with FFcuesplitter-GUI.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
from shutil import which
import argparse
import platform
from ffcuesplitter_gui.ffc_sys.about_app import (PRGNAME,
                                                 VERSION,
                                                 RELSTATE
                                                 )
try:
    import wx
    MSGWX = f"{wx.version()})"
except ModuleNotFoundError as errwx:
    MSGWX = f"not installed! ({errwx})"


def info_this_platform():
    """
    Get information about operating system, version of
    Python and wxPython.
    """
    osys = platform.system_alias(platform.system(),
                                 platform.release(),
                                 platform.version(),
                                 )
    thisplat = (f"Platform: {osys[0]}\n"
                f"Version: {osys[2]}\n"
                f"Release: {osys[1]}\n"
                f"Architecture: {platform.architecture()}\n"
                f"Python: {sys.version}\n"
                f"wxPython: {MSGWX}"
                )
    return thisplat


def arguments():
    """
    Parser for command line options
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version',
                        help="show the current version and exit",
                        action="store_true",
                        )
    parser.add_argument('-c', '--check',
                        help=('List of executables used by FFcuesplitter-GUI '
                              'found on the system'),
                        action="store_true",
                        )
    parser.add_argument('--make-portable',
                        help=('Make the application fully portable and '
                              'stealth. Use this option whenever you want to '
                              'keep all application data stored separately '
                              'from conventional platform directories and '
                              'provide only relative paths. It expects you to '
                              'specify a preferred location where storing the '
                              'new application data as user preferences, '
                              'cache files, log files and default output '
                              'folder. The first time, all of this involves '
                              'reconfiguring the application through the '
                              'wizard dialog.'
                              ),
                        metavar='DIRNAME',
                        )

    argmts = parser.parse_args()

    if argmts.check:
        deps = {'Required': {'ffmpeg': None, 'ffprobe': None}}
        for key, val in deps.items():
            if key in ('Required'):
                for exe in val:
                    val[exe] = which(exe, mode=os.F_OK | os.X_OK, path=None)
        print('\nList of executables used by FFcuesplitter-GUI:')
        for key, val in deps.items():
            for exe, path in val.items():
                if path:
                    print(f"\t[{key}] '{exe}' ...Ok")
                    print(f"\tpath: '{path}'\n")
                else:
                    print(f"\t[{key}] '{exe}' ...Not Installed")
                    print(f"\tpath: {path}\n")
        parser.exit(status=0, message=None)

    elif argmts.version:
        print(f'{PRGNAME}: {VERSION} ({RELSTATE})')
        print(info_this_platform())
        parser.exit(status=0, message=None)

    else:
        print("Type -h for help.")

    return vars(argmts)
