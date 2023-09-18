from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass
class BotConfig:
    token: str
    link: str
    # admin_ids: list


@dataclass
class MirrorConfig:
    bot_link: str

@dataclass
class MYSQLConfig:
    host: str
    password: str
    user: str
    database: str
    port: str


@dataclass
class Config:
    bot: BotConfig
    mirror: MirrorConfig
    mysql: MYSQLConfig

    def __init__(self):
        load_dotenv('.env')
        
        self.bot = BotConfig(
            token=os.getenv("BOT_TOKEN"),
            link=os.getenv('BOT_LINK'))

        self.mirror = MirrorConfig(bot_link=os.getenv("MIRROR_BOT_LINK"))

        self.mysql = MYSQLConfig(
            host=os.getenv('MYSQL_HOST'),
            password=os.getenv('MYSQL_PASSWORD'),
            user=os.getenv('MYSQL_USER'),
            database=os.getenv('MYSQL_DATABASE'),
            port=os.getenv('MYSQL_PORT'))