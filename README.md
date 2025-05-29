# Stock Analyzer

## Project Setup Visual Studio Code

- **Initialize the Project:**
  - Press `Shift + Ctrl + P` to open the command palette.
  - Execute commands such as `Python: Create Environment` to set up your development environment.

- **Open Terminal:**
  - Use the shortcut `Ctrl + '` to open a terminal with the Python shell.

- **Install Necessary Libraries:**
  - Install required libraries using pip:
    ```bash
    pip3 install matplotlib
    pip3 install pandas
    pip3 install plotly
    pip3 install dash
    pip3 install yfinance
    pip3 install feedparser
    pip3 install snscrape
    pip3 install scikit-learn
    pip3 install tensorflow
    pip3 install jb-news
    ```
    *(Add any other necessary libraries as needed.)*

- **Create config.json file in root directory:**
config.json
``` json
{
  "assets": {
        "^NDX": {
        "name": "Nasdaq100",
        "start": "2020-01-01",
        "interval": "1d"
    },
        "^GSPC": {
        "name": "S&P500",
        "start": "2019-01-01",
        "interval": "1wk"
    }
  },
  "feeds":[
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GDAXI&region=US&lang=en-US",
    "https://www.tagesschau.de/xml/rss2"
  ],
  "promts":{
    "promt-analyze": "",
    "promt-optimize": "",
    "promt-predict": ""
  },
  "telegram": {
    "token": "",
    "chat_id": ""
  },
  "openAIKey": "",
  "X-Bearer": ""
}
```

## To-Do List

- **Fetch Twitter:** Fetch from Twitter API but just for Elon Musk
- **Fetch Truth Social:** Donald Trump
- **Calender:** Implement Holidays calendar
- **Saisonality:** Saisonality
- **EarningCalls:** Earning Calls
- **CSV Formatting:** Bring all of these data in line

## RSS Feed Links:

