# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Porpose: input/output redirection to some processes
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June 13 2025
Code checker: flake8, pylint

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
import requests
import wx
from ffcuesplitter_gui.ffc_utils.utils import open_default_application


def openpath(where):
    """
    Call `open_default_application`
    """
    ret = open_default_application(where)
    if ret:
        wx.MessageBox(ret, _('FFcuesplitter-GUI - Error!'),
                      wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API:
    https://developer.github.com/v3/repos/releases/#get-the-latest-release

    see keyname examples here:
    <https://api.github.com/repos/jeanslack/FFcuesplitter-GUI/releases>

    """
    try:
        response = requests.get(url, timeout=20)
        not_found = None, None
    except Exception as err:
        not_found = 'request error:', err
    else:
        try:
            version = response.json()[f"{keyname}"]
        except Exception as err:
            not_found = 'response error:', err

    if not_found[0]:
        return not_found

    return version, None
# --------------------------------------------------------------------------#
