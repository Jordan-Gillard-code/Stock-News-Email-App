import requests
import datetime
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_PRICE_API_KEY = os.getenv("STOCK_PRICE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
params = {
    "function":"TIME_SERIES_DAILY",
    "symbol":STOCK,
    "apikey":STOCK_PRICE_API_KEY,
}

response = requests.get(url="https://www.alphavantage.co/query?", params=params)
response.raise_for_status()
data = response.json()

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
day_before_yesterday = yesterday - datetime.timedelta(days=1)

yesterday_open_price = float(data["Time Series (Daily)"][str(yesterday)]['1. open'])
day_before_open_price = float(data["Time Series (Daily)"][str(day_before_yesterday)]['1. open'])

pct_price_change = ((yesterday_open_price - day_before_open_price)/yesterday_open_price) * 100
# print(f"{round(pct_price_change,2)}%")

# if abs(pct_price_change) > 5:
#     print("Get News")

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
params = {
    "apikey":NEWS_API_KEY,
    "q":COMPANY_NAME,
    "language":"en",
    "sortBy":"relevancy",
    "pageSize":3,
}

response = requests.get(url="https://newsapi.org/v2/everything?", params=params)
response.raise_for_status()
news_data = response.json()

news_articles = []
for _ in range(3):
    news_articles.append(news_data['articles'][_])

## STEP 3:
# Send a seperate message with the percentage change and each article's title and description.
with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)

    increase_or_decrease = ""
    if pct_price_change > 0:
        increase_or_decrease = "🔺"
    else:
        increase_or_decrease = "🔻"

    message = f"""Subject: {STOCK} {increase_or_decrease}{round(pct_price_change,2)}%

Headline: {news_articles[0]['title']}
Brief: {news_articles[0]['description']}
Link: {news_articles[0]['url']}

Headline: {news_articles[1]['title']}
Brief: {news_articles[1]['description']}
Link: {news_articles[1]['url']}

Headline: {news_articles[2]['title']}
Brief: {news_articles[2]['description']}
Link: {news_articles[2]['url']}
"""

    connection.sendmail(from_addr=MY_EMAIL,
                        to_addrs=RECIPIENT_EMAIL,
                        msg=message.encode('utf-8')
                        )

#Optional: Format the message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

