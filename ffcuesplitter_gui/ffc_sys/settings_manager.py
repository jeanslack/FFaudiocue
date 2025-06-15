# -*- coding: UTF-8 -*-
"""
Name: settings_manager.py
Porpose: Set FFcuesplitter-gui configuration on startup
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.15.2025
Code checker: flake8, pylint .

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
import json
import platform


class ConfigManager:
    """
    It represents the setting of the user parameters
    of the program and the configuration file in its
    read and write fondamentals.

    Usage:

    write a new conf.json :
        >>> from settings_manager import ConfigManager
        >>> confmng = ConfigManager('fileconfpath.json')
        >>> confmng.write_options()

    read the current fileconf.json :
        >>> settings = confmng.read_options()

    example of modify data into current file conf.json:
        >>> settings['outputdir'] = '/home/user/MyVideos'
        >>> confmng.write_options(**settings)
    ------------------------------------------------------
    """
    VERSION = 4.4
    DEFAULT_OPTIONS = {"confversion": VERSION,
                       "locale_name": "Default",
                       "destination": "",
                       "ffmpeg_cmd": "",
                       "ffmpeg_islocal": False,
                       "ffmpegloglev": "info",
                       "ffprobe_cmd": "",
                       "ffprobe_islocal": False,
                       "warnexiting": True,
                       "clearlogfiles": False,
                       "icontheme": "Colored",
                       "toolbarsize": 32,
                       "toolbarpos": 2,
                       "toolbartext": True,
                       "showhidenmenu": False,
                       "main_window_size": [890, 670],
                       "main_window_pos": [0, 0],
                       }

    def __init__(self, fileconf, makeportable=None):
        """
        Expects an existing `filename` on the file system paths
        suffixed by `.json`. If `makeportable` is `True`, some
        paths on the `DEFAULT_OPTIONS` class attribute will be
        set as relative paths.
        """
        self.fileconf = fileconf
        self.makeportable = makeportable

        if self.makeportable:
            trscodepath = os.path.join(makeportable, "Album Collection")
            trscodedir = os.path.relpath(trscodepath)
            ConfigManager.DEFAULT_OPTIONS['destination'] = trscodedir
            self.destination = trscodedir
        else:
            self.destination = os.path.expanduser('~')

    def write_options(self, **options):
        """
        Writes options to configuration file. If **options is
        given, writes the new changes to filename, writes the
        DEFAULT_OPTIONS otherwise.
        """
        if options:
            set_options = options
        else:
            set_options = ConfigManager.DEFAULT_OPTIONS

        with open(self.fileconf, "w", encoding='utf-8') as settings_file:

            json.dump(set_options,
                      settings_file,
                      indent=4,
                      separators=(",", ": ")
                      )

    def read_options(self):
        """
        Reads options from the current configuration file.
        Returns: current options, `None` otherwise.
        Raise: json.JSONDecodeError
        """
        with open(self.fileconf, 'r', encoding='utf-8') as settings_file:
            try:
                options = json.load(settings_file)
            except json.JSONDecodeError:
                return None

        return options

    def default_outputdirs(self, **options):
        """
        This method is useful for restoring a consistent output
        directory for file destinations, in case they were previously
        set to physically non-existent file system paths (such as
        pendrives, hard drives, etc.) or to deleted directories.
        Returns a dict object.
        """
        path = options['destination']
        if not os.path.exists(path) and not os.path.isdir(path):
            if self.makeportable:
                options['destination'] = self.destination
            else:
                options['destination'] = f"{os.path.expanduser('~')}"

        return options


def get_options(fileconf, makeportable):
    """
    Check the application options. Reads the `settings.json`
    file; if it does not exist or is unreadable try to restore
    it. If VERSION is not the same as the version readed, it adds
    new missing items while preserving the old ones with the same
    values.

    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    conf = ConfigManager(fileconf, makeportable)
    version = ConfigManager.VERSION

    if os.path.isfile(fileconf):
        data = {'R': conf.read_options()}
        if not data['R']:
            conf.write_options()
            data = {'R': conf.read_options()}
        if float(data['R']['confversion']) != version:  # conf version
            data['R']['confversion'] = version
            new = ConfigManager.DEFAULT_OPTIONS  # model
            data = {'R': {**new, **data['R']}}
            conf.write_options(**data['R'])
    else:
        conf.write_options()
        data = {'R': conf.read_options()}

    diff = conf.default_outputdirs(**data['R'])
    if diff != data['R']:
        conf.write_options(**diff)  # write default outputdirs
        data = {'R': conf.read_options()}

    return data
