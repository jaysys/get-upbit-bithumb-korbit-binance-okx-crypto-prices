from dotenv import load_dotenv
import os
from web3 import Web3
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID

# Load environment variables
load_dotenv()


# WFLR Token ABI - Minimal ABI for balance checking
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
        
        # Jupiter token details
        self.jup_token_address = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"  # Jupiter token address
        self.jup_decimals = 6  # Jupiter uses 6 decimals
        
        # JPL token details
        self.jpl_token_address = "JPLxvNvzWzUZXmJ6YkkRAFSYZs9dKpPqWpeEGrskKYs"  # JPL token address
        self.jpl_decimals = 6  # JPL uses 6 decimals
        
        # WFLR token details
        self.wflr_contract_address = "0x1D80c49BbBCd1C0911346656B529DF9E5c2F783d"  # WFLR contract address
        self.wflr_contract = self.flare_w3.eth.contract(
            address=Web3.to_checksum_address(self.wflr_contract_address),
            abi=WFLR_ABI
        )

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

    def get_jup_balance(self):
        try:
            # Convert addresses to Pubkey objects
            owner_pubkey = Pubkey.from_string(self.sol_address)
            token_pubkey = Pubkey.from_string(self.jup_token_address)
            
            # Get the associated token account address
            from spl.token.instructions import get_associated_token_address
            token_account = get_associated_token_address(owner_pubkey, token_pubkey)
            
            # Get the token account info
            response = self.sol_client.get_token_account_balance(token_account)
            
            if response.value is None:
                return 0
                
            # Convert balance to JUP units (considering 6 decimals)
            balance = float(response.value.amount) / (10 ** self.jup_decimals)
            return balance
        except Exception as e:
            print(f"Error getting JUP balance: {e}")
            return 0

    def get_jpl_balance(self):
            try:
                # Convert addresses to Pubkey objects
                owner_pubkey = Pubkey.from_string(self.sol_address)
                token_pubkey = Pubkey.from_string(self.jpl_token_address)
                
                # Get the associated token account address
                from spl.token.instructions import get_associated_token_address
                token_account = get_associated_token_address(owner_pubkey, token_pubkey)
                
                try:
                    # Get the token account info
                    response = self.sol_client.get_token_account_balance(token_account)
                    
                    # Check if response is valid and has the expected structure
                    if hasattr(response, 'value') and response.value is not None:
                        balance = float(response.value.amount) / (10 ** self.jpl_decimals)
                        return balance
                    else:
                        # Account exists but might be empty
                        print("jpl is O !!!!!")
                        return 0
                        
                except Exception as account_error:
                    # This likely means the token account doesn't exist yet
                    if "could not find account" in str(account_error).lower():
                        print(f"No JPL token account found - this is normal if you've never held JPL")
                        return 0
                    else:
                        raise account_error  # Re-raise if it's a different error
                    
            except Exception as e:
                print(f"Error getting JPL balance: {str(e)}")
                return 0

    def get_wflr_balance(self):
        try:
            if not self.flare_w3.is_connected():
                print("Warning: Cannot connect to Flare node")
                return 0

            # Get the number of decimals
            decimals = self.wflr_contract.functions.decimals().call()
            
            # Get the balance
            balance = self.wflr_contract.functions.balanceOf(
                Web3.to_checksum_address(self.flare_address)
            ).call()
            
            # Convert to WFLR units
            return float(balance) / (10 ** decimals)
        except Exception as e:
            print(f"Error getting WFLR balance: {e}")
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
    jup_balance = checker.get_jup_balance()
    jpl_balance = checker.get_jpl_balance()
    wflr_balance = checker.get_wflr_balance()
    
    # Print results
    print("\nCryptocurrency Balances:")
    print("-----------------------")
    print(f"ETH Balance: {eth_balance:.6f} ETH")
    print(f"SOL Balance: {sol_balance:.6f} SOL")
    print(f"Flare Balance: {flare_balance:.6f} FLR")
    print(f"Jupiter Balance: {jup_balance:.6f} JUP")
    print(f"Jupiter PL Balance: {jpl_balance:.6f} JPL")
    print(f"Wrapped Flare Balance: {wflr_balance:.6f} WFLR")

if __name__ == "__main__":
    main()