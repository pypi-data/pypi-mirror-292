from requests import get
from bs4 import BeautifulSoup
import random, string

def genfake(xx):
    url = f"https://www.fakexy.com/fake-address-generator-{xx}"
    fk = get(url, timeout=10)
    soup = BeautifulSoup(fk.text, 'html.parser')
    table = soup.find('table', class_='table')
    street = city = state = zip_code = phone_number = country = None
    letters = string.ascii_lowercase
    first = ''.join(random.choice(letters) for _ in range(6))
    last = ''.join(random.choice(letters) for _ in range(6))
    pwd = ''.join(random.choice(letters) for _ in range(10))
    name = f'{first} {last}'
    email = f'{first}.{last}@gmail.com'
    if table:
        for row in table.find('tbody').find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 2:
                label = columns[0].text.strip()
                value = columns[1].text.strip()
                if label == "Street":
                    street = value
                elif label == "City/Town":
                    city = value
                elif label == "State/Province/Region":
                    state = value
                elif label == "Zip/Postal Code":
                    zip_code = value
                elif label == "Phone Number":
                    phone_number = value
                elif label == "Country":
                    country = value
        return first, last, name, email, pwd, street, city, state, zip_code, phone_number, country
    else:
        return "error"