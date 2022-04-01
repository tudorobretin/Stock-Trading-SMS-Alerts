import requests
import os
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
yesterday = None
before_yesterday = None
price_data = None
news_data = None
symbol = None


def getnews():
    global news_data
    key = os.environ['news_api_key']
    parameters = {
        'qInTitle': COMPANY_NAME,
        'from': yesterday,
        'sortBy': 'popularity',
        'apiKey': key
    }
    response = requests.get(url="https://newsapi.org/v2/everything", params = parameters)
    news_data = response.json()['articles']

# this can be done much easier by converting json dictionary to list and getting first two positions


def define_last_two_days():
    global yesterday
    global before_yesterday
    if today_weekday == 0:
        yesterday = today - dt.timedelta(days=3)
        before_yesterday = today - dt.timedelta(days=4)
    elif today_weekday == 1:
        yesterday = today - dt.timedelta(days=1)
        before_yesterday = today - dt.timedelta(days=4)
    elif today_weekday in range(2,5):
        yesterday = today - dt.timedelta(days=1)
        before_yesterday = today - dt.timedelta(days=2)


def get_prices():
    global price_data
    key = os.environ['stocks_api_key']
    parameters = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': STOCK,
        'apikey': key
    }
    response = requests.get(url="https://www.alphavantage.co/query", params=parameters)
    response.raise_for_status()
    price_data = response.json()['Time Series (Daily)']


def send_sms():

    account_sid = os.environ['twillo_account_sid']
    auth_token = os.environ['twillo_auth_token']

    client = Client(account_sid, auth_token)
    # this body is kinda hardcoded, it can be done more automated by list comprehension
    body = f"{STOCK}: {symbol}{change}%\n" \
           # f"Headline: {news_data[0]['title']}\n" \
           # f"Brief: {news_data[0]['description']}\n" \
           # f"Link: {news_data[0]['url']}\n\n" \
           # f"Headline: {news_data[1]['title']}\n" \
           # f"Brief: {news_data[1]['description']}\n" \
           # f"Link: {news_data[1]['url']}\n\n" \
           # f"Headline: {news_data[2]['title']}\n" \
           # f"Brief: {news_data[2]['description']}\n" \
           # f"Link: {news_data[2]['url']}\n" \

    message = client.messages.create(
        body=f"{body}",
        from_='+13867533168',
        to='+400727727397'
    )


def define_symbol():
    global symbol

    if change < 0:
        symbol = "🔻"
    else:
        symbol = "🔺"



today = dt.datetime.today().date()
today_weekday = dt.datetime.today().weekday()


if today_weekday in range(0, 5):

    get_prices()
    define_last_two_days()

    yesterday_close = float(price_data[f"{yesterday}"]['4. close'])
    before_yesterday_close = float(price_data[f"{before_yesterday}"]['4. close'])

    change = round((((yesterday_close - before_yesterday_close)/before_yesterday_close)*100), 2)
    define_symbol()

    if change <= -1 or change >= 1:

        getnews()
        send_sms()




#print(data)
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.



## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

