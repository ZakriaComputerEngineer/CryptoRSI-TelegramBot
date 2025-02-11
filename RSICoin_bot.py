import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
import telebot
from io import BytesIO
import threading

'''                                                            DATA
'''

# Define the dictionary with coin IDs
''' coin_dict = {
    "bitcoin": "btc",
    "ethereum": "eth",
    "binancecoin": "bnb",
} '''
coin_dict = {
    "bitcoin": "btc",
    "ethereum": "eth",
    "binancecoin": "bnb",
    "solana": "sol",
    "usd-coin": "usdc",
    "ripple": "xrp",
    "dogecoin": "doge",
    "cardano": "ada",
    "tron": "trx",
    "avalanche-2": "avax",
    "shiba-inu": "shib",
    "polkadot": "dot",
    "chainlink": "link",
    "bitcoin-cash": "bch",
    "uniswap": "uni",
    "near": "near",
    "litecoin": "ltc",
    "matic-network": "matic",
    "pepe": "pepe",
    "internet-computer": "icp",
    "ethereum-classic": "etc",
    "fetch-ai": "fet",
    "aptos": "apt",
    "render-token": "rndr",
    "stellar": "xlm",
    "hedera-hashgraph": "hbar",
    "cosmos": "atom",
    "arbitrum": "arb",
    "filecoin": "fil",
    "blockstack": "stx",
    "maker": "mkr",
    "vechain": "vet",
    "injective-protocol": "inj",
    "immutable-x": "imx",
    "first-digital-usd": "fdusd",
    "bittensor": "tao",
    "sui": "sui",
    "optimism": "op",
    "the-graph": "grt",
    "bonk": "bonk"
}

# CoinGecko API endpoint and headers
base_url = "https://api.coingecko.com/api/v3"

# Coin Gecko API
API_KEY = "ENTER YOUR COIN GECKO API KEY HERE"

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": API_KEY
}

# Initialize your bot with the token
bot_token = "ENTER YOUR BOT TOKEN HERE"
bot = telebot.TeleBot(bot_token)

# authenticated group ids
chat_id = "ENTER CHAT ID HERE"

# Global variable to control the monitoring loop
monitoring = False
monitoring_thread = None


'''                                                            FUNCTIONS
'''

''' # Main monitoring function (looped every 4 hours)
def start_monitoring(A_chat_id):
    #send_welcome_message(chat_id)  # Send welcome message again after authentication
    while True:
        process_coins(A_chat_id)
        # Sleep for 4 hours (14400 seconds)
        time.sleep(14400)
        #time.sleep(60) '''

# Main monitoring function (looped every 4 hours)


def start_monitoring(A_chat_id):
    global monitoring
    while monitoring:
        process_coins(A_chat_id)
        time.sleep(14400)  # 4 hours
        # time.sleep(300)  # 5 minutes for testing

# Function to check chat id and authenticate


def check_chat_id(A_chat_id):
    if str(A_chat_id) == chat_id:  # Replace with your predefined chat_id
        return True
    else:
        return False

# get dictionary items


def dictionary_to_string(dictionary):
    result = ""
    for key, value in dictionary.items():
        result += f"{key}: {value.upper()}\n"
    return result

# Function to send message to Telegram


def send_telegram_message(A_chat_id, message):
    bot.send_message(A_chat_id, message, parse_mode='HTML')

# Function to send welcome message


def send_welcome_message(A_chat_id):
    welcome_message = (
        "Hey, this is coin monitor here, I'll be updating you about which coin to buy or sell every 4 hours.\n\n"
        "Powered by coingecko.com X rsialert.com \n\n use this command to get all features: /help"
    )
    send_telegram_message(A_chat_id, welcome_message)


def search_dictionary(dictionary, search_value):
    for key, value in dictionary.items():
        if value == search_value:
            return key
    return "Value not found."


# Function to fetch historical market data and calculate RSI
def fetch_and_calculate_rsi(coin_id):
    try:
        url = f"{base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "30"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        prices = data["prices"]

        # Function to calculate RSI
        def calculate_rsi(prices, period=30):
            prices = pd.Series([price[1] for price in prices])
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        # Calculate RSI
        rsi = calculate_rsi(prices)
        rsi_value = rsi.iloc[-1]

        # Determine status based on RSI
        # status = "buy" if rsi_value < 20 else "sell" if (rsi_value > 60 & rsi_value < 70) else "overbought" if rsi_value > 70

        # Determine status based on RSI
        if rsi_value < 20:
            status = "oversold"
        # elif 60 < rsi_value <= 70:
        #    status = "sell"
        elif rsi_value > 80:
            status = "overbought"
        else:
            status = "hold"

        # Return status, latest price, and RSI value
        return status, prices[-1][1], rsi_value

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return None, None, None

