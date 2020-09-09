#!/usr/bin/env python
import asyncio
import json
from base64 import b64decode
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zlib import decompress, MAX_WBITS

from picotui.context import Context
from picotui.defs import *
from picotui.screen import Screen
from picotui.widgets import *

from signalr_aio import Connection


class MyBittrex:

    def __init__(self):
        self.url = 'https://socket-v3.bittrex.com/signalr'
        self.trade = 0.0
        self.ticker = 0.0
        self.tickers = -1
        self.book = -1
        self.summary = 0.0
        self.summaries = -1
        self.candle = -1
        self.last_state = self.current_time()
        self.last_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.last_message = ""

        # Schedule three calls *concurrently*:
        # Create connection
        # Users can optionally pass a session object to the client, e.g a cfscrape session to bypass cloudflare.
        self.con_master = Connection(self.url, session=None)

        # Register hub
        self.hub_master = self.con_master.register_hub('c3')

        # Assign debug message handler. It streams unfiltered data, uncomment it to test.
        # self.con_master.received += self.on_debug

        # Assign Time of last packet
        self.con_master.received += self.on_time

        # Assign error handler
        self.con_master.error += self.on_error

        # Assign hub message handler
        self.public_methods = [
            {'method': 'candle', 'routine': self.on_candle, 'subscribe': 'candle_ETH-BTC_HOUR_1'},
            {'method': 'heartbeat', 'routine': self.on_heartbeat, 'subscribe': 'heartbeat'},
            {'method': 'marketSummaries', 'routine': self.on_summaries, 'subscribe': 'market_summaries'},
            {'method': 'marketSummary', 'routine': self.on_summary, 'subscribe': 'market_summary_LTC-BTC'},
            {'method': 'orderBook', 'routine': self.on_book, 'subscribe': 'orderbook_ADA-BTC_1'},
            {'method': 'tickers', 'routine': self.on_tickers, 'subscribe': 'tickers'},
            {'method': 'ticker', 'routine': self.on_ticker, 'subscribe': 'ticker_TRX-BTC'},
            {'method': 'trade', 'routine': self.on_trade, 'subscribe': 'trade_BTC-USD'},
        ]

        for method in self.public_methods:
            self.hub_master.client.on(method['method'], method['routine'])
            self.hub_master.server.invoke('Subscribe', [[method['subscribe']]])

        # Start the client
        self.con_master.start()

    @staticmethod
    async def process_message(message):
        try:
            deflated_msg = decompress(b64decode(message), -MAX_WBITS)
            return json.loads(deflated_msg.decode())
        except Exception as ChoCho:
            print(ChoCho.args)
            return message

    # Create time handler.
    async def on_time(self, **msg):
        self.last_message = msg
        self.last_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # Create debug message handler.
    @staticmethod
    async def on_debug(**msg):
        print("Debug information: ", end='')
        print(str(msg))

    # Create error handler
    @staticmethod
    async def on_error(msg):
        if 'E' in msg:
            print('Error: ' + msg['E'])
        if 'M' in msg:
            print('Received method: ' + str(msg['M']))
        if 'A' in msg:
            print('Received message: ' + str(msg['A']))

    @staticmethod
    def current_time():
        return (Decimal.from_float(datetime.now().timestamp()) * 1000).quantize(Decimal("1"), ROUND_HALF_UP)

    async def on_message(self, msg):
        decoded_msg = await self.process_message(msg[0])
        print(decoded_msg)

    async def on_candle(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.candle = decoded_msg['sequence']

    async def on_heartbeat(self, msg):
        self.last_message = msg
        # print('.', end='')
        self.last_state = self.current_time()

    async def on_summaries(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.summaries = decoded_msg['sequence']

    async def on_summary(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.summary = decoded_msg['percentChange']

    async def on_book(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.book = decoded_msg['sequence']

    async def on_tickers(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.tickers = decoded_msg['sequence']

    async def on_ticker(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.ticker = decoded_msg['lastTradeRate']

    async def on_trade(self, msg):
        decoded_msg = await self.process_message(msg[0])
        self.trade = decoded_msg['deltas'][0]['rate']

    def restart(self):
        for method in self.public_methods:
            self.hub_master.server.invoke('Subscribe', [[method['subscribe']]])
        self.con_master.start()
        self.last_state = self.current_time()


async def main():
    connect_error = 0
    freeze = False
    bit = MyBittrex()
    try:
        import termios
        can_term = True
        with Context():
            Screen.attr_color(C_WHITE, C_BLACK)
            Screen.cls()
            Screen.attr_reset()
            d = Dialog(1, 1, 30, 11)

            d.add(1, 1, "Heartbeat: ")
            d.add(4, 2, "Candle:")
            d.add(1, 3, "Summaries:")
            d.add(3, 4, "Summary:")
            d.add(6, 5, "Book:")
            d.add(3, 6, "Tickers:")
            d.add(4, 7, "Ticker:")
            d.add(5, 8, "Trade:")
            d.add(6, 9, "Time:")

            b = WButton(8, "")
            d.add(12, 1, b)
            b.finish_dialog = ACTION_CANCEL

            w_candle = WLabel("", w=14)
            d.add(12, 2, w_candle)

            w_summaries = WLabel("", w=14)
            d.add(12, 3, w_summaries)

            w_summary = WLabel("", w=14)
            d.add(12, 4, w_summary)

            w_book = WLabel("", w=14)
            d.add(12, 5, w_book)

            w_tickers = WLabel("", w=14)
            d.add(12, 6, w_tickers)

            w_ticker = WLabel("", w=14)
            d.add(12, 7, w_ticker)

            w_trade = WLabel("", w=14)
            d.add(12, 8, w_trade)

            w_time = WLabel("", w=19)
            d.add(12, 9, w_time)

            d.redraw()

    except ImportError:
        can_term = False
    while True:
        if can_term:
            await asyncio.sleep(2)
            with Context():
                b.disabled = bit.last_state < (bit.current_time() - 2000)
                b.t = str((bit.current_time() - bit.last_state) / 1000) + 's'
                w_candle.t = str(bit.candle)
                w_summaries.t = str(bit.summaries)
                w_summary.t = str(bit.summary) + '%'
                w_book.t = str(bit.book)
                w_tickers.t = str(bit.tickers)
                w_ticker.t = str(bit.ticker)
                w_trade.t = str("%.2f" % float(bit.trade))
                w_time.t = bit.last_date
                d.redraw()
        else:
            await asyncio.sleep(5)
            if bit.last_state < (bit.current_time() - 10000) and not freeze:
                print(str(bit.last_date) + " — Heartbeat didn't get more than 10 sec")
                freeze = True
                connect_error = 1
                if bit.con_master.started:
                    bit.con_master.close()
            elif freeze and bit.last_state > (bit.current_time() - 10000):
                freeze = False
                print("Heartbeat Unfreezes")
            elif not freeze:
                print(".", end='')
                # print(str(bit.last_date) + ' — Candle: ' + str(bit.candle) +
                #       ', Summaries: ' + str(bit.summaries) +
                #       ', Summary: ' + str(bit.summary) +
                #       '%, Book: ' + str(bit.book) +
                #       ', Tickers: ' + str(bit.tickers) +
                #       ', Ticker: ' + str(bit.ticker) +
                #       ', Trade: ' + str(bit.trade) +
                #       ' — OK: ' + str((bit.current_time() - bit.last_state) / 1000) + 's')
            elif connect_error > 0:
                print(str(bit.last_date) + ' — Reconnect try ' + str(connect_error) + ': ', end='')
                try:
                    bit.restart()
                    connect_error = 0
                    freeze = False
                    print('Success.')
                except Exception as some_ex:
                    print('Error: ' + str(some_ex))
                    connect_error += 1
                    await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
