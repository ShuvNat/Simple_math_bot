from aiogram.types import CallbackQuery, FSInputFile, User
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Column, Start
from aiogram_dialog.widgets.text import Const, Format
from pandas import DataFrame, ExcelWriter
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_all_stats
from .filters import is_admin
from fsm.fsm_dialogs import Count, StartState, Stats

FILEPATH = Path(__file__).resolve().parent.parent


async def username_getter(
        dialog_manager: DialogManager,
        event_from_user: User,
        session: AsyncSession,
        **kwargs
):

    getter_data = {
            'username': event_from_user.first_name or event_from_user.username,
            'user_id': event_from_user.id
            }
    return getter_data


async def xlsx_stats(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    session = dialog_manager.middleware_data.get('session')
    list = await get_all_stats(session)
    filename = ('Статистика.xlsx')
    filepath = FILEPATH / f'files/{filename}'
    df = DataFrame(list, columns=[
        'Имя',
        'Фамилия',
        'Умножение',
        'Деление',
        '4 действия',
        'Всего',
        ])
    df.to_excel(filepath, index=False)
    with ExcelWriter(
            filepath, engine='openpyxl', mode='a'
            ) as writer:
        worksheet = writer.sheets['Sheet1']
        worksheet.title = 'Лист1'

        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[
                column_cells[0].column_letter].width = length + 2
    await callback.message.answer_document(
                FSInputFile(filepath, filename=filename)
            )
    filepath.unlink()
    await dialog_manager.start(
        StartState.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )

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
            Start(Const('Статистика'), id='stats', state=Stats.period),
            Button(Const('Скачать файл статитстики'), id='admin_stats',
                   on_click=xlsx_stats, when=is_admin)
        ),
        getter=username_getter,
        state=StartState.start
    )
)
