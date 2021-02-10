import argparse
import logging
import socks
import json
import asyncio

from telethon import TelegramClient, events, errors, sync, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.contacts import ImportContactsRequest, GetContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import FloodWaitError

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] - %(message)s', level=logging.INFO)

API_ID = 0
API_HASH = ""
s_string = ""

def confirm_result(raw, data):
    results_file = open("checked.json", "r")
    old_data = results_file.read()
    results_file.close()
    results_file = open("checked.json", "w")
    if old_data:
        old_data = json.loads(old_data)
        if old_data.get(raw, None):
            for k in old_data[raw].keys():
                if data[k] != old_data[raw][k]:
                    old_data[raw][k] = data[k]
        else:
            old_data[raw] = data
        results_file.write(json.dumps(old_data))
    else:
        results_file.write(json.dumps({raw : data}))
    results_file.close()

def configure_user(result, raw_data):
    if result:
        return  {
                    "id" : raw_data.id,
                    "first_name" : raw_data.first_name,
                    "last_name" : raw_data.last_name,
                    "username" : raw_data.username,
                    "phone" : raw_data.phone,
                    "is_bot" : raw_data.bot,
                    "is_deleted" : raw_data.deleted,
                    "has_photo" : True if raw_data.photo else False
                }
    else:
        return {"error" : raw_data}

async def check_phone(phone):
    logging.info("Check phone {}".format(phone))
    result = await client(ImportContactsRequest([InputPhoneContact(client_id=0, phone=phone, first_name="t", last_name="t")]))
    found = False
    for added_user in result.users:
        found = True
        logging.info("Got info about user with phone {}".format(phone))
        update = await client(DeleteContactsRequest(id=[added_user.id])) # We delete user from contacts, because in "result" will be
        for user_info in update.users:
            confirm_result(raw=phone, data=configure_user(result=True, raw_data=user_info)) # not actual info in fields first_name and last_name
                                                                                # because we set them to "t". We get actual info when we delete him
    if not found:
        confirm_result(raw=phone, data=configure_user(result=False, raw_data="End of requests limit or no user with this phone"))
    
    await client.disconnect()

async def check_username(username):
    logging.info("Check username {}".format(username))
    while True:
        try:
            user_info = await client(GetFullUserRequest(username))
        except ValueError:
            logging.info("Value Error. No user with this username")
            confirm_result(raw=username, data=configure_user(result=False, raw_data="User with this username not found"))
            break
        except TypeError:
            logging.info("Type Error. This username is channel/group")
            confirm_result(raw=username, data=configure_user(result=False, raw_data="Channel/group with this username exists. Not user"))
            break
        except FloodWaitError as err:
            logging.info("Required sleep for {} seconds".format(err.seconds))
            asyncio.sleep(err.seconds)
            continue
        logging.info("Got info about user with username {}".format(username))
        confirm_result(raw=username, data=configure_user(result=True, raw_data=user_info.user))
        break
    await client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check username or phone number")
    parser.add_argument("-p", help="Enter phone number")
    parser.add_argument("-u", help="Enter telegram username")
    parser.add_argument("--tor", help="Enable tor socks proxy")
    args = parser.parse_args()
    proxy = (socks.SOCKS5, '127.0.0.1', 9050) if args.tor else None

    client = TelegramClient(StringSession(s_string), API_ID, API_HASH, proxy=proxy).start()

    if args.p:
        phone = "".join(filter(str.isdigit, args.p))
        if len(phone) == 11 and phone.startswith("8"):
            phone = "7" + phone[1:]
        client.loop.create_task(check_phone(phone))
    elif args.u:
        client.loop.create_task(check_username(args.u))

    client.run_until_disconnected()