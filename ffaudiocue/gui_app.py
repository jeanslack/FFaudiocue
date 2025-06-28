# -*- coding: UTF-8 -*-
"""
Name: gui_app.py
Porpose: bootstrap for FFaudiocue app.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.13.2025
Code checker: flake8, pylint

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
from shutil import which
import builtins
import wx
try:
    from wx.svg import SVGimage
except ModuleNotFoundError:
    pass
from ffaudiocue.ffc_sys.argparser import arguments
from ffaudiocue.ffc_sys.settings_manager import DataSource  # data
from ffaudiocue.ffc_sys import app_const as appC
from ffaudiocue.ffc_utils.utils import del_filecontents

# add translation macro to builtin similar to what gettext does
builtins.__dict__['_'] = wx.GetTranslation


class CuesplitterGUI(wx.App):
    """
    bootstrap the wxPython GUI toolkit before
    starting the main_frame.

    """

    def __init__(self, redirect=True, filename=None, **kwargs):
        """
        - redirect=False will send print statements to a console
          window (in use)
        - redirect=True will be sent to a little textbox window.
        - filename=None Redirect sys.stdout and sys.stderr
          to a popup window.
        - filename='path/to/file.txt' Redirect sys.stdout
          and sys.stderr to file

        See main() function below to settings it.

        """
        self.locale = None
        self.appset = {'DISPLAY_SIZE': None,
                       'GETLANG': None,
                       # short name for the locale
                       'SUPP_LANGs': ['it_IT', 'en_EN', 'ru_RU'],
                       # supported help langs
                       }
        self.data = DataSource(kwargs)  # instance data
        self.appset.update(self.data.get_configuration())  # data system
        self.iconset = None

        wx.App.__init__(self, redirect, filename)  # constructor
        wx.SystemOptions.SetOption("osx.openfiledialog.always-show-types", "1")
    # -------------------------------------------------------------------

    def OnInit(self):
        """Bootstrap interface."""

        if self.appset.get('ERROR'):
            wx.MessageBox(f"FATAL: {self.appset['ERROR']}\n\nSorry, unable to "
                          f"continue..", 'FFaudiocue - ERROR',
                          wx.ICON_STOP)
            return False

        self.appset['DISPLAY_SIZE'] = wx.GetDisplaySize()  # get monitor res
        self.iconset = self.data.icons_set(self.appset['icontheme'])

        # locale
        wx.Locale.AddCatalogLookupPathPrefix(self.appset['localepath'])
        self.update_language(self.appset['locale_name'])

        if self.check_ffmpeg():
            self.wizard(self.iconset['ffaudiocue'])
            return True

        from ffaudiocue.ffc_main.main_frame import MainFrame
        main_frame = MainFrame()
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def check_ffmpeg(self):
        """
        Check the FFmpeg's executables (ffmpeg, ffprobe).
        Returns True if one of the executables is missing or if
        one of the executables doesn't have execute permission.
        Returns None otherwise.
        """
        for link in [self.appset['ffmpeg_cmd'], self.appset['ffprobe_cmd']]:
            if not which(link, mode=os.F_OK | os.X_OK, path=None):
                return True
        return None
    # -------------------------------------------------------------------

    def wizard(self, wizardicon):
        """
        Shows dialog to setup the application on initial start-up.
        """
        from ffaudiocue.ffc_dlg.wizard_dlg import Wizard
        main_frame = Wizard(wizardicon)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def update_language(self, lang=None):
        """
        Update the language to the requested one.
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes

        """
        # if an unsupported language is requested, default to English
        selectlang = appC.supLang.get(lang, wx.LANGUAGE_ENGLISH)

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selectlang[0])

        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
            self.appset['GETLANG'] = self.locale.GetName()
        else:
            self.locale = None
            self.appset['GETLANG'] = "en_US"
    # -------------------------------------------------------------------

    def OnExit(self):
        """
        OnExit provides an interface for exiting the application.
        The ideal place to run the last few things before completely
        exiting the application, eg. delete temporary files etc.
        """
        if self.appset['clearlogfiles'] is True:
            logdir = self.appset['logdir']
            if os.path.exists(logdir):
                flist = os.listdir(logdir)
                if flist:
                    for logname in flist:
                        logfile = os.path.join(logdir, logname)
                        try:
                            del_filecontents(logfile)
                        except Exception as err:
                            wx.MessageBox(_("Unexpected error while "
                                            "deleting file contents:\n\n"
                                            "{0}").format(err),
                                          'FFaudiocue - ERROR', wx.ICON_STOP)
                            return False

        if self.appset['auto-restart-app']:
            auto_restart(self.appset['app'], self.appset['make_portable'])
            return True

        return True
    # -------------------------------------------------------------------


def auto_restart(apptype, portmode):
    """
    This function spawn the same executable again, automatically
    restarting this application if required, for example after
    the wizard dialog ends or after applying settings that require
    the application to be restarted. Note that this behavior
    it is disabled using the Python interpreter (interactive
    mode).
    """
    if not ''.join(sys.argv) or sys.argv[0].startswith('-'):
        sys.exit()

    if apptype == 'pyinstaller':
        wx.Execute(f'{sys.executable}', flags=wx.EXEC_SYNC)
    else:
        makeportable = '' if not portmode else fr'--make-portable "{portmode}"'

        if os.path.basename(sys.argv[0]) == 'launcher':
            cmdargs = f'{sys.executable} {sys.argv[0]} {makeportable}'
        else:
            cmdargs = f'{sys.argv[0]} {makeportable}'
        wx.Execute(f'{cmdargs}', flags=wx.EXEC_SYNC)


def main():
    """
    Without arguments starts the wx.App mainloop
    instead to print output to console.
    """
    if not sys.argv[1:]:
        kwargs = {'make_portable': None}
    else:
        kwargs = arguments()

    app = CuesplitterGUI(redirect=False, **kwargs)
    app.MainLoop()
