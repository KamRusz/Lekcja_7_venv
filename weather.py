import datetime, time, requests, json, sys
from os import path

opad = ("Rain", "Snow", "Będzie padać", "Nie będzie padać", "Padało", "Nie padało")

if path.exists("pogoda.txt"):
    if path.isfile("pogoda.txt"):
        with open("pogoda.txt", 'r') as pogoda_log:
            historia = json.load(pogoda_log)
else:
    historia = {}

try:
    api_key = sys.argv[1]
except IndexError:
    exit("nie podano klucza api")
else:
    api_key = sys.argv[1]

try:
    pobrana_data = sys.argv[2]
except IndexError:
    pobrana_data = str(datetime.date.today())
else:
    pobrana_data = sys.argv[2]
wczytana_data = datetime.datetime.strptime(pobrana_data, '%Y-%m-%d')
 
if wczytana_data < (datetime.datetime.today() - datetime.timedelta(6)):
    exit(f"\n{pobrana_data} : Nie wiem"
    "\n\nProgram obsługuje wyłącznie daty od"
    f" {datetime.date.today() - datetime.timedelta(5)}"
    f" do {datetime.date.today() + datetime.timedelta(15)}"
    )

if wczytana_data > (datetime.datetime.today() + datetime.timedelta(15)):
    exit(f"\n{pobrana_data} : Nie wiem"
    "\n\nProgram obsługuje wyłącznie daty od"
    f" {datetime.date.today() - datetime.timedelta(5)}"
    f" do {datetime.date.today() + datetime.timedelta(15)}"
    )

def unix_na_ludzki(data_unix):
    data_ludzka = datetime.datetime.utcfromtimestamp(int(data_unix)).strftime('%Y-%m-%d')
    return data_ludzka

def ludzki_na_unix(data_ludzka):
    data_unix = int(datetime.datetime.strptime(
        f"{data_ludzka} 11:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
    return data_unix
   
def czytaj_16dni():
    url = "https://community-open-weather-map.p.rapidapi.com/forecast/daily"

    querystring = {"q":"roszkowo,pl","lat":"54.253841","lon":"18.681574","cnt":"16","units":"metric","mode":"json","lang":"pl"}

    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': api_key
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    dane = response.json()

    for dzien in dane["list"]:
        data = unix_na_ludzki(dzien["dt"]) 
        historia[data] = opad[2] if dzien["weather"][0]["main"] in opad else opad[3]
    return historia

def czytaj_historia(historyczna_data):
    data = ludzki_na_unix(historyczna_data)

    url = "https://community-open-weather-map.p.rapidapi.com/onecall/timemachine"

    querystring = {"lat":"54.253841","lon":"18.681574","dt":data}

    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': api_key
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    dane = response.json()["current"]["weather"][0]["main"]
    historia[historyczna_data] = opad[4] if dane in opad else opad[5]
    return historia

if pobrana_data in historia:
    print(f"\n{pobrana_data} : {historia.get(pobrana_data)}")
else:
    if str(datetime.date.today())<=pobrana_data:
        historia = czytaj_16dni()
    else:
        historia = czytaj_historia(pobrana_data)
    print(f"\n{pobrana_data} : {historia.get(pobrana_data)}")

with open("pogoda.txt", "w") as pogoda_log:
    json.dump(historia, pogoda_log, sort_keys=True, indent=4, ensure_ascii=False)