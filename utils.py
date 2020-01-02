import time
import ciso8601

def dateToTimestamp(date):
    date += 'T00:00:00.000000'
    return int((time.mktime(ciso8601.parse_datetime(date).timetuple()) + 7200) * 1000)

def getCurrentTimestamp():
    return int(time.time() * 1000)

def getIntervalMs(interval):
    if(interval[-1] == 'm'):
        return (60 * 1000) * int(interval.split('m')[0])
    
    if(interval[-1] == 'h'):
        return (3600 * 1000) * int(interval.split('h')[0])
        
    if(interval[-1] == 'd'):
        return (86400 * 1000) * int(interval.split('d')[0])
        
    if(interval[-1] == 'w'):
        return (604800 * 1000) * int(interval.split('w')[0])
        
    if(interval[-1] == 'M'):
        return (2419200 * 1000) * int(interval.split('M')[0])
        
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()