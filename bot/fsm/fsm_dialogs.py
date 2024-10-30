from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage, Redis

redis = Redis(host='localhost', port=6379, db=2)

storage = RedisStorage(
    redis=redis,
    key_builder=DefaultKeyBuilder(with_destiny=True)
    )


class StartState(StatesGroup):
    start = State()


class Count(StatesGroup):
    choice = State()
    task = State()


class Stats(StatesGroup):
    period = State()
    calendar = State()
    stats = State()
