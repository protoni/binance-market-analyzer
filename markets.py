from binance.client import Client
import requests
import json
import time
import datetime
import ciso8601
import utils
import constants
import os
import pickle



client = Client("api-key", "api-secret", {"verify": False, "timeout": 1800})



def getFirstCandle(params):
    limitOld = params['limit']
    
    # Temporarily change limit to 1
    params["limit"] = 1
    
    r = requests.get(constants.CANDLES_URL, params=params)
    
    # Change limit back to old value
    params["limit"] = limitOld
    
    return json.loads(r.content)

def getLastCandle(params):
    r = requests.get(constants.CANDLES_URL, params=params)

    return json.loads(r.content)

def getFirstCandleTimestamp(params):
    candle = getFirstCandle(params)
    
    return candle[0][constants.CANDLE_CLOSE_TIME_IDX]

def getLastCandleTimestamp(params):
    candle = getLastCandle(params)

    return candle[-1][constants.CANDLE_CLOSE_TIME_IDX]

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

def countDataSizeToFetch(symbol, ignoreExisting, ts):
    count = 0
    countTemp = 0
    for interval in constants.INTERVALS:
        if not checkFolderStructure(symbol, interval) or ignoreExisting:
            countTemp = getCandleDataCountForSymbol(symbol, interval)
            count += countTemp
            print("Symbol: " + symbol + " with interval: " + interval + " data count: " + str(countTemp))
        
    print("totalData: " + str(count) + " Estimated size: " + str((count * constants.AVERAGE_CANDLE_LINE_SIZE) / 1000) + " kB")
    return count

def getCandleDataCountForSymbol(symbol, interval):
    return (utils.getCurrentTimestamp() - getCandleStartTimeForSymbol(symbol)) / utils.getIntervalMs(interval)

def getRemainingCandleDataCountForSymbol(symbol, interval, ts):
    return (utils.getCurrentTimestamp() - ts) / utils.getIntervalMs(interval)

def getCandleStartTimeForSymbol(symbol):
    params = {
        'symbol': symbol + 'BTC',
        "interval": '1m',
        "startTime": utils.dateToTimestamp(constants.BTC_GENESIS_BLOCK_DATE),
        "endTime": utils.getCurrentTimestamp(),
        "limit": 1
    }
    
    return getFirstCandleTimestamp(params)

def getCandleEndTimeForSymbol(symbol):
    params = {
        'symbol': symbol + 'BTC',
        "interval": '1m',
        "startTime": utils.getCurrentTimestamp() - utils.getIntervalMs('5m'),
        "endTime": utils.getCurrentTimestamp(),
        "limit": 1
    }
    
    return getLastCandleTimestamp(params)

def get_candles(symbol, interval, startTime, endTime, totalData, fetchedData):

    candleFilePath = getCandleFileName(symbol, interval)
    candleFile = open(candleFilePath, 'a+')

    params = {
        'symbol': symbol + 'BTC',
        "interval": interval,
        "startTime": startTime,
        "endTime": endTime,
        "limit": 1000
    }
    first = getFirstCandleTimestamp(params)
    totalOneCandle = (endTime - first) / utils.getIntervalMs(interval)
    
    count = 0
    valuesAdded = 1
    lastTS = 0
    saved = 0

    while(valuesAdded > 0):
        
        r = requests.get(constants.CANDLES_URL, params=params)
       
        valuesAdded = 0
        for x in json.loads(r.content):

            # How many candle data points was saved after last request
            valuesAdded += 1

            # How many candle data points was saved in total for this interval
            count += 1

            # Keep track of current total progress
            fetchedData += 1

            candleFile.write(utils.listToString(x) + "\n")

            # How many lines are saved to the file
            saved += 1

            # Save the last closing timestamp
            lastTS = x[constants.CANDLE_CLOSE_TIME_IDX]
        
        params['startTime'] = lastTS
        
        print("Progress: " + str((totalData / fetchedData) * 100) + " %")

        '''
        if valuesAdded == 0:
            # If completed, force progress bar to 100%
            utils.progress(totalData, totalData)
        else:
            utils.progress(fetchedData, totalData)
        '''
    print("saved: " + str(saved))
    
    candleFile.close()
   
    return count

def getLastTimestampSaved(symbol, interval):
    data = load_candles(symbol, interval)
    print("items loaded: " + str(len(data)))
    if len(data) > 0:
        return int(data[-1][constants.CANDLE_CLOSE_TIME_IDX])
    else:
        return -1

def isDataInSync(symbol, interval):
    latestTsAvailable = getCandleEndTimeForSymbol(symbol)
    latestTsSaved = getLastTimestampSaved(symbol, interval)

    deviation = latestTsAvailable - latestTsSaved 

    if deviation > constants.DATA_DESYNC_LIMIT:
        print("Symbol: " + symbol + " Interval: " + interval + " data de sync deviation: " + str((deviation / 1000) / 60) + " min. Syncing data.")
        
        return False
    else:
        return True

def getStartingTimestamp(symbol, interval):
    return getLastTimestampSaved(symbol, interval)

