from qstrategy.base_strategy import BaseStrategy
from qstrategy.event import RtQuot
from qstrategy.qstrategy import ShareState


class Select(BaseStrategy):
    """选股策略基类，实现选股策略，要继承于该类"""

    def select(self, state: ShareState, code: str, name: str):
        """选股时回调，计算选择逻辑

        Args:
            state (ShareState): 共享状态
            code (str): 代码
            name (str): 名称
        """
        pass
