# -*- coding: UTF-8 -*-
"""
Name: track_info.py
Porpose: view and edit selected track metadata
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.08.2022
Code checher: flake8, pylint
########################################################

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
# import webbrowser
import wx


class TrackInfo(wx.Dialog):
    """
    Show dialog to view or edit selected track tag.
        if wx.ID_OK:
            Returns: self.metadata list, none otherwise.
    """
    def __init__(self, parent, metadata, trackindex):
        """
        self.metadata list is an object of type audio metadata CD.
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.metadata = metadata
        self.trackindex = trackindex
        title = _("Track ({}) Audio Tag").format(self.trackindex)

        wx.Dialog.__init__(self, parent, -1, title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        size_base = wx.BoxSizer(wx.VERTICAL)
        #  Artist
        size_line0 = wx.BoxSizer(wx.HORIZONTAL)
        size_base.Add(size_line0, 0, wx.ALL | wx.EXPAND, 0)
        box_artist = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                    _("Artist")),
                                       wx.VERTICAL)
        size_line0.Add(box_artist, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_artist = wx.TextCtrl(self, wx.ID_ANY, "")
        box_artist.Add(self.txt_artist, 0, wx.ALL | wx.EXPAND, 5)
        #  Album
        box_album = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                   _("Album")),
                                      wx.VERTICAL
                                      )
        size_line0.Add(box_album, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_album = wx.TextCtrl(self, wx.ID_ANY, "")
        box_album.Add(self.txt_album, 0, wx.ALL | wx.EXPAND, 5)
        #  track title
        size_line1 = wx.BoxSizer(wx.HORIZONTAL)
        size_base.Add(size_line1, 0, wx.ALL | wx.EXPAND, 0)
        box_title = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                   _("Track Title")),
                                      wx.VERTICAL
                                      )
        size_line1.Add(box_title, 1, wx.ALL | wx.EXPAND, 5)

        self.txt_title = wx.TextCtrl(self, wx.ID_ANY, "")
        box_title.Add(self.txt_title, 0, wx.ALL | wx.EXPAND, 5)
        #  Genre
        box_genre = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                   _("Genre")),
                                      wx.VERTICAL
                                      )
        size_line1.Add(box_genre, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_genre = wx.TextCtrl(self, wx.ID_ANY, "")
        box_genre.Add(self.txt_genre, 0, wx.ALL | wx.EXPAND, 5)
        size_line2 = wx.BoxSizer(wx.HORIZONTAL)
        size_base.Add(size_line2, 0, wx.ALL | wx.EXPAND, 0)
        #  Date
        box_date = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                  _("Date")),
                                     wx.VERTICAL
                                     )
        size_line2.Add(box_date, 1, wx.ALL | wx.EXPAND, 5)

        self.txt_date = wx.TextCtrl(self, wx.ID_ANY, "")
        box_date.Add(self.txt_date, 0, wx.ALL | wx.EXPAND, 5)
        #  Disc ID
        box_discid = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                    _("Disc ID")),
                                       wx.VERTICAL
                                       )
        size_line2.Add(box_discid, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_discid = wx.TextCtrl(self, wx.ID_ANY, value="")
        box_discid.Add(self.txt_discid, 0, wx.ALL | wx.EXPAND, 5)
        #  Comment
        box_comment = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                     _("Comment")),
                                        wx.VERTICAL
                                        )
        size_base.Add(box_comment, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_comment = wx.TextCtrl(self, wx.ID_ANY, "",
                                       style=wx.TE_MULTILINE
                                       )
        box_comment.Add(self.txt_comment, 1, wx.ALL | wx.EXPAND, 5)

        grdbtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        grdbtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_cancel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_save = wx.Button(self, wx.ID_OK, _("Apply"))
        grdexit.Add(self.btn_save, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_save.Disable()
        grdbtn.Add(grdexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        size_base.Add(grdbtn, 0, wx.EXPAND)
        # ------ set sizer
        self.SetMinSize((500, 450))
        self.SetSizer(size_base)
        self.Fit()
        self.Layout()

        # ----------------------Set Properties----------------------#

        idx = self.metadata[self.trackindex]
        self.txt_artist.AppendText(idx.get('PERFORMER', ''))
        self.txt_album.AppendText(idx.get('ALBUM', ''))
        self.txt_comment.AppendText(idx.get('COMMENT', ''))
        self.txt_title.AppendText(idx.get('TITLE', ''))
        self.txt_genre.AppendText(idx.get('GENRE', ''))
        self.txt_date.AppendText(str(idx.get('DATE', '')))
        self.txt_discid.AppendText(str(idx.get('DISCID', '')))

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_artist)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_album)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_comment)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_title)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_genre)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_date)
        self.Bind(wx.EVT_TEXT, self.on_text_event, self.txt_discid)

        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_save)

    # ---------------------Callback (event handler)----------------------#

    def on_text_event(self, event):
        """Set date text box"""
        if self.btn_save.IsEnabled() is False:
            self.btn_save.Enable()
            track = _("Track ({}) Audio Tag (EDITED)*"
                      ).format(self.trackindex)
            self.SetTitle(track)
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        wx.MessageBox(_("Not yet implemented"), _('Settings'),
                      wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Exit from dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Call getvalue interface
        """
        # self.Destroy() # con ID_OK e ID_CANCEL non serve
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        Return self.metadata value
        """
        if wx.MessageBox(_('Do you want to apply the new tag '
                           'properties to the selected track?\n\n'),
                         _('Please confirm'),
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.YES:

            idx = self.metadata[self.trackindex]
            idx['PERFORMER'] = self.txt_artist.GetValue()
            idx['ALBUM'] = self.txt_album.GetValue()
            idx['COMMENT'] = self.txt_comment.GetValue()
            idx['TITLE'] = self.txt_title.GetValue()
            idx['GENRE'] = self.txt_genre.GetValue()
            idx['DATE'] = self.txt_date.GetValue()
            idx['DISCID'] = self.txt_discid.GetValue()

            return self.metadata

        return None
