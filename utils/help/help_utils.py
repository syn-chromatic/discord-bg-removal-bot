from nextcord import Embed
from nextcord.ext.commands import Context

from typing import Optional

from utils.general_utils import EmbedForm
from utils.help.help_dcs import CommandInputType, InputDescription
from bot_instance import BotClient

client = BotClient()
bot = client.get_bot()


class HelpMenuBase:
    def __init__(self) -> None:
        self._description: str = ""
        self._input_descriptions: set[InputDescription] = set()
        self._embed_form = self._get_embed_form()
        self._bot_prefix = str(bot.command_prefix)

    def _get_embed_form(self):
        embed_form = EmbedForm().set_white()
        return embed_form

    def _add_embed_field(self, name: str, value: str, inline: bool):
        self._embed_form.add_field(name, value, inline)

    def _set_owner(self):
        embed = self._embed_form.get_embed()
        owner_name = client.get_owner_name()
        owner_avatar = client.get_owner_avatar()
        embed.set_author(
            name=owner_name,
            icon_url=owner_avatar,
        )
        self._embed_form._embed = embed

    def _set_client(self):
        client_avatar = client.get_client_avatar()
        embed = self._embed_form.get_embed()
        embed.set_thumbnail(url=client_avatar)
        self._embed_form._embed = embed

    def _set_input_descriptions(self):
        input_desc_str = ""
        input_descriptions = sorted(self._input_descriptions, key=lambda x: x.pos)
        for input_desc in input_descriptions:
            input_desc_str += input_desc.text
            input_desc_str += "\n"

        concat_desc = self._description + "\n\n" + input_desc_str
        self._embed_form.set_description(concat_desc)

    def _get_input_type_header(self, input_type: Optional[CommandInputType]) -> str:
        if input_type:
            return input_type.header
        return ""

    def _add_input_type_descriptions(self, input_type: Optional[CommandInputType]):
        if input_type:
            self._input_descriptions.update({*input_type.input_descriptions})

    def _get_prefix(self, custom_prefix: Optional[str]) -> str:
        if custom_prefix:
            return custom_prefix
        return self._bot_prefix

    def _get_field_name(
        self,
        name: str,
        input_type: Optional[CommandInputType],
        custom_prefix: Optional[str],
    ) -> str:
        input_header = self._get_input_type_header(input_type)
        prefix = self._get_prefix(custom_prefix)
        field_name = f"**{prefix}{name}**"
        if input_header:
            field_name += f" {input_header}"
        return field_name

    def _get_field_value(self, value: str):
        return f"*{value}*"

    @staticmethod
    def _get_support_link() -> str:
        return "[BuyMeACoffee](https://www.buymeacoffee.com/synchromatic)"


class HelpMenu(HelpMenuBase):
    def __init__(self) -> None:
        super().__init__()

    def set_title(self, title: str):
        self._embed_form.set_title(title)
        return self

    def set_description(self, description: str):
        self._description = description
        return self

    def add_command(
        self,
        name: str,
        value: str,
        input_type: Optional[CommandInputType] = None,
        inline: bool = False,
        custom_prefix: Optional[str] = None,
    ):
        field_name = self._get_field_name(name, input_type, custom_prefix)
        field_value = self._get_field_value(value)
        self._add_input_type_descriptions(input_type)
        self._add_embed_field(field_name, field_value, inline)

    def add_support_link(self):
        support_value = self._get_support_link()
        self._add_embed_field("Support Developer", support_value, False)

    def get_embed(self) -> Embed:
        self._set_owner()
        self._set_client()
        self._set_input_descriptions()
        embed = self._embed_form.get_embed()
        return embed

    async def reply(self, ctx: Context):
        embed = self.get_embed()
        await ctx.reply(embed=embed, mention_author=False)
