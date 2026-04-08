# -*- coding: utf-8 -*-
"""Tests for schedule lookups and day navigation logic."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bot import (
    SCHEDULE,
    HOMEWORK_FILES,
    schedule_for_day,
    homework_file_for_day,
)


class TestSchedule:
    def test_all_weekdays_have_schedules(self):
        for day in range(0, 7):
            result = schedule_for_day(day)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_monday_schedule_contains_subjects(self):
        sched = schedule_for_day(1)
        assert 'Литература' in sched
        assert 'Математика' in sched

    def test_sunday_returns_day_name(self):
        assert schedule_for_day(0) == 'Воскресенье'

    def test_saturday_schedule_has_seven_lessons(self):
        sched = schedule_for_day(6)
        # Saturday has 7 periods
        assert '7.' in sched

    def test_unknown_day_falls_back_gracefully(self):
        result = schedule_for_day(99)
        assert result == 'Воскресенье'


class TestHomeworkFiles:
    def test_monday_to_saturday_all_mapped(self):
        for day in range(1, 7):
            filename = homework_file_for_day(day)
            assert filename is not None
            assert filename.endswith('.txt')

    def test_sunday_maps_to_monday(self):
        assert homework_file_for_day(0) == 'monday.txt'

    def test_correct_filenames(self):
        assert homework_file_for_day(1) == 'monday.txt'
        assert homework_file_for_day(2) == 'tuesday.txt'
        assert homework_file_for_day(3) == 'wednesday.txt'
        assert homework_file_for_day(4) == 'thursday.txt'
        assert homework_file_for_day(5) == 'friday.txt'
        assert homework_file_for_day(6) == 'saturday.txt'

    def test_homework_files_dict_has_six_entries(self):
        assert len(HOMEWORK_FILES) == 6
