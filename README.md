
### Install
* Install Python 3: https://www.python.org/downloads/
* Open up a command prompt:
	* Windows: Search for 'cmd.exe'
	* Linux, Mac: Search for 'Terminal'
* Install Python modules by entering in the command prompt:
	* ```pip3 install beautifulsoup4 splinter```

Manjaro: Splinter needs geckodriver (which is in the repos).

### Run
* Edit the login information inside the file 'antakya_connection.py': Trage die Zugangsdaten eines Besteller-Kontos von base online ein. 
* Führe das Skript zwei mal aus und kommentiere beim zweiten Mal statt Zeile 15 'connection.visit(BASE_URL + 'food.do?group=16')' die nächste Zeile `connection.visit(BASE_URL + 'non_food.jsp?group=86')` ein, um Non-Food Waren zu erhalten. 
* Otherwise same use as FoodCoopOrderer 