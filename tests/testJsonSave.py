from binance.client import Client
import json
import unittest

# Helpers

def write_json():
    data = {}
    data['people'] = []
    data['people'].append({
        'name': 'Scott',
        'website': 'stackabuse.com',
        'from': 'Nebraska'
    })
    data['people'].append({
        'name': 'Larry',
        'website': 'google.com',
        'from': 'Michigan'
    })
    data['people'].append({
        'name': 'Tim',
        'website': 'apple.com',
        'from': 'Alabama'
    })
    
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)

def read_json():
    with open('data.txt') as json_file:
        return json.load(json_file)
    

def save_market_data():
    client = Client("api-key", "api-secret", {"verify": False, "timeout": 1800})
    
    klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1MINUTE, "23 Dec, 2018", "25 Dec, 2018")
    with open('minuteCandlesOneDay.txt', 'w') as outfile:
        json.dump(klines, outfile)
    
    return len(klines)

def load_market_data():
    with open('minuteCandlesOneDay.txt') as json_file:
        return json.load(json_file)

class TestReading(unittest.TestCase):

    def test_length(self):
        self.assertEqual(len(read_json()['people']), 3, "Should be 3")

    def test_values1(self):
        self.assertEqual(read_json()['people'][0]['name'], 'Scott')
        
    def test_values2(self):
        self.assertEqual(read_json()['people'][1]['website'], 'google.com')
        
    def test_values3(self):
        self.assertEqual(read_json()['people'][2]['from'], 'Alabama')
        
    def test_market_data_save(self):
        items = save_market_data()
        
        data = load_market_data()
        
        
        self.assertEqual(len(data), items, "Should be " + str(items))

if __name__ == '__main__':
    unittest.main()
