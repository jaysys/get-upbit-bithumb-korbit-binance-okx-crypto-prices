import requests
import pandas as pd
from tabulate import tabulate

def get_upbit_price(ticker: str) -> float:
    """
    Upbit에서 주어진 티커에 대한 현재 거래 가격을 가져옵니다.

    :param ticker: Upbit에서의 마켓 코드 (예: 'KRW-BTC')
    :return: 현재 거래 가격
    """
    try:
        url = f"https://api.upbit.com/v1/ticker?markets={ticker}"  # Upbit API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return data[0]['trade_price']  # 거래 가격 반환
    except Exception as e:
        print(f"Error fetching Upbit price for {ticker}: {e}")
        return None  # 오류 발생 시 None 반환

def get_korbit_price(ticker: str) -> float:
    """
    Korbit에서 주어진 티커에 대한 현재 거래 가격을 가져옵니다.

    :param ticker: Korbit에서의 통화 쌍 (예: 'btc')
    :return: 현재 거래 가격
    """
    try:
        url = f"https://api.korbit.co.kr/v1/ticker/detailed?currency_pair={ticker}_krw"  # Korbit API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return data['last']  # 마지막 거래 가격 반환
    except Exception as e:
        print(f"Error fetching Korbit price for {ticker}: {e}")
        return None  # 오류 발생 시 None 반환

def get_bithumb_price(ticker: str) -> float:
    """
    Bithumb에서 주어진 티커에 대한 현재 거래 가격을 가져옵니다.

    :param ticker: Bithumb에서의 마켓 코드 (예: 'BTC')
    :return: 현재 거래 가격
    """
    try:
        url = f"https://api.bithumb.com/public/ticker/{ticker}_KRW"  # Bithumb API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return float(data['data']['closing_price'])  # 종가 반환
    except Exception as e:
        print(f"Error fetching Bithumb price for {ticker}: {e}")
        return None  # 오류 발생 시 None 반환

def get_exchange_rate() -> float:
    """
    Upbit에서 KRW-USDT의 현재 환율을 가져옵니다.

    :return: KRW에 대한 USDT 환율
    """
    try:
        url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"  # Upbit API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return float(data[0]['trade_price'])  # 거래 가격 반환
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None  # 오류 발생 시 None 반환

def get_exchange_rate_ex() -> float:
    """
    USD에서 KRW로의 환율을 가져옵니다.

    :return: 환율 값 (USD to KRW)
    """
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"  # 환율 API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return data['rates']['KRW']  # KRW 환율 반환
    except Exception as e:
        print(f"Error fetching USD to KRW exchange rate: {e}")
        return None  # 오류 발생 시 None 반환



