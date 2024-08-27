# TIQS API Client

[![PyPI](https://img.shields.io/pypi/v/pytiqs.svg)](https://pypi.python.org/pypi/pytiqs) 

Official Python client for [Tiqs](https://tiqs.in/).

## Documentation

- [Tiqs HTTP API documentation](https://docs.tiqs.in/documentation)

## Installation

You can install the package using:
```shell
python3 -m pip install pytiqs
```

update to latest version
```shell
python3 -m pip install -U pytiqs
```

## API Usage

```python
import logging
from datetime import datetime
from pytiqs import Tiqs, constants

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s')

tiqs = Tiqs(app_id="<APP_ID>")

# login and generate the request token from the URL obtained from tiqs.login_url()

data = tiqs.generate_session(request_token="<REQUEST_TOKEN>", api_secret="<API_SECRET>")
token = data["token"]

# Optionally you can store the token in redis or local and load the token and set it in tiqs.
# which will allow you not to generate the token everytime

# tiqs = Tiqs(app_id="<APP_ID>")
# tiqs.set_token("<YOUR_TOKEN>")

try:
    order_no = tiqs.place_order(
        exchange=constants.Exchange.NFO,
        token="46338",
        qty=15,
        disclosed_qty=0,
        product=constants.ProductType.NRML,
        symbol="BANKNIFTY2441048900CE",
        transaction_type=constants.TransactionType.BUY,
        order_type=constants.OrderType.MARKET,
        variety=constants.Variety.REGULAR,
        price=0,
        validity=constants.Retention.DAY,
        tags=None,
        amo=False,
        trigger_price=None
    )
    logging.info("order id: {}".format(order_no))
except Exception as e:
    logging.error("error in order placement: {}".format(e))

# similarly you can modify order
modify_order_res = tiqs.modify_order_by_id(
    order_id="24040200000302",
    exchange=constants.Exchange.NFO,
    token="46338",
    qty=30,
    disclosed_qty=0,
    product=constants.ProductType.NRML,
    transaction_type=constants.TransactionType.BUY,
    order_type=constants.OrderType.MARKET,
    price=0,
    validity=constants.Retention.DAY,
    tags=None,
    amo=False,
    trigger_price=None
)

# get historical data with from date and to date.
data = tiqs.historical_data(
    "NSE",
    "7929",
    datetime(2024, 3, 21),
    datetime(2024, 3, 26),
    "5min"
)

# get order by order number
order = tiqs.get_order("24040200000302")

# delete order
delete_response = tiqs.delete_order("24040200000302")

# all orders
user_orders = tiqs.get_user_orders()

# all trades
user_trades = tiqs.get_user_trades()

# user details
user_details = tiqs.user_details()

# positions 
positions = tiqs.get_positions()

# all instruments
all_instruments = tiqs.get_instruments()

# market holidays
holidays = tiqs.holidays()

# index list
index_list = tiqs.index_list()

# get option chain symbols
option_chain_symbols = tiqs.option_chain_symbols()

# get greeks for instrument tokens
# response = {
#   46322: {    
#       'iv': 0.00010000000000000002, 
#       'delta': 0.9986509108400758, 
#       'gamma': 0, 
#       'theta': 4.48708902404856, 
#       'vega': 0
#       }, 
#   53007: {
#       'iv': 0.00010000000000000002, 
#       'delta': 0.9981117849253199, 
#       'gamma': 0, 
#       'theta': 5.15463209475131, 
#       'vega': 0
#       }
#   }
greeks = tiqs.greeks([46322, 53007])


# option chain for an underlying asset for a give expiry date
option_chain = tiqs.option_chain(params={
    "token": "26009",
    "exchange": "INDEX",
    "count": "10",
    "expiry": "10-APR-2024"
})

# get margin for order
order_margin = tiqs.order_margin(params={
    "exchange": "NFO",
    "token": "46304",
    "quantity": "30",
    "price": "0",
    "product": "I",
    "triggerPrice": "",
    "transactionType": "B",
    "order": "MKT"
})

# basket order margin
basket_orders_margin = tiqs.basket_order_margin(params=[{
    "exchange": "NFO",
    "token": "46304",
    "quantity": "30",
    "price": "0",
    "product": "I",
    "triggerPrice": "",
    "transactionType": "B",
    "order": "MKT"
}, {
    "exchange": "NFO",
    "token": "46304",
    "quantity": "15",
    "price": "0",
    "product": "I",
    "triggerPrice": "",
    "transactionType": "S",
    "order": "MKT"
}])

# full mode quote for single instrument
quote = tiqs.single_instrument_quote("full", 7929)

# full mode quote for multiple instruments
quotes = tiqs.multiple_instrument_quotes("full", [46304, 7929])


```

## Websockets

```python
import time
import logging
from pytiqs import TiqsSocket

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s')

def on_ticks(ws, ticks):
    logging.debug("Ticks: {}".format(ticks))


def on_connect(ws, response):
    ws.subscribe([7929])
    time.sleep(5)
    ws.set_mode(socketClient.MODE_LTP, [7929])
    
def on_order_update(ws, order):
    logging.debug("order: {}".format(order))


def on_close(ws, code, reason):
    logging.debug("closed, {}, {}".format(code, reason))
    ws.stop()
    

socketClient = TiqsSocket(app_id="<APP_ID>", token="<TOKEN>")
socketClient.on_ticks = on_ticks
socketClient.on_connect = on_connect
socketClient.on_order_update = on_order_update
socketClient.on_close = on_close

# if you want to keep this as non-blocking code use socketClient.connect(threaded=True)
socketClient.connect() 
```

### Constants
There are following types of constants:
```
Exchange: {
    NSE,
    NFO
}

TransactionType: {
    BUY,
    SELL
}

OrderType: {
    MARKET,
    LIMIT,
    STOP_LOSS_LIMIT,
    STOP_LOSS_MARKET
}

Retention: {
    DAY
    IOC
}

ProductType: {
    MIS,
    CNC,
    NRML
}

Variety: {
    REGULAR,
    COVER
}
```


### Flask app example:
Note: file should not be named as `flask.py` as it will interfere with package import.
```python
import logging

from flask import Flask, request, jsonify

import pytiqs

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s')

PORT = 3000
HOST = "127.0.0.1"

app_id = "<APP_ID>"
api_secret = "<API_SECRET>"
redirect_url = "http://{host}:{port}".format(host=HOST, port=PORT)

app = Flask(__name__, instance_relative_config=True)
tiqs = pytiqs.Tiqs(app_id=app_id)

root_html = """
    <div>Your app with appId: <b>{app_id}</b> should have redirect url set to: <b>{redirect_url}</b>.</div>
    <div>If not, please set it from developer console</a>.</div>
    <div>Please login <a href="{login_url}">here</a></div>
"""

login_html = """
    <div>
    <p><b>Id:</b> {id}</p>
    <p><b>Name:</b> {name}</p>
    <p><b>Token:</b> {token}</p>
    </div>
    <a target="_blank" href="/positions"><h4>Fetch user positions</h4></a>
    <a target="_blank" href="/orders"><h4>Fetch user orders</h4></a>
    """


@app.route("/")
def index():
    request_token = request.args.get("request-token")
    if not request_token:
        login_url = tiqs.login_url()
        return root_html.format(
            app_id=app_id,
            redirect_url=redirect_url,
            login_url=login_url
        )
    try:
        data = tiqs.generate_session(request_token=request_token, api_secret=api_secret)
        return login_html.format(token=data["token"], name=data["name"], id=data["userId"])
    except Exception as e:
        return """
            <span style="color: red">
                Error.
            </span>
            <a href='/'>Try again.<a>
        """


@app.route("/positions")
def positions():
    return jsonify(positions=tiqs.get_positions())


@app.route("/orders")
def orders():
    return jsonify(orders=tiqs.get_user_orders())


if __name__ == "__main__":
    logging.info("Starting server: http://{host}:{port}".format(host=HOST, port=PORT))
    app.run(host=HOST, port=PORT, debug=True)
```