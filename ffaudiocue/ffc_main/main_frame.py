# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.15.2025
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
import sys
import webbrowser
import wx
from pubsub import pub
from ffaudiocue.ffc_utils.get_bmpfromsvg import get_bmp
from ffaudiocue.ffc_dlg import preferences
from ffaudiocue.ffc_dlg import infoprg
from ffaudiocue.ffc_dlg.cd_info import CdInfo
from ffaudiocue.ffc_dlg.track_info import TrackInfo
from ffaudiocue.ffc_dlg import check_new_version
from ffaudiocue.ffc_dlg.showlogs import ShowLogs
from ffaudiocue.ffc_panels import cuesplitter_panel
from ffaudiocue.ffc_inout import io_tools
from ffaudiocue.ffc_sys.about_app import VERSION
from ffaudiocue.ffc_sys.settings_manager import ConfigManager


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
        self.showlogs = False
        self.cdinfo = False

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- others panel instances:
        self.gui_panel = cuesplitter_panel.CueGui(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # Layout externals panels:
        self.main_sizer.Add(self.gui_panel, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("FFaudiocue")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['ffaudiocue'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((550, 450))
        # self.CentreOnScreen()  # se lo usi, usa CentreOnScreen anziche Centre
        self.SetSizer(self.main_sizer)
        self.Fit()
        self.SetSize(tuple(self.appdata['main_window_size']))
        self.Move(tuple(self.appdata['main_window_pos']))

        # menu bar
        self.frame_menu_bar()
        # tool bar main
        self.frame_tool_bar()
        # status bar
        self.sbar = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'))
        self.Layout()
        # ---------------------- Binding (EVT) -----------------------
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # ------------------------------------------------------------
        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_WINDOWS")

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, bgrd=None, fgrd=None):
        """
        Set the status-bar message and color.
        Note that These methods don't always work on every platform.
        Usage:
            - self.statusbar_msg(_('...Finished'))  # no color
            - self.statusbar_msg(_('...Finished'),
                                 bgrd=colr,
                                 fgrd=color)  # with colors
        bgrd: background color
        fgrd: foreground color

        """
        if self.appdata['ostype'] == 'Linux':
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
    # ------------------------------------------------------------------#

    def check_modeless_window(self, msg=None):
        """
        Receives a message from a modeless window close event.
        This method is called using pub/sub protocol subscribing
        "DESTROY_ORPHANED_WINDOWS".
        """
        if msg == 'ShowLogs':
            self.showlogs.Destroy()
            self.showlogs = False
        elif msg == 'CdInfo':
            self.cdinfo.Destroy()
            self.cdinfo = False
    # ------------------------------------------------------------------#

    def destroy_orphaned_window(self):
        """
        Destroys all orphaned modeless windows, ie. on
        application exit or on opening or deleting files.
        """
        if self.showlogs:
            self.showlogs.Destroy()
            self.showlogs = False
        if self.cdinfo:
            self.cdinfo.Destroy()
            self.cdinfo = False
    # ---------------------- Event handler (callback) ------------------#

    def write_option_before_exit(self):
        """
        Write user settings to the configuration file
        before exit the application.
        """
        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        sett['main_window_size'] = list(self.GetSize())
        sett['main_window_pos'] = list(self.GetPosition())
        confmanager.write_options(**sett)
    # ------------------------------------------------------------------#

    def destroy_application(self):
        """
        Permanent exit from the application.
        Do not use this method directly.
        """
        self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        This method is called after from the `main_setup_dlg()` method.
        """
        if self.gui_panel.thread_type is not None:
            wx.MessageBox(_("There are still active windows with running "
                            "processes, make sure you finish your work "
                            "before exit."),
                          _('FFaudiocue - Warning'), wx.ICON_WARNING, self)
            self.appdata['auto-restart-app'] = False
            return

        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Application exit request given by the user.
        """
        if self.gui_panel.thread_type is not None:
            wx.MessageBox(_("There are still active windows with running "
                            "processes, make sure you finish your work "
                            "before exit."),
                          _('FFaudiocue - Warning'), wx.ICON_WARNING, self)
            return

        if self.appdata['warnexiting']:
            if wx.MessageBox(_('Are you sure you want to exit '
                               'the application?'),
                             _('FFaudiocue - Confirm'), wx.ICON_QUESTION
                             | wx.CANCEL
                             | wx.YES_NO, self) != wx.YES:
                return

        self.write_option_before_exit()
        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

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
        fileButton = wx.Menu()
        dscrp = (_("Open...\tCtrl+O"),
                 _("Open an existing CUE file"))
        fold_cue = fileButton.Append(wx.ID_FILE, dscrp[0], dscrp[1])
        dscrp = (_("Reload\tF5"),
                 _("Reload current CUE file from disk"))
        self.restoretag = fileButton.Append(wx.ID_REFRESH, dscrp[0], dscrp[1])
        self.restoretag.Enable(False)

        fileButton.AppendSeparator()
        dscrp = (_("Open output folder\tCtrl+A"),
                 _("Open the current audio folder"))
        fold_convers = fileButton.Append(wx.ID_OPEN, dscrp[0], dscrp[1])

        fileButton.AppendSeparator()
        dscrp = (_("Work Notes\tCtrl+N"),
                 _("Read or write your reminders."))
        notepad = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        fileButton.AppendSeparator()
        exititem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Quit application"))
        self.menu_bar.Append(fileButton, _("File"))

        self.Bind(wx.EVT_MENU, self.opencue, fold_cue)
        self.Bind(wx.EVT_MENU, self.restore_cuefile, self.restoretag)
        self.Bind(wx.EVT_MENU, self.open_myfiles, fold_convers)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        self.Bind(wx.EVT_MENU, self.on_close, exititem)

        # ------------------ Edit menu
        editButton = wx.Menu()
        self.setupItem = editButton.Append(wx.ID_PREFERENCES,
                                           _("Preferences\tCtrl+P"),
                                           _("Application preferences"))
        self.menu_bar.Append(editButton, _("Edit"))

        self.Bind(wx.EVT_MENU, self.on_setup, self.setupItem)

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
                 _("Checks for the latest FFaudiocue version at "
                   "<https://github.com/jeanslack/FFaudiocue>"))
        checkitem = help_button.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        help_button.AppendSeparator()
        spons = help_button.Append(wx.ID_ANY, _("Sponsor this project"), "")
        donat = help_button.Append(wx.ID_ANY, _("Donate"), "")
        help_button.AppendSeparator()
        infoitem = help_button.Append(wx.ID_ABOUT,
                                      _("About FFaudiocue"), "")
        self.menu_bar.Append(help_button, _("Help"))

        self.Bind(wx.EVT_MENU, self.help_me, helpitem)
        self.Bind(wx.EVT_MENU, self.wiki, wikiitem)
        self.Bind(wx.EVT_MENU, self.issues, issueitem)
        self.Bind(wx.EVT_MENU, self.doc_ffmpeg, docffmpeg)
        self.Bind(wx.EVT_MENU, self.check_new_releases, checkitem)

        self.Bind(wx.EVT_MENU, self.sponsor_this_project, spons)
        self.Bind(wx.EVT_MENU, self.donate_to_dev, donat)

        self.Bind(wx.EVT_MENU, self.show_infoprog, infoitem)

        # --------------------------- Set items
        self.SetMenuBar(self.menu_bar)

    # --------Menu Bar Event handler (callback)
    # --------- Menu  Files

    def open_myfiles(self, event):
        """
        Open the conversions folder with file manager

        """
        io_tools.openpath(self.appdata['destination'])
    # -------------------------------------------------------------------#

    def opencue(self, event):
        """
        Open CUE sheet
        """
        self.gui_panel.on_import_cuefile(self)
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
                              'FFaudiocue - Error', wx.ICON_ERROR, self)
            else:
                io_tools.openpath(fname)
    # ------------------------------------------------------------------#
    # --------- Menu Help  ###

    def help_me(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://github.com/jeanslack/ffaudiocue'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def wiki(self, event):
        """wiki page """

        page = 'https://github.com/jeanslack/FFaudiocue/wiki'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def issues(self, event):
        """Display issues page on github"""
        page = 'https://github.com/jeanslack/ffaudiocue/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def doc_ffmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
    # -------------------------------------------------------------------#

    def check_new_releases(self, event):
        """
        Compare the FFaudiocue version with a given
        new version found on github.
        """
        this = VERSION  # this version
        url = ("https://api.github.com/repos/jeanslack/"
               "FFaudiocue/releases/latest")

        vers = io_tools.get_github_releases(url, "tag_name")
        if vers[0] in ['request error:', 'response error:']:
            if str(vers[1]) == "'tag_name'":
                msg = _('No publications found!\nERROR: tag_name')
                dlg = check_new_version.CheckNewVersion(self, msg, VERSION,
                                                        VERSION)
                dlg.ShowModal()
                return
            wx.MessageBox(f"{vers[0]} {vers[1]}", f"{vers[0]}",
                          wx.ICON_ERROR, self)
            return

        vers = vers[0].split('v')[1]
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

    def sponsor_this_project(self, event):
        """Go to sponsor page"""
        page = 'https://github.com/sponsors/jeanslack'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def donate_to_dev(self, event):
        """Go to donation page"""
        page = 'https://www.paypal.me/GPernigotto'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def show_infoprog(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info_gui(self, self.icons['ffaudiocue'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def get_toolbar_pos(self):
        """
        Get toolbar position properties according to
        the user preferences.
        """
        if self.appdata['toolbarpos'] == 0:  # on top
            return wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL

        if self.appdata['toolbarpos'] == 1:  # on bottom
            return wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM

        if self.appdata['toolbarpos'] == 2:  # on right
            return wx.TB_TEXT | wx.TB_RIGHT

        if self.appdata['toolbarpos'] == 3:
            return wx.TB_TEXT | wx.TB_LEFT

        return None
    # ------------------------------------------------------------------#

    def frame_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.

            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        style = self.get_toolbar_pos()
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
        self.btn_trackinfo = self.toolbar.AddTool(14, _('Tag'),
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
        btn_setup = self.toolbar.AddTool(5, _('Preferences'),
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
        if self.cdinfo:
            self.cdinfo.Raise()
            return

        self.cdinfo = CdInfo(self,
                             self.gui_panel.data.cue.meta.data,
                             self.gui_panel.data.probedata,
                             self.gui_panel.txt_path_cue.GetValue(),
                             self.gui_panel.data.chars_enc
                             )
        self.cdinfo.Show()
    # ------------------------------------------------------------------#

    def on_track_info(self, event):
        """
        Call track info dialog
        """
        index = self.gui_panel.tracklist.GetFocusedItem()
        with TrackInfo(self,
                       self.gui_panel.author,
                       self.gui_panel.album,
                       self.gui_panel.data.audiotracks,
                       index
                       ) as trackinfo:

            if trackinfo.ShowModal() == wx.ID_OK:
                data = trackinfo.getvalue()
                if data:
                    self.gui_panel.author = data[0]
                    self.gui_panel.album = data[1]
                    self.gui_panel.data.audiotracks = data[2]
                    self.gui_panel.set_data_list_ctrl()
    # -------------------------------------------------------------------#

    def restore_cuefile(self, event):
        """
        Reload cue file resetting all data to default
        """
        self.gui_panel.on_import_cuefile(self, loadlast=True)
    # -------------------------------------------------------------------#

    def on_setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on FFaudiocue, being need
        to get the return code from getvalue interface.
        """
        msg = _("Some changes require restarting the application.")
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                changes = set_up.getvalue()
                self.gui_panel.txt_out.SetValue(self.appdata['destination'])
                if [x for x in changes if x is False]:
                    if wx.MessageBox(_("{0}\n\nDo you want to restart "
                                       "the application now?").format(msg),
                                     _('FFaudiocue - Confirm'),
                                     wx.ICON_QUESTION
                                     | wx.CANCEL
                                     | wx.YES_NO, self) == wx.YES:
                        self.appdata['auto-restart-app'] = True
                        self.on_Kill()
    # -------------------------------------------------------------------#

    def on_log(self, event):
        """
        Show log files dialog
        """
        if self.showlogs:
            self.showlogs.Raise()
            return

        self.showlogs = ShowLogs(self, self.appdata['logdir'])
        self.showlogs.Show()
    # ------------------------------------------------------------------#
