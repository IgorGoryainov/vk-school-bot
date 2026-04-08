# -*- coding: utf-8 -*-
"""Tests for data file read/write helpers."""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import bot


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    """Redirect all data I/O to a temp directory."""
    monkeypatch.setattr(bot, 'DATA_DIR', str(tmp_path))
    return tmp_path


class TestIdList:
    def test_read_empty_file_returns_empty_list(self, tmp_path):
        path = tmp_path / 'test.txt'
        path.write_text('0\n', encoding='utf-8')
        result = bot.read_id_list('test.txt')
        assert result == []

    def test_round_trip(self):
        ids = [111, 222, 333]
        bot.write_id_list('ids.txt', ids)
        loaded = bot.read_id_list('ids.txt')
        assert loaded == ids

    def test_read_missing_file_returns_empty_list(self):
        result = bot.read_id_list('nonexistent.txt')
        assert result == []

    def test_write_creates_correct_format(self, tmp_path):
        bot.write_id_list('check.txt', [42, 99])
        content = (tmp_path / 'check.txt').read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        assert lines[0] == '2'
        assert lines[1] == '42'
        assert lines[2] == '99'


class TestHomework:
    def test_read_missing_returns_message(self):
        result = bot.read_homework('monday.txt')
        assert 'не найдено' in result.lower() or 'не задано' in result.lower()

    def test_write_and_read_round_trip(self):
        bot.write_homework('monday.txt', 15, 'Алгебра: 101-105')
        result = bot.read_homework('monday.txt')
        assert result == 'Алгебра: 101-105'

    def test_empty_file_returns_not_assigned(self, tmp_path):
        (tmp_path / 'tuesday.txt').write_text('15\n', encoding='utf-8')
        result = bot.read_homework('tuesday.txt')
        assert 'не задано' in result.lower()

    def test_write_overwrites_previous(self):
        bot.write_homework('wednesday.txt', 15, 'Первое задание')
        bot.write_homework('wednesday.txt', 15, 'Второе задание')
        result = bot.read_homework('wednesday.txt')
        assert result == 'Второе задание'


class TestResetHomework:
    def test_resets_when_week_changes(self, tmp_path, monkeypatch):
        # Write old week number
        (tmp_path / 'monday.txt').write_text('1\nСтарое ДЗ\n', encoding='utf-8')
        for name in ['tuesday.txt', 'wednesday.txt', 'thursday.txt', 'friday.txt', 'saturday.txt']:
            (tmp_path / name).write_text('1\n', encoding='utf-8')

        monkeypatch.setattr(bot, 'current_week_number', lambda: 2)
        bot.reset_homework_if_new_week()

        content = (tmp_path / 'monday.txt').read_text(encoding='utf-8')
        assert content.strip() == '2'

    def test_no_reset_same_week(self, tmp_path, monkeypatch):
        (tmp_path / 'monday.txt').write_text('5\nТекущее ДЗ\n', encoding='utf-8')
        for name in ['tuesday.txt', 'wednesday.txt', 'thursday.txt', 'friday.txt', 'saturday.txt']:
            (tmp_path / name).write_text('5\n', encoding='utf-8')

        monkeypatch.setattr(bot, 'current_week_number', lambda: 5)
        bot.reset_homework_if_new_week()

        result = bot.read_homework('monday.txt')
        assert result == 'Текущее ДЗ'
