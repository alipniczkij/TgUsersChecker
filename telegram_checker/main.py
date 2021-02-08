import argparse
import logging
import socks
import asyncio

from telethon import TelegramClient, events, errors, sync, functions, types
from telethon.sessions import StringSession

logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

API_ID = 0
API_HASH = ""
s_string = ""

def check_phone(phone):
    raise NotImplementedError

def check_username(username):
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check username or phone number")
    parser.add_argument("-p", help="Enter phone number")
    parser.add_argument("-u", help="Enter telegram username")
    parser.add_argument("--tor", help="Enable tor socks proxy")
    args = parser.parse_args()
    proxy = (socks.SOCKS5, '127.0.0.1', 9050) if args.tor else None

    client = TelegramClient(StringSession(s_string) API_ID, API_HASH, proxy=proxy).start()

    loop = asyncio.get_event_loop()

    if args.p:
        phone = "".join(filter(str.isdigit, p))
        if len(phone) == 11 and phone.startswith("8"):
            phone = "7" + phone[1:]
        loop.run_until_complete(check_phone(phone))
    elif args.u:
        loop.run_until_complete(check_username(args.u))

    client.run_until_disconnected()