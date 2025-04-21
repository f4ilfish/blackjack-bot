import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.web.app import BlackJackApp


def setup_logging(_: 'BlackJackApp') -> None:
    logging.basicConfig(level=logging.INFO)
