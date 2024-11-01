from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

#upbit

#korbit

#bithumb

#binance

#okx


def main():
    # Access the environment variables
    secret_key = os.getenv("SECRET_KEY")
    debug = os.getenv("DEBUG")
    print(f"Secret Key: {secret_key}")
    print(f"Debug Mode: {debug}")


if __name__ == "__main__":
    main()  # 메인 함수 실행
