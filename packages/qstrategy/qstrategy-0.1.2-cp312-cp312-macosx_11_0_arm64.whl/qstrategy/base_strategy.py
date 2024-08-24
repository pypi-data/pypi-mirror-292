from abc import ABC
from typing import Optional
from qstrategy.event import QuotEvent
import pandas as pd
from qstrategy.qstrategy import ShareState
from qstrategy.tradecomm import Params


class BaseStrategy(ABC):
    """策略基类"""

    def init(self, state: ShareState, params: Optional[Params] = None):
        """策略初始化，策略如要初始化，重写该函数实现

        Args:
            state (ShareState): 策略共享状态
            params (Optional[Params], optional): 策略参数，默认是没有的
        """
        pass

    def destroy(self):
        """策略销毁，策略如要销毁，重写该函数实现
        """
        pass

    def description(self) -> str:
        """返回该策略是使用说明，参数配置等，markdown格式

        Returns:
            str: 策略说明
        """
        return "{} description".format(self.__class__.__name__)

    def name(self) -> str:
        """返回策略的名称，名称应该是有意义的，在同一个目录内唯一

        Returns:
            str: 策略名称
        """
        return self.__class__.__name__

    def on_start(self, state: ShareState):
        """策略启动时调用

        Args:
            state (ShareState): 策略共享状态
        """
        pass

    def on_end(self, state: ShareState):
        """策略结束时调用

        Args:
            state (ShareState): 策略共享状态
        """
        pass

    def on_strategy(self, state: ShareState, event: QuotEvent):
        """统一的调用入口，一般来说不要重写这个，保持原样就可以

        Args:
            state (ShareState): 策略共享状态
            event (QuotEvent): 事件

        """
        if event.event == QuotEvent.start:
            return self.on_start(state=state)
        elif event.event == QuotEvent.morning_open or event.event == QuotEvent.noon_open:
            return self.on_open(state=state, event=event)
        elif event.event == QuotEvent.morning_close or event.event == QuotEvent.noon_close:
            return self.on_close(state=state, event=event)
        elif event.event == QuotEvent.end:
            return self.on_end(state=state)
        elif event.event == QuotEvent.quot:
            for fn in ['on_broker', 'on_monitor', 'on_risk', 'on_trade']:
                fn = getattr(self, fn, None)
                if fn != None:
                    return fn(state, event.data)

    def on_open(self, state: ShareState, event: QuotEvent):
        """开市回调，一般不用管

        Args:
            state (ShareState): 策略共享状态
            event (QuotEvent): 事件

        """
        if event.event == QuotEvent.morning_open:
            return self.on_morning_open(state=state)
        elif event.event == QuotEvent.noon_open:
            return self.on_noon_open(state=state)

    def on_morning_open(self, state: ShareState):
        """早市开市回调

        Args:
            state (ShareState): 策略共享状态
        """
        pass

    def on_noon_open(self, state: ShareState):
        """午市开市回调

        Args:
            state (ShareState): 策略共享状态
        """
        pass

    def on_close(self, state: ShareState, event: QuotEvent):
        """休市回调，一般不用管

        Args:
            state (ShareState): 策略共享状态
            event (QuotEvent): 事件

        """
        if event.event == QuotEvent.morning_close:
            return self.on_morning_close(state=state)
        elif event.event == QuotEvent.noon_close:
            return self.on_noon_close(state=state)

    def on_morning_close(self, state: ShareState):
        """早市开市回调

        Args:
            state (ShareState): 策略共享状态
        """
        pass

    def on_noon_close(self, state: ShareState):
        """午市开市回调

        Args:
            state (ShareState): 策略共享状态
        """
        pass
