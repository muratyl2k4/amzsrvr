import configparser
import json

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import PeerChannel

from telethon.tl.functions.messages import GetHistoryRequest
from MarketDB import MarketDB
from MyMarketPlace import MyMarketPlace

from main_worker import work
import pandas as pd

import re


# you can get telegram development credentials in telegram API Development Tools
api_id = 29045397
api_hash = ''

# use full phone number including + and country code
phone = ''
username = ''


# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
#client.start()
#print("Client Created")
asin = ""
async def main():
    # Now you can use all client methods listed below, like for example...
    user_input_channel = 'https://t.me/linkdistributionco' #input("enter entity(telegram URL or entity id):")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity) 

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    history = await client(GetHistoryRequest(
        peer=my_channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))

    rows = history.messages[1].to_dict()['message'].split('\n')
    global asin
    asin = rows[2].strip()[-10:]

    print(rows[7].strip())

    x = re.search("\$",rows[7].strip())
    #print(x.span())
    print(history.messages[1].to_dict()['message'])

with client:
    client.loop.run_until_complete(main())


print(asin)

"""
us_market = MyMarketPlace('us')
ca = MarketDB('ca')
jp = MarketDB('ja')
au = MarketDB('au')
fr = MarketDB('fr')
de = MarketDB('de')
uk = MarketDB('uk')

markets = [ca,jp,au,fr,de,uk]



for market in markets:
    work(pd.DataFrame({'Asin' : [asin]}),us_market,market.my_market_place)
    """