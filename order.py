import re
import sys

from antakya_connection import *

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as input_file:
        # find first occurrence of 'Nummer    Menge   Name'
        order = input_file.read().split('Nummer    Menge   Name', 1)[1]
        with AntakyaConnection() as connection:
            for line in order.split('\n'):
                splitted_line = re.split(r' +', line)  # e.g. ['', '392459', '2', 'Bioland', 'Joghurt', 'Natur', '1L']
                if len(splitted_line) > 3:
                    article_id = splitted_line[1]
                    gebinde_count = splitted_line[2]
                    connection.visit(BASE_URL + 'bestellen.jsp?artikel=' + article_id)
                    connection.fill('gebinde', gebinde_count)
                    connection.find_by_name('UEBERNEHMEN').first.click()
