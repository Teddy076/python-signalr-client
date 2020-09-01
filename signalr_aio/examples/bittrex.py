#!/usr/bin/python
# -*- coding: utf-8 -*-

# Stanislav Lazarov

# A practical example showing how to connect to Bittrex
# Requires Python3.5+
# pip install git+https://github.com/slazarov/python-signalr-client.git
from signalr_aio import Connection
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import json


async def process_message(message):
    try:
        deflated_msg = decompress(b64decode(message), -MAX_WBITS)
        return json.loads(deflated_msg.decode())
    except Exception as ChoCho:
        print(ChoCho.args)
        return message


# Create debug message handler.
async def on_debug(**msg):
    print("Debug information: ", end='')
    print(msg)


# Create error handler
async def on_error(msg):
    print(msg)


# Create hub message handler
async def on_heartbeat(msg):
    print('.', end='')


# Create hub message handler
async def on_message(msg):
    decoded_msg = await process_message(msg[0])
    print(decoded_msg)


if __name__ == "__main__":
    # Create connection
    # Users can optionally pass a session object to the client, e.g a cfscrape session to bypass cloudflare.
    connection = Connection('https://socket-v3.bittrex.com/signalr', session=None)

    # Register hub
    hub = connection.register_hub('c3')

    # Assign debug message handler. It streams unfiltered data, uncomment it to test.
    # connection.received += on_debug

    # Assign error handler
    connection.error += on_error

    # Assign hub message handler
    hub.client.on('candle', on_message)
    hub.client.on('heartbeat', on_heartbeat)
    hub.client.on('marketSummaries', on_message)
    hub.client.on('marketSummary', on_message)
    hub.client.on('orderBook', on_message)
    hub.client.on('tickers', on_message)
    hub.client.on('ticker', on_message)
    hub.client.on('trade', on_message)

    # Public Bittrex Streams
    hub.server.invoke('Subscribe', [['candle_ETH-BTC_HOUR_1']])  # candleInterval: string  MINUTE_1, MINUTE_5, HOUR_1, DAY_1
    hub.server.invoke('Subscribe', [['heartbeat']])
    hub.server.invoke('Subscribe', [['market_summaries']])
    hub.server.invoke('Subscribe', [['market_summary_LTC-BTC']])
    hub.server.invoke('Subscribe', [['orderbook_ADA-BTC_1']])  # allowed values are [1, 25, 500]
    hub.server.invoke('Subscribe', [['tickers']])
    hub.server.invoke('Subscribe', [['ticker_TRX-BTC']])
    hub.server.invoke('Subscribe', [['trade_BTC-USD']])

    # Start the client
    connection.start()
