import robin_trade_stocks, extract_tiger
import read_config
robin_trade_stocks.robin_login()

configs = read_config.read_config("C:/Users/roseh/PycharmProjects/AutomatedStockTrading/config.yml")
strategies = configs["tiger_strategies"]
stock_file_names = configs["stock_file_names"]

# strategies = ["multi_factor"]
# stock_file_names = ["multi_factor.json"]
#
# strategies = ["quant_optimization"]
# stock_file_names = ["quant_optimization.json"]
for strategy_name, stock_file_name in zip(strategies, stock_file_names):
    strategy = extract_tiger.Strategy(strategy=strategy_name, stock_list_file_name=stock_file_name)
    strategy_stock_list = strategy.scrape_tiger_app()
    robin_trade_stocks.stock_operation_by_strategy(strategy, strategy_stock_list)

