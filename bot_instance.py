import logging
from nextcord import ClientUser
from nextcord import Activity, ActivityType, Intents
from nextcord.ext.commands import Bot
from configuration.bot_config import BOT_TOKEN, COMMAND_PREFIX, ACTIVITY_TEXT

logger = logging.getLogger("nextcord")


class BotClientBase:
    def __init__(self):
        self._token = self._get_token()
        self._prefix = self._get_prefix()
        self._activity = self._get_activity()
        self._bot_client = self._set_bot()

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
    def _get_token():
        return BOT_TOKEN

    @staticmethod
    def _get_prefix():
        return COMMAND_PREFIX

    @staticmethod
    def _get_activity():
        return ACTIVITY_TEXT


class BotClient(BotClientBase):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance") or not isinstance(cls.instance, cls):
            logger.log(logging.INFO, "Created bot client instance.")
            cls.instance = super(BotClient, cls).__new__(cls)
            super(cls, cls.instance).__init__(*args, **kwargs)
        return cls.instance

    def get_bot(self) -> Bot:
        return self._bot_client

    def run_bot(self):
        self._run_bot()

    def get_client_user(self) -> ClientUser:
        return self._get_client_user()
