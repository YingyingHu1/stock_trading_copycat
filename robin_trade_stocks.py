import robin_stocks.robinhood as robin

import deposit_funds_to_robin
import read_config
import email_notification

configs = read_config.read_config("C:/Users/roseh/PycharmProjects/AutomatedStockTrading/config.yml")


def robin_login():
    cred = configs["cred"]
    email, pw, key = cred["email"], cred["pw"], cred["robin_key"]
    robin.login(email, pw, mfa_code=key)


def buy(stock_ticker, buy_price):
    order_id = is_pending_order_exist(stock_ticker)
    if order_id:
        robin.cancel_stock_order(order_id)

    num_shares = num_shares_to_buy(buy_price)

    deposit_status = need_more_cash(num_shares, buy_price)

    if deposit_status == -1:  # No enough cash to buy this stock, skip to buy
        print("Can't buy %s at target price %d because lack of cash"%(stock_ticker, buy_price))
        return False

    try:
        robin.order_buy_limit(symbol=stock_ticker,
                              quantity=num_shares,
                              limitPrice=buy_price)
        return True
    except Exception as e:
        print("buying %s at target price %d with %d shares has failed"% (stock_ticker, buy_price, num_shares))
        return False


def sell(stock_ticker, sell_price):
    # is there a pending order that need to cancel
    order_id = is_pending_order_exist(stock_ticker)
    if order_id:
        robin.cancel_stock_order(order_id)
        return True

    num_shares = get_num_shares_given_ticker(stock_ticker)
    try:
        robin.order_sell_limit(symbol=stock_ticker,
                               quantity=num_shares,
                               limitPrice=sell_price)
        return True
    except Exception as e:
        print("selling %s at target price %d with %d shares has failed"%(stock_ticker, sell_price, num_shares))
        return False


def num_shares_to_buy(price):
    num_shares = 0
    if price <= 10:
        num_shares = 10
    elif price <= 50:
        num_shares = 5
    elif price <= 100:
        num_shares = 3
    elif price <= 300:
        num_shares = 1
    return num_shares


def get_num_shares_given_ticker(stock_ticker):
    stock_info = robin.build_holdings().get(stock_ticker, None)
    num_shares = stock_info["quantity"] if stock_info else 0
    return num_shares


def need_more_cash(num_shares, buy_price):
    portfolio_cash = float(robin.profiles.load_account_profile()["portfolio_cash"])
    price_gap = portfolio_cash - num_shares * buy_price

    pending_transfer_amount= int(float(robin.profiles.load_account_profile()["uncleared_deposits"]))
    no_pending_transfer = (0==pending_transfer_amount)

    if not no_pending_transfer:
        print("there's pending transfer %d with $" % pending_transfer_amount)
        if price_gap < 0:
            return -1

    if price_gap < 0 and no_pending_transfer:
        bank_info = configs["bank_info"]
        bank_name = bank_info["bank_nickname"]
        amount_to_deposit = max(bank_info["amount_to_deposit"], price_gap)
        deposit_funds_to_robin.deposit(bank_name, amount_to_deposit)

        new_portfolio_cash = float(robin.profiles.load_account_profile()["portfolio_cash"])
        if new_portfolio_cash - portfolio_cash < amount_to_deposit:
            return -1
        else:
            return 1
    return 0


def stock_operation_by_strategy(strategy, stock_list):
    message = strategy.strategy + " Unoperated Stocks:\n"
    try:
        for stock in stock_list:
            if stock.get("is_operated", 0) == 0:
                ticker, selectedPrice, direction = stock["symbol"], stock["selectedPrice"], stock["longShort"]
                is_buy_success = is_sell_success = False

                if direction == 1:
                    is_buy_success = buy(ticker, selectedPrice)
                elif direction == -1:
                    is_sell_success = sell(ticker, selectedPrice)

                if is_buy_success or is_sell_success:
                    stock["is_operated"] = 1
                else:
                    message+=stock["symbol"] + " " + stock["longShort"] + "\n"

        # update the stock list
        strategy.write_to_stock_json(stock_list)

    except Exception as e:
        print("The operation has failed due to "+ str(e))

    email_notification.send_email(message)


def is_pending_order_exist(stock_ticker):
    try:
        stock_orders = robin.find_stock_orders(symbol=stock_ticker)
        open_order = [stock_order for stock_order in stock_orders if stock_order["cancel"]][0]
        order_id = open_order["id"]
        return order_id
    except Exception as e:
        return None


