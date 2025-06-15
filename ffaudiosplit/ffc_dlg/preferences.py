# -*- coding: UTF-8 -*-
"""
Name: preferences.py
Porpose: FFaudiosplit setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.15.2025
Code checker: flake8, pylint
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
import os
import sys
import wx
from ffaudiosplit.ffc_sys.app_const import supLang
from ffaudiosplit.ffc_utils.utils import detect_binaries
from ffaudiosplit.ffc_sys.settings_manager import ConfigManager
from ffaudiosplit.ffc_inout import io_tools


class SetUp(wx.Dialog):
    """
    Represents settings and configuration
    storing of the program.

    """
    FFMPEG_LOGLEV = (("error (Show all errors)"),
                     ("warning (Show all warnings and errors)"),
                     ("info (Show informative messages during processing)"),
                     ("verbose (Same as `info`, except more verbose.)"),
                     ("debug (Show everything, including debugging info.)")
                     )
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) settings already loaded from main_frame .
        self.confmanager: instance to ConfigManager class
        self.settings: (dict) current user settings from file conf.
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.settings = self.confmanager.read_options()
        self.retcode = None

        if self.appdata['ostype'] == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tab_one = wx.Panel(notebook, wx.ID_ANY)
        sizer_gen = wx.BoxSizer(wx.VERTICAL)
        sizer_gen.Add((0, 15))
        self.ckbx_logclear = wx.CheckBox(tab_one, wx.ID_ANY,
                                         (_("Delete the contents of the log "
                                            "files\nwhen exiting the "
                                            "application")))
        sizer_gen.Add(self.ckbx_logclear, 0, wx.ALL, 5)
        sizer_gen.Add((0, 15))
        self.ckbx_exit = wx.CheckBox(tab_one, wx.ID_ANY, (_("Warn on exit")))
        sizer_gen.Add(self.ckbx_exit, 0, wx.ALL, 5)

        sizer_gen.Add((0, 15))
        self.ckbx_mnhiden = wx.CheckBox(tab_one, wx.ID_ANY,
                                        (_("Show hidden menu items")))
        sizer_gen.Add(self.ckbx_mnhiden, 0, wx.ALL, 5)

        tab_one.SetSizer(sizer_gen)
        notebook.AddPage(tab_one, _("General"))

        # -----tab 2
        tab_two = wx.Panel(notebook, wx.ID_ANY)
        sizer_files = wx.BoxSizer(wx.VERTICAL)
        sizer_files.Add((0, 15))
        msg = _("Where do you prefer to save your files?")
        labfile = wx.StaticText(tab_two, wx.ID_ANY, msg)
        sizer_files.Add(labfile, 0, wx.ALL | wx.EXPAND, 5)
        sizeffdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizer_files.Add(sizeffdirdest, 0, wx.EXPAND)
        self.txt_outdir = wx.TextCtrl(tab_two, wx.ID_ANY, "",
                                      style=wx.TE_READONLY
                                      )
        sizeffdirdest.Add(self.txt_outdir, 1, wx.ALL, 5)
        self.txt_outdir.AppendText(self.appdata['destination'])

        self.btn_outdir = wx.Button(tab_two, wx.ID_ANY, _("Change"))
        sizeffdirdest.Add(self.btn_outdir, 0, wx.RIGHT
                          | wx.ALIGN_CENTER_VERTICAL
                          | wx.ALIGN_CENTER_HORIZONTAL, 5
                          )
        # sizer_files.Add((0, 15))
        tab_two.SetSizer(sizer_files)
        notebook.AddPage(tab_two, _("File"))

        # -----tab 3
        tab_three = wx.Panel(notebook, wx.ID_ANY)
        sizer_ffmpeg = wx.BoxSizer(wx.VERTICAL)
        sizer_ffmpeg.Add((0, 15))
        lab_ffexec = wx.StaticText(tab_three, wx.ID_ANY,
                                   _('Path to the executables'))
        sizer_ffmpeg.Add(lab_ffexec, 0, wx.ALL | wx.EXPAND, 5)
        # ----
        msg = _("Enable a custom location to run FFmpeg")
        self.ckbx_exe_ffmpeg = wx.CheckBox(tab_three, wx.ID_ANY, (msg))
        self.btn_loc_ffmpeg = wx.Button(tab_three, wx.ID_ANY, _("Change"))
        self.txtctrl_ffmpeg = wx.TextCtrl(tab_three, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizer_ffmpeg.Add(self.ckbx_exe_ffmpeg, 0, wx.ALL, 5)
        grid_ffmpeg = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ffmpeg.Add(grid_ffmpeg, 0, wx.EXPAND)
        grid_ffmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALL, 5)
        grid_ffmpeg.Add(self.btn_loc_ffmpeg, 0, wx.RIGHT | wx.CENTER, 5)
        # ----
        self.ckbx_exe_ffprobe = wx.CheckBox(tab_three, wx.ID_ANY,
                                            (_("Enable a custom location to "
                                               "run FFprobe")))
        self.btn_loc_ffprobe = wx.Button(tab_three, wx.ID_ANY, _("Change"))
        self.txtctrl_ffprobe = wx.TextCtrl(tab_three, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizer_ffmpeg.Add(self.ckbx_exe_ffprobe, 0, wx.ALL, 5)
        grid_ffprobe = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ffmpeg.Add(grid_ffprobe, 0, wx.EXPAND)
        grid_ffprobe.Add(self.txtctrl_ffprobe, 1, wx.ALL, 5)
        grid_ffprobe.Add(self.btn_loc_ffprobe, 0, wx.RIGHT | wx.CENTER, 5)
        # ----
        tab_three.SetSizer(sizer_ffmpeg)
        notebook.AddPage(tab_three, _("FFmpeg"))

        # -----tab 4
        tab_four = wx.Panel(notebook, wx.ID_ANY)
        sizer_appearance = wx.BoxSizer(wx.VERTICAL)
        sizer_appearance.Add((0, 10))
        msg = _('Look and Feel (requires application restart)')
        lablook = wx.StaticText(tab_four, wx.ID_ANY, msg)
        sizer_appearance.Add(lablook, 0, wx.ALL | wx.EXPAND, 5)
        sizer_appearance.Add((0, 10))
        sizericon = wx.BoxSizer(wx.HORIZONTAL)
        labTheme = wx.StaticText(tab_four, wx.ID_ANY, _('Icon themes'))
        sizericon.Add(labTheme, 0, wx.LEFT | wx.TOP, 5)
        self.cmbx_icons = wx.ComboBox(tab_four, wx.ID_ANY,
                                      choices=[("Light"),
                                               ("Dark"),
                                               ("Colored"),
                                               ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        sizericon.Add(self.cmbx_icons, 0, wx.LEFT, 5)
        sizer_appearance.Add(sizericon, 0, wx.ALL, 5)
        tbchoice = [_('At the top of window (default)'),
                    _('At the bottom of window'),
                    _('At the right of window'),
                    _('At the left of window')]
        self.rdbx_tb_pos = wx.RadioBox(tab_four, wx.ID_ANY,
                                       (_("Place the toolbar")),
                                       choices=tbchoice,
                                       majorDimension=1,
                                       style=wx.RA_SPECIFY_COLS
                                       )
        sizer_appearance.Add(self.rdbx_tb_pos, 0, wx.ALL | wx.EXPAND, 5)

        grid_tb_size = wx.FlexGridSizer(0, 2, 0, 5)
        sizer_appearance.Add(grid_tb_size, 0, wx.ALL, 5)
        lab1_appearance = wx.StaticText(tab_four, wx.ID_ANY,
                                        _('Icon size:'))
        grid_tb_size.Add(lab1_appearance, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmbx_icon_size = wx.ComboBox(tab_four, wx.ID_ANY,
                                          choices=[("16"), ("24"), ("32"),
                                                   ("64")], size=(120, -1),
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY
                                          )
        grid_tb_size.Add(self.cmbx_icon_size, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        if 'wx.svg' not in sys.modules:  # only in wx version 4.1 to up
            self.cmbx_icon_size.Disable()
            lab1_appearance.Disable()

        self.ckbx_tb_showtxt = wx.CheckBox(tab_four, wx.ID_ANY,
                                           (_("Show text on toolbar buttons")))
        sizer_appearance.Add(self.ckbx_tb_showtxt, 0, wx.ALL, 5)
        sizer_appearance.Add((0, 10))
        msg = _('Application Language (requires application restart)')
        lablang = wx.StaticText(tab_four, wx.ID_ANY, msg)
        sizer_appearance.Add(lablang, 0, wx.ALL | wx.EXPAND, 5)
        sizer_appearance.Add((0, 10))
        langs = [lang[1] for lang in supLang.values()]
        self.cmbx_lang = wx.ComboBox(tab_four, wx.ID_ANY,
                                     choices=langs,
                                     size=(-1, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        sizer_appearance.Add(self.cmbx_lang, 0, wx.ALL, 5)
        sizer_appearance.Add((0, 20))

        tab_four.SetSizer(sizer_appearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tab_four, _("Look and Language"))

        # -----tab 5
        tab_five = wx.Panel(notebook, wx.ID_ANY)
        sizer_log = wx.BoxSizer(wx.VERTICAL)
        sizer_log.Add((0, 15))
        msglog = _("The following settings affect output messages and "
                   "the log messages during transcoding processes.\n"
                   "Be careful, by changing these settings some functions "
                   "of the application may not work correctly,\n"
                   "change only if you know what you are doing.\n")
        lab_log = wx.StaticText(tab_five, wx.ID_ANY, (msglog))
        sizer_log.Add(lab_log, 0, wx.ALL, 5)
        self.rdbx_log_ffmpeg = wx.RadioBox(tab_five, wx.ID_ANY,
                                           ("Set logging level flags used "
                                            "by FFmpeg"),
                                           choices=SetUp.FFMPEG_LOGLEV,
                                           majorDimension=1,
                                           style=wx.RA_SPECIFY_COLS,
                                           )
        sizer_log.Add(self.rdbx_log_ffmpeg, 0, wx.ALL | wx.EXPAND, 5)
        tab_five.SetSizer(sizer_log)
        notebook.AddPage(tab_five, _("Logging levels"))

        # -----tab 6
        tabSix = wx.Panel(notebook, wx.ID_ANY)
        sizeradv = wx.BoxSizer(wx.VERTICAL)
        sizeradv.Add((0, 10))
        msg = _("Default application directories")
        labdirtitle = wx.StaticText(tabSix, wx.ID_ANY, msg)
        sizeradv.Add(labdirtitle, 0, wx.ALL | wx.EXPAND, 5)
        sizeradv.Add((0, 20))
        labconf = wx.StaticText(tabSix, wx.ID_ANY,
                                _('Configuration directory'))
        self.btn_conf = wx.Button(tabSix, wx.ID_ANY, "...", size=(35, -1),
                                  name='config dir')
        self.txtctrl_conf = wx.TextCtrl(tabSix, wx.ID_ANY,
                                        self.appdata['confdir'],
                                        size=(500, -1),
                                        style=wx.TE_READONLY,
                                        )
        griddefdirs = wx.FlexGridSizer(2, 3, 5, 0)
        griddefdirs.Add(labconf, 0, wx.LEFT | wx.TOP, 5)
        griddefdirs.Add(self.txtctrl_conf, 1, wx.RIGHT
                        | wx.TOP | wx.LEFT | wx.EXPAND, 5)
        griddefdirs.Add(self.btn_conf, 0, wx.RIGHT | wx.TOP, 5)
        lablog = wx.StaticText(tabSix, wx.ID_ANY, _('Log directory'))
        self.btn_log = wx.Button(tabSix, wx.ID_ANY, "...", size=(35, -1),
                                 name='log dir')
        self.txtctrl_log = wx.TextCtrl(tabSix, wx.ID_ANY,
                                       self.appdata['logdir'],
                                       size=(500, -1),
                                       style=wx.TE_READONLY,
                                       )
        griddefdirs.Add(lablog, 0, wx.LEFT | wx.TOP, 5)
        griddefdirs.Add(self.txtctrl_log, 1, wx.RIGHT
                        | wx.TOP | wx.LEFT | wx.EXPAND, 5)
        griddefdirs.Add(self.btn_log, 0, wx.RIGHT | wx.TOP, 5)
        sizeradv.Add(griddefdirs, 0, wx.LEFT | wx.EXPAND, 5)
        tabSix.SetSizer(sizeradv)
        notebook.AddPage(tabSix, _("Advanced"))

        # ------ btns bottom
        grd_btns = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grd_btns.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_cancel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        grdexit.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grd_btns.Add(grdexit, flag=wx.ALL
                     | wx.ALIGN_RIGHT
                     | wx.RIGHT,
                     border=0
                     )
        sizer_base.Add(grd_btns, 0, wx.EXPAND)
        # ------ set sizer
        self.SetMinSize((650, 550))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------#
        self.SetTitle(_("Settings"))
        # set font
        if self.appdata['ostype'] == 'Darwin':
            lablang.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labfile.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lab_ffexec.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablook.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdirtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lab_log.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lablang.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labfile.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lab_ffexec.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablook.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdirtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lab_log.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_set_lang, self.cmbx_lang)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_conf)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_log)
        self.Bind(wx.EVT_CHECKBOX, self.exit_warn, self.ckbx_exit)
        self.Bind(wx.EVT_CHECKBOX, self.clear_logs, self.ckbx_logclear)
        self.Bind(wx.EVT_CHECKBOX, self.show_hiden_menu, self.ckbx_mnhiden)

        self.Bind(wx.EVT_BUTTON, self.on_output_path, self.btn_outdir)

        self.Bind(wx.EVT_CHECKBOX, self.exec_ffmpeg, self.ckbx_exe_ffmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_loc_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exec_ffprobe, self.ckbx_exe_ffprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_loc_ffprobe)

        self.Bind(wx.EVT_COMBOBOX, self.on_iconthemes, self.cmbx_icons)
        self.Bind(wx.EVT_RADIOBOX, self.on_toolbar_pos, self.rdbx_tb_pos)
        self.Bind(wx.EVT_COMBOBOX, self.on_toolbar_size, self.cmbx_icon_size)
        self.Bind(wx.EVT_CHECKBOX, self.on_toolbar_txt, self.ckbx_tb_showtxt)

        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbx_log_ffmpeg)

        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file

        """
        if self.appdata['locale_name'] in supLang:
            lang = supLang[self.appdata['locale_name']][1]
        else:
            lang = supLang["en_US"][1]
        self.cmbx_lang.SetValue(lang)

        self.cmbx_icons.SetValue(str(self.appdata['icontheme']))
        self.cmbx_icon_size.SetValue(str(self.appdata['toolbarsize']))
        self.rdbx_tb_pos.SetSelection(int(self.appdata['toolbarpos']))

        for strs in range(self.rdbx_log_ffmpeg.GetCount()):
            if (self.appdata['ffmpegloglev'] in
               self.rdbx_log_ffmpeg.GetString(strs).split()[0]):
                self.rdbx_log_ffmpeg.SetSelection(strs)

        if self.appdata['ffmpeg_islocal'] is False:
            self.btn_loc_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.ckbx_exe_ffmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.ckbx_exe_ffmpeg.SetValue(True)

        if self.appdata['ffprobe_islocal'] is False:
            self.btn_loc_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.ckbx_exe_ffprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.ckbx_exe_ffprobe.SetValue(True)

        self.ckbx_tb_showtxt.SetValue(self.appdata['toolbartext'])
        self.ckbx_logclear.SetValue(self.appdata['clearlogfiles'])
        self.ckbx_exit.SetValue(self.appdata['warnexiting'])
        self.ckbx_mnhiden.SetValue(self.appdata['showhidenmenu'])
    # --------------------------------------------------------------------#

    def opendir(self, event):
        """
        Open the configuration folder with file manager
        """
        name = event.GetEventObject().GetName()
        if name == 'config dir':
            io_tools.openpath(self.appdata['confdir'])
        elif name == 'log dir':
            io_tools.openpath(self.appdata['logdir'])
    # -------------------------------------------------------------------#

    def on_output_path(self, event):
        """set up a custom user path for file export"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save "
                                   "exported files"), "", wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.txt_outdir.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txt_outdir.AppendText(getpath)
            self.settings['destination'] = getpath
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def logging_ffmpeg(self, event):
        """specifies loglevel type for ffmpeg"""
        logg = self.rdbx_log_ffmpeg.GetStringSelection().split()[0]
        self.settings['ffmpegloglev'] = logg
    # --------------------------------------------------------------------#

    def exec_ffmpeg(self, event):
        """Enable or disable ffmpeg local binary"""
        if self.ckbx_exe_ffmpeg.IsChecked():
            self.btn_loc_ffmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.settings['ffmpeg_islocal'] = True
        else:
            self.btn_loc_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.settings['ffmpeg_islocal'] = False

            status = detect_binaries(self.ffmpeg, self.appdata['FFMPEG_DIR'])
            if status[0] == 'not installed':
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write('Not found')
                self.settings['ffmpeg_cmd'] = ''
            else:
                self.txtctrl_ffmpeg.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffmpeg.write(getpath)
                self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""

        with wx.FileDialog(self, _("{} location").format(self.ffmpeg),
                           "", "", "ffmpeg binary "
                           f"(*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffmpeg:
                    self.txtctrl_ffmpeg.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffmpeg.write(getpath)
                    self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exec_ffprobe(self, event):
        """Enable or disable ffprobe local binary"""
        if self.ckbx_exe_ffprobe.IsChecked():
            self.btn_loc_ffprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.settings['ffprobe_islocal'] = True

        else:
            self.btn_loc_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.settings['ffprobe_islocal'] = False

            status = detect_binaries(self.ffprobe, self.appdata['FFMPEG_DIR'])
            if status[0] == 'not installed':
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write('Not found')
                self.settings['ffprobe_cmd'] = ''
            else:
                self.txtctrl_ffprobe.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffprobe.write(getpath)
                self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""

        with wx.FileDialog(self, _("{} location").format(self.ffprobe),
                           "", "", "ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffprobe:
                    self.txtctrl_ffprobe.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffprobe.write(getpath)
                    self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def on_iconthemes(self, event):
        """
        Set themes of icons
        """
        self.settings['icontheme'] = self.cmbx_icons.GetStringSelection()
    # --------------------------------------------------------------------#

    def on_toolbar_size(self, event):
        """
        Set the size of the toolbar buttons and the size of its icons
        """
        size = self.cmbx_icon_size.GetStringSelection()
        self.settings['toolbarsize'] = size
    # --------------------------------------------------------------------#

    def on_toolbar_pos(self, event):
        """
        Set toolbar position on main frame
        """
        self.settings['toolbarpos'] = self.rdbx_tb_pos.GetSelection()
    # --------------------------------------------------------------------#

    def on_toolbar_txt(self, event):
        """
        Show or hide text along toolbar buttons
        """
        if self.ckbx_tb_showtxt.IsChecked():
            self.settings['toolbartext'] = True
        else:
            self.settings['toolbartext'] = False
    # --------------------------------------------------------------------#

    def on_set_lang(self, event):
        """set application language"""
        lang = 'Default'
        for key, val in supLang.items():
            if val[1] == self.cmbx_lang.GetValue():
                lang = key
        self.settings['locale_name'] = lang
    # --------------------------------------------------------------------#

    def exit_warn(self, event):
        """
        Enable or disable the warning message before
        exiting the program
        """
        if self.ckbx_exit.IsChecked():
            self.settings['warnexiting'] = True
        else:
            self.settings['warnexiting'] = False
    # --------------------------------------------------------------------#

    def clear_logs(self, event):
        """
        if checked, set to clear all log files on exit
        """
        if self.ckbx_logclear.IsChecked():
            self.settings['clearlogfiles'] = True
        else:
            self.settings['clearlogfiles'] = False
    # --------------------------------------------------------------------#

    def show_hiden_menu(self, event):
        """
        if checked, show items menu to open log
        directory and file configuration directory
        """
        if self.ckbx_mnhiden.IsChecked():
            self.settings['showhidenmenu'] = True
        else:
            self.settings['showhidenmenu'] = False
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        wx.MessageBox(_("Not yet implemented"), _('Settings'),
                      wx.ICON_INFORMATION, self)
    # --------------------------------------------------------------------#

    def getvalue(self):
        """
        Retrives data from here before destroyng this dialog.
        See main_frame --> on_setup method
        """
        return self.retcode
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Applies all changes writing the new entries on
        `settings.json` file aka file configuration.
        """
        self.retcode = (
            self.settings['locale_name'] == self.appdata['locale_name'],
            self.settings['icontheme'] == self.appdata['icontheme'],
            self.settings['toolbarsize'] == self.appdata['toolbarsize'],
            self.settings['toolbarpos'] == self.appdata['toolbarpos'],
            self.settings['toolbartext'] == self.appdata['toolbartext'],
            self.settings['showhidenmenu'] == self.appdata['showhidenmenu'])

        self.confmanager.write_options(**self.settings)
        self.appdata.update(self.settings)

        event.Skip()
