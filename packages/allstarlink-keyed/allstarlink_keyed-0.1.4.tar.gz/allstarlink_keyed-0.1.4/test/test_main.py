import unittest
from allstar_fetch.main import fetch_data

class TestFetchData(unittest.TestCase):
    def test_fetch_data(self):
        data = fetch_data("http://stats.allstarlink.org/stats/keyed")
        self.assertIsNotNone(data)

if __name__ == '__main__':
    unittest.main()
