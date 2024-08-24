from qstrategy.base_strategy import BaseStrategy
from qstrategy.event import RtQuot
from qstrategy.qstrategy import ShareState
from qstrategy.tradecomm import Entrust


class Broker(BaseStrategy):
    """交易券商基类，实现交易券商，要继承于该类"""

    def on_broker(self, state: ShareState, quots: RtQuot):
        """有行情时回调，一般券商不关心行情，所以不用管，为了接口完整性而已

        Args:
            state (ShareState): 共享状态
            quots (RtQuot): 行情
        """
        pass

    def on_entrust(self, state: ShareState, entrust: Entrust):
        """委托请求，一般券商接口收到后，发送委托单给真实的券商

        Args:
            state (ShareState): 共享状态
            entrust (Entrust): 委托单
        """
        pass

    def on_poll(self, state: ShareState):
        """沦陷交易单据状态，真实的券商结果缓存后，由这个接口返回的交易系统

        Args:
            state (ShareState): 共享状态
        """
        pass
