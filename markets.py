from binance.client import Client
import requests
import json
import time
import datetime
import ciso8601
import utils
import os
import pickle

BTC_GENESIS_BLOCK_DATE = '2009-01-03'

# (bytes)
AVERAGE_CANDLE_LINE_SIZE = 128

# Binance base URL
BASE_URL_BN = "https://api.binance.com"
ASSETS_URL = "{}/api/v1/exchangeInfo".format(BASE_URL_BN)
CANDLES_URL = "{}/api/v3/klines".format(BASE_URL_BN)

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

client = Client("api-key", "api-secret", {"verify": False, "timeout": 1800})

#startTime = getCurrentTimestamp()
#klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1HOUR, "1 Jan, 2014", "02 Jan, 2020")
#print("count: " + str(len(klines)))
#endTime = getCurrentTimestamp()

#print("elapsed time python api: " + str(endTime - startTime))

#print("count: " + str(len(klines)))

#print(client.get_exchange_info())

#klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1MINUTE, "23 Dec, 2008", "25 Dec, 2008")
#print("count: " + str(len(klines)))

#with open('minuteCandlesAllmin1.txt', 'w') as outfile:
#    json.dump(klines, outfile)

#with open('minuteCandlesAllmin1.txt') as json_file:
#    print(str(len(json.load(json_file))))





def getFirstKline(params):
    limitOld = params['limit']
    
    # Temporarily change limit to 1
    params["limit"] = 1
    
    r = requests.get(CANDLES_URL, params=params)
    #print(r.url)
    # Change limit back to old value
    params["limit"] = limitOld
    
    return json.loads(r.content)

def getFirstKlineTimestamp(params):
    kline = getFirstKline(params)
    
    return kline[0][6]

def createFolderRecursively(path):
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
            print("Created a new folder for Candle data: " + path)
    except OSError:
        print ("Creation of the directory %s failed" % path)

def getCandleFilePath(symbol):
    parentDir = os.getcwd().replace('\\', '/')
    path = parentDir + '/candles/' + symbol
    
    return path

def getIntervalFileName(interval):
    # Convert '1M' ( one month ) interval to '1month'. Other wise it will get mixed with 1 minute candle '1m'
    if interval[-1] == 'M':
        return interval.split('M')[0] + "month"
    else:
        return interval

def getCandleFileName(symbol, interval):
    parentDir = os.getcwd().replace('\\', '/')
    
    path = parentDir + '/candles/' + symbol + "/" + getIntervalFileName(interval)
    
    return path

def checkFolderStructure(symbol, interval):
    path = getCandleFilePath(symbol)
    #print(path)
    if os.path.isdir(path):
       
        if getIntervalFileName(interval) in os.listdir(path):
        #if os.path.exists(getCandleFileName(symbol, interval)):
            
            return True
    else:
        createFolderRecursively(path)
        return False

def countDataSizeToFetch(symbol, ignoreExisting):
    count = 0
    countTemp = 0
    for interval in INTERVALS:
        if not checkFolderStructure(symbol, interval) or ignoreExisting:
            countTemp = getCandleDataCountForSymbol(symbol, interval)
            count += countTemp
            print("Symbol: " + symbol + " with interval: " + interval + " data count: " + str(countTemp))
    
    print("totalData: " + str(count) + " Estimated size: " + str((count * AVERAGE_CANDLE_LINE_SIZE) / 1000) + " kB")
    return count
        
def createFolderStructure(symbol):
    totalData = countDataSizeToFetch(symbol, False)
    fetchedData = 0
    
    intervalsToLoad = []
    for interval in INTERVALS:
        if not checkFolderStructure(symbol, interval):
            intervalsToLoad.append(interval)
        else:
            print("Symbol: " + symbol + " candle data for interval: " + interval + " exists already")
            
    for interval in intervalsToLoad:
        print("Creating candle data for symbol: " + symbol + " with interval: " + interval)
        print("totalData: " + str(totalData) + " Estimated size: " + str((totalData * AVERAGE_CANDLE_LINE_SIZE) / 1000) + " kB")
        fetchedData += get_candles(symbol, interval, utils.dateToTimestamp(BTC_GENESIS_BLOCK_DATE), utils.getCurrentTimestamp(), totalData, fetchedData)
        #print("fetched: " + str(fetchedData))

