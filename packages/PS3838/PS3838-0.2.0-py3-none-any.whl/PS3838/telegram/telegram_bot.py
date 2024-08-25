import logging
from typing import Dict

import requests


class CustomLogger:
    """
    This class creates a custom logger that can log to a file and send messages to a Telegram chat and a .log file.
    """
    def __init__(
            self, 
            name : str, 
            log_file : str = None, 
            func : str = "retrieving", 
            credentials : Dict[str, str] = None,
            *args, 
            **kwargs
        ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        if log_file:
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG) # Log everything to the file

            # Insert a newline before starting a new logging session (only for clarity)
            with open(log_file, 'a') as f:
                f.write('\n')

            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Telegram handler
        if 'telegram_token' in credentials.keys() and 'telegram_chat_id' in credentials.keys():
            telegram_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            telegram_handler = TelegramBotHandler(credentials['telegram_token'], credentials['telegram_chat_id'], func)
            telegram_handler.setLevel(logging.INFO)  # Only INFO and above will be sent to Telegram
            telegram_handler.setFormatter(telegram_formatter)
            self.logger.addHandler(telegram_handler)
        else:
            self.logger.error("No Telegram credentials provided. Telegram logging will not work.")
    
    def get_logger(self):
        return self.logger
    
class TelegramBotHandler(logging.Handler):
    """
    This class is a custom logging handler that sends messages to a Telegram chat.
    """
    def __init__(self, token : str, chat_id : str, func : str):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.func = func
        self.display_new_betting_request()
    
    def send_msg(self, msg):
        if self.chat_id:
            apiURL = f"https://api.telegram.org/bot{self.token}/sendMessage"
            response = requests.post(
                apiURL, json={"chat_id": self.chat_id, "text": msg}
            )

    def format(self, record):
        emoji = self.get_emoji(record.levelname)
        if record.levelname == "INFO":
            return f"{emoji} {record.message}"
        return f"{emoji} {record.levelname} - {record.message}"

    def emit(self, record):
        log_entry = self.format(record)
        self.send_msg(log_entry)

    def display_new_betting_request(self):
        # Create a decorative header
        if self.func == "betting":
            header = (
                "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨\n"
                f"🕒 Betting Request Started 🕒\n"
                "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨\n"
            )
            # Send the header and messages
            self.send_msg(header)
            self.send_msg("🎉 New matches to bet on 🎉")
        if self.func == "retrieving":
            header = (
                "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨\n"
                f"🕒 Retrieving Request Started 🕒\n"
                "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨\n"
            )
            # Send the header and messages
            self.send_msg(header)
            self.send_msg("🎉 New matches to retrieve 🎉")

        self.send_msg("🔍 Let's see how it goes...")

    def get_emoji(self, levelname):
        emojis = {
            "DEBUG": "🐞",
            "INFO": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🔥"
        }
        return emojis.get(levelname, "ℹ️")