def get_binance_price(ticker: str) -> tuple[float, float]:
    """
    Binance에서 주어진 티커에 대한 현재 거래 가격을 가져오고,
    Upbit에서의 환율을 이용해 KRW 가격을 계산합니다.

    :param ticker: Binance에서의 티커 (예: 'BTC')
    :return: USDT 가격과 KRW 가격의 튜플
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}USDT"  # Binance API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        usdt_price = float(data['price'])  # USDT 가격
        
        # Upbit에서 KRW-USDT 환율 가져오기
        exchange_rate = get_exchange_rate()  # 환율 가져오기
        
        # KRW 가격 계산
        krw_price = usdt_price * exchange_rate if exchange_rate else None
        return usdt_price, krw_price  # USDT 가격과 KRW 가격 반환
    except Exception as e:
        print(f"Error fetching Binance price for {ticker}: {e}")
        return None, None  # 오류 발생 시 None 반환

def get_okx_price(ticker: str) -> tuple[float, float]:
    """
    OKX에서 주어진 티커에 대한 현재 거래 가격을 가져오고,
    Upbit에서의 환율을 이용해 KRW 가격을 계산합니다.

    :param ticker: OKX에서의 티커 (예: 'BTC')
    :return: USDT 가격과 KRW 가격의 튜플
    """
    try:
        url = f"https://www.okx.com/api/v5/market/ticker?instId={ticker}-USDT"  # OKX API URL
        response = requests.get(url)  # API 요청
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        usdt_price = float(data['data'][0]['last'])  # USDT 가격
        
        # Upbit에서 KRW-USDT 환율 가져오기
        exchange_rate = get_exchange_rate()  # 환율 가져오기
        
        # KRW 가격 계산
        krw_price = usdt_price * exchange_rate if exchange_rate else None
        return usdt_price, krw_price  # USDT 가격과 KRW 가격 반환
    except Exception as e:
        print(f"Error fetching OKX price for {ticker}: {e}")
        return None, None  # 오류 발생 시 None 반환

def get_crypto_prices_df():
    """
    다양한 거래소에서 특정 자산의 가격을 수집하여 DataFrame으로 반환합니다.

    :return: 자산 가격 데이터가 포함된 DataFrame과 환율
    """
    # 추적할 암호화폐 및 거래소 정의
    tickers = {
        "BTC": {"upbit": "KRW-BTC", "korbit": "btc", "binance": "BTC", "okx": "BTC", "bithumb": "BTC"},
        "SOL": {"upbit": "KRW-SOL", "korbit": "sol", "binance": "SOL", "okx": "SOL", "bithumb": "SOL"},
        "ETH": {"upbit": "KRW-ETH", "korbit": "eth", "binance": "ETH", "okx": "ETH", "bithumb": "ETH"},
        "FLR": {"upbit": "KRW-FLR", "korbit": "flr", "binance": "FLR", "okx": "FLR", "bithumb": "FLR"},
        "JUP": {"upbit": "KRW-JUP", "korbit": "jup", "binance": "JUP", "okx": "JUP", "bithumb": "JUP"},
    }
    
    data = []  # 가격 데이터를 저장할 리스트
    exchange_rate = None  # 환율 초기화
    
    # 각 자산에 대해 가격을 가져오기
    for asset, exchanges in tickers.items():
        binance_usdt, binance_krw = get_binance_price(exchanges['binance'])  # Binance 가격 가져오기
        if not exchange_rate:
            exchange_rate = get_exchange_rate()  # exchange_rate를 업데이트

        upbit_price = get_upbit_price(exchanges['upbit'])  # Upbit 가격 가져오기

        korbit_price = get_korbit_price(exchanges['korbit'])  # Korbit 가격 가져오기

        okx_usdt_price, okx_krw_price = get_okx_price(exchanges['okx'])  # OKX 가격 가져오기

        bithumb_price = get_bithumb_price(exchanges['bithumb'])  # Bithumb 가격 가져오기

        # 가격 데이터를 리스트에 추가
        data.append({
            "Asset": asset,
            "Upbit (KRW)": upbit_price,
            "Bithumb (KRW)": bithumb_price,
            "Korbit (KRW)": korbit_price,
            "Binance (USDT)": binance_usdt,
            "Binance (KRW)": binance_krw,
            "OKX (USDT)": okx_usdt_price,
            "OKX (KRW)": okx_krw_price
        })
    
    return pd.DataFrame(data), exchange_rate  # DataFrame과 환율 반환

def main():
    """
    메인 함수: 가격 데이터를 가져오고 포맷팅하여 출력합니다.
    """
    df, exchange_rate = get_crypto_prices_df()  # 데이터 가져오기
    
    # 숫자를 소수점 2자리로 포맷
    df["Upbit (KRW)"] = pd.to_numeric(df["Upbit (KRW)"], errors='coerce').map(lambda x: f"{x:.1f}" if x is not None else 'N/A')
    df["Bithumb (KRW)"] = pd.to_numeric(df["Bithumb (KRW)"], errors='coerce').map(lambda x: f"{x:.1f}" if x is not None else 'N/A')
    df["Korbit (KRW)"] = pd.to_numeric(df["Korbit (KRW)"], errors='coerce').map(lambda x: f"{x:.1f}" if x is not None else 'N/A')
    df["Binance (USDT)"] = pd.to_numeric(df["Binance (USDT)"], errors='coerce').map(lambda x: f"{x:.3f}" if x is not None else 'N/A')
    df["Binance (KRW)"] = pd.to_numeric(df["Binance (KRW)"], errors='coerce').map(lambda x: f"{x:.1f}" if x is not None else 'N/A')
    df["OKX (USDT)"] = pd.to_numeric(df["OKX (USDT)"], errors='coerce').map(lambda x: f"{x:.3f}" if x is not None else 'N/A')
    df["OKX (KRW)"] = pd.to_numeric(df["OKX (KRW)"], errors='coerce').map(lambda x: f"{x:.1f}" if x is not None else 'N/A')

    # DataFrame 출력
    tab = tabulate(df, headers='keys', tablefmt='pretty', showindex=False, colalign=("left", "right", "right", "right", "right", "right", "right", "right"))
    print(tab)

    # 환율 출력
    if exchange_rate is not None:  # krw to usdt
        print(f"Current Exchange Rate (KRW to USDT): {exchange_rate:.2f}")
    else:
        print("Failed to fetch exchange rate.")
    
    # 환율 출력_ex
    exchange_rate = get_exchange_rate_ex() # krw to usd
    if exchange_rate is not None:
        print(f"Current Exchange Rate (KRW to USD): {exchange_rate:.2f}")
    else:
        print("Failed to fetch exchange rate_ex.")

if __name__ == "__main__":
    main()  # 메인 함수 실행
