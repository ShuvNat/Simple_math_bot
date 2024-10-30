from aiogram.types import User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Column, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.ext.asyncio import AsyncSession


from fsm.fsm_dialogs import Count, StartState, Stats


async def username_getter(
        dialog_manager: DialogManager,
        event_from_user: User,
        session: AsyncSession,
        **kwargs
):

    getter_data = {
            'username': event_from_user.first_name or event_from_user.username,
            }
    return getter_data

start_dialog = Dialog(
    Window(
        Format('<b>Приветствую, {username}!</b>\n'),
        Const('Это тренировочный бот, в котором можно порешать '
              'примеры на таблицу умножения и счет в пределах 100\n\n'
              'Выбери режим, в котором ты хочешь потренироваться\n'),
        Column(
            Start(Const('Умножение'), id='multi', state=Count.choice,
                  data='×'),
            Start(Const('Деление'), id='div', state=Count.choice,
                  data='÷'),
            Start(Const('Умножение и деление'), id='multi_div',
                  state=Count.choice, data='×÷'),
            Start(Const('Уможение и деление\nсо сложением и вычитанием'),
                  id='all_ops', state=Count.task),
            Start(Const('Статистика'), id='stats', state=Stats.period)
        ),
        getter=username_getter,
        state=StartState.start
    )
)
