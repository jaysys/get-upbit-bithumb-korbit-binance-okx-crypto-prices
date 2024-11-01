import requests
from datetime import datetime

def get_jupiter_price():
    try:
        # CoinGecko API endpoint
        url = "https://api.coingecko.com/api/v3/simple/price"
        
        # Parameters for Jupiter
        params = {
            'ids': 'jupiter',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            price = data['jupiter']['usd']
            price_change = data['jupiter'].get('usd_24h_change', 0)
            
            # Print formatted results
            print("\n🪐 Jupiter (JUP) Price Information")
            print("--------------------------------")
            print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"💰 Current Price: ${price:.4f}")
            print(f"📈 24h Change: {price_change:.2f}%")
            
            return price
        else:
            print(f"Error: Could not fetch price. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching Jupiter price: {e}")
        return None

if __name__ == "__main__":
    get_jupiter_price()