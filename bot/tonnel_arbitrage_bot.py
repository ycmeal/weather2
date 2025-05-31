"""Telegram bot for arbitrage opportunities on Tonnel Marketplace.

This script scans the marketplace for specified models and notifies
about offers that are cheaper than the current floor price.

Configuration is provided via environment variables loaded from a
```.env``` file.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Set

from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode
import schedule

# This import assumes the ``tonnelmp`` package provides a ``Client``
# class with methods to interact with the Tonnel API. Adjust as needed
# for the actual library.
try:
    from tonnelmp import Client
except ImportError:  # pragma: no cover - library might not be available during tests
    Client = None  # type: ignore


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_models(path: str = "models.txt") -> List[str]:
    """Load gift models from a text file."""
    models: List[str] = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    models.append(line)
    return models


def load_processed(path: str = "processed.json") -> Set[str]:
    """Load set of already processed listing IDs."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    return set()


def save_processed(processed: Set[str], path: str = "processed.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)


@dataclass
class Config:
    tonnel_api_key: str
    tg_bot_token: str
    tg_chat_id: str
    interval_minutes: int = 5
    threshold_percent: float = 30.0


class ArbitrageBot:
    def __init__(self, cfg: Config):
        if Client is None:
            raise RuntimeError("tonnelmp package is required but not installed")

        self.cfg = cfg
        self.client = Client(api_key=cfg.tonnel_api_key)
        self.bot = Bot(token=cfg.tg_bot_token)
        self.models = load_models()
        self.processed = load_processed()

    def _send_message(self, text: str) -> None:
        logger.info("Sending telegram notification: %s", text)
        self.bot.send_message(chat_id=self.cfg.tg_chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

    def _check_model(self, model: str) -> None:
        logger.info("Checking model: %s", model)
        try:
            offers = self.client.get_offers(model)
        except Exception as exc:  # pragma: no cover - network errors ignored
            logger.error("Failed to fetch offers for %s: %s", model, exc)
            return

        if not offers:
            return

        floor_price = min(o["price"] for o in offers)
        threshold_price = floor_price * (1 - self.cfg.threshold_percent / 100)

        for offer in offers:
            offer_id = str(offer.get("id"))
            price = offer.get("price")
            if offer_id in self.processed:
                continue
            if price <= threshold_price:
                diff_percent = (price - floor_price) / floor_price * 100
                message = (
                    f"\U0001F9F2 <b>Найден дешёвый подарок для арбитража!</b>\n"
                    f"\U0001F381 Модель: {model}\n"
                    f"\U0001F4B0 Цена: {price}₽\n"
                    f"\U0001F4C9 Floor: {floor_price}₽\n"
                    f"\U0001F4CA Разница: {diff_percent:.1f}%\n"
                    f"\U0001F6D2 <a href='https://market.tonnel.network/item/{offer_id}'>Купить сейчас</a>"
                )
                self._send_message(message)
                # Mark as processed
                self.processed.add(offer_id)

        save_processed(self.processed)

    def check_marketplace(self) -> None:
        logger.info("Starting marketplace check")
        self.models = load_models()  # reload models each cycle
        for model in self.models:
            self._check_model(model)
        logger.info("Check complete")

    def run(self) -> None:
        logger.info("Bot started")
        schedule.every(self.cfg.interval_minutes).minutes.do(self.check_marketplace)
        while True:
            schedule.run_pending()
            time.sleep(1)


def load_config() -> Config:
    load_dotenv()
    return Config(
        tonnel_api_key=os.environ.get("TONNEL_API_KEY", ""),
        tg_bot_token=os.environ.get("TG_BOT_TOKEN", ""),
        tg_chat_id=os.environ.get("TG_CHAT_ID", ""),
        interval_minutes=int(os.environ.get("CHECK_INTERVAL_MINUTES", "5")),
        threshold_percent=float(os.environ.get("ARBITRAGE_THRESHOLD_PERCENT", "30")),
    )


if __name__ == "__main__":
    config = load_config()
    bot = ArbitrageBot(config)
    bot.run()
