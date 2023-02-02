import logging
from typing import Optional


from nextcord import User, ClientUser
from nextcord import Activity, ActivityType, Intents
from nextcord.ext.commands import Bot

from configuration.bot_config import BOT_TOKEN, COMMAND_PREFIX

logger = logging.getLogger("nextcord")


class BotClientBase:
    def __init__(self):
        self._token = self._get_token()
        self._prefix = self._get_prefix()
        self._activity = self._get_activity()
        self._bot_client = self._set_bot()
        self._owner_id: Optional[int] = None

    def _set_bot(self) -> Bot:
        intents = Intents.all()
        bot_client = Bot(
            command_prefix=self._prefix,
            intents=intents,
            activity=Activity(type=ActivityType.watching, name=self._activity),
            help_command=None,
        )
        return bot_client

    def _run_bot(self):
        self._bot_client.run(self._token)

    def _get_client_user(self):
        client_user = self._bot_client.user
        if client_user:
            return client_user
        raise Exception("Bot failed to connect.")

    @staticmethod
    def _get_token() -> str:
        return BOT_TOKEN

    @staticmethod
    def _get_prefix() -> str:
        return COMMAND_PREFIX

    def _get_activity(self):
        prefix = self._get_prefix()
        return f"{prefix}help"


class BotClient(BotClientBase):
    def __init__(self):
        pass  # For Singleton class to work properly

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance") or not isinstance(cls.instance, cls):
            logger.log(logging.INFO, "Created bot client instance.")
            cls.instance = super(BotClient, cls).__new__(cls)
            super(cls, cls.instance).__init__(*args, **kwargs)
        return cls.instance

    def run_bot(self):
        self._run_bot()

    def get_bot(self) -> Bot:
        return self._bot_client

    def get_client_user(self) -> ClientUser:
        return self._get_client_user()

    def get_client_name(self) -> str:
        client = self.get_client_user()
        return str(client)

    def get_client_avatar(self) -> str:
        client = self.get_client_user()
        if client.avatar:
            return client.avatar.url
        return ""

    def get_owner(self) -> Optional[User]:
        bot = self.get_bot()
        if self._owner_id is not None:
            return bot.get_user(self._owner_id)

    def get_owner_name(self) -> str:
        owner = self.get_owner()
        if owner:
            return str(owner)
        return ""

    def get_owner_avatar(self) -> str:
        owner = self.get_owner()
        if owner and owner.avatar:
            return owner.avatar.url
        return ""
