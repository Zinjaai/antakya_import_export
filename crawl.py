"""
Load articles from Antakya base into csv files.
These csv files can be used to add the articles in the foodsoft
"""

import re
from datetime import datetime
from bs4 import BeautifulSoup

from antakya_connection import *

NOW = datetime.utcnow()
COLUMN_NAMES = ';{bestellnummer};{name};;;;{einheit};{preis};{mehrwertsteuer};' \
               '{pfand};{gebindegroesse};;;{kategorie}'
MEHRWERTSTEUER_FOOD = '7'
MEHRWERTSTEUER_NON_FOOD = '19'

PRICE_MODIFICATOR = 1.01  # increase price by this factor (more money for foodcoop)

MWST_AUSNAMEN_KATEGORIE = {
    # Food, but high tax
    'Bier': 19,
    'Bionade': 19,
    'Liköre und Spirituosen': 19,
    'Soja-, Hafer- & Reisprodukte': 19,  # sofa-cuisine und quiona reis drink haben eigentl.  7% ... grrrrr
    'Säfte': 19,
    'Teenetze': 19,
    'Wasser-Cidre': 19,
    'Wein': 19,
    'Prosecco, Sekt & Champagner': 19,

    # NON-Food but reduced
    'Tiernahrung': 7,
    'Ostern': 7,
    'Weihnachten': 7,
}


MSWT_AUSNAMEN_ARTIKEL_ID = {
    # Weihnachts und Oster artikel... meiste ist schoki
    17782: 19,  # Glühwein 10% Vol. 6x1l
    23576: 19,  # Stearinbaumkerzen elfenbein 1x20Stück
    23577: 19,  # Stearinbaumkerzen rot 1x20Stück
    23579: 19,  # Bienenwachs-Baumkerzen 20 Stck.
    70105: 19,  # Weihnachtskugel Mischkarton 50x15g
    70140: 19,  # Adventskalender 12x75g
    70281: 19,  # Adventskalender Tee 6x24Beutel

    # Soja, Hafer & Reisproduke -->  most hafer/soja/hirse drinks are 19%
    15019: 7,  # CreSoy Cuisine Soja (Sahne) 15x200ml
    15130: 7,  # *V*Quinoa-Reis Drink 12x1l  (for real?!?!)
    15150: 7,  # Soya Cuisine 3er 5x3x250ml
    15155: 7,  # Kokos Cuisine 15x200ml
    15170: 7,  # Hafer Cuisine 15x200ml

    # Sirups (data from antakya katalog.pdf of 2017)
    10268: 7,  # Apfel-Dicksaft 12x0,33l
    10269: 7,  # Birnen-Dicksaft 12x0,33l
    10300: 7,  # Zuckerrübensirup 6x330g
    10303: 7,  # Zuckerrübensirup Becher 12x450g
    10310: 7,  # [guess!] Dattelsirup 6x350g
    10315: 7,  # [guess!] Dinkelsirup 6x350g
    10331: 7,  # Agavendicksaft 6x350g
    10332: 7,  # Agavendicksaft - in der Spenderflasche- 6x500ml
    10344: 7,  # Agavendicksaft 3x2kg
    10346: 7,  # Reissirup 6x400g
    10351: 7,  # Ahornsirup, Grad  A 6x250g
    19206: 19,  # Cassis-Sirup 6x0,5l
    19207: 19,  # Grenadine-Sirup 6x0,5l
    19208: 19,  # Himbeer-Sirup 6x0,5l
    19209: 19,  # Holunderblüten-Sirup 6x0,5l
    19210: 19,  # Limetten-Sirup 6x0,5l
    19211: 19,  # [guess!] Rhabarber-Sirup 6x0,5l
    19218: 19,  # Limettensirup 6x350g
    10374: 7,  # Fruchtsauce Mango-Orange 6x250ml:
}

IGNORE_CATEGORIES = ['Sonderartikel', 'Pfandartikel']


