# python-signalr-client
**Python** signalR client using asyncio.
It's mainly based on [TargetProcess signalR client](https://github.com/TargetProcess/signalr-client-py) which uses gevent and
[python-signalr-client](https://github.com/slazarov/python-signalr-client) from Stanislav Lazarov

# Road map
- Error handling

# Notices
None right now.

# Performance and supplemental libraries
* For better performance users can install `uvloop` and `ujson` which are automatically detected.
* Users can pass a custom session to the client, i.e a [`cfscrape`](https://github.com/Anorov/cloudflare-scrape) session in order to bypass Cloudflare.

# Compatibility
Asyncio requires Python 3.5+.

For Python2.X compatibility try [TargetProcess' gevent based SignalR client](https://github.com/TargetProcess/signalr-client-py).

# Installation
#### Pypi (most stable)
```python
pip install signalr-client-aio
```
#### Github (master)
```python
pip install git+https://github.com/r3bers/python-signalr-client.git
```
#### Github (work in progress branch)
```python
pip install git+https://github.com/r3bers/python-signalr-client.git@next-version-number
```

# Sample usage
```python
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
```

# Change log
0.0.2.8.2 - 01/09/2020:
* Change Sample Bittrex API to v3 and client version to 2.0

0.0.1.6.2 - 16/04/2018:
* * Removed `uvloop` as a requirement. However, it will be detected and utilized if installed.

0.0.1.5 - 06/04/2018:
* Removed `cfscrape` from package. Users can optionally pass a `cfscrape` session to clients.
* Removed `ujson`. The package will automatically detect if the user chooses to use `ujson`.

0.0.1.0 - Initial release.
