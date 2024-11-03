from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Tasks


async def add_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
):

    stmt = upsert(User).values(
        {
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
        }
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=['telegram_id'],
        set_=dict(
            first_name=first_name,
            last_name=last_name,
        ),
    )
    await session.execute(stmt)
    await session.commit()


async def add_or_update_task(
    session: AsyncSession,
    telegram_id: int,
    task_type: str,
):
    async with session.begin():
        stmt = select(Tasks).filter_by(user_id=telegram_id,
                                       created_at=date.today())
        result = await session.execute(stmt)

        try:
            task_record = result.scalar_one()
            current_value = getattr(task_record, task_type)
            setattr(task_record, task_type, current_value+1)
            await session.commit()

        except NoResultFound:
            new_task = Tasks(
                user_id=telegram_id,
                multi=1 if task_type == "multi" else 0,
                div=1 if task_type == "div" else 0,
                all_ops=1 if task_type == "all_ops" else 0
            )
            session.add(new_task)
            await session.commit()


async def get_daily_results(
    session: AsyncSession,
    telegram_id: int,
    selected_date: date
):
    stmt = select(Tasks).filter_by(user_id=telegram_id,
                                   created_at=selected_date)
    result = await session.execute(stmt)
    task_record = result.scalar_one_or_none()
    return task_record


async def get_interval_results(
    session: AsyncSession,
    telegram_id: int,
    selected_date: date
):
    end_date = date.today()
    start_date = selected_date
    stmt = (
        select(
            func.sum(Tasks.multi).label('multi'),
            func.sum(Tasks.div).label('div'),
            func.sum(Tasks.all_ops).label('all_ops'),
            func.sum(Tasks.total).label('total'),
        )
        .filter(Tasks.user_id == telegram_id)
        .filter(Tasks.created_at.between(start_date, end_date))
    )
    result = await session.execute(stmt)
    task_records = result.fetchone()
    return task_records


async def get_all_stats(
    session: AsyncSession,
):
    stmt = (
        select(
            User.first_name,
            User.last_name,
            func.sum(Tasks.multi),
            func.sum(Tasks.div),
            func.sum(Tasks.all_ops),
            func.sum(Tasks.total)
        )
        .join(Tasks, User.telegram_id == Tasks.user_id)
        .group_by(User.telegram_id)
        .order_by(User.last_name, User.first_name)
    )

    result = await session.execute(stmt)
    summary = result.fetchall()
    return summary
