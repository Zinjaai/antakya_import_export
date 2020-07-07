"""
Import der zu bestellenden Waren aus der Foodsoft in die
Antakya-Base Seite

Dazu die Foodsoft Bestellübersicht (als csv) runterladen und
die Datei hier als command-line-argument übergeben.

Am besten die csv datei noch einmal in einem texteditor öffnen und als latin-1
kodierung abspeichern. (glaube es ging sonst schief)

"""

import sys

from antakya_connection import *

if __name__ == '__main__':

    csv_path = sys.argv[1]

    with open(csv_path, 'r', encoding='latin1') as input_file:
        order = input_file.read()

    with AntakyaConnection() as connection:
        for idx, line in enumerate(order.split('\n')):
            if idx == 0:
                continue

            print('\n\nLine', idx)

            splitted_line = line.split(';')
            if len(splitted_line) <= 3:
                print('Uhm ignoring the row: ', line)
                continue

            article_id = splitted_line[1]
            gebinde_count = splitted_line[0]

            url = BASE_URL + 'bestellen.jsp?artikel=' + article_id.zfill(5)
            print('gebinde count', gebinde_count)
            print(url)
            connection.visit(url)
            connection.fill('gebinde', gebinde_count)
            connection.find_by_name('UEBERNEHMEN').first.click()
            print(f'Added {article_id}')

#  http://217.86.233.218/FoodCoop/bestellen.jsp?artikel=905


