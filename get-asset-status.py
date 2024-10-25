from dotenv import load_dotenv
import os
from web3 import Web3
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient
from tabulate import tabulate
from datetime import datetime
import requests

class CryptoBalanceChecker:
    def __init__(self):
        self.eth_w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        self.sol_client = SolanaClient('https://api.mainnet-beta.solana.com')
        self.flare_w3 = Web3(Web3.HTTPProvider('https://flare-api.flare.network/ext/C/rpc'))
        
        self.eth_address = os.getenv("ETH_ADDRESS")
        self.sol_address = os.getenv("SOL_ADDRESS")
        self.flare_address = os.getenv("FLARE_ADDRESS")
        
        # 가격 정보를 위한 CoinGecko API 엔드포인트
        self.price_api = "https://api.coingecko.com/api/v3/simple/price"

    def get_crypto_prices(self):
        try:
            params = {
                'ids': 'ethereum,solana,flare-networks',  # flare-networks로 변경
                'vs_currencies': 'usd'
            }
            response = requests.get(self.price_api, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return None

    def get_eth_balance(self):
        try:
            if not self.eth_w3.is_connected():
                print("Warning: Cannot connect to Ethereum node")
                return 0.0
            balance = self.eth_w3.eth.get_balance(self.eth_address)
            return float(Web3.from_wei(balance, 'ether'))  # float로 변환
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0.0

    def get_sol_balance(self):
        try:
            pubkey = Pubkey.from_string(self.sol_address)
            response = self.sol_client.get_balance(pubkey)
            balance_lamports = response.value
            return float(balance_lamports) / 10**9
        except Exception as e:
            print(f"Error getting SOL balance: {e}")
            return 0.0

    def get_flare_balance(self):
        try:
            if not self.flare_w3.is_connected():
                print("Warning: Cannot connect to Flare node")
                return 0.0
            balance = self.flare_w3.eth.get_balance(self.flare_address)
            return float(Web3.from_wei(balance, 'ether'))  # float로 변환
        except Exception as e:
            print(f"Error getting Flare balance: {e}")
            return 0.0

    def format_address(self, address, length=12):
        if not address:
            return "N/A"
        return f"{address[:length]}...{address[-4:]}"

def main():
    debug = os.getenv("DEBUG", "False").lower() == "true"
    checker = CryptoBalanceChecker()
    
    # Get balances
    eth_balance = checker.get_eth_balance()
    sol_balance = checker.get_sol_balance()
    flare_balance = checker.get_flare_balance()
    
    # Get current prices
    prices = checker.get_crypto_prices()
    
    # Prepare data for tables
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Balance table data
    balance_headers = ["Cryptocurrency", "Address", "Balance", "USD Value", "Status"]
    balance_data = [
        ["Ethereum", checker.format_address(checker.eth_address), 
         f"{eth_balance:.4f} ETH",
         f"${eth_balance * prices.get('ethereum', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✅" if eth_balance > 0 else "❌"],
        ["Solana", checker.format_address(checker.sol_address), 
         f"{sol_balance:.4f} SOL",
         f"${sol_balance * prices.get('solana', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✅" if sol_balance > 0 else "❌"],
        ["Flare", checker.format_address(checker.flare_address), 
         f"{flare_balance:.4f} FLR",
         f"${flare_balance * prices.get('flare-networks', {}).get('usd', 0):,.2f}" if prices else "N/A",  # 수정
         "✅" if flare_balance > 0 else "❌"]
    ]
    
    # Price table data
    price_headers = ["Cryptocurrency", "Current Price"]
    price_data = [
        ["ETH/USD", f"${prices.get('ethereum', {}).get('usd', 0):.2f}" if prices else "N/A"],
        ["SOL/USD", f"${prices.get('solana', {}).get('usd', 0):.2f}" if prices else "N/A"],
        ["FLR/USD", f"${prices.get('flare-networks', {}).get('usd', 0):.2f}" if prices else "N/A"]  # 수정
    ]
    
    # Print formatted tables
    print("\n🔍 Cryptocurrency Balance Report")
    print(f"📅 Generated at: {current_time}")
    print("\n📊 Balance Details:")
    print(tabulate(balance_data, headers=balance_headers, tablefmt="fancy_grid"))
    
    print("\n💰 Current Prices:")
    print(tabulate(price_data, headers=price_headers, tablefmt="fancy_grid"))
    
    if debug:
        print("\n🐛 Debug Information:")
        print(f"ETH Node Connected: {checker.eth_w3.is_connected()}")
        print(f"Price API Status: {'Connected' if prices else 'Not Connected'}")

if __name__ == "__main__":
    main()
