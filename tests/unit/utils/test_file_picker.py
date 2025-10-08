"""Tests for File Picker - Smoke tests"""
import pytest
from unittest.mock import patch
from pathlib import Path

class TestFilePicker:
    @patch('samplemind.utils.file_picker.tk.Tk')
    @patch('samplemind.utils.file_picker.filedialog.askopenfilename', return_value='')
    def test_select_cancelled(self, m1, m2):
        from samplemind.utils.file_picker import select_audio_file
        assert select_audio_file() is None

    @patch('samplemind.utils.file_picker.tk.Tk')
    @patch('samplemind.utils.file_picker.filedialog.askopenfilename', return_value='/test.wav')
    def test_select_success(self, m1, m2):
        from samplemind.utils.file_picker import select_audio_file
        assert select_audio_file() == Path('/test.wav')
