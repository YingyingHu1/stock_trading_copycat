import robin_stocks.robinhood as robin


def deposit(bank_name, amount_to_deposit):
    try:
        chase_checking_acct = [acct for acct in robin.get_linked_bank_accounts() if acct["bank_account_nickname"] == bank_name][0]
        chase_url = chase_checking_acct["url"]
        robin.deposit_funds_to_robinhood_account(chase_url, amount_to_deposit)
    except Exception as e:
        print("deposit has failed due to" + str(e))
