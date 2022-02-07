# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2022/2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.04.2022
Code checker: flake8, pylint
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
import os
import sys
import webbrowser
import wx
from ffcuesplitter_gui._utils.get_bmpfromsvg import get_bmp
from ffcuesplitter_gui._dialogs import preferences
from ffcuesplitter_gui._dialogs import infoprg
from ffcuesplitter_gui._dialogs.cd_info import CdInfo
from ffcuesplitter_gui._dialogs.track_info import TrackInfo
from ffcuesplitter_gui._dialogs import check_new_version
from ffcuesplitter_gui._dialogs.showlogs import ShowLogs
from ffcuesplitter_gui._panels import cuesplitter_panel
from ffcuesplitter_gui._io import io_tools
from ffcuesplitter_gui._sys import version
from ffcuesplitter_gui._sys.settings_manager import ConfigManager


class MainFrame(wx.Frame):
    """
    This is the main frame top window
    for panels implementation.
    """
    def __init__(self):
        """
        Set constructor
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.icons = get.iconset
        # -------------------------------#
        self.outpath_ffmpeg = None  # path name for FFmpeg file destination
        self.same_destin = False  # same source FFmpeg output destination
        self.time_seq = "-ss 00:00:00.000 -t 00:00:00.000"  # FFmpeg time seq.

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- others panel instances:
        self.gui_panel = cuesplitter_panel.CueGui(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # Layout externals panels:
        self.main_sizer.Add(self.gui_panel, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("FFcuesplitter-GUI")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['ffcuesplittergui'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((500, 400))
        # self.CentreOnScreen()  # se lo usi, usa CentreOnScreen anziche Centre
        self.SetSizer(self.main_sizer)
        self.Fit()

        # menu bar
        self.frame_menu_bar()
        # tool bar main
        self.frame_tool_bar()
        # status bar
        self.sbar = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'))
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, bgrd=None, fgrd=None):
        """
        Set the status-bar message and color
        Usage:
            - self.statusbar_msg(_('...Finished'))  # no color
            - self.statusbar_msg(_('...Finished'),
                                 bgrd=colr,
                                 fgrd=color)  # with colors
        bgrd: background color
        fgrd: foreground color
        """
        if bgrd is None:
            self.sbar.SetBackgroundColour(wx.NullColour)
        else:
            self.sbar.SetBackgroundColour(bgrd)

        if fgrd is None:
            self.sbar.SetForegroundColour(wx.NullColour)
        else:
            self.sbar.SetForegroundColour(fgrd)

        self.sbar.SetStatusText(msg)
        self.sbar.Refresh()
    # ---------------------- Event handler (callback) ------------------#

    def on_close(self, event):
        """
        destroy the cuesplittergui app.;
        `thread_type` is the current thread, None otherwise.

        """
        def _setsize():
            """
            Write last panel dimension for next start if changed
            """
            if tuple(self.appdata['panel_size']) != self.GetSize():
                confmanager = ConfigManager(self.appdata['fileconfpath'])
                sett = confmanager.read_options()
                sett['panel_size'] = list(self.GetSize())
                confmanager.write_options(**sett)

        if self.gui_panel.thread_type is not None:
            if wx.MessageBox(_('There are still processes running.. if you '
                               'want to stop them, use the "Abort" button.\n\n'
                               'Do you want to kill application?'),
                             _('Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            self.on_kill()
            return

        if self.appdata['warnexiting'] is True:
            if wx.MessageBox(_('Are you sure you want to exit?'),
                             _('Exit'),  wx.ICON_QUESTION
                             | wx.YES_NO, self) == wx.YES:
                _setsize()
                self.Destroy()
        else:
            _setsize()
            self.Destroy()
    # ------------------------------------------------------------------#

    def on_kill(self):
        """
        In some cases you need to exit the application
        without any confirm dialog.
        """
        self.Destroy()

    # -------------   BUILD THE MENU BAR  ----------------###

    def frame_menu_bar(self):
        """
        Make a menu bar. Per usare la disabilitazione di un
        menu item devi
        prima settare l'attributo self sull'item interessato
        - poi lo gestisci con self.item.Enable(False) per disabilitare
        o (True) per abilitare. Se vuoi disabilitare l'intero top di
        items fai per esempio: self.menu_bar.EnableTop(6, False) per
        disabilitare la voce Help.
        """
        self.menu_bar = wx.MenuBar()

        # ----------------------- file menu
        file_button = wx.Menu()
        dscrp = (_("Open a CUE sheet...\tCtrl+C"),
                 _("Open a new CUE file"))
        fold_cue = file_button.Append(wx.ID_FILE, dscrp[0], dscrp[1])

        dscrp = (_("Open output directory\tCtrl+A"),
                 _("Open the current audio dirctory"))
        fold_convers = file_button.Append(wx.ID_OPEN, dscrp[0], dscrp[1])

        file_button.AppendSeparator()
        dscrp = (_("Work Notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = file_button.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        file_button.AppendSeparator()
        exititem = file_button.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                      _("Quit application"))
        self.menu_bar.Append(file_button, _("File"))

        self.Bind(wx.EVT_MENU, self.opencue, fold_cue)
        self.Bind(wx.EVT_MENU, self.open_myfiles, fold_convers)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        self.Bind(wx.EVT_MENU, self.quiet, exititem)

        # ------------------ Go menu
        if self.appdata['showhidenmenu'] is True:
            go_button = wx.Menu()
            dscrp = (_("Configuration Directory"),
                     _("Opens the FFcuesplitter-GUI configuration directory"))
            openconfdir = go_button.Append(wx.ID_ANY, dscrp[0], dscrp[1])
            dscrp = (_("Logs Directory"),
                     _("Opens the logs directory, if exists"))
            openlogdir = go_button.Append(wx.ID_ANY, dscrp[0], dscrp[1])
            self.menu_bar.Append(go_button, _("Goto"))

            self.Bind(wx.EVT_MENU, self.open_log_dir, openlogdir)
            self.Bind(wx.EVT_MENU, self.openconf, openconfdir)

        # ------------------ help menu
        help_button = wx.Menu()
        helpitem = help_button.Append(wx.ID_HELP, _("User Guide"), "")
        wikiitem = help_button.Append(wx.ID_ANY, _("Wiki"), "")
        help_button.AppendSeparator()
        issueitem = help_button.Append(wx.ID_ANY, _("Issue tracker"), "")
        help_button.AppendSeparator()
        docffmpeg = help_button.Append(wx.ID_ANY,
                                       _("FFmpeg documentation"), "")
        help_button.AppendSeparator()
        dscrp = (_("Check for newer version"),
                 _("Checks for the latest FFcuesplitter-GUI version at "
                   "<https://github.com/jeanslack/FFcuesplitter-GUI>"))
        checkitem = help_button.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        help_button.AppendSeparator()
        infoitem = help_button.Append(wx.ID_ABOUT,
                                      _("About FFcuesplitter-GUI"), "")
        self.menu_bar.Append(help_button, _("Help"))

        self.Bind(wx.EVT_MENU, self.help_me, helpitem)
        self.Bind(wx.EVT_MENU, self.wiki, wikiitem)
        self.Bind(wx.EVT_MENU, self.issues, issueitem)
        self.Bind(wx.EVT_MENU, self.doc_ffmpeg, docffmpeg)
        self.Bind(wx.EVT_MENU, self.check_new_releases, checkitem)
        self.Bind(wx.EVT_MENU, self.show_infoprog, infoitem)

        # --------------------------- Set items
        self.SetMenuBar(self.menu_bar)

    # --------Menu Bar Event handler (callback)
    # --------- Menu  Files

    def open_myfiles(self, event):
        """
        Open the conversions folder with file manager

        """
        io_tools.openpath(self.appdata['outputfile'])
    # -------------------------------------------------------------------#

    def opencue(self, event):
        """
        Open CUE sheet
        """
        self.gui_panel.on_import_cuefile(self)
    # -------------------------------------------------------------------#

    def quiet(self, event):
        """
        destroy the cuesplittergui.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#

    def reminder(self, event):
        """
        Call `io_tools.openpath` to open a 'user_memos.txt' file
        with default GUI text editor. If 'user_memos.txt' file does
        not exist a new empty file with the same name will be created.

        """
        fname = os.path.join(self.appdata['confdir'], 'user_memos.txt')

        if os.path.exists(fname) and os.path.isfile(fname):
            io_tools.openpath(fname)
        else:
            try:
                with open(fname, "w", encoding='utf8') as text:
                    text.write("")
            except Exception as err:
                wx.MessageBox(_("Unexpected error while creating file:\n\n"
                                "{0}").format(err),
                              'FFcuesplitter-GUI', wx.ICON_ERROR, self)
            else:
                io_tools.openpath(fname)
    # ------------------------------------------------------------------#
    # --------- Menu  Go  ###

    def open_log_dir(self, event):
        """
        Open the log directory with file manager

        """
        if not os.path.exists(self.appdata['logdir']):
            wx.MessageBox(_("There are no logs to show."),
                          "FFcuesplitter-GUI", wx.ICON_INFORMATION, self)
            return
        io_tools.openpath(self.appdata['logdir'])
    # ------------------------------------------------------------------#

    def openconf(self, event):
        """
        Open the configuration folder with file manager

        """
        io_tools.openpath(self.appdata['confdir'])
    # -------------------------------------------------------------------#
    # --------- Menu Help  ###

    def help_me(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://github.com/jeanslack/ffcuesplitter-gui'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def wiki(self, event):
        """wiki page """

        page = 'https://github.com/jeanslack/FFcuesplitter-GUI/wiki'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def issues(self, event):
        """Display issues page on github"""
        page = 'https://github.com/jeanslack/ffcuesplitter-gui/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def doc_ffmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
    # -------------------------------------------------------------------#

    def check_new_releases(self, event):
        """
        Compare the FFcuesplitter-GUI version with a given
        new version found on github.
        """
        this = version.__version__  # this version
        url = ("https://api.github.com/repos/jeanslack/"
               "FFcuesplitter-GUI/releases/latest")
        vers = io_tools.get_github_releases(url, "tag_name")

        if vers[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{vers[0]} {vers[1]}", f"{vers[0]}",
                          wx.ICON_ERROR, self)
            return

        vers = vers[0].split('v.')[1]
        newmajor, newminor, newmicro = vers.split('.')
        new_vers = int(f'{newmajor}{newminor}{newmicro}')
        major, minor, micro = this.split('.')
        this_vers = int(f'{major}{minor}{micro}')

        if new_vers > this_vers:
            msg = _('A new release is available - '
                    'v.{0}\n').format(vers)
        elif this_vers > new_vers:
            msg = _('You are using a development version '
                    'that has not yet been released!\n')
        else:
            msg = _('Congratulation! You are already '
                    'using the latest version.\n')

        dlg = check_new_version.CheckNewVersion(self, msg, vers, this)
        dlg.ShowModal()
    # -------------------------------------------------------------------#

    def show_infoprog(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info_gui(self, self.icons['ffcuesplittergui'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def frame_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.

            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        if self.appdata['toolbarpos'] == 0:  # on top
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL)
            else:
                style = (wx.TB_DEFAULT_STYLE)

        elif self.appdata['toolbarpos'] == 1:  # on bottom
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_BOTTOM)

        elif self.appdata['toolbarpos'] == 2:  # on right
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_RIGHT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_RIGHT)

        elif self.appdata['toolbarpos'] == 3:
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_LEFT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_LEFT)

        self.toolbar = self.CreateToolBar(style=style)

        bmp_size = (int(self.appdata['toolbarsize']),
                    int(self.appdata['toolbarsize']))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up

            bmplog = get_bmp(self.icons['log'], bmp_size)
            bmpsetup = get_bmp(self.icons['setup'], bmp_size)
            bmpcdinfo = get_bmp(self.icons['CDinfo'], bmp_size)
            bmptrkinfo = get_bmp(self.icons['trackinfo'], bmp_size)
            bmpsplit = get_bmp(self.icons['startsplit'], bmp_size)
            bmpstop = get_bmp(self.icons['stop'], bmp_size)

        else:
            bmplog = wx.Bitmap(self.icons['log'], wx.BITMAP_TYPE_ANY)
            bmpsetup = wx.Bitmap(self.icons['setup'],
                                 wx.BITMAP_TYPE_ANY)
            bmpcdinfo = wx.Bitmap(self.icons['CDinfo'],
                                  wx.BITMAP_TYPE_ANY)
            bmptrkinfo = wx.Bitmap(self.icons['trackinfo'],
                                   wx.BITMAP_TYPE_ANY)
            bmpsplit = wx.Bitmap(self.icons['startsplit'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(8,
                                     wx.DEFAULT,
                                     wx.NORMAL,
                                     wx.NORMAL,
                                     0,
                                     ""))
        # self.toolbar.AddSeparator()
        # self.toolbar.AddStretchableSpace()
        tip = _("View or Edit selected track tag")
        self.btn_trackinfo = self.toolbar.AddTool(14, _('Track Tag'),
                                                  bmptrkinfo,
                                                  tip, wx.ITEM_NORMAL
                                                  )
        # self.toolbar.AddSeparator()
        tip = _("Audio CD informations and file properties")
        self.btn_cdinfo = self.toolbar.AddTool(8, _('Properties'),
                                               bmpcdinfo,
                                               tip, wx.ITEM_NORMAL,
                                               )
        # self.toolbar.AddStretchableSpace()
        self.toolbar.AddSeparator()
        tip = _("Start extracting audio tracks")
        self.start_splitting = self.toolbar.AddTool(12, _('Start'),
                                                    bmpsplit,
                                                    tip, wx.ITEM_NORMAL
                                                    )
        tip = _("Stop all operations")
        self.stop_splitting = self.toolbar.AddTool(13, _('Abort'),
                                                   bmpstop,
                                                   tip, wx.ITEM_NORMAL
                                                   )
        self.toolbar.AddSeparator()
        tip = _("Program setup")
        btn_setup = self.toolbar.AddTool(5, _('Settings'),
                                         bmpsetup,
                                         tip, wx.ITEM_NORMAL
                                         )
        tip = _("View logs")
        log = self.toolbar.AddTool(4, _('Logs'),
                                   bmplog,
                                   tip, wx.ITEM_NORMAL
                                   )
        # self.toolbar.AddStretchableSpace()
        # finally, create it
        self.toolbar.EnableTool(12, False)
        self.toolbar.EnableTool(13, False)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(14, False)
        # self.toolbar.EnableTool(5, False)

        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.start_splitting)
        self.Bind(wx.EVT_TOOL, self.click_stop, self.stop_splitting)
        self.Bind(wx.EVT_TOOL, self.on_log, log)
        self.Bind(wx.EVT_TOOL, self.on_cd_info, self.btn_cdinfo)
        self.Bind(wx.EVT_TOOL, self.on_track_info, self.btn_trackinfo)
        self.Bind(wx.EVT_TOOL, self.on_setup, btn_setup)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def click_stop(self, event):
        """
        The user change idea and was stop process
        """
        self.gui_panel.on_stop(self)
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        By clicking on Convert/Download buttons in the main frame,
        calls the `on_start method` of the corresponding panel shown,
        which calls the 'switch_to_processing' method above.
        """
        if self.gui_panel.IsShown():
            self.gui_panel.on_start()

    # ------------------------------------------------------------------#

    def on_cd_info(self, event):
        """
        Call CdInfo class dialog
        """
        cdinfo = CdInfo(self,
                        self.gui_panel.data.cue.meta.data,
                        self.gui_panel.data.probedata,
                        self.gui_panel.data.cue_encoding,
                        )
        cdinfo.Show()
    # ------------------------------------------------------------------#

    def on_track_info(self, event):
        """
        Call track info dialog
        """
        index = self.gui_panel.tlist.GetFocusedItem()
        with TrackInfo(self,
                       self.gui_panel.data.audiotracks,
                       index
                       ) as trackinfo:

            if trackinfo.ShowModal() == wx.ID_OK:
                data = trackinfo.getvalue()
                if data:
                    self.gui_panel.data.audiotracks = data
                    self.gui_panel.set_data_list_ctrl()
    # -------------------------------------------------------------------#

    def on_setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Videomass, being need
        to get the return code from getvalue interface.
        """
        with preferences.SetUp(self, self.appdata) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                newdata = set_up.getvalue()
                self.appdata = {**self.appdata, **newdata}
                self.gui_panel.appdata = self.appdata
                self.gui_panel.txt_out.SetValue(self.appdata['outputfile'])
    # -------------------------------------------------------------------#

    def on_log(self, event):
        """
        Show miniframe to view log files
        """
        if not os.path.exists(self.appdata['logdir']):
            wx.MessageBox(_("There are no logs to show."),
                          "FFcuesplitter-GUI", wx.ICON_INFORMATION, self)
        else:
            logdlg = ShowLogs(self, self.appdata['logdir'])
            logdlg.Show()
    # ------------------------------------------------------------------#
