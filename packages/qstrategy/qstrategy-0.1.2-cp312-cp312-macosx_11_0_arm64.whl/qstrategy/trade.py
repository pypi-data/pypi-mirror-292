from qstrategy.base_strategy import BaseStrategy
from qstrategy.event import RtQuot
from qstrategy.qstrategy import ShareState


class Strategy(BaseStrategy):
    """交易策略基类，实现交易策略，要继承于该类"""

    def on_trade(self, state: ShareState, quots: RtQuot):
        """有行情时回调，实现交易逻辑

        Args:
            state (ShareState): 共享状态
            quots (RtQuot): 行情
        """
        pass
