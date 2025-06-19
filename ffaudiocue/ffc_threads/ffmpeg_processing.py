# -*- coding: UTF-8 -*-
"""
Name: ffmpeg_processing.py
Porpose: FFmpeg long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.03.2022
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
from threading import Thread
import time
import subprocess
import platform
from ffcuesplitter.utils import Popen
import wx
from pubsub import pub
if not platform.system() == 'Windows':
    import shlex


class Processing(Thread):
    """
    This class represents a separate thread for running
    ffmpeg processes, which need to read the stdout/stderr
    in real time.

    NOTE MS Windows:

    subprocess.STARTUPINFO()

    https://stackoverflow.com/questions/1813872/running-
    a-process-in-pythonw-with-popen-without-a-console?lq=1>

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """
    get = wx.GetApp()  # get wx.App attribute
    appdata = get.appset
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ---------------------------------------------------------------

    def __init__(self, args, logname):
        """
        args: dict
        logname: absolute path name of the file log.
        """
        self.stop_work_thread = False  # if True the process terminates
        self.args = args  # list of commands/aguments
        self.logname = logname  # path name of file log
        subline = '-----------------------------'
        slog = (f'\nFFaudiocue: Creating log file\nDate: {time.strftime("%c")}'
                f'\n{subline}\n\n')
        with open(self.logname, "w", encoding='utf-8') as log:
            log.write(slog)
        self.count = 0  # count for loop
        self.countmax = len(args['recipes'])  # length list

        Thread.__init__(self)

        self.start()  # start the thread
    # --------------------------------------------------------------------#

    def run(self):
        """
        Subprocess initialize thread.
        """
        for recipes in self.args['recipes']:
            self.count += 1
            track = f'{self.count}/{self.countmax}'

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         msg='',
                         end='',
                         )

            cmdargs = recipes[0]
            if not platform.system() == 'Windows':
                cmdargs = shlex.split(recipes[0])

            with open(self.logname, "a", encoding='utf-8') as log:
                log.write(f"\n[INFO: COMMAND]: {recipes[0]}\n{'=' * 94}\n\n")

                try:
                    with Popen(cmdargs,
                               stdout=subprocess.PIPE,
                               stderr=log,
                               bufsize=1,
                               encoding='utf8',
                               universal_newlines=True) as proc:
                        for line in proc.stdout:
                            if "out_time_ms" in line.strip():
                                wx.CallAfter(pub.sendMessage,
                                             "UPDATE_EVT",
                                             output=line,
                                             duration=recipes[1]['duration'],
                                             track=track,
                                             status=0,
                                             )
                            if self.stop_work_thread:
                                proc.terminate()
                                break  # break second 'for' loop

                        if proc.wait():  # error
                            wx.CallAfter(pub.sendMessage,
                                         "UPDATE_EVT",
                                         output='',
                                         duration=recipes[1]['duration'],
                                         track='',
                                         status=proc.wait(),
                                         )
                except (OSError, FileNotFoundError) as err:
                    excepterr = f"{err}\n  {Processing.NOT_EXIST_MSG}"
                    log.write(f'\nERROR: {excepterr}')
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 msg=excepterr,
                                 end='error',
                                 )
                    break

                if self.stop_work_thread:
                    proc.terminate()
                    break  # break second 'for' loop

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
