import requests
import re
from bs4 import BeautifulSoup
import statistics
from datetime import datetime

BASE_URL = 'https://www.autotrader.co.uk/car-search?advertClassification=standard&make={make}&postcode=SW1A2AA&model={model}{age}&advertising-location=at_cars&is-quick-search=TRUE&page={page}'
BASE_URL_ADVERT = 'https://www.autotrader.co.uk/classified/advert/{id}'


class Scraper:
    def __init__(self, make, model, used=True, nearlyNew=True, new=True):
        self.queries = {'make': make, 'model': model}
        if not (used or new or nearlyNew):
            raise ValueError("Must include at least one of new, nearlynew, used")
        self.used = used
        self.nearlyNew = nearlyNew
        self.new = new
        self.page = 1
        self.cars = []
        self.stats = []

    @property
    def url(self):
        age = "&onesearchad=Used" if self.used else ""
        age = age + ("&onesearchad=New" if self.new else "")
        age = age + ("&onesearchad=Nearly%20New" if self.nearlyNew else "")
        url = BASE_URL.format(make=self.queries['make'], model=self.queries['model'], age=age, page=self.page)
        return url

    def get_cars(self):

        while True:
            page = requests.get(self.url)
            if page.url != self.url:
                # This means that the page we've requested doesn't exist - i.e. we have a number of cars divisible by 10 in
                # results. Therefore we should break as we've come to the end of the results
                break
            soup = BeautifulSoup(page.text, 'html.parser')
            listings = soup.find_all(class_='search-listing sso-listing') + soup.find_all(
                class_='search-listing standard-listing') + soup.find_all(class_='search-listing sso-listing no-logo')
            for listing in listings:
                name = listing.find(class_='listing-title title-wrap').text.strip()
                price = listing.find(class_='vehicle-price').text
                price_int = int(price.replace('£', '').replace(',', ''))
                id = listing.parent.attrs['id']
                url = BASE_URL_ADVERT.format(id=id)
                dealer = True  # todo - non dealer ads have different classes
                car_dict = {'name': name,
                            'price': price,
                            'price_int': price_int,
                            'dealer': dealer,
                            'id': id,
                            'url': url}
                specs = listing.find(class_='listing-key-specs').find_all('li')
                car_dict.update(self.__parse_specs(specs))
                self.cars.append(car_dict)

            if len(listings) == 10:
                self.page += 1
            else:
                break  # Either 0 listings on this page or fewer than 10. Either way there's no next page

        return self.cars

    def get_stats(self):
        price_list = [int(x['price_int']) for x in self.cars]
        self.stats = {
            'make': self.queries['make'],
            'model': self.queries['model'],
            'mean_price': statistics.mean(price_list),
            'median_price': statistics.median(price_list),
            'min_price': min(price_list),
            'max_price': max(price_list),
            'timestamp': datetime.utcnow()
        }
        return self.stats

    def get_full_info(self):
        if not self.cars:
            self.get_cars()
        if not self.stats:
            self.get_stats()
        return {'stats': self.stats, 'full_list': self.cars}

    def __parse_specs(self, specs):
        found_specs = {}
        for spec in specs:
            year_regex = re.compile('\d{4} \(\d{2} reg\)')
            if year_regex.match(spec.text):
                year = spec.text[0:4]  # get the year numerically
                reg = spec.text[6:7]  # and the reg
                found_specs["year"] = year
                found_specs['reg'] = reg
                continue
            miles_regex = re.compile('\d+\,?\d* miles')
            if miles_regex.match(spec.text):
                found_specs["miles"] = spec.text.split(' ')[0]
                continue
            transmission_regex = re.compile('[Automatic|Manual]')
            if transmission_regex.match(spec.text):
                found_specs["transmission"] = spec.text
        return found_specs
