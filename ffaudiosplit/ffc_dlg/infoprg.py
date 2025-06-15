# -*- coding: UTF-8 -*-
"""
Name: infoprog.py
Porpose: about ffaudiosplit
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.08.2022
########################################################

This file is part of FFaudiosplit.

   FFaudiosplit is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FFaudiosplit is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with FFaudiosplit.  If not, see <http://www.gnu.org/licenses/>.
"""
import wx
import wx.adv
from ffaudiosplit.ffc_sys.about_app import (COPYRIGHT,
                                                 RELNAME,
                                                 AUTHOR,
                                                 WEBSITE,
                                                 LICENSE,
                                                 MAIL,
                                                 VERSION
                                                 )


def info_gui(parent, prg_icon):
    """
    It's a predefined template to create a dialog on
    the program information

    """
    infoprg = wx.adv.AboutDialogInfo()
    infoprg.SetIcon(wx.Icon(prg_icon, type=wx.BITMAP_TYPE_PNG))
    infoprg.SetName(RELNAME)
    infoprg.SetVersion(f'{VERSION}')
    infoprg.SetDescription(_("Extracts audio tracks from an audio CD image\n"
                             "supplied with the CUE sheet, using FFmpeg."))
    infoprg.SetCopyright(f'Copyleft {COPYRIGHT} {AUTHOR}')
    infoprg.SetWebSite(WEBSITE)
    infoprg.SetLicence(LICENSE)
    infoprg.AddDeveloper(f"{AUTHOR} <{MAIL}>")
    infoprg.AddDocWriter(f"{AUTHOR} <{MAIL}>")
    infoprg.AddTranslator(f"{AUTHOR} <{MAIL}> (it_IT)")
    infoprg.AddTranslator("ChourS <ChourS2008@yandex.ru> (ru_RU)")
    # info.AddTranslator("Nestor Blanco <random@mail.es> (es_ES)")
    infoprg.SetArtists(
        [(f"{AUTHOR} <{MAIL}>")])
    wx.adv.AboutBox(infoprg)
    # event.Skip()
