import requests


def get_currency_rate():
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    return data['Valute']['USD']['Previous']

# print (data['Valute']['USD']['Value'])
# print (data['Valute']['USD']['Previous']) # this
