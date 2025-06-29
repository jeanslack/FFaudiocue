# -*- coding: UTF-8 -*-
"""
Name: cuesplitter_panel.py
Porpose: main ffcuesplitter panel interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.04.2022
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
import shutil
import tempfile
import datetime
import wx
import wx.lib.scrolledpanel as scrolled
from pubsub import pub
from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.utils import makeoutputdirs, remove_source_file, sanitize
from ffaudiocue.ffc_utils.utils import get_codec_quality_items
from ffaudiocue.ffc_threads.ffmpeg_processing import Processing
from ffaudiocue.ffc_dlg.widget_utils import notification_area
from ffaudiocue.ffc_dlg.list_warning import ListWarning


def move_files_to_outputdir(outputdir, tmpdir):
    """
    All files are processed in a /temp folder. After the split
    operation is complete, all tracks are moved from /temp folder
    to output folder. Here evaluates what to do if files already
    exists on output folder.
    """
    tracklist = []
    existslist = []

    for track in os.listdir(tmpdir):
        tracklist.append(track)
        fdest = os.path.join(outputdir, track)
        if os.path.exists(fdest):
            existslist.append(f'"{fdest}"')

    if existslist:
        msg = _('Files already exist, do you want to overwrite them?')
        with ListWarning(None,
                         dict.fromkeys(existslist, ''),
                         caption=_('Please confirm'),
                         header=msg,
                         buttons='CONFIRM',
                         ) as log:
            response = log.ShowModal()

            if response == wx.ID_YES:
                for track in tracklist:
                    orig = os.path.join(tmpdir, track)
                    dest = os.path.join(outputdir, track)
                    try:
                        shutil.move(orig, dest)
                    except Exception as error:
                        return error
            elif response == wx.ID_NO:
                for track in tracklist:
                    orig = os.path.join(tmpdir, track)
                    dest = os.path.join(outputdir, track)
                    if not os.path.exists(dest):
                        try:
                            shutil.move(orig, dest)
                        except Exception as error:
                            return error
            else:
                return 'cancelled'

            return None

    for track in tracklist:
        orig = os.path.join(tmpdir, track)
        dest = os.path.join(outputdir, track)
        try:
            shutil.move(orig, dest)
        except Exception as error:
            return error

    return None


class CueGui(wx.Panel):
    """
    Represents the only one main panel for FFaudiocue
    implemented on main_frame.
    """
    def __init__(self, parent):
        """
        This constructor subscribes three listener of pubsub
        package. All references to subscribed callables are
        located on the Processing class thread.
        """
        self.parent = parent  # main_frame
        get = wx.GetApp()
        self.appdata = get.appset  # current appdata
        self.thread_type = None  # the instantiated thread
        self.abort = False  # if True set to abort current process
        self.error = False  # if True set to error current process
        self.data = None  # it is the ffcuesplitter instance
        self.author = None
        self.album = None
        self.tmpdir = None  # path to tempdir folder

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_div = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_div, 1, wx.EXPAND)
        boxoptions = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, ('')), wx.VERTICAL)
        sizer_div.Add(boxoptions, 0, wx.ALL | wx.EXPAND, 5)
        boxlistctrl = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, ('')), wx.VERTICAL)
        sizer_div.Add(boxlistctrl, 1, wx.ALL | wx.EXPAND, 5)
        boxoptions.Add((5, 5))
        panelscroll = scrolled.ScrolledPanel(self, -1, size=(250, 600),
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        # fgs1.Add((5, 5))
        self.lbl_formats = wx.StaticText(panelscroll,
                                         wx.ID_ANY,
                                         label=_("Audio format:")
                                         )
        fgs1.Add(self.lbl_formats, 0, wx.ALL | wx.EXPAND, 5)
        self.cmbx_formats = wx.ComboBox(panelscroll, wx.ID_ANY,
                                        choices=(('wav', 'flac', 'opus',
                                                  'mp3', 'ogg')),
                                        size=(-1, -1), style=wx.CB_DROPDOWN
                                        | wx.CB_READONLY
                                        )
        fgs1.Add(self.cmbx_formats, 0, wx.ALL | wx.EXPAND, 5)
        self.cmbx_formats.SetSelection(1)
        self.lbl_quality = wx.StaticText(panelscroll,
                                         wx.ID_ANY,
                                         label=_("Quality/Bitrate:")
                                         )
        fgs1.Add(self.lbl_quality, 0, wx.ALL | wx.EXPAND, 5)

        items = get_codec_quality_items(self.cmbx_formats.GetValue())
        self.cmbx_quality = wx.ComboBox(panelscroll, wx.ID_ANY,
                                        choices=(list(items.keys())),
                                        size=(-1, -1), style=wx.CB_DROPDOWN
                                        | wx.CB_READONLY
                                        )
        self.cmbx_quality.SetSelection(6)
        # grid_v.Add((20, 20), 0,)
        fgs1.Add(self.cmbx_quality, 0, wx.ALL | wx.EXPAND, 5)
        msg = _('Copy codec and format\n(very fast)')
        self.ckbx_codec_copy = wx.CheckBox(panelscroll, wx.ID_ANY, msg)
        fgs1.Add(self.ckbx_codec_copy, 0, wx.ALL, 5)
        line1 = wx.StaticLine(panelscroll, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add(line1, 0, wx.ALL | wx.EXPAND, 10)
        lbl_outdir = wx.StaticText(panelscroll,
                                   wx.ID_ANY,
                                   label=_("Audio track destination:")
                                   )
        fgs1.Add(lbl_outdir, 0, wx.ALL | wx.EXPAND, 5)
        msg = _('Same as input file')
        self.ckbx_samedest = wx.CheckBox(panelscroll, wx.ID_ANY, msg)
        fgs1.Add(self.ckbx_samedest, 0, wx.ALL, 5)
        sizer_outdir = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_outdir, 0, wx.EXPAND | wx.ALL, 5)
        self.btn_out = wx.Button(panelscroll, wx.ID_ANY, "...", size=(35, -1))
        self.txt_out = wx.TextCtrl(panelscroll,
                                   wx.ID_ANY,
                                   f"{self.appdata['destination']}",
                                   style=wx.TE_PROCESS_ENTER
                                   | wx.TE_READONLY
                                   )
        sizer_outdir.Add(self.txt_out, 1, wx.RIGHT | wx.EXPAND, 2)
        sizer_outdir.Add(self.btn_out, 0, wx.LEFT
                         | wx.ALIGN_CENTER_HORIZONTAL
                         | wx.ALIGN_CENTER_VERTICAL, 2
                         )
        msg = _('Create collection folders\n(Author/Album)')
        self.ckbx_collection = wx.CheckBox(panelscroll, wx.ID_ANY, msg)
        fgs1.Add(self.ckbx_collection, 0, wx.ALL, 5)
        line2 = wx.StaticLine(panelscroll, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add(line2, 0, wx.ALL | wx.EXPAND, 10)
        lbl_misc = wx.StaticText(panelscroll, wx.ID_ANY,
                                 label=_("Miscellaneous:")
                                 )
        fgs1.Add(lbl_misc, 0, wx.ALL | wx.EXPAND, 5)
        msg = _('Remove original files at the end\n(after successful)')
        self.ckbx_removesrc = wx.CheckBox(panelscroll, wx.ID_ANY, msg)
        fgs1.Add(self.ckbx_removesrc, 0, wx.ALL, 5)
        boxoptions.Add(panelscroll, 0, wx.ALL | wx.CENTRE, 0)

        panelscroll.SetSizer(fgs1)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        # -------------listctrl
        self.tracklist = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                     | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        boxlistctrl.Add(self.tracklist, 1, wx.ALL | wx.EXPAND, 5)
        self.tracklist.InsertColumn(0, (_('Track')), width=60)
        self.tracklist.InsertColumn(1, (_('Author')), width=130)
        self.tracklist.InsertColumn(2, (_('Title')), width=130)
        self.tracklist.InsertColumn(3, (_('Length')), width=80)
        self.tracklist.InsertColumn(4, (_('Album')), width=180)

        sizer_cuefile = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_cuefile, 0, wx.EXPAND | wx.ALL, 5)
        self.btn_import = wx.Button(self, wx.ID_OPEN, "...", size=(35, -1))
        self.txt_path_cue = wx.TextCtrl(self, wx.ID_ANY, "*.cue",
                                        style=wx.TE_PROCESS_ENTER
                                        | wx.TE_READONLY
                                        )
        sizer_cuefile.Add(self.txt_path_cue, 1, wx.RIGHT | wx.EXPAND, 2)
        sizer_cuefile.Add(self.btn_import, 0, wx.LEFT
                          | wx.ALIGN_CENTER_HORIZONTAL
                          | wx.ALIGN_CENTER_VERTICAL, 2
                          )
        sizer_cenc = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_cenc, 0, wx.ALL, 5)
        msg = _('Enter custom character encoding')
        self.ckbx_charsenc = wx.CheckBox(self, wx.ID_ANY, msg)
        sizer_cenc.Add(self.ckbx_charsenc, 0, wx.LEFT | wx.CENTRE, 2)
        self.ckbx_charsenc.Disable()

        self.txt_charsenc = wx.TextCtrl(self, wx.ID_ANY, "auto",
                                        style=wx.TE_PROCESS_ENTER,
                                        size=(170, -1))
        self.txt_charsenc.Disable()
        sizer_cenc.Add(self.txt_charsenc, 0, wx.LEFT | wx.CENTRE, 2)

        self.btn_confirm = wx.Button(self, wx.ID_ANY, _("Apply"))
        self.btn_confirm.Disable()
        sizer_cenc.Add(self.btn_confirm, 0, wx.LEFT | wx.CENTRE, 10)
        self.barprog = wx.Gauge(self, wx.ID_ANY, range=0)
        sizer_base.Add(self.barprog, 0, wx.EXPAND | wx.ALL, 5)
        sizer_base.Add((0, 10))
        self.SetSizerAndFit(sizer_base)
        self.Layout()

        tip = (_('If invalid, type in this text field the correct encoding of '
                 'the corresponding CUE file, for example some valid '
                 'character encoding names are:'
                 '\nutf-8\nascii\niso-8859-15\ncp1257\netc.'))
        self.txt_charsenc.SetToolTip(tip)

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_import_cuefile, self.btn_import)
        self.Bind(wx.EVT_BUTTON, self.on_output_dir, self.btn_out)

        self.Bind(wx.EVT_COMBOBOX, self.on_formats, self.cmbx_formats)
        self.Bind(wx.EVT_CHECKBOX, self.on_codec_copy, self.ckbx_codec_copy)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.tracklist)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect,
                  self.tracklist)
        self.Bind(wx.EVT_CHECKBOX, self.on_same_dest, self.ckbx_samedest)
        self.Bind(wx.EVT_CHECKBOX, self.on_charset_enc, self.ckbx_charsenc)
        self.Bind(wx.EVT_TEXT, self.on_charset_enter, self.txt_charsenc)
        self.Bind(wx.EVT_BUTTON, self.on_charset_confirm, self.btn_confirm)
        # -----------------------------------------------------------------#
        pub.subscribe(self.update_progress_bar, "UPDATE_EVT")
        pub.subscribe(self.update_count_items, "COUNT_EVT")
        pub.subscribe(self.end_processing, "END_EVT")
        # ---------------------------------------- #

    def on_output_dir(self, event):
        """
        Set output Directory. Note that this function set
        a new path on self.appdata['destination'] as well.

        """
        if self.txt_path_cue.GetValue() == '*.cue':
            txt = self.appdata['destination']
        else:
            txt = os.path.dirname(self.txt_path_cue.GetValue())

        dlg = wx.DirDialog(self, message=_("Set a destination folder"),
                           defaultPath=txt,
                           style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.txt_out.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())  # relativize
            self.appdata['destination'] = getpath
            self.txt_out.AppendText(getpath)
            dlg.Destroy()
    # -----------------------------------------------------------------#

    def on_same_dest(self, event):
        """
        Set same destination as input file
        """
        if self.ckbx_samedest.IsChecked():
            self.txt_out.Disable(), self.btn_out.Disable()
        else:
            self.txt_out.Enable(), self.btn_out.Enable()
    # -----------------------------------------------------------------#

    def load_cuefile(self, newincoming):
        """
        Load the imported CUE file using FFCueSplitter package
        """
        self.txt_path_cue.SetValue(newincoming)
        newenc = " ".join(self.txt_charsenc.GetValue().split())

        kwargs = {'filename': newincoming,
                  'ffprobe_cmd': self.appdata['ffprobe_cmd'],
                  'ffmpeg_cmd': self.appdata['ffmpeg_cmd'],
                  'ffmpeg_loglevel': self.appdata['ffmpegloglev'],
                  'progress_meter': 'tqdm',
                  'characters_encoding': newenc,
                  }  # for instance
        try:
            self.data = FFCueSplitter(**kwargs)
        except Exception as err:
            wx.MessageBox(f'{err}', "FFaudiocue - Error", wx.ICON_ERROR, self)
            return

        self.txt_charsenc.ChangeValue(self.data.chars_enc['encoding'])
        self.author = self.data.cue.meta.data['PERFORMER']
        self.album = self.data.cue.meta.data['ALBUM']
        self.parent.restoretag.Enable(True)  # enables Reload on menu bar
        self.ckbx_charsenc.Enable()

        self.set_data_list_ctrl()
    # -----------------------------------------------------------------#

    def on_import_cuefile(self, event, loadlast=None):
        """
        Displays dialog for importing CUE files.
        """
        if loadlast:
            newincoming = self.txt_path_cue.GetValue()
            self.load_cuefile(newincoming)
            return

        wildcard = "Source (*.cue;*.CUE)|*.cue;*.CUE|All files (*.*)|*.*"

        with wx.FileDialog(self, _("Open a CUE sheet"),
                           "", "", wildcard, wx.FD_OPEN
                           | wx.FD_FILE_MUST_EXIST) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return
            newincoming = filedlg.GetPath()

        self.load_cuefile(newincoming)
    # -----------------------------------------------------------------#

    def set_data_list_ctrl(self):
        """
        Populates listctrl and enable/disable some btns
        """
        self.tracklist.DeleteAllItems()

        for num, item in enumerate(self.data.audiotracks):
            self.tracklist.InsertItem(num, item.get('TRACK_NUM', 'N/A'))
            self.tracklist.SetItem(num, 1, item.get('PERFORMER', 'N/A'))
            self.tracklist.SetItem(num, 2, item.get('TITLE', 'N/A'))
            dur = item.get('DURATION', '')
            sec = str(datetime.timedelta(seconds=dur))[2:7]
            self.tracklist.SetItem(num, 3, sec)
            self.tracklist.SetItem(num, 4, item.get('ALBUM', 'N/A'))

        self.parent.toolbar.EnableTool(12, True)  # start
        self.parent.toolbar.EnableTool(8, True)  # audio CD
        self.parent.toolbar.EnableTool(14, False)  # track tag
        self.parent.statusbar_msg(_("Ready"))
    # -----------------------------------------------------------------#

    def on_formats(self, event):
        """
        Audio format selection
        """
        items = get_codec_quality_items(self.cmbx_formats.GetValue())
        self.cmbx_quality.Clear()
        self.cmbx_quality.Append((list(items.keys())),)
        if self.cmbx_formats.GetValue() == 'wav':
            self.cmbx_quality.SetSelection(0)

        elif self.cmbx_formats.GetValue() == 'flac':
            self.cmbx_quality.SetSelection(6)

        elif self.cmbx_formats.GetValue() == 'opus':
            self.cmbx_quality.SetSelection(6)

        elif self.cmbx_formats.GetValue() == 'mp3':
            self.cmbx_quality.SetSelection(3)

        elif self.cmbx_formats.GetValue() == 'ogg':
            self.cmbx_quality.SetSelection(5)
    # -----------------------------------------------------------------#

    def on_codec_copy(self, event):
        """
        Set for copy the source audio codec
        """
        if self.ckbx_codec_copy.IsChecked():
            self.cmbx_formats.Disable()
            self.cmbx_quality.Disable()
            self.lbl_quality.Disable()
            self.lbl_formats.Disable()
        else:
            self.cmbx_formats.Enable()
            self.cmbx_quality.Enable()
            self.lbl_quality.Enable()
            self.lbl_formats.Enable()
    # -----------------------------------------------------------------#

    def on_select(self, event):
        """
        self.tracklist selection event. Enables Track Tag
        button on toolbar.
        """
        self.parent.toolbar.EnableTool(14, True)
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        self.tracklist de-selection event. Disables Track Tag
        button on toolbar.
        """
        self.parent.toolbar.EnableTool(14, False)
    # ----------------------------------------------------------------------

    def on_charset_enc(self, event):
        """
        Check box event to Enable or Disable text field to
        enter custon characters encoding.
        """
        if self.ckbx_charsenc.IsChecked():
            self.txt_charsenc.Enable()
        else:
            self.txt_charsenc.Disable()
            self.txt_charsenc.ChangeValue('auto')
            self.btn_confirm.Disable()
            self.on_import_cuefile(self, loadlast=True)
    # ----------------------------------------------------------------------

    def on_charset_enter(self, event):
        """
        Text control event for type custon characters encoding.
        This event enables the confirm button.
        """
        if self.btn_confirm.IsEnabled() is False:
            self.btn_confirm.Enable()
    # ----------------------------------------------------------------------

    def on_charset_confirm(self, event):
        """
        Button event to applying custon characters encoding.
        This event reload the previous cue file.
        """
        self.on_import_cuefile(self, loadlast=True)
        self.btn_confirm.Disable()
    # ----------------------------------------------------------------------

    def update_attributes_of_ffcuesplitter_api(self):
        """
        Set required arguments on ffcuesplitter API
        """
        self.data.kwargs['ffmpeg_cmd'] = self.appdata['ffmpeg_cmd']
        self.data.kwargs['ffmpeg_loglevel'] = self.appdata['ffmpegloglev']

        msg = (_('Due to a known issue in FFmpeg with cutting FLAC files, '
                 'Copy Codec and Format may lead to unexpected results.\n'
                 'This issue appears to only affect the FLAC format.'))
        if self.ckbx_codec_copy.IsChecked():
            src = os.path.splitext(self.data.audiosource)[1]
            if src in ('.flac', '.FLAC'):
                wx.MessageBox(f'{msg}', "FFaudiocue- Information",
                              wx.ICON_INFORMATION, self)
            self.data.kwargs['ffmpeg_add_params'] = "-c copy"
        else:
            self.data.kwargs['outputformat'] = self.cmbx_formats.GetValue()
            items = get_codec_quality_items(self.cmbx_formats.GetValue())
            compression = items[self.cmbx_quality.GetValue()]
            self.data.kwargs['ffmpeg_add_params'] = compression

        if self.ckbx_samedest.IsChecked():
            self.appdata['destination'] = self.data.kwargs['dirname']
        else:
            self.appdata['destination'] = self.txt_out.GetValue()

        if self.ckbx_collection.IsChecked() is True:
            unkp, unka = 'Unknown Author', 'Unknown Album'
            author = unkp if not sanitize(self.author) else self.author
            album = unka if not sanitize(self.album) else self.album
            coll = os.path.join(self.appdata['destination'],
                                sanitize(author),
                                sanitize(album),
                                )
            self.appdata['destination'] = coll
            self.data.kwargs['outputdir'] = self.appdata['destination']
        else:
            self.data.kwargs['outputdir'] = self.appdata['destination']

        return False
    # ----------------------------------------------------------------------

    def on_start(self):
        """
        Prepares and updates the required operations
        for thread instance
        """
        if self.btn_confirm.IsEnabled() is True:
            msg = (_('The character encoding of the CUE file has not been '
                     'applied yet. Please click the Appy button before '
                     'proceeding.'))
            wx.MessageBox(msg, "FFaudiocue - Information",
                          wx.ICON_INFORMATION, self)
            return
        ret = self.update_attributes_of_ffcuesplitter_api()
        if ret:
            return

        self.tmpdir = tempfile.mkdtemp(suffix=None,
                                       prefix='FFaudiocue_',
                                       dir=None)
        self.data.kwargs['tempdir'] = self.tmpdir
        try:
            args = self.data.commandargs(self.data.audiotracks)
        except Exception as err:
            wx.MessageBox(f'{err}', "FFaudiocue - Error",
                          wx.ICON_ERROR, self)
            return

        self.parent.toolbar.EnableTool(13, True)  # stop
        self.parent.toolbar.EnableTool(12, False)  # start
        self.parent.toolbar.EnableTool(5, False)  # setup

        logfile = os.path.join(self.appdata['logdir'], 'ffaudiocue.log')
        self.thread_type = Processing(args, logfile)
    # ----------------------------------------------------------------------

    def on_stop(self, event):
        """
        The user changes his mind and wants to abort
        the ongoing process.
        """
        self.abort = True
        self.thread_type.stop()
        self.parent.statusbar_msg(_("Please wait..."),
                                  'GOLDENROD',
                                  'BLACK')
        self.thread_type.join()
    # ----------------------------------------------------------------------

    def update_progress_bar(self, output, duration, track, status):
        """
        Update progress bar by receving ffmpeg stdout pipe on
        thread loop. If `status` is not 0 means an error is
        occurred. This is usually a syntax error or some
        incompatibility in the arguments passed to the FFmpeg
        command.
        """
        if not status == 0:
            self.error = True
            return

        secs = round(int(output.split('=')[1]) / 1_000_000)
        percent = secs / round(duration) * 100
        msg = _("Processing... File number: {} | Status "
                "Progress: {}%").format(track, round(percent))
        self.barprog.SetValue(round(percent))
        self.parent.statusbar_msg(msg, bgrd='BLACK', fgrd='GREEN YELLOW')
    # ----------------------------------------------------------------------

    def update_count_items(self, msg, end):
        """
        Counts occurences for each loop and sets barprog range
        to max percentage starting to 0 (min) value. Note that
        when `msg` argument is equal to str('error') it means
        that an exception is raised by thread with one of the
        exceptions of class OSError, FileNotFoundError.
        """
        if end == 'error':
            self.error = True
            wx.MessageBox(f'{msg}', "FFaudiocue - Error", wx.ICON_ERROR, self)
        else:
            self.barprog.SetRange(100)  # set overall percentage range
            self.barprog.SetValue(0)  # reset bar progress to 0
    # ----------------------------------------------------------------------

    def end_processing(self):
        """
        At the end of the process
        """
        if self.abort is True:
            self.parent.statusbar_msg(_("...Interrupted"),
                                      'BLUE VIOLET', 'WHITE')
        elif self.error is True:
            self.parent.statusbar_msg(_("ERROR: See Logs for details"),
                                      'RED', 'WHITE')
            notification_area(_("ERROR!"), _("An error has occurred.\n"
                                             "See Logs for details."),
                              wx.ICON_ERROR)
        else:
            makeoutputdirs(self.data.kwargs['outputdir'])  # if doesn't exists
            ret = move_files_to_outputdir(self.data.kwargs['outputdir'],
                                          self.data.kwargs['tempdir'])
            if ret == 'cancelled':
                self.parent.statusbar_msg(_("FAILED: Operation cancelled"),
                                          'YELLOW', 'BLACK')
                notification_area(_('FAILED!'),
                                  _("Operation canceled by user"),
                                  wx.ICON_WARNING)
                self.barprog.SetValue(0)
                self.reset_gui()
                return

            if ret:
                wx.MessageBox(str(ret), "FFaudiocue - Error",
                              wx.ICON_ERROR, self)
                self.barprog.SetValue(0)
                self.reset_gui()
                self.parent.statusbar_msg(_(f'ERROR: {str(ret)}'),
                                          'RED', 'WHITE')
                return

            if self.ckbx_removesrc.IsChecked():
                cuef = self.data.kwargs['filename']
                audf = self.data.audiosource
                msg = (_('Do you really want to delete the following '
                         'source files?\n\n«{0}»\n«{1}»').format(cuef, audf))
                dlg = wx.MessageDialog(self, msg,
                                       _("FFaudiocue - Warning"),
                                       wx.ICON_WARNING
                                       | wx.YES_NO
                                       | wx.CANCEL).ShowModal()
                if dlg == wx.ID_YES:
                    ret = remove_source_file(cuef, audf)
                    if ret is False:
                        msg = _("File deletion failed: Files are missing")
                        wx.MessageBox(msg, "FFaudiocue - Error",
                                      wx.ICON_ERROR, self)

            self.parent.statusbar_msg(_("...Finished!"),
                                      'DARK GREEN', 'WHITE')
            notification_area(_('Success!'), _("Get your files at the "
                                               "destination you specified"),
                              wx.ICON_INFORMATION)
            self.barprog.SetValue(0)
        self.reset_gui()
    # ----------------------------------------------------------------------

    def reset_gui(self):
        """
        Reset gui after exit status
        """
        self.parent.toolbar.EnableTool(13, False)  # stop
        self.parent.toolbar.EnableTool(12, True)  # start
        self.parent.toolbar.EnableTool(5, True)  # setup
        self.thread_type = None
        self.abort = False
        self.error = False

        shutil.rmtree(self.tmpdir, ignore_errors=True)
    # ----------------------------------------------------------------------
