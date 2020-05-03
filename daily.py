import ccxt
import requests
import json

api_key = "YOUR_BINANCE_API_KEY"
api_secret = "YOUR_BINANCE_API_SECRET"

line_notify_key = "YOUR_LINE_NOTIFY_API_KEY"


def line_notify(message, pic=False, path=None):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    message = "\n" + message
    payload = {'message': message}

    if pic == False:
        headers = {'Authorization': 'Bearer ' + line_notify_key}
        requests.post(line_notify_api, data=payload, headers=headers)
    else:
        files = {"imageFile": open(path, "rb")}
        headers = {'Authorization': 'Bearer ' + line_notify_key}
        requests.post(line_notify_api, data=payload, headers=headers, files=files)


def lambda_handler(event, context):
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
    })

    # 毎日購入する金額(USDT)
    order_size = 10

    digit = 6

    btc_price = float(binance.fetch_ticker('BTC/USDT')["last"])

    # 毎日購入する量(BTC)
    order_amount = round(order_size / btc_price, digit) + 0.000002

    # 成行注文
    try:
        market_buy_order = binance.create_market_buy_order("BTC/USDT", order_amount)
        line_notify(str(json.dumps(market_buy_order["info"], indent=4)))
    except Exception as e:
        line_notify(str(e))


    # 動作テスト用の指値注文の例
    # try:
    #     sample_price = 7333.02
    #     order_amount_sample = round(order_size / sample_price, digit)
    #     limit_order = binance.create_limit_buy_order("BTC/USDT", order_amount_sample, sample_price)
    #     # print(json.dumps(limit_order, indent=4))
    #     line_notify(str(json.dumps(limit_order["info"], indent=4)))
    # except Exception as e:
    #     line_notify(str(e))

    usdt_balance = binance.fetch_balance()["USDT"]["free"]
    btc_balance = binance.fetch_balance()["BTC"]["free"]
    avg_cost = round((1000 - usdt_balance) / btc_balance, 3)
    return_balance = (usdt_balance + btc_balance * btc_price - 1000) * 100 / 1000
    Estimated_Value = usdt_balance + btc_balance * btc_price

    text_1 = "BTC/USDT: " + str(btc_price) + "\n" + "\n"
    text_2 = "[Balance] \n" + "USDT: " + str(round(usdt_balance, 2)) + "\n" + "BTC: " + str(
        round(btc_balance, 8)) + "\n" + "Avg: " + str(avg_cost) + "\n" + "\n"
    text_3 = "Estimated Value: " + str(round(Estimated_Value, 3)) + "\n"
    text_4 = "Return: " + str(round(return_balance, 3)) + "%"
    line_notify(text_1 + text_2 + text_3 + text_4)


# if __name__ == '__main__':
#     lambda_handler(None, None)
