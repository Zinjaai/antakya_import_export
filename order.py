from antakya_connection import *

with AntakyaConnection() as connection:
    article_id = '00901'
    connection.visit(BASE_URL + 'bestellen.jsp?artikel=' + article_id)
    gebinde_count = '5'
    connection.fill('gebinde', gebinde_count)
    connection.find_by_name('UEBERNEHMEN').first.click()
