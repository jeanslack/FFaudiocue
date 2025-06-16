# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the utils.py object.
# Rev: 07.Feb.2024

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from ffaudiocue.ffc_utils.utils import (detect_binaries,
                                            get_codec_quality_items,
                                            )
except ImportError as error:
    sys.exit(error)


class TestFFmpegBinary(unittest.TestCase):
    """Test case for the detect_binaries function."""

    def test_ffmpeg(self):
        self.assertEqual(detect_binaries('ffmpeg'), (None, '/usr/bin/ffmpeg'))


class TestFFprobeBinary(unittest.TestCase):
    """Test case for the detect_binaries function."""

    def test_ffprobe(self):
        self.assertEqual(detect_binaries('ffprobe'), (None, '/usr/bin/ffprobe'))


class TestAudioFormatReferences(unittest.TestCase):
    """Test case for the get_codec_quality_items function."""

    def test_wav_format(self):
        self.assertEqual(get_codec_quality_items('wav'), {'Auto': ''})

    def test_format_error(self):
        with self.assertRaises(KeyError):
            # Accepts only wav, flac, ogg, opus, mp3 formats not ape .
            get_codec_quality_items('ape')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