# Function to process all coins in the dictionary


def process_coins(A_chat_id):
    status_messages = []
    status_messages.append("<b>Symbol</b>: Price : RSI : Status")
    for coin_id, coin_name in coin_dict.items():
        status, price, rsi = fetch_and_calculate_rsi(coin_id)
        if status:
            status_messages.append(
                f"<b>{coin_name.upper()}</b>: {round(price, 2)} : {round(rsi, 2)} : {status}")

    # Join all status messages
    all_status_message = "\n".join(status_messages)

    # Send message with all statuses
    # send_telegram_message(A_chat_id, all_status_message)

    # Send separate message for coins with status not hold ''
    not_hold_coins_message = "\n".join(
        [msg for msg in status_messages if "hold" not in msg.lower()])
    if not_hold_coins_message:
        send_telegram_message(A_chat_id, not_hold_coins_message)


# Function to check the coin symbol and send back information of one coin
def get_coin_info(message):
    user_chat_id = message.chat.id
    coin_symbol = message.text.strip().lower()
    coin_id = search_dictionary(coin_dict, coin_symbol)
    if coin_id == "Value not found.":
        send_telegram_message(
            user_chat_id, "Invalid coin symbol. Please try again.")
    else:
        status, price, rsi = fetch_and_calculate_rsi(coin_id)
        message = f'''
        Coin: {coin_symbol.upper()}
        Price: {round(price, 2)}
        RSI: {round(rsi, 2)}
        Status: {status}
        '''
        send_telegram_message(user_chat_id, message)


# Function to fetch and plot the coin chart
def get_coin_chart(coin_id, days):
    try:
        url = f"{base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        prices = data["prices"]

        # Plot the closing prices
        plt.figure(figsize=(12, 6))
        plt.plot(pd.Series([price[1]
                 for price in prices]), label='Closing Price')
        plt.title(f'{coin_id} Closing Prices')
        plt.legend()

        # Save plot to a bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return buf

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return None


def process_days(message, coin_id, coin_symbol):
    days = message.text.strip()
    chat_id = message.chat.id

    try:
        days = int(days)
        if days > 0:
            # Fetch and send the coin chart
            # buf = get_coin_chart(coin_id, days)
            # bot.send_photo(chat_id, buf, caption=f'{coin_symbol.capitalize()} {days}-day Market Chart')
            # Fetch and send the coin chart
            buf = get_coin_chart(coin_id, days)
            if buf is not None:
                bot.send_photo(
                    chat_id, buf, caption=f'{coin_symbol.capitalize()} {days}-day Market Chart')
            else:
                bot.send_message(
                    chat_id, "Error fetching data. Please try again later.")
        else:
            bot.send_message(
                chat_id, "Please enter a valid number of days (greater than 0).")
    except ValueError:
        bot.send_message(
            chat_id, "Please enter a valid number of days (integer).")


# Function to check the coin symbol and send chart
def market_chart(message):
    user_chat_id = message.chat.id
    coin_symbol = message.text.strip().lower()

    if coin_symbol in coin_dict.values():

        # Get coin id from coin symbol
        coin_id = search_dictionary(coin_dict, coin_symbol)

        # send_telegram_message(user_chat_id, f"The symbol '{coin_id}' is valid and present in the data.")

        sent_msg_days = bot.send_message(
            chat_id, "Please enter the number of days for the market chart (e.g., 30):")

        bot.register_next_step_handler(
            sent_msg_days, lambda msg: process_days(msg, coin_id, coin_symbol))

        # Get coin chart
        # chart = get_coin_chart(coin_id)

        # Send the plot as an image
        # bot.send_photo(user_chat_id, chart)
    else:
        send_telegram_message(
            user_chat_id, f"The given symbol '{coin_symbol}' is either incorrect or not present in the data.")
        # Optionally, you could ask the user to try again by calling ask_for_coin_symbol again
        # ask_for_coin_symbol(message)


'''                                                            MESSAGE & COMMAND HANDLERS
'''


