# -*- coding: UTF-8 -*-
"""
Name: cd_info.py
Porpose: view CD audio info and other informations
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.15.2025
Code checher: flake8, pylint
########################################################

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
import os
import datetime
# import webbrowser
import wx
from pubsub import pub


class CdInfo(wx.Dialog):
    """
    Dialog to view CD audio informations and other data.
    """
    def __init__(self, parent, cd_info, probedata, filecue, cue_enc):
        """
        constructor
        """
        get = wx.GetApp()
        appdata = get.appset
        vidicon = get.iconset['ffaudiocue']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )

        size_base = wx.BoxSizer(wx.VERTICAL)
        self.tinfo = wx.TextCtrl(self, wx.ID_ANY, "",
                                 style=wx.TE_MULTILINE
                                 | wx.TE_READONLY
                                 | wx.HSCROLL
                                 # | wx.TE_RICH2
                                 )
        size_base.Add(self.tinfo, 1, wx.ALL | wx.EXPAND, 5)

        # bottom btns
        gridbtn = wx.GridSizer(1, 1, 0, 0)
        size_base.Add(gridbtn, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")
        gridbtn.Add(self.button_close, 1, wx.ALL, 5)
        # ------ set sizer
        self.SetTitle(_('Audio CD Informations'))
        self.SetMinSize((600, 400))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetSizer(size_base)
        self.Fit()
        self.Layout()

        # ----------------------Set Properties----------------------#
        def to_time(arg):
            """convert seconds to time format
            """
            return str(datetime.timedelta(seconds=float(arg)))

        text = (f'-------------------\n'
                f"AUDIO CD PROPERTIES\n"
                f'-------------------\n'
                f"Performer:  {cd_info.get('PERFORMER', 'N/A')}\n"
                f"Album:  {cd_info.get('ALBUM', 'N/A')}\n"
                f"Genre:  {cd_info.get('GENRE', 'N/A')}\n"
                f"Disc id:  {cd_info.get('DISCID', 'N/A')}\n"
                f"Date:  {str(cd_info.get('DATE', ''))}\n"
                f"Disc Number:  {cd_info.get('DISCNUMBER', 'N/A')}\n"
                f"Total Disc:  {cd_info.get('TOTALDISC', 'N/A')}\n"
                f"Comment:  {cd_info.get('COMMENT', 'N/A')}\n\n"
                f'--------\n'
                f"CUE FILE\n"
                f'--------\n'
                f"File name:  '{os.path.basename(filecue)}'\n"
                f"Position:  '{os.path.dirname(filecue)}'\n"
                f"Encoding:  {cue_enc['encoding']}\n"
                f"Confidence:  {cue_enc['confidence']}\n"
                f"Language:  {cue_enc['language']}\n\n"
                )
        self.tinfo.AppendText(text)
        index = 0
        for data in probedata:
            index += 1
            text = (f'---------------\n'
                    f"AUDIO FILE ({index})\n"
                    f'---------------\n'
                    f"Name:  {data['format']['filename']}\n")
            self.tinfo.AppendText(text)
            for stream in data['streams']:
                if stream['codec_type'] == 'audio':
                    text = (f"Codec:   {stream['codec_name']}\n"
                            f"Bit deph:  {stream['sample_fmt']}\n"
                            f"Sample rate:  {stream['sample_rate']}\n"
                            f"Channels:  {stream['channels']}\n"
                            f"Duration seconds:  {stream['duration']}\n"
                            f"Time lenght:  {to_time(stream['duration'])}\n\n"
                            )
                    self.tinfo.AppendText(text)

        if appdata['ostype'] == 'Darwin':
            self.tinfo.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.tinfo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        # ----------------------Binder (EVT)----------------------#

        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # ---------------------Callback (event handler)----------------------#

    def on_close(self, event):
        """
        destroy dialog by button and the X
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='CdInfo')
