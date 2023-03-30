import requests
import pymysql
import time
import json
from datetime import datetime, timedelta

# 資料庫設定
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "db": "crypto",
    "charset": "utf8"
}

# 設定需要查詢的幣種列表
symbols = ["BTC-USDT", "ETH-USDT", "XRP-USDT", "SOL-USDT",
           "AVAX-USDT", "NEAR-USDT", "ADA-USDT", "QNT-USDT", "LINK-USDT"]

while True:
    try:
        # 建立Connection物件
        conn = pymysql.connect(**db_settings)
        # 建立Cursor物件
        with conn.cursor() as cursor:
            # 建立空的字典
            data_dict = {}
            for symbol in symbols:
                url = f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}"
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    last_price = float(data["data"]["last"])
                    change_percent = round(
                        float(data["data"]["changeRate"]) * 100, 2)
                    volume = int(float(data["data"]["vol"]))

                    # 新增資料SQL語法
                    command = "INSERT INTO data(ticker, price, rate, vol, timestamp)VALUES(%s, %s, %s, %s, %s)"
                    
                    # 將現在時間減去一個月，以得到最近一個月的時間範圍
                    one_month_ago = datetime.now() - timedelta(days=30)
                    # 轉換時間格式
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 刪除一個月前的數據
                    delete_command = f"DELETE FROM data WHERE ticker='{symbol}' AND timestamp<'{one_month_ago_str}'"
                    cursor.execute(delete_command)
                    
                    # 新增最新的數據
                    cursor.execute(
                        command, (symbol, last_price, f"{change_percent:.2f}%", volume, timestamp))
                    # 儲存變更
                    conn.commit()
                    print(f"Data inserted for symbol {symbol}")

                    # 將資料加入字典中
                    # 修改 key 名稱為對應 HTML 元素的 ID 名稱
                    data_dict[f"{symbol.split('-')[0]}"] = {
                        "price": last_price,
                        "rate": change_percent,
                        "vol": volume
                    }
                else:
                    print(f"Failed to get data for symbol {symbol}")

        # 將字典資料寫入 JSON 檔案
        with open("data.json", "w") as f:
            json.dump(data_dict, f, indent=4)
        print("Data written to JSON file successfully")

    except Exception as ex:
        print(ex)
    finally:
        # 關閉Connection物件
        conn.close()

    # 每隔1秒執行一次
    time.sleep(1)
