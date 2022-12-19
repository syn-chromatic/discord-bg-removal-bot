def report_error(error):
    input(error)
    sys.exit()


def run_bot():
    if not BOT_TOKEN:
        report_error("Configure the BOT_TOKEN variable.")

    if not COMMAND_PREFIX:
        report_error("Configure the COMMAND_PREFIX variable.")


if __name__ == "__main__":
    import sys
    from configuration.bot_config import (
        BOT_TOKEN,
        COMMAND_PREFIX,
    )

    import inits
    import events
    from bot_instance import BotClient

    __all__ = ["inits", "events"]
    BotClient().run_bot()
