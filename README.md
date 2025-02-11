# CryptoRSI-TelegramBot

A Telegram bot that monitors cryptocurrency prices, calculates the Relative Strength Index (RSI), and provides buy/sell alerts based on RSI thresholds. The bot leverages CoinGecko API for real-time market data.

--- 

## **Project Overview**  
This project is a Telegram bot that provides cryptocurrency market updates and RSI-based alerts for buying or selling coins. It integrates with the CoinGecko API for real-time data and supports automated alerts every four hours.
![about](https://github.com/user-attachments/assets/79307364-a002-4a42-978e-702f8a60c2b3)

---

## **Key Features**  
- **Market Updates:** Get information on top 40 cryptocurrencies.  
- **RSI Alerts:** Determine whether to buy, sell, or hold based on RSI values.  
- **Chart Visualization:** Generate historical price charts for specified coins.  
- **Automated Alerts:** Receive automated updates every four hours.  
- **Admin-only Access:** Only admins can trigger bot commands.  

---

## **Installation and Setup**  
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CryptoRSI-TelegramBot.git
   cd CryptoRSI-TelegramBot
   ```
2. Install the required packages:
   ```bash
   pip install requests pandas matplotlib pyTelegramBotAPI
   ```
3. Replace placeholders in the code:
   - `API_KEY = "ENTER YOUR COIN GECKO API KEY HERE"`
   - `bot_token = "ENTER YOUR BOT TOKEN HERE"`
   - `chat_id = "ENTER CHAT ID HERE"`

4. Run the bot:
   ```bash
   python CryptoRSI_bot.py
   ```

---

## **Important Code Highlights**  

### **Fetching and Calculating RSI**
```python
def fetch_and_calculate_rsi(coin_id):
    url = f"{base_url}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "30"}
    response = requests.get(url, headers=headers, params=params)
    prices = response.json()["prices"]

    # RSI Calculation
    prices = pd.Series([price[1] for price in prices])
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=30).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=30).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]
```

### **Sending Coin Status Alerts**
```python
def process_coins(A_chat_id):
    status_messages = ["<b>Symbol</b>: Price : RSI : Status"]
    for coin_id, coin_name in coin_dict.items():
        status, price, rsi = fetch_and_calculate_rsi(coin_id)
        if status:
            status_messages.append(f"<b>{coin_name.upper()}</b>: {round(price, 2)} : {round(rsi, 2)} : {status}")
    bot.send_message(A_chat_id, "\n".join(status_messages), parse_mode='HTML')
```

---

## **Bot Commands**

- `/getupdate`: Get updates on top 40 coins.
  
![getupdate](https://github.com/user-attachments/assets/0c9c65cf-66a1-469a-a2fd-3bb81340eb7a)

- `/getcoininfo`: Get detailed info on a specific coin.
  
![getcoininfo](https://github.com/user-attachments/assets/33f329d4-88c2-4cdf-8276-2dcdf4cff1d6)

- `/marketchart`: Generate and view a coin's price history chart.
  
![marketchart](https://github.com/user-attachments/assets/fdb6bab7-cfe2-47df-8d2f-34dc1e35882c)

- `/startmonitoring`: Start 4-hour auto alert function.

![startmonitoring](https://github.com/user-attachments/assets/a79e8cc1-3d42-40c1-bc00-a073220b8197)

- `/stopmonitoring`: Stop auto alert function.
- `/help`: List available commands.

---

## **Future Work and Motivation**  
This project demonstrates the potential for automating crypto trading alerts using AI agents. Future work includes:  
- Full automation of the buying/selling process.  
- Integration with multiple chat services (e.g., WhatsApp).  
- Advanced trading strategies based on machine learning models.  

---

## **Call for Collaboration**  
I'm a student working on this project and looking for resources to bring it to life. If you're interested in supporting or collaborating, please reach out so we can make this happen together!

---
