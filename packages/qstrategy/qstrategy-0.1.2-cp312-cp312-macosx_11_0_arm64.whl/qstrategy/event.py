from typing import Dict, List, Optional, Tuple, Union
from qstrategy.dictclass import DictClass
from qstrategy.tradecomm import Entrust, Position, Signal

MonitorEvent = DictClass
"""监控事件"""

SelectHit = DictClass
"""选股命中信息"""

SelectEvent = DictClass
"""选股事件"""


class BrokerEvent:
    """q券商事件"""

    def __init__(self, *, event: str, data: Union[List[Signal], Tuple, List[Position]]) -> None:
        """构造函数

        Args:
            event (str): 事件名称
            data (Union[Signal, List[str], Entrust, BrokerEvent, MonitorEvent, SelectEvent]): 事件数据
        """
        self._event = event
        self._data = data

    def to_dict(self) -> Optional[Dict]:
        """事件转换为字典形式"""
        if self._event == 'entrust' or self._event == 'position':
            data = []
            for v in self._data:
                data.append(v.to_dict())
            return {self._event: data}
        elif self._event == 'fund_sync':
            return {self._event: self._data}


class Event:
    """事件"""

    def __init__(self, *, event: str, data: Union[Signal, List[str], Entrust, BrokerEvent, MonitorEvent, SelectEvent]) -> None:
        """构造函数

        Args:
            event (str): 事件名称
            data (Union[Signal, List[str], Entrust, BrokerEvent, MonitorEvent, SelectEvent]): 事件数据
        """
        self._event = event
        self._data = data

    @property
    def event(self) -> Optional[Dict]:
        """事件转为字典形式"""
        return self.to_dict()

    def to_dict(self) -> Optional[Dict]:
        """事件转为字典形式"""
        if self._event == 'signal' or self._event == 'entrust' or self._event == 'broker' or self._event == 'monitor' or self._event == 'select':
            return {self._event: self._data.to_dict()}
        elif self._event == 'subscribe':
            data = []
            for v in self._data:
                data.append(v)
            return {self._event: data}


Quot = DictClass
"""单个标的行情"""

RtQuot = DictClass
"""多个标的行情"""


class QuotEvent:
    start = 'start'
    morning_open = 'morning_open'
    morning_close = 'morning_close'
    noon_open = 'noon_open'
    noon_close = 'noon_close'
    end = 'end'
    quot = 'quot'

    def __init__(self, event):
        self._event = ''
        self._data = None
        if isinstance(event, str):
            self._event = event
        elif isinstance(event, dict):
            quot = DictClass(event)
            self._event = self.quot
            self._data = quot.quot

    @property
    def event(self) -> str:
        return self._event

    @property
    def data(self) -> Optional[RtQuot]:
        return self._data
