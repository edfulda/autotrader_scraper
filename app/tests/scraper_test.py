import unittest
from app.scraper import Scraper


class TestURL(unittest.TestCase):
    def test_age(self):
        with self.assertRaises(ValueError):
            s = Scraper("any", "any", used=False, new=False, nearlyNew=False)
        used = Scraper("any", "any", used=True, new=False, nearlyNew=False)
        self.assertIn('onesearchad=Used', used.url)
        self.assertNotIn('onesearchad=New', used.url)
        self.assertNotIn('onesearchad=Nearly%20New', used.url)

        new  = Scraper("any", "any", used=False, new=True, nearlyNew=False)
        self.assertIn('onesearchad=New', new.url)
        self.assertNotIn('onesearchad=Nearly%20New', new.url)
        self.assertNotIn('onesearchad=Used', new.url)


        nearlyNew  = Scraper("any", "any", used=False, new=False, nearlyNew=True)
        self.assertIn('onesearchad=Nearly%20New', nearlyNew.url)
        self.assertNotIn('onesearchad=New', nearlyNew.url)
        self.assertNotIn('onesearchad=Used', nearlyNew.url)




if __name__ == '__main__':
    unittest.main()
