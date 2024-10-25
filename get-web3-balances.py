from dotenv import load_dotenv
import os
from web3 import Web3
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient

# Load environment variables
load_dotenv()

class CryptoBalanceChecker:
    def __init__(self):
        # Initialize connections using public nodes
        # Ethereum - Using public nodes (note: rate limits may apply)
        self.eth_w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        
        # Solana - Using public RPC
        self.sol_client = SolanaClient('https://api.mainnet-beta.solana.com')
        
        # Flare - Using public RPC
        self.flare_w3 = Web3(Web3.HTTPProvider('https://flare-api.flare.network/ext/C/rpc'))
        
        # Store addresses
        self.eth_address = os.getenv("ETH_ADDRESS")
        self.sol_address = os.getenv("SOL_ADDRESS")
        self.flare_address = os.getenv("FLARE_ADDRESS")

    def get_eth_balance(self):
        try:
            if not self.eth_w3.is_connected():
                print("Warning: Cannot connect to Ethereum node")
                return 0
            
            balance = self.eth_w3.eth.get_balance(self.eth_address)
            return Web3.from_wei(balance, 'ether')
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0

    def get_sol_balance(self):
        try:
            # Convert string address to Pubkey object using solders
            pubkey = Pubkey.from_string(self.sol_address)
            response = self.sol_client.get_balance(pubkey)
            
            # 수정된 부분: response.value로 직접 접근
            balance_lamports = response.value
            return float(balance_lamports) / 10**9  # Convert lamports to SOL
        except Exception as e:
            print(f"Error getting SOL balance: {e}")
            return 0

    def get_flare_balance(self):
        try:
            if not self.flare_w3.is_connected():
                print("Warning: Cannot connect to Flare node")
                return 0
                
            balance = self.flare_w3.eth.get_balance(self.flare_address)
            return Web3.from_wei(balance, 'ether')
        except Exception as e:
            print(f"Error getting Flare balance: {e}")
            return 0

def main():
    # Load debug mode from environment
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    if debug:
        print("Debug mode enabled")
        print(f"Using ETH address: {os.getenv('ETH_ADDRESS')}")
        print(f"Using SOL address: {os.getenv('SOL_ADDRESS')}")
        print(f"Using Flare address: {os.getenv('FLARE_ADDRESS')}")

    # Initialize balance checker
    checker = CryptoBalanceChecker()
    
    # Get balances
    eth_balance = checker.get_eth_balance()
    sol_balance = checker.get_sol_balance()
    flare_balance = checker.get_flare_balance()
    
    # Print results
    print("\nCryptocurrency Balances:")
    print("-----------------------")
    print(f"ETH Balance: {eth_balance:.6f} ETH")
    print(f"SOL Balance: {sol_balance:.6f} SOL")
    print(f"Flare Balance: {flare_balance:.6f} FLR")

if __name__ == "__main__":
    main()