def createFolderStructure(symbol):
    
    fetchedData = 0

    intervalsToLoad = []
    for interval in constants.INTERVALS:
        if not checkFolderStructure(symbol, interval) or not isDataInSync(symbol, interval):
            intervalsToLoad.append(interval)
        else:
            print("Symbol: " + symbol + " candle data for interval: " + interval + " OK")
            
    for interval in intervalsToLoad:
        startTimeStamp = getStartingTimestamp(symbol, interval)
        
        if startTimeStamp != -1:
            totalData = getRemainingCandleDataCountForSymbol(symbol, interval, startTimeStamp)
        else:
            startTimeStamp = getCandleStartTimeForSymbol(symbol)
            totalData = getCandleDataCountForSymbol(symbol, interval)
        print("startTimeStamp: " + str(startTimeStamp))
        
        print("Creating candle data for symbol: " + symbol + " with interval: " + interval)
        print("totalData: " + str(totalData) + " Estimated size: " + str((totalData * constants.AVERAGE_CANDLE_LINE_SIZE) / 1000) + " kB")

        fetchedData += get_candles(symbol, interval, startTimeStamp, utils.getCurrentTimestamp(), totalData, fetchedData)
        #print("fetched: " + str(fetchedData))

def load_candles(symbol, interval):
    candleFilePath = getCandleFileName(symbol, interval)

    list = []

    f = utils.readFile(candleFilePath)

    if f != 0:
        for x in f:
            list.append(x.split(","))

        #print("symbol: " + symbol + " list len: " + str(len(list)))
        #print("first TS: " + list[0][constants.CANDLE_CLOSE_TIME_IDX])
        #print("last TS: " + list[-1][constants.CANDLE_CLOSE_TIME_IDX])
    
        f.close()

    return list

def reFetchCandleData(symbol, interval):
    print("Re fetcing all data for symbol: " + symbol + " with interval: " + interval)
    utils.deleteFile(getCandleFileName(symbol, interval))
    createFolderStructure(symbol)

def getTimestampDifferences(data, interval):
    if len(data) > 0:
        oldTs = int(data[0][constants.CANDLE_CLOSE_TIME_IDX])
        newTs = int(data[0][constants.CANDLE_CLOSE_TIME_IDX])
        
        # Row index
        idx = 0
        intervalMs = utils.getIntervalMs(interval)
        maxDeviance = constants.RESYNC_DATA_MISSING_TS_COUNT * intervalMs

        diffCountTotal = 0
        for row in data:
            newTs = int(data[idx][constants.CANDLE_CLOSE_TIME_IDX])

            difference = newTs - (oldTs + intervalMs)
            #print("difference for row " + str(idx) + ": " + str(difference))
            #print("maxDeviance: " + str(maxDeviance))
            if difference > maxDeviance:
                diffCountTotal += difference / maxDeviance
            oldTs = int(data[idx][constants.CANDLE_CLOSE_TIME_IDX])

            idx += 1
        

    return diffCountTotal

def getDesyncCountFromFile(symbol, interval):
    f = utils.readFile(constants.DESYNC_DATA_FILE)

    if f != 0:
        for x in f:
            row = x.split(",")
            if len(row) >= 3:
                if row[0] == symbol and row[1] == interval:
                    return int(row[2].split('.')[0])

        f.close()

    return -1

def updateItemInDeSyncReport(symbol, interval, missing):
    f = utils.readFile(constants.DESYNC_DATA_FILE)

    if f != 0:
        rows = []
        newRow = ""
        for x in f:
            row = x.split(",")
            if len(row) >= 3:
                if row[0] == symbol and row[1] == interval:
                    row[2] = str(missing)

                newRow = row[0] + "," + row[1] + "," + row[2] + ", \n"
                rows.append(newRow)
        f.close()

        # Delete old one
        archiveOldDesyncReport()
        
        # Create a new one
        for row in rows:
            utils.writeFile(constants.DESYNC_DATA_FILE, row, True)

def generateDeSyncReport(symbol, interval, missing):
    data = symbol + "," + interval + "," + str(missing) + ", \n"

    utils.writeFile(constants.DESYNC_DATA_FILE, data, True)

def checkCandleData(symbol, interval, updateDesyncFile):
    
    currentData = load_candles(symbol, interval)
    totalDataCount = getCandleDataCountForSymbol(symbol, interval)
    currentDataCount = len(currentData)
    deviance = 0

    diff = getTimestampDifferences(currentData, interval)
    
    if updateDesyncFile:
        generateDeSyncReport(symbol, interval, diff)
    else:
        diffSaved = getDesyncCountFromFile(symbol, interval)

        if diffSaved != -1:
            devianceMax = constants.RESYNC_DATA_MISSING_TS_COUNT
            deviance = diff - diffSaved
            
            if deviance > devianceMax or deviance < (devianceMax * -1):
                print("Symbol: " + symbol + " interval: " + interval + " deviance: " + str(deviance))
                reFetchCandleData(symbol, interval)
                updateItemInDeSyncReport(symbol, interval, diff)
        else:
            print("Error loading saved missing data point from a file!")
            print("Generating a new missing data point row for symbol: " + symbol + " interval: " + interval)
            generateDeSyncReport(symbol, interval, diff)

    return deviance


def archiveOldDesyncReport():
    utils.deleteFile(constants.DESYNC_DATA_FILE)

def checkAllCandleData(updateDesyncFile):
    
    itemsChecked = 0
    devianceTotal = 0

    if updateDesyncFile:
        print("Generating missing data point report..")
        archiveOldDesyncReport()
    else:
        print("Checking missing data points..")

    for interval in constants.INTERVALS:
        itemsChecked += 1
        devianceTotal += checkCandleData('ETH', interval, updateDesyncFile)

    if updateDesyncFile:
        print("Checked missing data point report.")
    else:
        print("Checked missing data points.")
        print("Checked items: " + str(itemsChecked) + ". Average deviance: " + str(devianceTotal / itemsChecked) + " Max deviance: " + str(constants.RESYNC_DATA_MISSING_TS_COUNT))

#checkAllCandleData(False)
#checkCandleData('ETH', '30m')

#checkFolderStructure('ETH', '1m')

createFolderStructure('ETH')
#countDataSizeToFetch('ETH', True)

