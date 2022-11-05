def report_error(error):
    input(error)
    sys.exit()


def run_bot():
    bot_token = bot_config.BOT_TOKEN
    command_prefix = bot_config.COMMAND_PREFIX
    relay_channel_id = bot_config.RELAY_CHANNEL_ID

    if not bot_token:
        report_error(
            "Misconfiguration in /variables/bot_keys.py\n"
            "Configure the BOT_TOKEN variable."
        )

    if not command_prefix:
        report_error(
            "Misconfiguration in /variables/bot_config.py\n"
            "Configure the COMMAND_PREFIX variable."
        )

    if not isinstance(relay_channel_id, int) and relay_channel_id is not None:
        report_error(
            "Misconfiguration in /variables/bot_config.py\n"
            "RELAY_CHANNEL_ID must be an integer."
        )

    try:
        bot.run(bot_token)
    except Exception as error:
        report_error(error)


if __name__ == '__main__':
    import sys
    import logging
    import bot_instance

    from variables import bot_config

    import inits
    import events

    __all__ = ["inits", "events"]

    logging.basicConfig(level=logging.INFO)

    bot = bot_instance.BOT
    run_bot()
