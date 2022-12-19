def set_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("nextcord")
    logger.setLevel(level=logging.INFO)


if __name__ == "__main__":
    import logging

    set_logger()

    import inits
    import events
    from bot_instance import BotClient

    __all__ = ["inits", "events"]
    BotClient().run_bot()
