from threading import Timer

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData
)

from vnpy.trader.utility import BarGenerator, ArrayManager


class TestStrategy(CtaTemplate):
    """"""
    author = "用Python的交易员"

    test_trigger = 10

    tick_count = 0
    test_all_done = False

    parameters = ["test_trigger"]
    variables = {"tick_count": 'tick_count',
                 "test_all_done": 'tick_count',
                 "macd": 'macd',
                 "rsi": 'rsi'
                 }

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 15, self.on_x_min_bar)
        self.am = ArrayManager(900)

        self.last_bar: BarData = None
        self.macd = 0
        self.rsi = 0

        self.test_funcs = [
            self.test_market_order,
            self.test_limit_order,
            self.test_cancel_all,
            self.test_stop_order
        ]
        self.last_tick: TickData = None

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.load_bar(11)
        self.write_log("策略初始化")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        # self.bg.update_tick(tick)
        # if self.test_all_done:
        #     return
        #
        # self.last_tick = tick
        #
        # self.tick_count += 1
        # if self.tick_count >= self.test_trigger:
        #     self.tick_count = 0
        #
        #     if self.test_funcs:
        #         test_func = self.test_funcs.pop(0)
        #
        #         start = time()
        #         test_func()
        #         time_cost = (time() - start) * 1000
        #         self.write_log("耗时%s毫秒" % (time_cost))
        #     else:
        #         self.write_log("测试已全部完成")
        #         self.test_all_done = True

        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

        if self.inited:
            self.write_log(f"o:{bar.open_price};h:{bar.high_price};l:{bar.low_price};c:{bar.close_price}")

        self.put_event()

    def on_x_min_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)

        if not am.inited:
            return

        _dif, _dea, _macd = am.macd(144, 169, 22, True)
        _rsi = am.rsi(6, True)

        self.macd = round(_macd[-1]*2, 2)
        self.rsi = round(_rsi[-1], 2)

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        self.put_event()

    def test_market_order(self):
        """"""
        self.buy(self.last_tick.limit_up, 1)
        self.write_log("执行市价单测试")

    def test_limit_order(self):
        """"""
        self.buy(self.last_tick.limit_down, 1)
        self.write_log("执行限价单测试")

    def test_stop_order(self):
        """"""
        self.buy(self.last_tick.ask_price_1, 1, True)
        self.write_log("执行停止单测试")

    def test_cancel_all(self):
        """"""
        self.cancel_all()
        self.write_log("执行全部撤单测试")
