import nextcord
from nextcord.errors import Forbidden
from nextcord.ext.commands import Context
from nextcord import TextChannel

from copy import copy
from io import BytesIO
from typing import Union

from variables import bot_config
from utils.media_dataclasses import RelayMessage, RelayConfig


class ConstructEmbed():
    def __init__(self):
        self._embed = nextcord.Embed()
        self._embed.color = 0x00FF00

    def message(self, message):
        self._embed.description = message
        return self

    def title(self, title):
        self._embed.title = title
        return self

    def footer(self, footer_text):
        self._embed.set_footer(text=footer_text)
        return self

    def fields(self, fields: dict[str, tuple[str, bool]]):
        for key, (value, inline_bool) in fields.items():
            self._embed.add_field(name=key, value=value, inline=inline_bool)
        return self

    def color(self, color):
        self._embed.color = color
        return self

    def is_error(self):
        self._embed.color = 0xC82323
        return self

    def get_embed(self) -> nextcord.Embed:
        return self._embed


class IteratorBase:
    def __init__(self, ctx: Context):
        self._ctx = ctx
        self._relay_id = bot_config.RELAY_CHANNEL_ID
        self._relay_channel = self._get_channel(self._relay_id)
        self._previous_relay: Union[RelayMessage, None] = None
        self._message = None
        self._error = ""

    async def _transmit(self, image: BytesIO):
        image = copy(image)

        relay_file = nextcord.File(image, filename="relay_image.png")
        if self._relay_channel:
            try:
                message = await self._relay_channel.send(file=relay_file)
                url = str(message.attachments[0])
                relay_message = RelayMessage(
                    message=message,
                    url=url,
                )
                return relay_message

            except Forbidden:
                self._error = "Missing Permissions to send messages to Relay Channel."
        self._error = "Invalid Relay Channel ID or Missing Permissions to view it."

    def _get_channel(self, channel_id):
        guild = self._ctx.guild
        if guild:
            channel = guild.get_channel(channel_id)
            if isinstance(channel, TextChannel):
                return channel

    @staticmethod
    def _init_embed(message: str):
        embed = nextcord.Embed(
            description=message,
        )
        return embed

    def _iteration_embed(
        self, relay_config: RelayConfig, relay: Union[RelayMessage, None]
    ):
        idx = relay_config.idx
        total_idx = relay_config.total_idx

        description = f"Processed {idx} out of {total_idx} frames."
        description += f"\n{self._error}"

        embed = nextcord.Embed(description=description)

        if relay:
            embed.set_image(url=relay.url)
        return embed

    def _create_embed(
        self, relay_config: RelayConfig, relay: Union[RelayMessage, None]
    ):
        if relay_config.init:
            return self._init_embed("Initializing..")

        return self._iteration_embed(relay_config, relay)

    async def _remove_previous(self):
        if self._previous_relay:
            message = self._previous_relay.message
            await message.delete()

    async def _remove_message(self):
        if self._message:
            await self._message.delete()

    async def _get_relay(self, relay_config: RelayConfig):
        image = relay_config.image
        if image:
            current_relay = await self._transmit(image)
            await self._remove_previous()
            self._previous_relay = current_relay
            return self._previous_relay

    async def _send_embed(self, embed):
        if not self._message:
            self._message = await self._ctx.reply(embed=embed)
            return
        await self._message.edit(embed=embed)


class RelayIterator(IteratorBase):
    def __init__(self, ctx: Context):
        super().__init__(ctx)

    async def send(self, relay_config: RelayConfig):
        relay = await self._get_relay(relay_config)
        embed = self._create_embed(relay_config, relay)
        await self._send_embed(embed)

    async def clean(self):
        await self._remove_previous()
        await self._remove_message()
