from random import randint

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Column, Select, Start
from aiogram_dialog.widgets.text import Case, Const, Format
from operator import itemgetter

from db.requests import add_or_update_task
from fsm.fsm_dialogs import Count, StartState
from tasks import AllOperations, MultiDiv


async def keyboard_getter(
    dialog_manager: DialogManager,
    **kwargs
):
    sign = dialog_manager.start_data
    buttons = [
        ['2', f'{sign}2'],
        ['3', f'{sign}3'],
        ['4', f'{sign}4'],
        ['5', f'{sign}5'],
        ['6', f'{sign}6'],
        ['7', f'{sign}7'],
        ['8', f'{sign}8'],
        ['9', f'{sign}9'],
        ['any', 'Все сразу'],
    ]
    return {'buttons': buttons}


async def on_button_clicked(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected_item: str,
):
    dialog_manager.dialog_data['type'] = selected_item
    await dialog_manager.next()


async def text_getter(
    dialog_manager: DialogManager,
    **kwargs
):
    if dialog_manager.dialog_data.get('again') is True:
        return {'text': 1}
    elif not dialog_manager.start_data:
        return {'text': 2}
    else:
        return {'text': 3}


async def question_getter(
    dialog_manager: DialogManager,
    **kwargs
):
    try:
        type = dialog_manager.dialog_data['type']
        task = MultiDiv()
        if type == 'any':
            task.a = randint(2, 9)
        else:
            task.a = int(type)
        if dialog_manager.start_data == '×':
            func = task.multi
        elif dialog_manager.start_data == '÷':
            func = task.div
        else:
            func = task.random
    except KeyError:
        task = AllOperations()
        func = task.random_task
    func()
    dialog_manager.dialog_data['answer'] = task.answer
    dialog_manager.dialog_data['task_type'] = task.name
    data = {'question': task.question}
    return data


async def answer_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager,
):
    correct_answer = dialog_manager.dialog_data.get('answer')
    task_type = dialog_manager.dialog_data.get('task_type')
    user_answer = message.text
    if user_answer.isdigit() and int(user_answer) == correct_answer:
        dialog_manager.dialog_data['again'] = True
        session = dialog_manager.middleware_data.get('session')
        await add_or_update_task(session, message.from_user.id,
                                 task_type)
        await dialog_manager.switch_to(state=Count.task)
    else:
        dialog_manager.show_mode = ShowMode.NO_UPDATE
        await message.answer(text='Неправильно. Попробуй еще раз.')


count_dialog = Dialog(
    Window(
        Const('На сколько будешь умножать?'),
        Column(
            Select(
                    Format("{item[1]}"),
                    id="select_multi",
                    items="buttons",
                    item_id_getter=itemgetter(0),
                    on_click=on_button_clicked
                ),
            ),
        Start(Const('На старт'), id='start', state=StartState.start,
              mode=StartMode.RESET_STACK),
        getter=keyboard_getter,
        state=Count.choice,
    ),
    Window(
        Case(
            texts={
                1: Const('Правильно! Молодец!\nРешишь еще один?'),
                2: Const('Здесь нет выбора вариантов, только примеры\n'
                         'на счет в пределах 100\nРеши пример'),
                3: Const('Реши пример'),
            },
            selector='text',
        ),
        Format('{question}'),
        MessageInput(
            func=answer_handler,
            content_types=ContentType.TEXT,
        ),
        Start(Const('Достаточно'), id='start', state=StartState.start,
              mode=StartMode.RESET_STACK),
        state=Count.task,
        getter=(text_getter, question_getter),
    ),
)
