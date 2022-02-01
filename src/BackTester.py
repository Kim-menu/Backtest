"""
You must select a monetary unit carefully considering stock of country.
"""

# import for using abstract class
from abc import *
# import for stock information
import FinanceDataReader as Fdr
# import util functions
import util


# Abstract class for variety back tester
class BackTester(metaclass=ABCMeta):
    str_format = '%Y-%m-%d'
    last_price = 0

    def __init__(self, balance):
        self.balance = balance
        self.share = 0

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount

    def period_check(self, today, amount):
        if util.is_month_start(today) == 1:
            self.deposit(amount)

    def buy(self, ticker_data, today, buy_share):
        str_date = util.date_to_str(today)
        price = ticker_data['Close'][str_date]
        buy_share = min(buy_share, self.balance//price)
        self.withdraw(price * buy_share)
        self.share += buy_share

    def sell(self, ticker_data, today, sell_share):
        str_date = util.date_to_str(today)
        price = ticker_data['Close'][str_date]
        sell_share = min(sell_share, self.share)
        self.share -= sell_share
        self.deposit(price * sell_share)

    def valid(self, ticker_data, today):
        str_date = util.date_to_str(today)
        try:
            close = ticker_data['Close'][str_date]
        except KeyError:
            return False
        else:
            self.last_price = close
            return True

    def get_eval(self, today):
        return round((self.balance + self.share * self.last_price), 2)

    def status(self, today):
        print(util.date_to_str(today),
              "|", round(self.last_price, 2),
              "|", round(self.balance, 2),
              "|", self.share,
              "|", self.get_eval(today))

    @abstractmethod
    def trade(self, ticker_data, today):
        pass

    @abstractmethod
    def simulation(self, str_ticker, str_start_date, str_end_date, monthly_money):
        pass


# Smurf strategy
class SmurfTester(BackTester):
    def trade(self, ticker_data, today):
        if self.valid(ticker_data, today):
            str_date = util.date_to_str(today)
            change = ticker_data['Change'][str_date]
            if change <= 0:
                return True
        return False

    def simulation(self, str_ticker, str_start_date, str_end_date, monthly_money):
        ticker_data = Fdr.DataReader(str_ticker,
                                     str_start_date,
                                     str_end_date)
        today = util.str_to_date(str_start_date)
        end_date = util.str_to_date(str_end_date)
        print("date| price| balance| share| eval")
        while today <= end_date:
            self.period_check(today, monthly_money)
            if self.trade(ticker_data, today):
                if today.day > 24:
                    self.buy(ticker_data, today, 10000)
                else:
                    self.buy(ticker_data, today, 1)
            if self.valid(ticker_data, today):
                self.status(today)
            today = util.day_pass(today)


# Simple strategy
class SimpleTester(BackTester):
    this_month_buy = False

    def trade(self, ticker_data, today):
        if self.valid(ticker_data, today):
            if not self.this_month_buy:
                return True
        return False

    def simulation(self, str_ticker, str_start_date, str_end_date, monthly_money):
        ticker_data = Fdr.DataReader(str_ticker,
                                     str_start_date,
                                     str_end_date)
        today = util.str_to_date(str_start_date)
        end_date = util.str_to_date(str_end_date)
        print("date| price| balance| share| eval")
        while today <= end_date:
            if util.is_month_start(today):
                self.this_month_buy = False
            self.period_check(today, monthly_money)
            if self.trade(ticker_data, today):
                self.buy(ticker_data, today, 10000)
                self.this_month_buy = True
            if self.valid(ticker_data, today):
                self.status(today)
            today = util.day_pass(today)


# Rebalancing strategy
class RebalancingTester(BackTester):
    def trade(self, ticker_data, today):
        if self.valid(ticker_data, today):
            if self.risk_ratio(today) < 0.2 or self.risk_ratio(today) > 0.4:
                return True
        return False

    def risk_ratio(self, today):
        return self.balance / self.get_eval(today)

    def simulation(self, str_ticker, str_start_date, str_end_date, monthly_money):
        ticker_data = Fdr.DataReader(str_ticker,
                                     str_start_date,
                                     str_end_date)
        today = util.str_to_date(str_start_date)
        end_date = util.str_to_date(str_end_date)
        print("date| price| balance| share| eval")
        while today <= end_date:
            self.period_check(today, monthly_money)
            if self.trade(ticker_data, today):
                self.rebalancing(ticker_data, today)
            if self.valid(ticker_data, today):
                self.status(today)
            today = util.day_pass(today)

    def rebalancing(self, ticker_data, today):
        target_share = (self.get_eval(today) * 0.7) // self.last_price
        self.sell(ticker_data, today, 10000)
        self.buy(ticker_data, today, target_share)