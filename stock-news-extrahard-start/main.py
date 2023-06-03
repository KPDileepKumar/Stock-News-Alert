import requests
from datetime import date, timedelta
from twilio.rest import Client

account_sid = "ACf16a968c08bd490d98f3b2829bc3bceb"
auth_token = "82f8adf3fbe65c7b64c67ecb2078bb97"

twilio_number = '+16203902014'
verified_number = '+918971474762'

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

api_key = "B8Q0ZY5BBL8YEJ8F"
parameters = {"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": STOCK, "apikey": api_key}

need_news = False
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
response = requests.get(url="https://www.alphavantage.co/query", params=parameters)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
days_list = [value for key, value in data.items()]

yesterday_stock = float(days_list[0]["4. close"])
b_yesterday_stock = float(days_list[1]["4. close"])

change = yesterday_stock - b_yesterday_stock
percentage_change = round(abs(change) / b_yesterday_stock * 100)
if change > 0:
    symbol = "🔻"
else:
    symbol = "🔺"
if percentage_change >= 5:
    need_news = True

# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
today_date = date.today()
yesterday_date = str(today_date - timedelta(2))
before_yesterday_date = str(today_date - timedelta(3))

news_api_key = "da52f58b66644cfeaa2c7f8775ba822a"
news_parameters = {"q": COMPANY_NAME, "searchIn": "title,description", "from": before_yesterday_date,
                   "to": yesterday_date, "language": "en", "sortBy": "popularity", "pageSize": 3,
                   "apiKey": news_api_key}
response = requests.get(url="https://newsapi.org/v2/everything", params=news_parameters)
response.raise_for_status()
data = response.json()["articles"]
required_articles = data[:3]

# STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
if need_news:
    client = Client(account_sid, auth_token)
    for j in range(3):
        message = client.messages.create(
            body=f"TSLA: {symbol}{percentage_change}%\nHEADLINE: {required_articles[j]['title']}\n\nBRIEF:"
                 f" {required_articles[j]['description']}",
            from_=twilio_number,
            to=verified_number
        )

        print(message.status)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required 
to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height
 of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required
 to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height
  of the coronavirus market crash.
"""
