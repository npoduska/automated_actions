"""This program sends SMS stock alerts.
Whenever ARCC gets below a certain price OR is trending downward,
an alert is sent, along with a few news clips about ARCC."""

import requests, os
# from config import API_KEY, NEWS_API_KEY,ACCOUNT_SID, AUTH_TOKEN,FROM_NUMBER,TO_NUMBER #Get your own API Keys!
from datetime import *
from twilio.rest import Client

STOCK = "ARCC"
COMPANY_NAME = "Ares Capital Corporation"

API_KEY= os.environ.get('API_KEY')
NEWS_API_KEY= os.environ.get('NEWS_API_KEY')
FROM_NUMBER= os.environ.get('FROM_NUMBER')
TO_NUMBER= os.environ.get('TO_NUMBER')

#Twilio account access stuff
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')

print("All secrets collected successfully")

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))
print("Collected Stock info successfully")

low_prices =[]  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
print("Stock prices collected.")
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
# print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
# print (f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
# print (f" Long term (50 day) simple moving average: ${long_sma:.2f}")
print("SMA successfully")
#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    # print("Trending Up")
    trending_condition = "Trending Upward"
else:
    # print("Trending Down")
    trending_condition = "Trending Downward"

if latest_low_price < 21:
    # print("GET NEWS!")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body= f"A new low! The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}",
    from_=f"{FROM_NUMBER}",
    to=f"{TO_NUMBER}",)
    print("Message sent via SMS successfully")
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-09-13&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    # print(data['totalResults']) 
    if 0 < int(data['totalResults']): 
        if int(data['totalResults']) >5:
            max_articles = 4
        for i in range (0, max_articles):
            # print(data['articles'][i]["source"]['name']) #Get where the article came from.
            # print(data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            # print(data['articles'][i]["description"])    # This will print the parsed JSON data, particularly the description portion
            # print(data) 
            #Send the news out via Twilio SMS
            news_source = (data['articles'][i]["source"]['name']) #Get where the article came from.
            news_title = (data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            news_description = (data['articles'][i]["description"])   
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
            body= f"News source: {news_source}, Title: {news_title}, Desciption: {news_description}",
            from_=f"{FROM_NUMBER}",
            to=f"{TO_NUMBER}",)
    else:
        print(f"There are no news articles found for {COMPANY_NAME}.")  
        client = Client(account_sid, auth_token)
        message = client.messages.create(
        body= f"There are no news articles found for {COMPANY_NAME}.",
        from_=f"{FROM_NUMBER}",
        to=f"{TO_NUMBER}",)   

print("ARCC_stock_check.py has been ran")
