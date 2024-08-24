from qstrategy.base_strategy import BaseStrategy
from qstrategy.event import RtQuot
from qstrategy.qstrategy import ShareState


class Monitor(BaseStrategy):
    """监控策略基类，实现监控策略，要继承于该类"""

    def on_monitor(self, state: ShareState, quots: RtQuot):
        """有行情时回调，实现监控逻辑

        Args:
            state (ShareState): 共享状态
            quots (RtQuot): 行情
        """
        pass
