import re
from decimal import Decimal

from bs4 import BeautifulSoup

from antakya_connection import *

COLUMN_NAMES = ';{bestellnummer};{name};;;;{einheit};{preis};{mehrwertsteuer};{pfand};{gebindegroesse};;;{kategorie}'
mehrwertsteuer = '7'

with AntakyaConnection() as connection:
    articles = [COLUMN_NAMES]
    categories = set()

    connection.visit(BASE_URL + 'food.do?group=16')
    # connection.visit(BASE_URL + 'non_food.jsp?group=86')
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
                name = name_element.string.strip().replace('"', "'")

                kategorie = soup.find('td', class_='tab_th_norm', attrs={'colspan': 7}).contents[0].string.strip()
                categories.add(kategorie)

                gebinde_element = name_element.next_sibling.next_sibling
                einzel_preis_element = gebinde_element.next_sibling.next_sibling
                einzel_preis = float(einzel_preis_element.string.replace(',', '.'))
                gesamt_preis = float(einzel_preis_element.next_sibling.next_sibling.string.replace(',', '.'))
                if re.match('\d*l', gebinde_element.string):
                    gebindegroesse, _ = gebinde_element.string.split('l')
                    einheit = '1l'
                else:
                    einheit = gebinde_element.string
                    if einheit == '5Kg' or einheit == '25Kg' or einheit == '5kg' or einheit == '25kg' \
                            or einheit == '5 kg' or einheit == '25 kg':
                        gebindegroesse = einheit.replace('Kg', '').replace('kg', '')
                        einheit = '1kg'

                    elif einheit == '1kg' and kategorie == 'Gewürze':
                        gebindegroesse = 10
                        einheit = '100g'
                    else:
                        gesamt_preis_mal10 = int('{:.2f}'.format(gesamt_preis).replace('.', ''))
                        einzel_preis_mal10 = int('{:.2f}'.format(einzel_preis).replace('.', ''))
                        if einzel_preis_mal10 == 0:
	                        print(kategorie, name, 'costs zero, an error from antakya, this article is ignored')
                        	continue
                        if gesamt_preis_mal10 % einzel_preis_mal10 > 0:
                            print('gesamt und einzelpreis passen nicht bei {} {} {}'.format(name, gesamt_preis,
                                                                                            einzel_preis))
                            raise Exception
                        gebindegroesse = int(gesamt_preis_mal10 / einzel_preis_mal10)
                        einheit = gebinde_element.string.replace('1x', '')
                        if gebindegroesse != 1:
                            if einheit.startswith('{}x'.format(gebindegroesse)):
                                einheit = einheit.replace('{}x'.format(gebindegroesse), '')
                            else:
                                einheit = '{} / {}'.format(einheit, gebindegroesse)

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

                preis = round(gesamt_preis / float(gebindegroesse), 2)

                pfand = '0'

                item = COLUMN_NAMES.format_map(vars())
                articles.append(item)

    with open('antakya_articles.csv', 'w') as file:
        for article in articles:
            file.write(article + '\n')

    print('\n Wrote "antakya_articles.csv"\nCreate these categories in the foodsoft once:')
    for c in categories:
        print(c)
