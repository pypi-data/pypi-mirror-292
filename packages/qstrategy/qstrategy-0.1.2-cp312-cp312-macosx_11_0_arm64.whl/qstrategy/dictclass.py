from typing import Dict


class DictClass:
    """字段类，将字典数据类型转换为类类型，方便直接访问"""

    def __init__(self, the_dict):
        """构造函数

        Args:
            the_dict (_type_): 字段对象
        """
        self._map = {}
        for key in the_dict:
            value = the_dict[key]
            if isinstance(value, dict):
                value = DictClass(value)
            elif isinstance(value, list):
                data = []
                for d in value:
                    if isinstance(d, dict):
                        data.append[DictClass(d)]
                    else:
                        data.append(d)
                value = d
            if isinstance(key, int):
                self._map[key] = value
            else:
                setattr(self, key, value)

    def to_dict(self) -> Dict:
        """类转换回字典

        Returns:
            Dict: 转换回去的字典
        """
        the_dict = {}
        for k, v in self.__dict__.items():
            if k == '_map':
                continue
            if isinstance(v, DictClass):
                v = v.to_dict()
            elif isinstance(v, list):
                data = []
                for d in data:
                    if isinstance(d, DictClass):
                        data.append(d.to_dict())
                    else:
                        data.append(d)
                v = data

            the_dict[k] = v
        if len(self._map) > 0:
            the_dict.update(self._map)
        return the_dict
