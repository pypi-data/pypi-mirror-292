
from typing import Dict
from qstrategy.dictclass import DictClass


Params = DictClass
"""策略参数"""

Account = DictClass
"""交易账户"""

Deal = DictClass
"""成交单"""

Entrust = DictClass
"""委托单"""

Position = DictClass
"""交易头寸"""

Signal = DictClass
"""交易信号"""


SignalTypeBuy = 'buy'
SignalTypeSell = 'sell'
SignalTypeCancel = 'cancel'


class SignalSource:
    @classmethod
    def risk(data: str) -> Dict:
        return {'risk': data}

    @classmethod
    def strategy(data: str) -> Dict:
        return {'strategy': data}

    @classmethod
    def broker(data: str) -> Dict:
        return {'broker': data}

    @classmethod
    def manual(data: str) -> Dict:
        return {'manual': data}