- **NASDAQ Earnings:**  
  [NASDAQ Earnings RSS Feed](https://www.nasdaq.com/feed/rssoutbound?category=Earnings)

- **Financial Times:**  
  [Financial Times RSS Feed](https://www.ft.com/myft/following/4c25743e-1f2f-4323-9269-d3e87c74de16.rss)

- **NASDAQ Feeds:**  
  - [NASDAQ General Feed](https://www.nasdaq.com/feed/rssoutbound?category=all)  
  - [NASDAQ-100 Feed](https://www.nasdaq.com/feed/rssoutbound?category=nasdaq-100)  
  - [NASDAQ ETFs Feed](https://www.nasdaq.com/feed/rssoutbound?category=ETFs)  
  - [NASDAQ IPOs Feed](https://www.nasdaq.com/feed/rssoutbound?category=IPOs)  
  - [NASDAQ Artificial Intelligence Feed](https://www.nasdaq.com/feed/rssoutbound?category=artificial-intelligence)  
  - [NASDAQ Nvidia Feed](https://www.nasdaq.com/feed/rssoutbound?symbol=NVDA)

- **Reuters:**  
  [Reuters News Releases RSS Feed](https://ir.thomsonreuters.com/rss/news-releases.xml?items=15)

- **Yahoo Finance:**  
  [Yahoo Finance RSS Feed](https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GDAXI&region=US&lang=en-US)

- **SEC:**  
  [SEC Press Releases RSS Feed](https://www.sec.gov/news/pressreleases.rss)

- **FED:**  
  [Federal Reserve Monetary Policy RSS Feed](https://www.federalreserve.gov/feeds/press_monetary.xml)

- **BEA:**  
  [Bureau of Economic Analysis RSS Feed](https://apps.bea.gov/rss/rss.xml)

- **EZB:**  
  [European Central Bank RSS Feed](https://www.ecb.europa.eu/rss/press.html)

- **Wall Street Journal:**  
  [Wall Street Journal World News RSS Feed](https://feeds.content.dowjones.io/public/rss/RSSWorldNews)

- **Boerse Frankfurt:**  
  [Boerse Frankfurt News RSS Feed](https://api.boerse-frankfurt.de/v1/feeds/news.rss)

- **Tagesschau:**  
  [Tagesschau RSS Feed](https://www.tagesschau.de/xml/rss2)

### Strategy Development
- **Performance Calculations:**
  - Calculate performance based on crossover markers.
  - Determine the average annual return.
  - Compute the win/loss ratio.
  - Calculate the profit factor (total profit divided by total loss).
  - Incorporate tax considerations into calculations.
  - Compare annual returns.
  - Assess time spent in the market.

### Seasonality Strategies

- **Sell in May and Go Away:**
  - *Traditional Approach:*
    - **Buy:** First trading day in May.
    - **Sell:** First trading day in September.
  - *Alternative Approach:*
    - **Buy:** First trading day in March and October.
    - **Sell:** First trading day in February and August.

- **January Barometer:**
  - *Traditional Saying:* "As goes January, so goes the year."
  - **Strategy:**
    - **Buy:** First trading day in February if January had a positive return.
    - **Sell:** Last trading day in December.
  - *Modified Strategy:*
    - **Buy:** If the closing price between January 7th and 11th exceeds the previous year's closing price.
    - **Sell:** Last trading day in December.

- **Year-End Rally (Santa Claus Rally):**
  - **Strategy 1:**
    - **Buy:** First trading day after December 14th.
    - **Sell:** First trading day after January 4th.
  - **Strategy 2:**
    - **Buy:** First trading day after October 24th.
    - **Sell:** First trading day after January 4th.

- **Holiday Effects:**
  - Analyze market performance around major holidays:
    - Christmas
    - Easter
    - Independence Day
    - Memorial Day
    - Thanksgiving

### Technical Indicators

- **Moving Averages:**
  - **200-Day Simple Moving Average (SMA):**
    - **Buy Signal:** When the price rises above the SMA200 by 3%.
    - **Sell Signal:** When the price falls below the SMA200 by 3%.

- **Momentum Indicators:**
  - Measure whether the price has increased or decreased over a specific period.
  - **Triple Momentum Indicator (TMI):**
    - **Entry Strategy:**
      - **Buy:** After the 24th of the month if the TMI is positive.
      - **Avoid Trading:** In July and August.

- **Donchian Channel:**
  - **Uptrend Market Phase:** Identified when a new 90-day high is reached without forming a 200-day low.
  - **Downtrend Market Phase:** Identified when a new 200-day low is reached without forming a 90-day high.

## Additional Considerations

- **Backtesting:** Implement backtesting for all strategies to validate their effectiveness.
- **Risk Management:** Define clear stop-loss and take-profit levels for each strategy.
- **Documentation:** Maintain thorough documentation for all strategies and calculations for future reference.

# 📬 Sending Telegram Notifications with Python

This guide shows you how to send messages from your Python application directly to your phone using a **Telegram bot**.

---

## Step 1: Create a Telegram Bot
1. Open the Telegram app.
2. Search for and start a chat with [@BotFather](https://t.me/BotFather).
3. Send the command: /newbot
4. Choose a **name** and a **username** (the username must end in `bot`, e.g., `my_alert_bot`).
5. BotFather will give you a **bot token**, e.g.: 123456789:ABCDefGhIJKlmNoPQRsTUVwxYZ
Save this token.
---
## Step 2: Get Your Chat ID
1. Send any message (e.g., "Hello") to your new bot.
2. Open this URL in your browser (replace `<TOKEN>` with your bot token):
3. Look for a `chat` object in the JSON response:
```json
"chat": {
  "id": 123456789,
  ... 
}
```
---
## Creaete config.json file
```json
{
  "telegram": {
    "token": "123456789:ABCDefGhIJKlmNoPQRsTUVwxYZ",
    "chat_id": "987654321"
  }
}
```

---