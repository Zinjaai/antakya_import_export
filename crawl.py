import re

from bs4 import BeautifulSoup

from antakya_connection import *

COLUMN_NAMES = ';{bestellnummer};{name};;;;{einheit};{preis};{mehrwertsteuer};{pfand};{gebindegroesse};;;{kategorie}'
mehrwertsteuer = '0'

with AntakyaConnection() as connection:
    articles = ['empty row']
    categories = set()

    connection.visit(BASE_URL + 'food.do?group=16')
    soup = BeautifulSoup(connection.html, 'html.parser')
    selector = soup.find('select')
    for child in selector.contents:
        if not isinstance(child, str):
            group_id = child['value']
            connection.visit(BASE_URL + 'food.do?group=' + group_id)
            soup = BeautifulSoup(connection.html, 'html.parser')
            link_elements = soup.find_all(href=re.compile('artikelinfo.jsp'))
            for link_element in link_elements:
                bestellnummer = link_element.string
                # item with same id exists
                if any([bestellnummer in item for item in articles]):
                    continue

                name_element = link_element.parent.next_sibling.next_sibling

                gebinde_element = name_element.next_sibling.next_sibling
                try:
                    gebindegroesse, einheit = gebinde_element.string.split('x')
                except:
                    gebindegroesse, einheit = 1, gebinde_element.string

                # compute bundles
                if einheit == '5kg' or einheit == '25kg':
                    gebindegroesse = einheit.replace('kg', '')
                    einheit = '1kg'

                name = name_element.string.strip().replace('"', "'")
                append = ' ' + gebinde_element.string
                # cut name if name is too long
                if len(name + append) > 60:
                    name = name[:(59 - len(append))]
                name += append

                # item with same name exists
                if any([name in item for item in articles]):
                    # todo:  get and append company
                    # skipping is okay, because this case is rare (a tomato ketchup only)
                    continue

                preis_element = gebinde_element.next_sibling.next_sibling
                preis = preis_element.string

                pfand = '0'

                kategorie = soup.find('td', class_='tab_th_norm', attrs={'colspan': 7}).contents[0].string.strip()
                categories.add(kategorie)

                item = COLUMN_NAMES.format_map(vars())
                articles.append(item)

    with open('antakya_articles.csv', 'w') as file:
        for article in articles:
            file.write(article + '\n')

    print('Create these categories in the foodsoft once:')
    for c in categories:
        print(c)
