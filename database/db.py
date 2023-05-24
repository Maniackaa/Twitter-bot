import asyncio
import datetime
import sys

from sqlalchemy import create_engine, ForeignKey, Date, String, \
    UniqueConstraint, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import config

print(f"mysql+aiomysql:/{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}")
engine = create_async_engine(f"mysql+asyncmy://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}", echo=False)


class Base(DeclarativeBase):
    pass


class Tweet(Base):
    __tablename__ = 'tweets'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    date: Mapped[datetime] = mapped_column(DateTime())
    text: Mapped[str] = mapped_column(String(255))
    addet_time: Mapped[str] = mapped_column(DateTime(), default=str(
        datetime.datetime.now()))
    volume: Mapped[float] = mapped_column(Float(), nullable=True)
    __table_args__ = (UniqueConstraint('date', 'text', name='tweet_row'),)


    def __repr__(self):
        return f'{self.id}. {self.date} {self.text}'


class BotSettings(Base):
    __tablename__ = 'bot_settings'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    name: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(50), nullable=True, default='')
    description: Mapped[str] = mapped_column(String(255),
                                             nullable=True,
                                             default='')

# Base.metadata.create_all(engine)


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == '__main__':
    if sys.version_info[:2] == (3, 7):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_models())
        loop.run_until_complete(asyncio.sleep(2.0))
    finally:
        loop.close()

