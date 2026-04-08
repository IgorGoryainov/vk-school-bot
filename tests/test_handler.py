# -*- coding: utf-8 -*-
"""Tests for the message handler dispatch logic."""
import os
import sys
import pytest
from unittest.mock import MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import bot


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, 'DATA_DIR', str(tmp_path))
    # Pre-create homework file for today tests
    (tmp_path / 'monday.txt').write_text('15\nАлгебра: 1-5\n', encoding='utf-8')
    (tmp_path / 'tuesday.txt').write_text('15\nФизика: 10-12\n', encoding='utf-8')
    (tmp_path / 'wednesday.txt').write_text('15\n', encoding='utf-8')
    (tmp_path / 'thursday.txt').write_text('15\n', encoding='utf-8')
    (tmp_path / 'friday.txt').write_text('15\n', encoding='utf-8')
    (tmp_path / 'saturday.txt').write_text('15\n', encoding='utf-8')
    return tmp_path


@pytest.fixture()
def vk():
    mock = MagicMock()
    mock.method.return_value = {}
    return mock


USER_ID = 12345


def handle(vk, text, subscribers=None, dz_subs=None, sched_subs=None):
    subscribers = subscribers if subscribers is not None else []
    dz_subs = dz_subs if dz_subs is not None else []
    sched_subs = sched_subs if sched_subs is not None else []
    bot.handle_message(vk, USER_ID, text, subscribers, dz_subs, sched_subs)
    return subscribers, dz_subs, sched_subs


class TestHelpCommand:
    def test_help_sends_help_message(self, vk):
        handle(vk, 'help')
        sent = vk.method.call_args[0][1]['message']
        assert 'help' in sent.lower() or 'команд' in sent.lower()


class TestSubscriptions:
    def test_subscribe_to_dz(self, vk):
        _, dz_subs, _ = handle(vk, '1')
        assert USER_ID in dz_subs

    def test_subscribe_to_dz_twice_no_duplicate(self, vk):
        _, dz_subs, _ = handle(vk, '1', dz_subs=[USER_ID])
        assert dz_subs.count(USER_ID) == 1

    def test_unsubscribe_from_dz(self, vk):
        _, dz_subs, _ = handle(vk, '2', dz_subs=[USER_ID])
        assert USER_ID not in dz_subs

    def test_unsubscribe_when_not_subscribed(self, vk):
        handle(vk, '2')
        sent = vk.method.call_args[0][1]['message']
        assert 'не подписан' in sent.lower()

    def test_subscribe_to_schedule(self, vk):
        _, _, sched_subs = handle(vk, '3')
        assert USER_ID in sched_subs

    def test_unsubscribe_from_schedule(self, vk):
        _, _, sched_subs = handle(vk, '4', sched_subs=[USER_ID])
        assert USER_ID not in sched_subs


class TestHomeworkCommands:
    def test_add_homework_valid(self, vk):
        handle(vk, '101 1 Алгебра: 100')
        result = bot.read_homework('monday.txt')
        assert result == 'Алгебра: 100'

    def test_add_homework_invalid_day(self, vk):
        handle(vk, '101 9 Что-то')
        sent = vk.method.call_args[0][1]['message']
        assert 'неверный' in sent.lower() or '1–6' in sent

    def test_add_homework_malformed(self, vk):
        handle(vk, '101')
        # Falls through to unknown command — welcome or "не понимаю"
        vk.method.assert_called()


class TestNewUserWelcome:
    def test_unknown_user_gets_welcome_and_is_added(self, vk):
        subs, _, _ = handle(vk, 'some random text')
        sent = vk.method.call_args[0][1]['message']
        assert USER_ID in subs

    def test_known_user_unknown_command_gets_hint(self, vk):
        handle(vk, 'gibberish', subscribers=[USER_ID])
        sent = vk.method.call_args[0][1]['message']
        assert 'help' in sent.lower() or 'понимаю' in sent.lower()


class TestTextbooksCommand:
    def test_command_9_returns_links(self, vk):
        handle(vk, '9')
        sent = vk.method.call_args[0][1]['message']
        assert 'http' in sent
