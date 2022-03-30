import json
import requests
from requests.structures import CaseInsensitiveDict
import datetime
import read_config

configs = read_config.read_config("C:/Users/roseh/PycharmProjects/AutomatedStockTrading/config.yml")


class Strategy():
    def __init__(self, strategy, stock_list_file_name):
        self.strategy = strategy
        self.file_name = stock_list_file_name

    def get_old_stock_list_date(self):
        file = open(self.file_name)
        try:
            stock_list = json.load(file)
            return stock_list
        except json.decoder.JSONDecodeError:
            return []

    def write_to_stock_json(self, stock_list):
        with open(self.file_name, 'w') as outfile:
            json.dump(stock_list, outfile)
            outfile.close()

    def scrape_tiger_app(self):
        origin_stock_list = self.get_old_stock_list_date()
        date_checker = 0
        if origin_stock_list:
            date_checker = datetime.datetime.utcfromtimestamp(origin_stock_list[-1]["date"] // 1000) # latest timestamp for the current strategy

        url = configs["tiger_urls"][self.strategy]

        headers = CaseInsensitiveDict()
        headers["accept"] = "*/*"
        headers["x-api-version"] = "v2"
        headers["cookie"] = configs["tiger_cookie"][self.strategy]
        headers["user-agent"] = configs["tiger_user_agent"]
        headers["accept-language"] = "en-US;q=1, zh-Hans-US;q=0.9, zh-Hant-US;q=0.8"
        headers["authorization"] = configs["tiger_authorization"]

        resp = requests.get(url, headers=headers)
        stock_list = resp.json()["data"]["stockList"]

        for stock in stock_list:
            if date_checker == 0 or datetime.datetime.utcfromtimestamp(stock["date"]//1000) > date_checker:
                origin_stock_list.append(stock)

        self.write_to_stock_json(origin_stock_list)

        return origin_stock_list






