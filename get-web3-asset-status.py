from dotenv import load_dotenv
import os
from web3 import Web3
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
from tabulate import tabulate
from datetime import datetime
import requests

# WFLR Token ABI
WFLR_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

class CryptoBalanceChecker:
    def __init__(self):
        # Initialize connections
        self.eth_w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        self.sol_client = SolanaClient('https://api.mainnet-beta.solana.com')
        self.flare_w3 = Web3(Web3.HTTPProvider('https://flare-api.flare.network/ext/C/rpc'))
        
        # Load addresses from environment
        self.eth_address = os.getenv("ETH_ADDRESS")
        self.sol_address = os.getenv("SOL_ADDRESS")
        self.flare_address = os.getenv("FLARE_ADDRESS")
        
        # Token details
        self.jup_token_address = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
        self.jpl_token_address = "JPLxvNvzWzUZXmJ6YkkRAFSYZs9dKpPqWpeEGrskKYs"
        self.jup_decimals = 6
        self.jpl_decimals = 6
        
        # WFLR contract setup
        self.wflr_contract_address = "0x1D80c49BbBCd1C0911346656B529DF9E5c2F783d"
        self.wflr_contract = self.flare_w3.eth.contract(
            address=Web3.to_checksum_address(self.wflr_contract_address),
            abi=WFLR_ABI
        )
        
        # Price API endpoint
        self.price_api = "https://api.coingecko.com/api/v3/simple/price"

    def get_crypto_prices(self):
        try:
            params = {
                'ids': 'ethereum,solana,flare-networks,jupiter,jupiter-protocol',
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
                return 0
            balance = self.eth_w3.eth.get_balance(self.eth_address)
            return float(Web3.from_wei(balance, 'ether'))
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0

    def get_sol_balance(self):
        try:
            pubkey = Pubkey.from_string(self.sol_address)
            response = self.sol_client.get_balance(pubkey)
            balance_lamports = response.value
            return float(balance_lamports) / 10**9
        except Exception as e:
            print(f"Error getting SOL balance: {e}")
            return 0

    def get_flare_balance(self):
        try:
            if not self.flare_w3.is_connected():
                print("Warning: Cannot connect to Flare node")
                return 0
            balance = self.flare_w3.eth.get_balance(self.flare_address)
            return float(Web3.from_wei(balance, 'ether'))
        except Exception as e:
            print(f"Error getting Flare balance: {e}")
            return 0

    def get_jup_balance(self):
        try:
            owner_pubkey = Pubkey.from_string(self.sol_address)
            token_pubkey = Pubkey.from_string(self.jup_token_address)
            token_account = get_associated_token_address(owner_pubkey, token_pubkey)
            response = self.sol_client.get_token_account_balance(token_account)
            
            if response.value is None:
                return 0
            return float(response.value.amount) / (10 ** self.jup_decimals)
        except Exception as e:
            print(f"Error getting JUP balance: {e}")
            return 0

    def get_jpl_balance(self):
        try:
            owner_pubkey = Pubkey.from_string(self.sol_address)
            token_pubkey = Pubkey.from_string(self.jpl_token_address)
            token_account = get_associated_token_address(owner_pubkey, token_pubkey)
            
            try:
                response = self.sol_client.get_token_account_balance(token_account)
                if hasattr(response, 'value') and response.value is not None:
                    return float(response.value.amount) / (10 ** self.jpl_decimals)
                return 0
            except Exception as account_error:
                if "could not find account" in str(account_error).lower():
                    print(f"No JPL token account found - this is normal if you've never held JPL")
                    return 0
                raise account_error
        except Exception as e:
            print(f"Error getting JPL balance: {str(e)}")
            return 0

    def get_wflr_balance(self):
        try:
            if not self.flare_w3.is_connected():
                print("Warning: Cannot connect to Flare node")
                return 0
            decimals = self.wflr_contract.functions.decimals().call()
            balance = self.wflr_contract.functions.balanceOf(
                Web3.to_checksum_address(self.flare_address)
            ).call()
            return float(balance) / (10 ** decimals)
        except Exception as e:
            print(f"Error getting WFLR balance: {e}")
            return 0

    def format_address(self, address, length=12):
        if not address:
            return "N/A"
        return f"{address[:length]}...{address[-4:]}"

def main():
    # Load environment variables
    load_dotenv()
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Initialize checker
    checker = CryptoBalanceChecker()
    
    # Get balances
    eth_balance = checker.get_eth_balance()
    sol_balance = checker.get_sol_balance()
    flare_balance = checker.get_flare_balance()
    jup_balance = checker.get_jup_balance()
    jpl_balance = checker.get_jpl_balance()
    wflr_balance = checker.get_wflr_balance()
    
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
         "✓" if eth_balance > 0 else "×"],
        ["Solana", checker.format_address(checker.sol_address), 
         f"{sol_balance:.4f} SOL",
         f"${sol_balance * prices.get('solana', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✓" if sol_balance > 0 else "×"],
        ["Flare", checker.format_address(checker.flare_address), 
         f"{flare_balance:.4f} FLR",
         f"${flare_balance * prices.get('flare-networks', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✓" if flare_balance > 0 else "×"],
        ["Jupiter", checker.format_address(checker.sol_address),
         f"{jup_balance:.4f} JUP",
         f"${jup_balance * prices.get('jupiter', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✓" if jup_balance > 0 else "×"],
        ["JPL", checker.format_address(checker.sol_address),
         f"{jpl_balance:.4f} JPL",
         f"${jpl_balance * prices.get('jupiter-protocol', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✓" if jpl_balance > 0 else "×"],
        ["Wrapped Flare", checker.format_address(checker.flare_address),
         f"{wflr_balance:.4f} WFLR",
         f"${wflr_balance * prices.get('flare-networks', {}).get('usd', 0):,.2f}" if prices else "N/A",
         "✓" if wflr_balance > 0 else "×"]
    ]
    
    # Price table data
    price_headers = ["Cryptocurrency", "Current Price"]
    price_data = [
        ["ETH/USD", f"${prices.get('ethereum', {}).get('usd', 0):.2f}" if prices else "N/A"],
        ["SOL/USD", f"${prices.get('solana', {}).get('usd', 0):.2f}" if prices else "N/A"],
        ["FLR/USD", f"${prices.get('flare-networks', {}).get('usd', 0):.4f}" if prices else "N/A"],
        ["JUP/USD", f"${prices.get('jupiter', {}).get('usd', 0):.4f}" if prices else "N/A"],
        ["JPL/USD", f"${prices.get('jupiter-protocol', {}).get('usd', 0):.4f}" if prices else "N/A"],
        ["WFLR/USD", f"${prices.get('flare-networks', {}).get('usd', 0):.4f}" if prices else "N/A"]
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