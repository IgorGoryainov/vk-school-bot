# -*- coding: utf-8 -*-
import os
import time
import datetime

import vk_api

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

# Timetables for each day (Mon=1 .. Sat=6, Sun=0)
SCHEDULE = {
    1: (
        '1. Электив(матан)\n'
        '2. Литература\n'
        '3. Английский язык\n'
        '4. Биология\n'
        '5. Математика\n'
        '6. Математика'
    ),
    2: (
        '1. Инф(гр1)/Ино(гр2)\n'
        '2. История\n'
        '3. ОБЖ\n'
        '4. Геометрия\n'
        '5. Ино(гр1)/Инф(гр2)\n'
        '6. Физика'
    ),
    3: (
        '1. Сон\n'
        '2. Алгебра\n'
        '3. Обществознание\n'
        '4. Обществознание\n'
        '5. Литература\n'
        '6. Астрономия'
    ),
    4: (
        '1. Электив(матан)\n'
        '2. Химия\n'
        '3. Физика\n'
        '4. Физкультура\n'
        '5. История\n'
        '6. Английский язык'
    ),
    5: (
        '1. Сон\n'
        '2. Литература\n'
        '3. Геометрия\n'
        '4. Геометрия\n'
        '5. Русский язык\n'
        '6. Физкультура'
    ),
    6: (
        '1. Алгебра\n'
        '2. Физика\n'
        '3. Алгебра\n'
        '4. Физкультура\n'
        '5. Физика\n'
        '6. Русский язык\n'
        '7. Физика'
    ),
    0: 'Воскресенье',
}

# Homework storage filenames, Mon=1..Sat=6
HOMEWORK_FILES = {
    1: 'monday.txt',
    2: 'tuesday.txt',
    3: 'wednesday.txt',
    4: 'thursday.txt',
    5: 'friday.txt',
    6: 'saturday.txt',
}

MSG_WELCOME = (
    'Привет! Ты добавлен в список учеников 11А класса школы №63 г.о.Самара.\n\n'
    'Этот бот поможет узнать расписание и домашнее задание.\n'
    'Напиши "help", чтобы узнать доступные команды.'
)

MSG_HELP = (
    'Доступные команды:\n\n'
    'ПОДПИСКИ\n'
    '1 — подписаться на рассылку ДЗ\n'
    '2 — отписаться от рассылки ДЗ\n'
    '3 — подписаться на рассылку расписания\n'
    '4 — отписаться от рассылки расписания\n\n'
    'КОМАНДЫ\n'
    '5 — ДЗ на сегодня\n'
    '6 — ДЗ на завтра\n'
    '7 — расписание на сегодня\n'
    '8 — расписание на завтра\n'
    '9 — ссылки на учебники\n\n'
    'Добавить ДЗ: 101 [день] [текст]\n'
    'Пример: 101 1 Алгебра: 1034-1044'
)

MSG_TEXTBOOKS = (
    'Литература: http://rabochaya-tetrad-uchebnik.com/literatura/literatura_11_klass_uchebnik_kurdyumova_chastj_1/\n'
    'Алгебра задачник: http://rabochaya-tetrad-uchebnik.com/algebra/uchebnik_algebra_11_klass_zadachnik_mordkovich_chastj_2_profiljnyy_urovenj/\n'
    'Алгебра учебник: http://rabochaya-tetrad-uchebnik.com/algebra/algebra_11_klass_uchebnik_mordkovich_semenov_chastj_1/\n'
    'История: http://rabochaya-tetrad-uchebnik.com/istoriya/uchebnik_istoriya_rossiya_i_mir_11_klass_bazovyy_urovenj_volobuev_klokov/'
)


def data_path(filename):
    return os.path.join(DATA_DIR, filename)


def read_id_list(filename):
    path = data_path(filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return []
    count = int(lines[0].strip())
    return [int(lines[i].strip()) for i in range(1, count + 1) if i < len(lines)]


def write_id_list(filename, id_list):
    with open(data_path(filename), 'w', encoding='utf-8') as f:
        f.write(str(len(id_list)) + '\n')
        for user_id in id_list:
            f.write(str(user_id) + '\n')


def current_weekday():
    """Return weekday as int: Mon=1 .. Sat=6, Sun=0 (matches strftime %w)."""
    return int(time.strftime('%w', time.localtime()))


def current_week_number():
    return datetime.datetime.utcnow().isocalendar()[1]


def schedule_for_day(weekday):
    return SCHEDULE.get(weekday, 'Воскресенье')


def homework_file_for_day(weekday):
    if weekday == 0:
        weekday = 1
    return HOMEWORK_FILES.get(weekday)


def read_homework(filename):
    path = data_path(filename)
    if not os.path.exists(path):
        return 'ДЗ не найдено.'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) < 2:
        return 'ДЗ не задано.'
    return lines[1].strip()


def write_homework(filename, week_number, homework_text):
    with open(data_path(filename), 'w', encoding='utf-8') as f:
        f.write(str(week_number) + '\n')
        f.write(homework_text + '\n')


def reset_homework_if_new_week():
    monday_path = data_path('monday.txt')
    if not os.path.exists(monday_path):
        return
    with open(monday_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    stored_week = int(lines[0].strip()) if lines else 0
    current_week = current_week_number()
    if stored_week != current_week:
        for filename in HOMEWORK_FILES.values():
            with open(data_path(filename), 'w', encoding='utf-8') as f:
                f.write(str(current_week) + '\n')


def send(vk, peer_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'message': message})