# --------------------------------------------------------------------------


def msg(arg):
    """
    print logging messages during startup
    """
    print(arg)


def create_dirs(dirname, fconf):
    """
    This function is responsible for the recursive creation
    of directories required for FFcuesplitter-GUI if they do
    not exist.
    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname, mode=0o777)
        except Exception as err:
            return {'ERROR': err}

    return {'R': None}


def restore_dirconf(dirconf, srcdata, portable):
    """
    This function is responsible for restoring the
    configuration directory if it is missing and
    populating it with its essential files.
    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    if not os.path.exists(dirconf):  # create the configuration directory
        try:
            os.mkdir(dirconf, mode=0o777)
        except FileNotFoundError as err:  # parent directory does not exist
            return {'ERROR': err}

    if portable:
        albcoll = os.path.join(dirconf, "Album Collection")
        try:
            if not os.path.exists(albcoll):
                os.makedirs(albcoll, mode=0o777)
        except Exception as err:
            return {'ERROR': err}

    return {'R': None}
# --------------------------------------------------------------------------


def conventional_paths():
    """
    Establish the conventional paths based on OS

    """
    user = os.path.expanduser('~')

    if platform.system() == 'Windows':
        fpath = "\\AppData\\Roaming\\ffcuesplitter-gui\\settings.json"
        file_conf = os.path.join(user + fpath)
        dir_conf = os.path.join(user + "\\AppData\\Roaming\\ffcuesplitter-gui")
        log_dir = os.path.join(dir_conf, 'log')  # logs

    elif platform.system() == "Darwin":
        fpath = "Library/Application Support/ffcuesplitter-gui/settings.json"
        file_conf = os.path.join(user, fpath)
        dir_conf = os.path.join(user, os.path.dirname(fpath))
        log_dir = os.path.join(user, "Library/Logs/ffcuesplitter-gui")

    else:  # Linux, FreeBsd, etc.
        fpath = ".config/ffcuesplitter-gui/settings.json"
        file_conf = os.path.join(user, fpath)
        dir_conf = os.path.join(user, ".config/ffcuesplitter-gui")
        log_dir = os.path.join(user, ".local/share/ffcuesplitter-gui/log")

    return file_conf, dir_conf, log_dir


def portable_paths(portdirname):
    """
    Make portable-data paths based on OS

    """
    dir_conf = portdirname
    file_conf = os.path.join(dir_conf, "settings.json")
    log_dir = os.path.join(dir_conf, 'log')  # logs

    return file_conf, dir_conf, log_dir


def data_location(kwargs):
    """
    Determines data location and modes to make the app
    portable, fully portable or using conventional paths.
    Returns data location dict.
    """
    if kwargs['make_portable']:
        portdir = kwargs['make_portable']
        (conffile, confdir, logdir) = portable_paths(portdir)
    else:
        conffile, confdir, logdir = conventional_paths()

    return {"conffile": conffile, "confdir": confdir, "logdir": logdir}


