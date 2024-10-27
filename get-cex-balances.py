import os
import time
import requests
import pyupbit
import pykorbit
import pybithumb
import pprint as pp
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dotenv import load_dotenv  # make .env file, then put CEX Access Key Info

class Exchange(ABC):
    """Abstract base class for cryptocurrency exchanges"""
    
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        
    @abstractmethod
    def get_balances(self) -> Optional[Dict[str, Any]]:
        """Get account balances"""
        pass
    
    @abstractmethod
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for given ticker"""
        pass
    
    @abstractmethod
    def get_ticker_symbol(self, base_currency: str) -> str:
        """Get exchange specific ticker symbol"""
        pass
    
    @abstractmethod
    def get_detailed_price(self, ticker: str) -> Optional[Dict[str, float]]:
        """Get detailed price information"""
        pass

class UpbitExchange(Exchange):
    """Upbit exchange implementation"""
    
    def __init__(self, access_key: str, secret_key: str):
        super().__init__(access_key, secret_key)
        self.client = pyupbit.Upbit(access_key, secret_key)
        
    def get_balances(self) -> Optional[Dict[str, Any]]:
        try:
            balances = self.client.get_balances()
            if not balances:
                print("Error: No balances retrieved from Upbit.")
                return None
            return balances
        except Exception as e:
            print(f"Error fetching balances from Upbit: {e}")
            return None
            
    def get_current_price(self, ticker: str) -> Optional[float]:
        if ticker.upper() == 'KRW':
            return 1.0
        
        ticker_symbol = self.get_ticker_symbol(ticker)
        try:
            price = pyupbit.get_current_price(ticker_symbol)
            return price
        except Exception as e:
            print(f"Error retrieving price for {ticker}: {e}")
            return None
            
    def get_ticker_symbol(self, base_currency: str) -> str:
        return f"KRW-{base_currency}"
    
    def get_detailed_price(self, ticker: str) -> Optional[Dict[str, float]]:
        """Get detailed price information from Upbit"""
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"markets": self.get_ticker_symbol(ticker)}
        
        try:
            response = requests.get(url, params=querystring)
            response.raise_for_status()
            res_json = response.json()
            
            if not res_json or 'trade_price' not in res_json[0]:
                print(f"Error: No data found for ticker {ticker} from Upbit.")
                return None
            
            price_info = {
                'market': res_json[0]['market'],
                'prev_closing_price': res_json[0]['prev_closing_price'],
                'opening_price': res_json[0]['opening_price'],
                'current_price': res_json[0]['trade_price'],
                'low_price': res_json[0]['low_price'],
                'high_price': res_json[0]['high_price']
            }
            
            # Print formatted price information
            print(f"[Upbit] {price_info['market']}")
            print(f" 전일 종료가: {price_info['prev_closing_price']:,.1f}")
            print(f" 오늘 시작가: {price_info['opening_price']:,.1f}")
            print(f" 오늘 현재가: {price_info['current_price']:,.1f}")
            print(f" 오늘 최저가: {price_info['low_price']:,.1f}")
            print(f" 오늘 최고가: {price_info['high_price']:,.1f}")
            
            return price_info
            
        except (requests.RequestException, IndexError, KeyError, ValueError) as e:
            print(f"Error fetching price information for {ticker} from Upbit: {e}")
            return None

class KorbitExchange(Exchange):
    """Korbit exchange implementation"""
    
    def __init__(self, access_key: str, secret_key: str):
        super().__init__(access_key, secret_key)
        self.client = pykorbit.Korbit(access_key, secret_key)
        
    def get_balances(self) -> Optional[Dict[str, Any]]:
        try:
            balances = self.client.get_balances()
            if not balances:
                print("Error: No balances retrieved from Korbit.")
                return None
            return balances
        except Exception as e:
            print(f"Error fetching balances from Korbit: {e}")
            return None
            
    def get_current_price(self, ticker: str) -> Optional[float]:
        if ticker.upper() == 'KRW':
            return 1.0
            
        try:
            price = pykorbit.get_current_price(ticker.upper())
            if price is None:
                return 0
            return price
        except Exception as e:
            print(f"Error retrieving price for {ticker}: {e}")
            return None
            
    def get_ticker_symbol(self, base_currency: str) -> str:
        return base_currency.upper()

    def get_detailed_price(self, ticker: str) -> Optional[Dict[str, float]]:
        """Get detailed price information from Korbit"""
        if ticker.upper() == 'KRW':
            return None

        try:
            # Korbit API를 통해 상세 가격 정보 조회
            ticker_symbol = f"{ticker.lower()}_krw"
            url = f"https://api.korbit.co.kr/v1/ticker/detailed?currency_pair={ticker_symbol}"
            
            response = requests.get(url)
            response.raise_for_status()
            res_json = response.json()
            
            if not res_json or 'last' not in res_json:
                print(f"Error: No data found for ticker {ticker} from Korbit.")
                return None
            
            # Korbit의 timestamp는 milliseconds 단위이므로 초 단위로 변환
            timestamp = int(res_json.get('timestamp', 0) / 1000)
            last_day = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            
            price_info = {
                'market': f"{ticker.upper()}",
                'prev_closing_price': float(res_json.get('prev_close', 0)),
                'opening_price': float(res_json.get('open', 0)),
                'current_price': float(res_json.get('last', 0)),
                'low_price': float(res_json.get('low', 0)),
                'high_price': float(res_json.get('high', 0)),
                'volume': float(res_json.get('volume', 0)),
                'timestamp': last_day
            }
            
            # Print formatted price information
            print(f"[Korbit] {ticker.upper()}/KRW ({price_info['timestamp']})")
            print(f" 전일 종료가: {price_info['prev_closing_price']:,.1f}")
            print(f" 오늘 시작가: {price_info['opening_price']:,.1f}")
            print(f" 오늘 현재가: {price_info['current_price']:,.1f}")
            print(f" 오늘 최저가: {price_info['low_price']:,.1f}")
            print(f" 오늘 최고가: {price_info['high_price']:,.1f}")
            print(f" 거래량: {price_info['volume']:,.4f}")
            
            return price_info
            
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Error fetching price information for {ticker} from Korbit: {e}")
            return None


class BithumbExchange(Exchange):
    """Bithumb exchange implementation"""
    
    def __init__(self, access_key: str, secret_key: str):
        super().__init__(access_key, secret_key)
        self.client = pybithumb.Bithumb(access_key, secret_key)
        
    def get_balances(self) -> Optional[Dict[str, Any]]:
        try:
            balances = self.client.get_balance('ALL')
            if not balances:
                print("Error: No balances retrieved from Bithumb.")
                return None
                
            # Bithumb returns (total, in_use, available) tuple for each currency
            formatted_balances = {}
            for currency, balance_info in balances.items():
                if isinstance(balance_info, tuple) and len(balance_info) >= 3:
                    formatted_balances[currency] = {
                        'total': float(balance_info[0]),
                        'in_use': float(balance_info[1]),
                        'available': float(balance_info[2])
                    }
            return formatted_balances
            
        except Exception as e:
            print(f"Error fetching balances from Bithumb: {e}")
            return None
            
    def get_current_price(self, ticker: str) -> Optional[float]:
        if ticker.upper() == 'KRW':
            return 1.0
            
        try:
            price = pybithumb.get_current_price(ticker)
            if price is None:
                return 0
            return float(price)
        except Exception as e:
            print(f"Error retrieving price for {ticker}: {e}")
            return None
            
    def get_ticker_symbol(self, base_currency: str) -> str:
        return base_currency.upper()
 

    def get_detailed_price(self, ticker: str) -> Optional[Dict[str, float]]:
        """Get detailed price information from Bithumb"""
        if ticker.upper() == 'KRW':
            return None

        try:
            # Ticker symbol을 대문자로 변환
            ticker_symbol = ticker.upper()
            
            # OHLCV 데이터 조회
            ohlcv = pybithumb.get_ohlcv(ticker_symbol)
            if ohlcv is None or ohlcv.empty:
                print(f"Error: No OHLCV data found for ticker {ticker} from Bithumb.")
                return None
                
            # 현재가 조회
            current_price = pybithumb.get_current_price(ticker_symbol)
            if current_price is None:
                print(f"Error: No current price found for ticker {ticker} from Bithumb.")
                return None
                
            # OHLCV 데이터에서 전일 및 금일 데이터 가져오기
            yesterday = ohlcv.iloc[-2] if len(ohlcv) >= 2 else ohlcv.iloc[-1]
            today = ohlcv.iloc[-1]
            
            # 가격 정보 구성
            price_info = {
                'market': f"{ticker_symbol}",
                'prev_closing_price': float(yesterday['close']),
                'opening_price': float(today['open']),
                'current_price': float(current_price),
                'low_price': float(today['low']),
                'high_price': float(today['high']),
                'volume': float(today['volume']),
                'timestamp': today.name.strftime('%Y-%m-%d')
            }
            
            # 포맷된 가격 정보 출력
            print(f"[Bithumb] {ticker_symbol}/KRW ({price_info['timestamp']})")
            print(f" 전일 종료가: {price_info['prev_closing_price']:,.1f}")
            print(f" 오늘 시작가: {price_info['opening_price']:,.1f}")
            print(f" 오늘 현재가: {price_info['current_price']:,.1f}")
            print(f" 오늘 최저가: {price_info['low_price']:,.1f}")
            print(f" 오늘 최고가: {price_info['high_price']:,.1f}")
            print(f" 거래량: {price_info['volume']:,.4f}")
            
            return price_info
            
        except Exception as e:
            print(f"Error fetching price information for {ticker} from Bithumb: {e}")
            return None


class ExchangeManager:
    """Manager class to handle multiple exchanges"""
    
    def __init__(self):
        load_dotenv()
        self.exchanges = {}
        
    def add_exchange(self, name: str, exchange: Exchange):
        self.exchanges[name] = exchange
        
    def get_exchange(self, name: str) -> Optional[Exchange]:
        return self.exchanges.get(name)
        
    @classmethod
    def create_default_manager(cls):
        """Create manager with default exchanges configured from environment variables"""
        manager = cls()
        
        # Initialize Upbit
        upbit_access = os.getenv("UPBIT_ACCESS_KEY")
        upbit_secret = os.getenv("UPBIT_SECRET_KEY")
        if upbit_access and upbit_secret:
            manager.add_exchange("upbit", UpbitExchange(upbit_access, upbit_secret))
            
        # Initialize Korbit
        korbit_access = os.getenv("KORBIT_ACCESS_KEY")
        korbit_secret = os.getenv("KORBIT_SECRET_KEY")
        if korbit_access and korbit_secret:
            manager.add_exchange("korbit", KorbitExchange(korbit_access, korbit_secret))
            
        # Initialize Bithumb
        bithumb_access = os.getenv("BITHUMB_ACCESS_KEY")
        bithumb_secret = os.getenv("BITHUMB_SECRET_KEY")
        if bithumb_access and bithumb_secret:
            manager.add_exchange("bithumb", BithumbExchange(bithumb_access, bithumb_secret))
            
        return manager


def util_clear():
    """Clear the console screen"""
    print("\033[H\033[J", end="")  # 현재 화면만 클리어
    print("\033[H\033[3J", end="")  # whole buffer clear



def util_timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.6f} seconds to execute.")
        return result
    return wrapper


@util_timing_decorator
def main():
    util_clear()
    
    # Create exchange manager with default configurations
    manager = ExchangeManager.create_default_manager()
    
    # Example usage with Upbit
    upbit = manager.get_exchange("upbit")
    if upbit:
        balances = upbit.get_balances()
        print("[Upbit balances]")
        pp.pprint(balances, width=300)
        #print("Upbit balances:", balances)    
           
        upbit_detailed_price = upbit.get_detailed_price("BTC")
        #print(upbit_detailed_price)

        price = upbit.get_current_price("BTC")
        print(f"Upbit, BTC price: {price}")
        print("-"*50)  # 구분선


    # Example usage with Korbit
    korbit = manager.get_exchange("korbit")
    if korbit:
        balances = korbit.get_balances()
        
        # 잔액(available)이 0보다 큰 항목만 필터링
        non_zero_balances = {
            asset: balance_info for asset, balance_info in balances.items()
            if float(balance_info.get('available', 0)) > 0 
                or float(balance_info.get('trade_in_use', 0)) > 0
                or float(balance_info.get('withdrawal_in_use', 0)) > 0
        }
        print("[Korbit balances]")        
        pp.pprint(non_zero_balances, width=300)        
        # print("Korbit non-zero balances:", non_zero_balances)

        korbit_detailed_price = korbit.get_detailed_price("BTC")
        #print(korbit_detailed_price)

        price = korbit.get_current_price("BTC")
        print(f"Korbit, BTC price: {price}")
        print("-" * 50)  # 구분선


    # Example usage with Bithumb
    bithumb = manager.get_exchange("bithumb")
    if bithumb:
        balances = bithumb.get_balances()
        print("[Bithumb balances]")
        pp.pprint(balances, width=300) 

        bithumb_detailed_price = bithumb.get_detailed_price("BTC")
        #print(bithumb_detailed_price)

        bit_ticker = "FLR"
        price = bithumb.get_current_price(bit_ticker)
        print(f"Bithumb, {bit_ticker} price: {price}")
        print("-"*50)  # 구분선

if __name__ == "__main__":
    main()