def broadcast(vk, recipients, message):
    for user_id in recipients:
        send(vk, user_id, message)


def handle_message(vk, user_id, text, subscribers, dz_subscribers, schedule_subscribers):
    stripped = text.strip()
    cmd = stripped.lower()
    tokens = cmd.split()

    if cmd == 'sending000':
        broadcast(vk, subscribers, MSG_WELCOME)
        return

    if cmd == 'sendingdz':
        weekday = current_weekday()
        tomorrow = (weekday % 6) + 1 if weekday != 0 else 2
        hw = read_homework(homework_file_for_day(tomorrow))
        broadcast(vk, dz_subscribers, 'Домашнее задание на завтра:\n\n' + hw)
        return

    if cmd == 'sendingboard':
        weekday = current_weekday()
        tomorrow = (weekday % 7) + 1 if weekday != 0 else 1
        sched = schedule_for_day(tomorrow)
        broadcast(vk, schedule_subscribers, 'Расписание на завтра:\n\n' + sched)
        return

    if cmd == 'help':
        send(vk, user_id, MSG_HELP)
        return

    if cmd == '1':
        if user_id not in dz_subscribers:
            dz_subscribers.append(user_id)
            write_id_list('dzsend.txt', dz_subscribers)
            send(vk, user_id, 'Подписка на рассылку ДЗ оформлена.')
        else:
            send(vk, user_id, 'Ты уже подписан.')
        return

    if cmd == '2':
        if user_id in dz_subscribers:
            dz_subscribers.remove(user_id)
            write_id_list('dzsend.txt', dz_subscribers)
            send(vk, user_id, 'Отписка от рассылки ДЗ выполнена.')
        else:
            send(vk, user_id, 'Ты не подписан.')
        return

    if tokens and tokens[0] == '3':
        if user_id not in schedule_subscribers:
            schedule_subscribers.append(user_id)
            write_id_list('boardsend.txt', schedule_subscribers)
            send(vk, user_id, 'Подписка на рассылку расписания оформлена.')
        else:
            send(vk, user_id, 'Ты уже подписан.')
        return

    if cmd == '4':
        if user_id in schedule_subscribers:
            schedule_subscribers.remove(user_id)
            write_id_list('boardsend.txt', schedule_subscribers)
            send(vk, user_id, 'Отписка от рассылки расписания выполнена.')
        else:
            send(vk, user_id, 'Ты не подписан.')
        return

    if cmd == '5':
        hw = read_homework(homework_file_for_day(current_weekday()))
        send(vk, user_id, hw)
        return

    if cmd == '6':
        weekday = current_weekday()
        tomorrow = (weekday % 6) + 1 if weekday != 0 else 2
        hw = read_homework(homework_file_for_day(tomorrow))
        send(vk, user_id, hw)
        return

    if cmd == '7':
        send(vk, user_id, schedule_for_day(current_weekday()))
        return

    if cmd == '8':
        weekday = current_weekday()
        tomorrow = (weekday % 7) + 1 if weekday != 0 else 1
        send(vk, user_id, schedule_for_day(tomorrow))
        return

    if cmd == '9':
        send(vk, user_id, MSG_TEXTBOOKS)
        return

    # Add homework: "101 <day_number> <homework text>"
    if len(tokens) >= 3 and tokens[0] == '101':
        try:
            day_number = int(tokens[1])
            # Preserve original case for homework text (only the prefix is parsed lowercase)
            original_tokens = stripped.split(None, 2)
            homework_text = original_tokens[2] if len(original_tokens) >= 3 else ' '.join(tokens[2:])
            hw_file = HOMEWORK_FILES.get(day_number)
            if hw_file:
                write_homework(hw_file, current_week_number(), homework_text)
                send(vk, user_id, 'ДЗ сохранено: ' + homework_text)
            else:
                send(vk, user_id, 'Неверный номер дня (1–6).')
        except (ValueError, IndexError):
            send(vk, user_id, 'Ошибка формата. Пример: 101 1 Алгебра: 1034-1044')
        return

    # Unknown user or unrecognised command
    if user_id not in subscribers:
        send(vk, user_id, MSG_WELCOME)
        subscribers.append(user_id)
        write_id_list('idbase.txt', subscribers)
    else:
        send(vk, user_id, 'Не понимаю команду. Напиши "help".')


def main():
    token = os.environ.get('VK_TOKEN')
    if not token:
        raise RuntimeError('VK_TOKEN environment variable is not set.')

    vk = vk_api.VkApi(token=token)
    vk._auth_token()

    subscribers = read_id_list('idbase.txt')
    dz_subscribers = read_id_list('dzsend.txt')
    schedule_subscribers = read_id_list('boardsend.txt')

    while True:
        try:
            reset_homework_if_new_week()
            conversations = vk.method(
                'messages.getConversations',
                {'offset': 0, 'count': 20, 'filter': 'unanswered'},
            )
            if conversations['count'] >= 1:
                last_message = conversations['items'][0]['last_message']
                user_id = last_message['from_id']
                text = last_message['text']
                handle_message(
                    vk, user_id, text,
                    subscribers, dz_subscribers, schedule_subscribers,
                )
        except Exception:
            time.sleep(1)


if __name__ == '__main__':
    main()
