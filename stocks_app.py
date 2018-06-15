from dotenv import load_dotenv
import json
import os
import requests
import sys
import csv
import time

load_dotenv()  # loads environment variables set in a ".env" file

api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

print(api_key)
symbol = input("Please enter a crypto-currency symbol (e.g. BTC, IOTA, ETH, XLM): ")

while True:
    if len(symbol) > 4:
        symbol = input("The symbol you entered has too many characters. Please enter a proper symbol with less than 5 characters: ")
    if any(i.isdigit() for i in symbol):
        symbol = input("The symbol you entered has a number. Please enter a proper symbol containing no numbers: ")
    else:
        break

# https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=CNY&apikey=demo
json_input = "https://www.alphavantage.co/query?"
input_market = "USD"

request_url = f"""https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={input_market}&apikey={api_key}"""

response = requests.get(request_url)

if response.text.find("Error") > 0:
    symbol = input("We encountered an error. Please enter a new symbol or enter Quit to exit: ")
    if symbol == "Quit":
        sys.exit()

request_url = f"""https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={input_market}&apikey={api_key}"""
response = requests.get(request_url)

# print(request_url)
# print(response.text)

json_response = json.loads(response.text)
list_time_series_daily = json_response["Time Series (Digital Currency Daily)"]



filename = "prices.csv"
file_path = os.path.join(os.path.dirname(__file__), "data", filename)

dict_daily_prices = []
with open(file_path, "w+") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=["date", "open", "high", "low", "close", "volume"])
    writer.writeheader()  # uses fieldnames set above

    high_price = -1.2
    low_price = 1000000000.2
    result = []
    for trade_date in list_time_series_daily:
        dict_daily_prices = list_time_series_daily[trade_date]
        result = {
            "date": trade_date,
            "open": dict_daily_prices["1a. open (USD)"],
            "high": dict_daily_prices["2a. high (USD)"],
            "low": dict_daily_prices["3a. low (USD)"],
            "close": dict_daily_prices["4a. close (USD)"],
            "volume": dict_daily_prices["5. volume"]
        }

        high_price_test = float(dict_daily_prices["4a. close (USD)"])
        if high_price_test > high_price:
            high_price = high_price_test
        else:
            pass

        low_price_test = float(dict_daily_prices["4a. close (USD)"])
        if low_price_test < low_price:
            low_price = low_price_test
        else:
            pass

        writer.writerow(result)

currency_name = json_response["Meta Data"]["3. Digital Currency Name"]
run_time = time.strftime("%I:%M:%S")
run_date = time.strftime("%d/%m/%Y")
days_in_series = len(json_response["Time Series (Digital Currency Daily)"])
as_of_date = json_response["Meta Data"]["6. Last Refreshed"]
as_of_date = as_of_date.replace(" (end of day)", "")
latest_close = float(json_response["Time Series (Digital Currency Daily)"][as_of_date]["4a. close (USD)"])
latest_close_formatted = "${0:,.2f}".format(latest_close)

print("Currency Name: ", currency_name)
print("Run at: ", run_time, " on ", run_date)
print("Data as of: ", as_of_date)
print("Last close :", latest_close_formatted)
print("High price over ", days_in_series, " days: ", "${0:,.2f}".format(float(high_price)))
print("Low price over ", days_in_series, " days: ", "${0:,.2f}".format(float(low_price)))

recommendation = ""
if latest_close < high_price * 0.5:
    print(currency_name, " is below 50% of it's ", days_in_series, " day high. Buy buy buy")
else:
    print(currency_name, " is NOT below 50% it's ", days_in_series, " day high. Do not buy.")
