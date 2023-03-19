import requests


def get_currency_rate() -> float:
    # data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    # return data['Valute']['USD']['Previous']
    """
    Retrieves the currency rate of USD to RUB from an external API.

    :return: The currency rate as a float.
    :raise: If the API is not reachable or if the response format
            is unexpected.
    """
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        response.raise_for_status()
        data = response.json()
        return data['Valute']['USD']['Previous']
    except (requests.exceptions.RequestException, KeyError) as error:
        raise requests.exceptions.RequestException(
            f"Failed to retrieve currency rate: {error}"
        )
