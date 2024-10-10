import requests
import selectorlib
import smtplib
import ssl
import time
import sqlite3

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
                  'Safari/537.36'
}


def scrape(url):
    """Scrape the page source from the URL"""
    try:
        response = requests.get(url=url, headers=HEADERS)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return None


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "nikolay.korbut@gmail.com"
    password = "juff wljr qdeq anbc"

    receiver = "nikolay.korbut@gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent!")


def store(extracted):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor.execute("INSERT INTO events VALUES (?, ?, ?)", row)
    connection.commit()
    connection.close()
    print(row)


def read(extracted):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?",
                   (band, city, date))
    rows = cursor.fetchall()
    connection.close()
    print(rows)
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        if scraped:
            extracted = extract(scraped)
            print(extracted)

            if extracted != "No upcoming tours":
                row = read(extracted)
                if not row:
                    store(extracted)
                    send_email(message=f"Hey! There is a new tour: "
                                       f" {extracted}")

        # Збільшення інтервалу до 20 секунд для зменшення навантаження на систему
        time.sleep(20)