''' # Handle the /getupdate command
@bot.message_handler(commands=['getupdate'])
def hand;le_get_update(message):
    print("message handler called!")
    chat_id = message.chat.id
    process_coins(chat_id)
 '''

# Handle the /getupdate command


@bot.message_handler(commands=['getupdate'])
def handle_get_update(message):
    user_chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is an admin
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            process_coins(user_chat_id)
        else:
            send_telegram_message(
                user_chat_id, "You are not authorized to use this command.")
    else:
        send_telegram_message(
            user_chat_id, "Only admins can use this feature.")


''' # Handle the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    #send_telegram_message(chat_id, "Please enter the authentication code.")
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            start_monitoring(user_chat_id)
        else:
            send_telegram_message(user_chat_id, "You are not authorized to use this command.")
    else:
            send_telegram_message(user_chat_id, "Only admins can use this feature.")
 '''
''' @bot.message_handler(func=lambda message: message.text == auth_code)
    def handle_auth_code(message):
        send_telegram_message(chat_id, "Authentication successful! Starting monitoring process.")
        start_monitoring(chat_id)

    @bot.message_handler(func=lambda message: message.text != auth_code)
    def handle_wrong_code(message):
        send_telegram_message(chat_id, "Incorrect code. Please try again.") '''


# Handle the /help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_chat_id = message.chat.id
    message = ("This bot can provide you multiple information by these commands (ONLY ADMINS ARE ALLOWED TO USE THESE COMMANDS):\n\n1) /getupdate - gives you update of top 40 coins (Please avoid using this command  )\n2) /getcoininfo - gives update of one coin\n3) /marketchart - gives coin price history chart\n4) /startmonitoring - initiate the 4 hour auto alert function of bot\n5) /stopmonitoring - stop the 4 hour auto alert function")
    send_telegram_message(user_chat_id, message)


# Handle the /getcoininfo command
@bot.message_handler(commands=['getcoininfo'])
def handle_get_coin_info(message):
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            message_text = "Please enter coin symbol from these given options:\n"
            message_text += dictionary_to_string(coin_dict)
            send_telegram_message(user_chat_id, message_text)
            # Register a handler to process the next message (coin symbol)
            bot.register_next_step_handler(message, get_coin_info)
        else:
            send_telegram_message(
                user_chat_id, "You are not authorized to use this command.")
    else:
        send_telegram_message(
            user_chat_id, "Only admins can use this feature.")


# Function to handle coin symbol input
@bot.message_handler(commands=['marketchart'])
def ask_for_coin_symbol(message):
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            message_text = "Please enter coin symbol from these given options:\n"
            message_text += dictionary_to_string(coin_dict)
            send_telegram_message(user_chat_id, message_text)
            # Register a handler to process the next message (coin symbol)
            bot.register_next_step_handler(message, market_chart)
        else:
            send_telegram_message(
                user_chat_id, "You are not authorized to use this command.")
    else:
        send_telegram_message(
            user_chat_id, "Only admins can use this feature.")


# Handle the /startmonitoring command
@bot.message_handler(commands=['startmonitoring'])
def handle_start_monitoring(message):
    global monitoring, monitoring_thread
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            if not monitoring:
                monitoring = True
                monitoring_thread = threading.Thread(
                    target=start_monitoring, args=(chat_id,))
                monitoring_thread.start()
                send_telegram_message(chat_id, "Monitoring started.")
            else:
                send_telegram_message(
                    chat_id, "Monitoring is already running.")
        else:
            send_telegram_message(
                user_chat_id, "You are not authorized to use this command.")
    else:
        send_telegram_message(
            user_chat_id, "Only admins can use this feature.")


# Handle the /stopmonitoring command
@bot.message_handler(commands=['stopmonitoring'])
def handle_stop_monitoring(message):
    global monitoring, monitoring_thread
    user_chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(user_chat_id, user_id)
    if member.status == 'administrator' or member.status == 'creator':
        if str(user_chat_id) == chat_id:
            if monitoring:
                monitoring = False
                monitoring_thread.join()
                send_telegram_message(chat_id, "Monitoring stopped.")
            else:
                send_telegram_message(chat_id, "Monitoring is not running.")
        else:
            send_telegram_message(
                user_chat_id, "You are not authorized to use this command.")
    else:
        send_telegram_message(
            user_chat_id, "Only admins can use this feature.")


# Start the bot
if __name__ == "__main__":
    send_welcome_message(chat_id)
    bot.infinity_polling()