class DataSource():
    """
    DataSource class determines the FFcuesplitter-GUI's
    configuration according to the used Operating
    System and installed package.

    """
    def __init__(self, kwargs):
        """
        Having the pathnames returned by `dataloc`
        it performs the initialization described in
        DataSource.

        """
        self.dataloc = data_location(kwargs)
        self.relativepaths = bool(kwargs['make_portable'])
        self.makeportable = kwargs['make_portable']

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            sitepkg = getattr(sys, '_MEIPASS', os.path.abspath(__file__))
            srcdata = sitepkg
            self.dataloc["app"] = 'pyinstaller'
            msg('Info: Stand-Alone application bundle (build by pyinstaller)')
        else:
            sitepkg = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))
            srcdata = os.path.join(sitepkg, 'ffcuesplitter_gui', 'data')
            self.dataloc["app"] = None
            msg(f"Info: Package: «ffcuesplitter-gui»\n"
                f"Info: Location: «{sitepkg}»")

        self.dataloc["localepath"] = os.path.join(srcdata, 'locale')
        self.dataloc["srcdata"] = srcdata
        self.dataloc["icodir"] = os.path.join(srcdata, 'icons')
        self.dataloc["FFMPEG_DIR"] = os.path.join(srcdata, 'FFMPEG')

        self.prg_icon = os.path.join(self.dataloc['icodir'],
                                     "ffcuesplittergui.png")
    # ---------------------------------------------------------------------

    def get_configuration(self):
        """
        Get configuration data of the application.
        Returns a dict object with current data-set for bootstrap.

        Note: If returns a dict key == ERROR it will raise a windowed
        fatal error in the gui_app bootstrap.
        """
        # checks configuration directory
        ckdconf = restore_dirconf(self.dataloc['confdir'],
                                  self.dataloc['srcdata'],
                                  self.makeportable,
                                  )
        if ckdconf.get('ERROR'):
            return ckdconf

        # handle configuration file
        userconf = get_options(self.dataloc['conffile'], self.makeportable)
        if userconf.get('ERROR'):
            return userconf
        userconf = userconf['R']

        # create the required directories if not existing
        create = create_dirs(self.dataloc['logdir'], self.dataloc['conffile'],)
        if create.get('ERROR'):
            return create

        def _relativize(path, relative=self.relativepaths):
            """
            Returns a relative pathname if *relative* param is True.
            If not, it returns the given pathname. Also return the given
            pathname if `ValueError` is raised. This function is called
            several times during program execution.
            """
            try:
                return os.path.relpath(path) if relative else path
            except (ValueError, TypeError):
                # return {'ERROR': f'{error}'}  # use `as error` here
                return path

        return ({'ostype': platform.system(),
                 'srcdata': _relativize(self.dataloc['srcdata']),
                 'localepath': _relativize(self.dataloc['localepath']),
                 'fileconfpath': _relativize(self.dataloc['conffile']),
                 'confdir': _relativize(self.dataloc['confdir']),
                 'logdir': _relativize(self.dataloc['logdir']),
                 'FFMPEG_DIR': _relativize(self.dataloc['FFMPEG_DIR']),
                 'app': self.dataloc['app'],
                 'relpath': self.relativepaths,
                 'getpath': _relativize,
                 'ffmpeg_cmd': _relativize(userconf['ffmpeg_cmd']),
                 'ffprobe_cmd': _relativize(userconf['ffprobe_cmd']),
                 'auto-restart-app': False,
                 'make_portable': self.makeportable,
                 **userconf
                 })
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the configuration
        file (see `icontheme` in the settings.json file).
        Returns a icontheme dict object.

        """
        keys = ('ffcuesplittergui', 'startsplit', 'setup',
                'stop', 'trackinfo', 'CDinfo', 'log',
                'empty_2',
                )  # must match with items on `iconset` tuple, see following
        icodir = self.dataloc['icodir']

        iconames = {'Light':  # icons for light themes
                    {'x22': f'{icodir}/Light/24x24'},
                    'Dark':  # icons for dark themes
                    {'x22': f'{icodir}/Dark/24x24'},
                    'Colored':  # icons for all themes
                    {'x22': f'{icodir}/Colored/24x24'},
                    }
        choose = iconames.get(icontheme)  # set appropriate icontheme
        ext = 'svg' if 'wx.svg' in sys.modules else 'png'
        iconset = (self.prg_icon,
                   f"{choose.get('x22')}/startsplit.{ext}",
                   f"{choose.get('x22')}/setup.{ext}",
                   f"{choose.get('x22')}/stop.{ext}",
                   f"{choose.get('x22')}/trackinfo.{ext}",
                   f"{choose.get('x22')}/CDinfo.{ext}",
                   f"{choose.get('x22')}/log.{ext}",
                   f"{choose.get('x22')}/empty_2.{ext}",
                   )
        values = [os.path.join(norm) for norm in iconset]  # normalize pathns

        return dict(zip(keys, values))
