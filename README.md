# test_googletable

A script that allows you to get data from Google Sheets, save them to a PostgreSQL database. Update the data in the database when adding/deleting/updating them in Google Sheets. Check the delivery date from the database with the current date and send a message in telegram if the deadline has passed. Update the cost in rubles daily according to the change in the ruble exchange rate.A script that allows you to get data from Google Sheets, save them to a PostgreSQL database. Update the data in the database when adding/deleting/updating them in Google Sheets. Check the delivery date from the database with the current date and send a message in telegram if the deadline has passed. Update the cost in rubles daily according to the change in the ruble exchange rate.

## Technology stack

- Python
- Flask
- PostgreSQL
- git

## How to launch a project

Clone the repository and go to it on the command line

```bash
    git clone https://github.com/Evgenia789/test_googletable.git
    cd test_googletable
```

Create and activate a virtual environment

```bash
python -m venv venv
source venv/Scripts/activate
```

In the project directory, create a .env file in which you write the following environment variables.

```python
SECRET_KEY=<SECRET_KEY>
SHEET_ID = <SHEET_ID>
DB_HOST=<DB_HOST>
DB_NAME=<DB_NAME>
DB_PORT=<DB_PORT>
POSTGRES_USER=<POSTGRES_USER>
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_DB=<POSTGRES_DB>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>

```

Install dependencies from a file requirements.txt

```bash
 pip install -r requirements.txt 
```

For using Google Sheets API and getting file service_account.json, you need to follow the instructions on this page: [https://github.com/burnash/gspread/blob/master/docs/oauth2.rst](https://github.com/burnash/gspread/blob/master/docs/oauth2.rst)

Launch a project

```bash
python manage.py
```

---

You can try to access the app

```bash
http://127.0.0.1:5000
```

## License

This project is under the MIT License - see the LICENSE file for details.
