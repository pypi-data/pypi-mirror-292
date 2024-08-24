from ast import Dict
from typing import List, Optional, Tuple

from qdatac.loader import BlockLoader
from qstrategy.event import Event
from qstrategy.tradecomm import Account, Entrust, Position, Signal


# ta

def calc_chip_dist(data: List[Dict], ac: int = 1, chip_dist: Dict = None) -> Dict:
    """筹码分布计算，计算winner或cost时，先调用该函数

    Args:
        data (List[Dict]): k线数据
        ac (int, optional): 衰减系数，如不清楚怎么设置，直接用默认值， 默认值为 1。
        chip_dist (Dict, optional): 筹码分布，如果之前计算过，则传过来，减少计算量

    Returns:
        Dict: 筹码分布情况
    """
    pass


def calc_winner(chip_dist: Dict, data: List[Dict] = None, price: float = None) -> Dict:
    """计算胜率分布

    Args:
        chip_dist (Dict): 筹码分布情况，使用calc_chip_dist调用的结果
        data (List[Dict], optional): 原始k线数据。胜率的标准，使用的是close价格，data和price两者不能同时为空
        price (float, optional): 胜率的标准，使用的是固定价格，data和price两者不能同时为空

    Returns:
        Dict: 胜率分布情况
    """
    pass


def calc_cost(chip_dist: Dict, ratio: int) -> Dict:
    """计算成本分布

    Args:
        chip_dist (Dict): 筹码分布情况，使用calc_chip_dist调用的结果
        ratio (int): 百分之几的成本的价格

    Returns:
        Dict:  成本分布情况
    """
    pass


def ma(bar: List[float], ma_type: int) -> List[float]:
    """均线

    Args:
        bar (List[float]): K线
        ma_type (int): ma类型

    Returns:
        List[float]: 日线
    """
    pass


def shadow(last_close: float,
           open: float,
           close: float,
           low: float,
           high: float,) -> Tuple[float]:
    """k线各部分占比

    Args:
        last_close (float): 昨收价
        open (float): 开盘价
        close (float): 收盘价
        low (float): 最低价
        high (float): 最高价

    Returns:
        Tuple[float]: (振幅， 上天线占比， 蜡烛图占比， 下天线占比)
    """
    pass


# util
def uuid() -> str:
    pass


def new_signal(type: str, source: Dict, code: str, name: str, price: float, volume: int, desc: str) -> Dict:
    pass


def stat_select_hit(data: List[Dict], hit: int, hit_max: int) -> Dict:
    pass


# share state
class ShareState:
    def __init__(self, loader: BlockLoader, is_trading: bool,
                 is_started: bool, account: Optional[Account] = None) -> None:
        pass

    @property
    def loader(self) -> BlockLoader:
        pass

    @property
    def account(self) -> Optional[Account]:
        pass

    @property
    def is_trading(self) -> bool:
        pass

    @property
    def is_started(self) -> bool:
        pass

    def can_buy(self, price: float, volume: int) -> bool:
        pass

    def can_sell(self, code: str) -> int:
        pass

    def can_cancel(self, code: str) -> Optional[List[Entrust]]:
        pass

    def get_position_volume(self, code: str) -> Tuple[int, int]:
        pass

    def get_position(self, code: Optional[str] = None) -> Optional[List[Position]]:
        pass

    # 事件相关
    def buy(self, signal: Signal) -> None:
        pass

    def sell(self, signal: Signal) -> None:
        pass

    def cancel(self, signal: Signal) -> None:
        pass

    # 订阅行情
    def subscribe(self, codes: List[str]) -> None:
        pass

    def emit(self, event: Event) -> None:
        pass
