from dataclasses import dataclass
from datetime import date
from typing import Callable

from aiogram.types import CallbackQuery, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import (
    Calendar, Column, Group, ManagedCalendar, Row,  Start, Select, SwitchTo
    )
from aiogram_dialog.widgets.text import Case, Const, Format
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_daily_results,  get_interval_results
from fsm.fsm_dialogs import StartState, Stats
from .utils import str_date


@dataclass
class DateChoise:
    id: str
    name: str
    start_date: date
    function: Callable


DATECHOICE_LIST = [
    DateChoise(
        'today',
        'За сегодня',
        date.today(),
        get_daily_results,
    ),
    DateChoise(
        'week',
        'За неделю',
        date.today() - relativedelta(weeks=1),
        get_interval_results,
    ),
    DateChoise(
        'month',
        'За месяц',
        date.today() - relativedelta(months=1),
        get_interval_results,
    )
]


async def date_getter(dialog_manager: DialogManager,
                      event_from_user: User,
                      **kwargs):
    getter_data = {'datechoice_list': DATECHOICE_LIST,
                   'user_id': event_from_user.id}
    return getter_data


async def on_datechoice_clicked(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected_item: str,
):
    datechoice = next((
            choice for choice in DATECHOICE_LIST if choice.id == selected_item
        ), None)
    dialog_manager.dialog_data['datechoice'] = datechoice
    await dialog_manager.next()


async def on_date_clicked(
    callback: CallbackQuery,
    widget: ManagedCalendar,
    dialog_manager: DialogManager,
    selected_date: date, /,
):
    datechoice = DateChoise(
        'any_day',
        'За другой день',
        selected_date,
        get_daily_results,
    )
    dialog_manager.dialog_data['datechoice'] = datechoice
    await dialog_manager.back()


async def stats_getter(
        dialog_manager: DialogManager,
        event_from_user: User,
        session: AsyncSession,
        **kwargs):
    try:
        user_id = dialog_manager.dialog_data['user_id']
    except KeyError:
        user_id = dialog_manager.event.from_user.id
    datechoice = dialog_manager.dialog_data['datechoice']
    selected_date = datechoice.start_date
    func = datechoice.function
    task_record = await func(session, user_id, selected_date)
    # если не очистить это поле, будет ошибка сериализации json
    dialog_manager.dialog_data['datechoice'] = None
    if task_record and task_record.total is not None:
        data = {
            'total': task_record.total,
            'multi': task_record.multi,
            'div': task_record.div,
            'all_ops': task_record.all_ops,
            'start_date': str_date(selected_date),
            'end_date': str_date(date.today()),
            'text': 2,
            'date': func.__name__ == 'get_daily_results'
        }
    else:
        data = {
            'start_date': str_date(selected_date),
            'end_date': str_date(date.today()),
            'text': 1,
            'date': func.__name__ == 'get_daily_results'
            }
    return data


stats_dialog = Dialog(
    Window(
        Const('За какой период вы хотите посмотреть статистику?'),
        Group(
            Row(
                Select(
                    Format("{item.name}"),
                    id="datechoice_id",
                    items="datechoice_list",
                    item_id_getter=lambda x: x.id,
                    on_click=on_datechoice_clicked,
                ),
                SwitchTo(Const('За другой день'), id='calendar',
                         state=Stats.calendar),
            ),
            width=2,
        ),
        Start(Const('На старт'), id='start', state=StartState.start,
              mode=StartMode.RESET_STACK),
        getter=date_getter,
        state=Stats.period,
    ),
    Window(
        Case(
            texts={
                True: Format('{start_date}\n'),
                False: Format('В период с {start_date} по '
                              '{end_date}\n'),
            },
            selector='date'
        ),
        Case(
            texts={
                1: Const('Hе было решено ни одного примера\n'
                         'Может быть стоит решить парочку?'),
                2: Format(
                    'Всего решено примеров: {total}\n\n'
                    'Из них\n'
                    'Умножение: {multi}\n'
                    'Деление: {div}\n'
                    'Все действия: {all_ops}\n'
                    )
            },
            selector='text',
        ),
        Column(
            SwitchTo(Const('Статистика за другой период'), id='stats',
                     state=Stats.period),
            Start(Const('На старт'), id='start', state=StartState.start,
                  mode=StartMode.RESET_STACK),
        ),
        getter=stats_getter,
        state=Stats.stats,
    ),
    Window(
        Const('Выберите день, за который хотите увидеть статистику'),
        Calendar(
            id="pick_any_day",
            on_click=on_date_clicked,
        ),
        state=Stats.calendar,
    ),
)
