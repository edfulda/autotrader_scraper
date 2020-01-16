import requests
import re
from bs4 import BeautifulSoup

def parse_specs(spec):
    year_regex = re.compile('\d{4} \(\d{2} reg\)')
    if year_regex.match(spec):
        year = spec[0:4]#get the year numerically
        reg = spec[6:7]#and the reg
        return {"year" : year, 'reg': reg}
    miles_regex = re.compile('\d+\,?\d* miles')
    if miles_regex.match(spec):
        return {"miles":spec.split(' ')[0]}
    return None

url = 'https://www.autotrader.co.uk/car-search?advertClassification=standard&make=LAMBORGHINI&postcode=SW1A2AA&model=MURCIELAGO&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&advertising-location=at_cars&is-quick-search=TRUE&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

listings = soup.find_all(class_='search-listing sso-listing')
car_list = []
for listing in listings:

    name = listing.find(class_='listing-title title-wrap').text.strip()
    price = listing.find(class_='vehicle-price').text
    car_dict = {'name':name,
                'price':price}
    car_list.append(car_dict)

    specs = listing.find(class_='listing-key-specs').find_all('li')
    for spec in specs:
        found_spec = parse_specs(spec.text)
        if found_spec:
            car_dict.update(found_spec)

print(car_list)