def crawl(connection, articles, categories, food_articles):
    """
    Crawl antakya page an fetch all articles
    :param connection:
    :param articles: list
        Append articles to this list
    :param categories: set
        Add categories to this set

    :return:
    list (articles)
    set (categories)
    """

    if food_articles:
        connection.visit(BASE_URL + 'food.do?group=16')
    else:
        connection.visit(BASE_URL + 'non_food.jsp?group=86')

    soup = BeautifulSoup(connection.html, 'html.parser')
    selector = soup.find('select')
    for child in selector.contents:
        if isinstance(child, str):
            continue

        group_id = child['value']
        connection.visit(BASE_URL + 'food.do?group=' + group_id)
        soup = BeautifulSoup(connection.html, 'html.parser')
        link_elements = soup.find_all(href=re.compile('artikelinfo.jsp'))
        for link_element in link_elements:
            bestellnummer = link_element.string

            name_element = link_element.parent.next_sibling.next_sibling
            name = name_element.string.strip().replace('"', "'")

            # item with same id exists
            if any([bestellnummer in item for item in articles]):
                # thats okay, the list the same stuff multiple times ..
                continue

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

            if kategorie in IGNORE_CATEGORIES:
                print('Ignoring category', kategorie)
                continue

            if gesamt_preis <= 0:
                print('preis <= 0, ignoring', name)
                continue

            # item with same name exists
            if any([name in item for item in articles]):
                # todo:  get and append company
                # skipping is okay, because this case is rare (a tomato ketchup only)
                continue

            if float(gebindegroesse) == 0:
                print('skipping - gebindegr of 0', kategorie, name)
                continue
            preis = round(gesamt_preis * PRICE_MODIFICATOR / float(gebindegroesse), 2)
            pfand = '0'

            # Determine mehrwertsteuer
            if food_articles:
                mehrwertsteuer = MEHRWERTSTEUER_FOOD
            else:
                mehrwertsteuer = MEHRWERTSTEUER_NON_FOOD

            # Not all food articles have reduced mwst...
            if kategorie in MWST_AUSNAMEN_KATEGORIE:
                mehrwertsteuer = MWST_AUSNAMEN_KATEGORIE[kategorie]
            if int(bestellnummer) in MSWT_AUSNAMEN_ARTIKEL_ID:
                mehrwertsteuer = MSWT_AUSNAMEN_ARTIKEL_ID[int(bestellnummer)]

            # add article
            item = COLUMN_NAMES.format(bestellnummer=bestellnummer, name=name, einheit=einheit, preis=preis,
                                       mehrwertsteuer=mehrwertsteuer, pfand=pfand, gebindegroesse=gebindegroesse,
                                       kategorie=kategorie)
            articles.append(item)

    return articles, categories


if __name__ == '__main__':

    # Get all food and non-food articles
    with AntakyaConnection() as connection:
        articles, categories = crawl(connection, [], set(), True)  # food

    with AntakyaConnection() as connection:
        articles, categories = crawl(connection, articles, categories, False)  # non-food

    # Write article-csv with chunked rows (only n rows per csv file)
    articles_per_file = 800
    for file_number, start_idx in enumerate(range(0, len(articles), articles_per_file)):
        with open(f'{NOW:%Y_%m_%d}_antakya_articles_{file_number}.csv', 'w') as file:
            file.write('\n'.join([COLUMN_NAMES] + articles[start_idx: start_idx+articles_per_file]))

    # Write complete article-csv
    with open(f'{NOW:%Y_%m_%d}_antakya_articles_complete.csv', 'w') as file:
        file.write('\n'.join([COLUMN_NAMES] + articles))

    # Write mysql-statements for category-creation
    # print('\n Wrote "antakya_articles.csv"\nMYSQL-cmd to create these categories in the foodsoft:')
    # for c in categories:
    #    print(f"INSERT INTO `article_categories` (`name`) VALUES ('{c}');")

    if PRICE_MODIFICATOR != 1:
        print('\n\n!!!! ATTENTION\n Modified price by factor: ', PRICE_MODIFICATOR)
