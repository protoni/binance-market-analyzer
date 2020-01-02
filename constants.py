from enum import Enum, auto

# Starting time for finding the first data point from the candle data
BTC_GENESIS_BLOCK_DATE = '2009-01-03'

# Average size on disk of 1 candle datapoint (bytes)
AVERAGE_CANDLE_LINE_SIZE = 128

# Binance API base URL
BASE_URL_BN = "https://api.binance.com"

# Binance API asset listings URL
ASSETS_URL = "{}/api/v1/exchangeInfo".format(BASE_URL_BN)

# Binance API candle data URL
CANDLES_URL = "{}/api/v3/klines".format(BASE_URL_BN)

# Candle data intervals
INTERVALS = [
'1m',
'3m',
'5m',
'15m',
'30m',
'1h',
'2h',
'4h',
'6h',
'8h',
'12h',
'1d',
'3d',
'1w',
'1M'
]

# Data indexes in candle data list
CANDLE_OPEN_TIME_IDX = 0
CANDLE_OPEN_IDX = 1
CANDLE_HIGH_IDX = 2
CANDLE_LOW_IDX = 3
CANDLE_CLOSE_IDX = 4
CANDLE_VOLUME_IDX = 5
CANDLE_CLOSE_TIME_IDX = 6
CANDLE_QUOTE_ASSET_VOL_IDX = 7
CANDLE_NUM_OF_TRADEX_IDX = 8
CANDLE_TAKER_BUY_BASE_ASSET_VOL_IDX = 9
CANDLE_TAKER_BUY_QUOTE_ASSET_VOL_IDX = 10
CANDLE_IGNORE_IDX = 11