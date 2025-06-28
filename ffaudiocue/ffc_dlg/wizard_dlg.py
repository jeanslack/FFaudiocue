# -*- coding: UTF-8 -*-
"""
Name: wizard_dlg.py
Porpose: wizard setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.13.2025
Code checker: flake8, pylint
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
import wx
from ffaudiocue.ffc_utils.utils import detect_binaries
from ffaudiocue.ffc_sys.settings_manager import ConfigManager


def write_changes(ffmpeg, ffprobe, binfound):
    """
    Writes changes to the configuration file

    """
    get = wx.GetApp()
    appdata = get.appset
    conf = ConfigManager(appdata['fileconfpath'])
    dataread = conf.read_options()
    dataread['ffmpeg_cmd'] = ffmpeg
    dataread['ffprobe_cmd'] = ffprobe
    # local = False if binfound == 'system' else True
    local = not binfound == 'system'
    dataread['ffmpeg_islocal'] = local
    dataread['ffprobe_islocal'] = local
    conf.write_options(**dataread)


class PageOne(wx.Panel):
    """
    This is a first panel displayed on Wizard dialog box

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    MSG2 = _("Please take a moment to set up the application")
    MSG3 = _('Click the "Next" button to get started')

    def __init__(self, parent, icon):
        """
        constructor
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.Bitmap(icon, wx.BITMAP_TYPE_ANY)
        img = bitmap.ConvertToImage()
        img = img.Scale(64, 64, wx.IMAGE_QUALITY_NORMAL)
        img = img.ConvertToBitmap()
        bitmap_vdms = wx.StaticBitmap(self, wx.ID_ANY, img)
        lab1 = wx.StaticText(self, wx.ID_ANY,
                             _("Welcome to the FFaudiocue Wizard!"))
        lab2 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG2,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab3 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG3,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)

        if PageOne.OS == 'Darwin':
            lab1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(13, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(11, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 80), 0)
        sizer_base.Add(bitmap_vdms, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab1, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab3, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 80), 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()


class PageTwo(wx.Panel):
    """
    Shows panel wizard to locate FFmpeg executables
    and set the Wizard attributes on parent.

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    GETPATH = get.appset['getpath']
    FFMPEG_LOCALDIR = get.appset['FFMPEG_DIR']

    MSG0 = _('FFaudiocue is an application based on FFmpeg\n')

    MSG1 = (_('If FFmpeg is not on your computer, this application '
              'will be unusable'))

    MSG2 = (_('If you have already installed FFmpeg on your operating\n'
              'system, click the "Auto-detection" button.'))

    MSG3 = (_('If you want to use a version of FFmpeg located on your\n'
              'filesystem but not installed on your operating system,\n'
              'click the "Locate" button.'))

    def __init__(self, parent):
        """
        constructor
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        self.parent = parent

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_text = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG0,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG1,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        lab2 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG2)
        lab3 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG3)
        self.detect_btn = wx.Button(self, wx.ID_ANY, _("Auto-detection"),
                                    size=(250, -1))
        self.locate_btn = wx.Button(self, wx.ID_ANY, _("Locate"),
                                    size=(250, -1))
        self.lab_ff_path = wx.StaticText(self, wx.ID_ANY, "",
                                         style=wx.ST_ELLIPSIZE_END
                                         | wx.ALIGN_CENTRE_HORIZONTAL
                                         )
        if PageTwo.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            self.lab_ff_path.SetFont(wx.Font(13, wx.MODERN,
                                             wx.NORMAL, wx.BOLD, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            self.lab_ff_path.SetFont(wx.Font(10, wx.MODERN,
                                             wx.NORMAL, wx.BOLD, 0, ""))
        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        # sizer_base.Add((0, 5), 0)
        sizer_base.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(sizer_text, 0, wx.CENTER)
        sizer_text.Add(lab2, 0, wx.EXPAND)
        sizer_text.Add((0, 15), 0)
        sizer_text.Add(lab3, 0, wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(self.detect_btn, 0, wx.CENTER)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(self.locate_btn, 0, wx.CENTER)
        sizer_base.Add((0, 25), 0)
        sizer_base.Add(self.lab_ff_path, 0, wx.CENTER | wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # bindings
        self.Bind(wx.EVT_BUTTON, self.detectbin, self.detect_btn)
        self.Bind(wx.EVT_BUTTON, self.locate, self.locate_btn)
    # -------------------------------------------------------------------#

    def locate(self, event):
        """
        The user browse manually to find ffmpeg, ffprobe,
        ffplay executables

        """
        self.parent.btn_next.Enable()
        self.locate_btn.Disable()
        self.detect_btn.Enable()
        self.lab_ff_path.SetLabel(_('Click the "Next" button'))
        self.Layout()
    # -------------------------------------------------------------------#

    def detectbin(self, event):
        """
        The user push the auto-detect button to automatically
        detect ffmpeg, ffprobe and ffplay on the O.S.

        """
        if PageTwo.OS == 'Windows':
            executable = ('ffmpeg.exe', 'ffprobe.exe')
        else:
            executable = ('ffmpeg', 'ffprobe')

        exiting = None
        path = []
        for exe in executable:
            status = detect_binaries(exe, PageTwo.FFMPEG_LOCALDIR)

            if status[0] == 'not installed':
                wx.MessageBox(_("'{}' is not installed on your computer. "
                                "Install it or indicate another location by "
                                "clicking the 'Locate' button.").format(exe),
                              'FFaudiocue - Warning', wx.ICON_EXCLAMATION, self)
                return

            if status[0] == 'provided':
                exiting = status[0]
                path.append(status[1])

            elif not status[0]:
                path.append(status[1])

        if exiting == 'provided':
            if wx.MessageBox(_("FFaudiocue already seems to include "
                               "FFmpeg.\n\nDo you want to use that?"),
                             _('FFaudiocue - Confirm'), wx.ICON_QUESTION
                             | wx.YES_NO, self) == wx.NO:
                return

        self.parent.ffmpeg = PageTwo.GETPATH(path[0])
        self.parent.ffprobe = PageTwo.GETPATH(path[1])
        self.parent.btn_next.Enable()
        self.detect_btn.Disable()
        self.locate_btn.Enable()
        self.lab_ff_path.SetLabel(f'...Found: "{PageTwo.GETPATH(path[0])}"')
        self.Layout()


class PageThree(wx.Panel):
    """
    Shows panel to locate manually ffmpeg, ffprobe,
    and ffplay executables and set attributes on parent.

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    GETPATH = get.appset['getpath']

    MSG0 = _('Locating FFmpeg executables\n')

    MSG1 = (_('"ffmpeg" and "ffprobe" are required. Complete all\n'
              'the text boxes below by clicking on the respective buttons.'))

    def __init__(self, parent):
        """
        constructor
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        self.parent = parent

        if PageTwo.OS == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_text = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG0,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG1)
        #  ffmpeg
        gridffmpeg = wx.BoxSizer(wx.HORIZONTAL)
        self.ffmpeg_txt = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_READONLY)
        gridffmpeg.Add(self.ffmpeg_txt, 1, wx.ALL, 5)

        self.ffmpeg_btn = wx.Button(self, wx.ID_ANY, "ffmpeg")
        gridffmpeg.Add(self.ffmpeg_btn, 0, wx.RIGHT | wx.CENTER, 5)
        #  ffprobe
        gridffprobe = wx.BoxSizer(wx.HORIZONTAL)
        self.ffprobe_txt = wx.TextCtrl(self, wx.ID_ANY, "",
                                       style=wx.TE_READONLY)
        gridffprobe.Add(self.ffprobe_txt, 1, wx.ALL, 5)

        self.ffprobe_btn = wx.Button(self, wx.ID_ANY, "ffprobe")
        gridffprobe.Add(self.ffprobe_btn, 0, wx.RIGHT | wx.CENTER, 5)

        if PageThree.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(sizer_text, 0, wx.CENTER)
        sizer_text.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(gridffmpeg, 0, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(gridffprobe, 0, wx.ALL | wx.EXPAND, 5)
        # sizer_base.Add((0, 5), 0)
        # sizer_base.Add(gridffplay, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # bindings
        self.Bind(wx.EVT_BUTTON, self.on_ffmpeg, self.ffmpeg_btn)
        self.Bind(wx.EVT_BUTTON, self.on_ffprobe, self.ffprobe_btn)

    def on_ffmpeg(self, event):
        """
        Open filedialog to locate ffmpeg executable
        """
        with wx.FileDialog(self, _("{} location").format(self.ffmpeg),
                           "", "", "ffmpeg binary "
                           f"(*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffmpeg:
                    self.ffmpeg_txt.Clear()
                    ffmpegpath = PageThree.GETPATH(dlgfile.GetPath())
                    self.ffmpeg_txt.write(ffmpegpath)
                    self.parent.ffmpeg = ffmpegpath

    def on_ffprobe(self, event):
        """
        Open filedialog to locate ffprobe executable
        """
        with wx.FileDialog(self, _("{} location").format(self.ffprobe),
                           "", "", "ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffprobe:
                    self.ffprobe_txt.Clear()
                    ffprobepath = PageThree.GETPATH(dlgfile.GetPath())
                    self.ffprobe_txt.write(ffprobepath)
                    self.parent.ffprobe = ffprobepath


class PageFinish(wx.Panel):
    """
    This is last panel to show during wizard session

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    MSG0 = _("Wizard completed successfully!\n")
    MSG1 = (_("Remember that you can always change these settings "
              "later, through the Setup dialog."))
    MSG3 = _("Thank You!")
    MSG2 = _('To exit click the "Finish" button')

    def __init__(self, parent):
        """
        constructor
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG0,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG1,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab2 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG2,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab3 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG3,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        if PageFinish.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab1.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab1.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 120), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab3, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()


class Wizard(wx.Dialog):
    """
    Provides a multi-panel dialog box (dynamic wizard)
    for configuring FFaudiocue during the startup.

    """
    def __init__(self, prg_icon):
        """
        Note that the attributes of ffmpeg are set in the "PageTwo"
        and "PageThree" panels. The other values are obtained with
        the `wizard_finished` method and not on the panels

        """
        self.ffmpeg = None
        self.ffprobe = None

        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER)
        main_sizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        self.page_one = PageOne(self, prg_icon)  # start...
        self.page_two = PageTwo(self)  # choose ffmpeg modality
        self.page_three = PageThree(self)  # browse for ffmpeg binaries
        self.page_finished = PageFinish(self)  # ...end
        #  hide panels
        self.page_two.Hide()
        self.page_three.Hide()
        self.page_finished.Hide()
        #  adds panels to sizer
        main_sizer.Add(self.page_one, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.page_two, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.page_three, 1, wx.ALL | wx.EXPAND, 5)

        main_sizer.Add(self.page_finished, 1, wx.ALL | wx.EXPAND, 5)
        # bottom side layout
        grid_btns = wx.GridSizer(1, 2, 0, 0)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        grid_btns.Add(btn_cancel, 0)
        gridchoices = wx.GridSizer(1, 2, 0, 5)
        self.btn_back = wx.Button(self, wx.ID_ANY, _("< Previous"))
        self.btn_back.Disable()
        gridchoices.Add(self.btn_back, 0, wx.EXPAND)
        self.btn_next = wx.Button(self, wx.ID_ANY, _("Next >"))
        gridchoices.Add(self.btn_next, 0, wx.EXPAND)
        grid_btns.Add(gridchoices, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        main_sizer.Add(grid_btns, 0, wx.ALL | wx.EXPAND, 5)
        #  properties
        self.SetTitle(_("FFaudiocue Wizard"))
        self.SetMinSize((700, 500))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(prg_icon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetSizer(main_sizer)
        self.Fit()
        self.Layout()

        #  bindings
        self.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_back, self.btn_back)
        self.Bind(wx.EVT_BUTTON, self.on_next, self.btn_next)
        self.Bind(wx.EVT_CLOSE, self.on_cancel)  # controlla la chiusura (x)

    # events:
    def on_cancel(self, event):
        """
        Destroy app
        """
        self.Destroy()
    # -------------------------------------------------------------------#

    def on_next(self, event):
        """
        Set the panels to show when the 'Next'
        button is clicked

        """
        if self.btn_next.GetLabel() == _('Finish'):
            self.wizard_finished()

        if self.page_one.IsShown():
            self.page_one.Hide()
            self.page_two.Show()
            self.btn_back.Enable()

            if (self.page_two.locate_btn.IsEnabled()
                    and self.page_two.detect_btn.IsEnabled()):
                self.btn_next.Disable()

        elif self.page_two.IsShown():

            if not self.page_two.locate_btn.IsEnabled():
                self.page_two.Hide()
                self.page_three.Show()
            else:
                self.page_two.Hide()
                self.page_finished.Show()
                self.btn_next.SetLabel(_('Finish'))

        elif self.page_three.IsShown():
            if (self.page_three.ffmpeg_txt.GetValue()
                    and self.page_three.ffprobe_txt.GetValue()):
                self.page_three.Hide()
                self.page_finished.Show()
                self.btn_next.SetLabel(_('Finish'))
            else:
                wx.MessageBox(_("Some text boxes are still incomplete"),
                              ("FFaudiocue - Information"),
                              wx.ICON_INFORMATION, self)

        self.Layout()
    # -------------------------------------------------------------------#

    def on_back(self, event):
        """
        Set the panels to show when the 'Previous'
        button is clicked

        """
        if self.page_two.IsShown():
            self.page_two.Hide()
            self.page_one.Show()
            self.btn_back.Disable()
            self.btn_next.Enable()

        elif self.page_three.IsShown():
            self.page_three.Hide()
            self.page_two.Show()

        elif self.page_finished.IsShown():
            self.btn_next.SetLabel(_('Next >'))
            if self.page_two.locate_btn.IsEnabled():
                self.page_finished.Hide()
                self.page_two.Show()
            else:
                self.page_finished.Hide()
                self.page_three.Show()

        self.Layout()
    # -------------------------------------------------------------------#

    def wizard_finished(self):
        """
        Get all settings and call `write_changes`
        to applies changes.

        """
        if not self.page_two.locate_btn.IsEnabled():
            binfound = 'local'
        else:
            # this if not self.page_two.detect_btn.IsEnabled()
            binfound = 'system'

        write_changes(self.ffmpeg,
                      self.ffprobe,
                      binfound
                      )
        get = wx.GetApp()
        appdata = get.appset
        appdata['auto-restart-app'] = True
        self.Destroy()