def ensureFileExists(path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.mkdirs(os.path.dirname(file_path))

def dumpListToAFile(list, file):
    pickle.dump(list, file)

def load_candles(symbol, interval):
    candleFilePath = getCandleFileName(symbol, interval)
    list = []
    f = open(candleFilePath, "r")
    for x in f:
        list.append(x.split(","))
    
    print("symbol: " + symbol + " list len: " + str(len(list)))
    print("first TS: " + list[0][6])
    print("last TS: " + list[-1][6])
#load_candles('ETH', '1M')

def listToString(list):
    string = ""
    for item in list:
        string += str(item) + ","
        
    return string

def ensureFileExists(symbol, interval):
    path = getCandleFilePath(symbol)
    
    if os.path.isdir(path):
        if not interval in os.listdir(path):
            name = getCandleFileName()
            f = open(name, 'w')
            f.write("")
            f.close()
            print("Created new file: " + name)

def getCandleStartTimeForSymbol(symbol):
    params = {
        'symbol': symbol + 'BTC',
        "interval": '1m',
        "startTime": utils.dateToTimestamp(BTC_GENESIS_BLOCK_DATE),
        "endTime": utils.getCurrentTimestamp(),
        "limit": 1
    }
    
    return getFirstKlineTimestamp(params)

def getCandleDataCountForSymbol(symbol, interval):
    return (utils.getCurrentTimestamp() - getCandleStartTimeForSymbol(symbol)) / utils.getIntervalMs(interval)

def progress(current, total):
    utils.printProgressBar(current, total, prefix = 'Progress:', suffix = 'Complete', length = 50)

def get_candles(symbol, interval, startTime, endTime, totalData, fetchedData):
    klines = []
    
    #candleFile = open(getCandleFile(symbol, interval), "w+")
    #candleFile.write("")
    #candleFile.close()
    
    candleFilePath = getCandleFileName(symbol, interval)
    candleFile = open(candleFilePath, 'a+')
    #ensureFileExists(candleFile)
    
    params = {
        'symbol': symbol + 'BTC',
        "interval": interval,
        "startTime": startTime,
        "endTime": endTime,
        "limit": 1000
    }
    first = getFirstKlineTimestamp(params)
    totalOneCandle = (endTime - first) / utils.getIntervalMs(interval)
    
    
    count = 0
    valuesAdded = 1
    lastTS = 0
    #with open(candleFilePath, 'wb') as candleFile:
    while(valuesAdded > 0):
        
        klinesLenOld = len(klines)
        r = requests.get(CANDLES_URL, params=params)
        #candleFile.write(r.text)
        #print(r.text)
        
        valuesAdded = 0
        for x in json.loads(r.content):
            valuesAdded += 1
            klines.append(x)
            #print(x)
            #dumpListToAFile(x, candleFile)
            count += 1
            fetchedData += 1
            candleFile.write(listToString(x) + "\n")
            lastTS = x[6]
        
        print("valuesAdded: " + str(valuesAdded))
        #print("items saved: " + str(count))
        
        #str = json.dumps(r.content)
        #print("len: " + str(len(str)))
        #candleFile.write(json.dumps(r.content))
        #with open(candleFilePath, 'a+') as outfile:
        #    json.dump(r.content, outfile)
        
        #valuesAdded = len(klines) - klinesLenOld
        
        params['startTime'] = lastTS
        
        #print("progress: " + str((len(klines) / totalOneCandle) * 100))
        #print("Progress total for all " + symbol + " data: " + str(fetchedData / totalData * 100))
        #progress(len(klines), totalOneCandle)
        progress(fetchedData, totalData)
        
    candleFile.close()
   
    return count


#print("count: " + str(len(get_candles('ETH', '1m'))))


#dateToTimestamp('2014-12-05T12:30:45.123456-02:00')
test = utils.dateToTimestamp('2014-12-05')
current = utils.getCurrentTimestamp()

print("test: " + str(test))
print("current: " + str(current))

#startTime = utils.getCurrentTimestamp()
#print("count: " + str(len(get_candles('ETH', '1h', utils.dateToTimestamp('2014-12-05'), utils.getCurrentTimestamp()))))
#endTime = utils.getCurrentTimestamp()
#print("elapsed time python api: " + str(endTime - startTime))
#print("count: " + str(get_candles('ETH', '1h', dateToTimestamp('2014-12-05'), getCurrentTimestamp())))

#checkFolderStructure('ETH', '1m')

#createFolderStructure('ETH')
countDataSizeToFetch('ETH', True)