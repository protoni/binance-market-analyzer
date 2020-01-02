import unittest
import sys
sys.path.append('..')
import utils

class TestReading(unittest.TestCase):

    def testIntervalParsingMinutes(self):
        self.assertEqual(utils.getIntervalMs('1m'), 60000, "Should be 60000 ms")
        self.assertEqual(utils.getIntervalMs('3m'), 180000, "Should be 180000 ms")
        self.assertEqual(utils.getIntervalMs('5m'), 300000, "Should be 300000 ms")
        self.assertEqual(utils.getIntervalMs('15m'), 900000, "Should be 900000 ms")
        self.assertEqual(utils.getIntervalMs('30m'), 1800000, "Should be 1800000 ms")
        
    
    def testIntervalParsingHours(self):
        self.assertEqual(utils.getIntervalMs('1h'), 3600000, "Should be 3600000 ms")
        self.assertEqual(utils.getIntervalMs('2h'), 7200000, "Should be 7200000 ms")
        self.assertEqual(utils.getIntervalMs('4h'), 14400000, "Should be 14400000 ms")
        self.assertEqual(utils.getIntervalMs('6h'), 21600000, "Should be 21600000 ms")
        self.assertEqual(utils.getIntervalMs('8h'), 28800000, "Should be 28800000 ms")
        self.assertEqual(utils.getIntervalMs('12h'), 43200000, "Should be 43200000 ms")
        
    def testIntervalParsingDays(self):
        self.assertEqual(utils.getIntervalMs('1d'), 86400000, "Should be 86400000 ms")
        self.assertEqual(utils.getIntervalMs('3d'), 259200000, "Should be 259200000 ms")
     
    def testIntervalParsingWeeks(self):
        self.assertEqual(utils.getIntervalMs('1w'), 604800000, "Should be 604800000 ms")
        
    def testIntervalParsingMonths(self):
        self.assertEqual(utils.getIntervalMs('1M'), 2419200000, "Should be 2419200000 ms")
     
if __name__ == '__main__':
    unittest.main()