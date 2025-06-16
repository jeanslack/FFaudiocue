# -*- coding: UTF-8 -*-
"""
Name: utils.py
Porpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June 13 2025
Code checker: flake8, pylint .

This file is part of FFaudiocue.

   FFaudiocue is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FFaudiocue is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with FFaudiocue.  If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess
import platform
import shutil
import os


def open_default_application(pathname):
    """
    Given a path to a specific file or directory, opens the
    operating system's default application according to the
    user-set file type association. Currently supported platforms
    are Windows, Darwin and Linux. Note that Linux uses xdg-open
    which should also be used by other OSes that may support
    it, eg freebsd.

    Return error if any error, None otherwise.
    """
    if platform.system() == 'Windows':
        try:
            os.startfile(os.path.realpath(pathname))
        except FileNotFoundError as error:
            return str(error)

        return None

    if platform.system() == "Darwin":
        cmd = ['open', pathname]
    else:  # Linux, FreeBSD or any supported
        cmd = ['xdg-open', pathname]
    try:
        subprocess.run(cmd, check=True, shell=False, encoding='utf-8')
    except subprocess.CalledProcessError as error:
        return str(error)

    return None
# ------------------------------------------------------------------------


def get_codec_quality_items(_format_):
    """
    Given an audio format, it returns the corresponding
    audio compression references,if available.
    """
    qualities = {'wav': {"Auto": ""},
                 'flac': {"Auto": "",
                          "very high quality": "-compression_level 0",
                          "quality 1": "-compression_level 1",
                          "quality 2": "-compression_level 2",
                          "quality 3": "-compression_level 3",
                          "quality 4": "-compression_level 4",
                          "Standard quality": "-compression_level 5",
                          "quality 6": "-compression_level 6",
                          "quality 7": "-compression_level 7",
                          "low quality": "-compression_level 8"
                          },
                 'ogg': {"Auto": "",
                         "very poor quality": "-aq 1",
                         "VBR 92 kbit/s": "-aq 2",
                         "VBR 128 kbit/s": "-aq 3",
                         "VBR 160 kbit/s": "-aq 4",
                         "VBR 175 kbit/s": "-aq 5",
                         "VBR 192 kbit/s": "-aq 6",
                         "VBR 220 kbit/s": "-aq 7",
                         "VBR 260 kbit/s": "-aq 8",
                         "VBR 320 kbit/s": "-aq 9",
                         "very good quality": "-aq 10"
                         },
                 'opus': {"Auto": "",
                          "low quality 0": "-compression_level 0",
                          "low quality 1": "-compression_level 1",
                          "quality 2": "-compression_level 2",
                          "quality 3": "-compression_level 3",
                          "quality 4": "-compression_level 4",
                          "medium quality 5": "-compression_level 5",
                          "quality 6": "-compression_level 6",
                          "quality 7": "-compression_level 7",
                          "quality 8": "-compression_level 8",
                          "high quality 9": "-compression_level 9",
                          "highest quality 10 (default)":
                          "-compression_level 10",
                          },
                 'mp3': {"Auto": "",
                         "VBR 128 kbit/s (low quality)": "-b:a 128k",
                         "VBR 160 kbit/s": "-b:a 160k",
                         "VBR 192 kbit/s": "-b:a 192k",
                         "VBR 260 kbit/s": "-b:a 260k",
                         "CBR 320 kbit/s (very good quality)": "-b:a 320k"
                         }
                 }
    return qualities[_format_]
# ------------------------------------------------------------------------


def del_filecontents(filename):
    """
    Delete the contents of the file if it is not empty.
    Please be careful as it assumes the file exists.

    USAGE:

        if fileExists is True:
            try:
                del_filecontents(logfile)
            except Exception as err:
                print("Unexpected error while deleting "
                      "file contents:\n\n{0}").format(err)

    MODE EXAMPLE SCHEME:

    |          Mode          |  r   |  r+  |  w   |  w+  |  a   |  a+  |
    | :--------------------: | :--: | :--: | :--: | :--: | :--: | :--: |
    |          Read          |  +   |  +   |      |  +   |      |  +   |
    |         Write          |      |  +   |  +   |  +   |  +   |  +   |
    |         Create         |      |      |  +   |  +   |  +   |  +   |
    |         Cover          |      |      |  +   |  +   |      |      |
    | Point in the beginning |  +   |  +   |  +   |  +   |      |      |
    |    Point in the end    |      |      |      |      |  +   |  +   |

    """
    with open(filename, "r+", encoding='utf8') as fname:
        content = fname.read()
        if content:
            fname.flush()  # clear previous content readed
            fname.seek(0)  # it places the file pointer to position 0
            fname.write("")
            fname.truncate()  # truncates the file to the current file point.
# ------------------------------------------------------------------#


def detect_binaries(name, extradir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    name = name of executable without extension
    extradir = additional dirname to perform search

    Given an executable (binary) file name, it looks for it
    in the operating system using the `which` function, if it
    doesn't find it, it tries to look for it in the optional
    `extradir` .

        Return (None, path) if found in the OS $PATH.
        Return ('provided', path) if found on the `extradir`
        Return ('not installed', None) if both failed.

    """
    execpath = shutil.which(name)
    if execpath:
        return None, execpath
    if extradir:  # check onto extradir
        execpath = os.path.join(extradir, "bin", name)
        if os.path.isfile(execpath):
            return 'provided', execpath
    return 'not installed', None
