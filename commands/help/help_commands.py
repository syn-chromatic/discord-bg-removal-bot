from bot_instance import BotClient
from utils.general_utils import EmbedForm


client = BotClient()
bot = client.get_bot()


@bot.command()
async def help(ctx):
    bot_user = client.get_client_user()
    bot_avatar_url = bot_user.avatar.url if bot_user.avatar else ""

    embed_form = EmbedForm().set_white()
    embed_form.set_title(f"**{client.get_client_user().name}**")
    embed = embed_form.get_embed()

    embed.set_thumbnail(url=bot_avatar_url)
    embed.add_field(
        name=f"**{bot.command_prefix}helpbgr**",
        value="*Automatic Background Removal*",
        inline=True,
    )

    buymeacoffee = "[BuyMeACoffee](https://www.buymeacoffee.com/synchromatic)"
    embed.add_field(name="**Support Developer**", value=buymeacoffee, inline=False)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command(description="")
async def helpbgr(ctx):
    bot_user = client.get_client_user()
    bot_avatar_url = bot_user.avatar.url if bot_user.avatar else ""

    description = (
        "`[IMAGE]` ― *Expects attachment*\n"
        "`[R\\IMAGE]` ― *Expects reference attachment*\n"
    )

    embed_form = EmbedForm().set_white()
    embed_form.set_title("Automatic Background Removal")
    embed_form.set_description(description)
    embed = embed_form.get_embed()

    embed.set_thumbnail(url=bot_avatar_url)
    embed.add_field(
        name=f"**{bot.command_prefix}rembg** `[IMAGE]` ⚬ `[R\\IMAGE]`",
        value="*Removes background from media.*",
        inline=False,
    )
    await ctx.channel.send(embed=embed)
