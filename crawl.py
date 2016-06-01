import re

from bs4 import BeautifulSoup

from antakya_connection import *

COLUMN_NAMES = ';{bestellnummer};{name};;;;{einheit};{preis};{mehrwertsteuer};{pfand};{gebindegroesse};;;{kategorie}'
mehrwertsteuer = '0'

with AntakyaConnection() as connection:

    articles = ['empty row']

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

                name_element = link_element.parent.next_sibling.next_sibling
                name = name_element.string.strip()[:59].replace('"', "'")  # cut too long names

                gebinde_element = name_element.next_sibling.next_sibling
                try:
                    einheit, gebindegroesse = gebinde_element.string.split('x')
                except:
                    einheit, gebindegroesse = 1, gebinde_element.string

                preis_element = gebinde_element.next_sibling.next_sibling
                preis = preis_element.string

                pfand = '0'

                kategorie = soup.find('td', class_='tab_th_norm', attrs={'colspan': 7}).contents[0].string

                item = COLUMN_NAMES.format_map(vars())
                articles.append(item)

    with open('antakya_articles.csv', 'w') as file:
        for article in articles:
            file.write(article + '\n')
