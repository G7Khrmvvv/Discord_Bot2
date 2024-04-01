#U6P7CXOHBOMKUUQ7
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=CNY&apikey=U6P7CXOHBOMKUUQ7'
r = requests.get(url)
data = r.json()

print(data)