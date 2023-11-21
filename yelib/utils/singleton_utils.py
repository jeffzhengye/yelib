
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


if __name__=="__main__":
    @singleton
    class Cls2(object):
        def __init__(self):
            pass

    cls1 = Cls2()
    cls2 = Cls2()
    print(id(cls1) == id(cls2))
    
    class Cls4(metaclass=SingletonMeta):
        pass

    cls1 = Cls4()
    cls2 = Cls4()
    print(id(cls1) == id(cls2))
