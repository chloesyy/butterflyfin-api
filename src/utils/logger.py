import logging
from colorlog import ColoredFormatter


class CustomColoredFormatter(ColoredFormatter):
    def format(self, record):
        record.level_colon = f"{record.levelname}:{' ' * (8 - len(record.levelname))}"
        return super().format(record)


handler = logging.StreamHandler()
formatter = CustomColoredFormatter(
    "%(log_color)s%(level_colon)s%(reset)s %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
handler.setFormatter(formatter)
logger = logging.getLogger("butterflyfin_api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
