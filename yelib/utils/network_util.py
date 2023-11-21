import os

class ProxyContext(object):
    def __init__(self, proxy='http://192.168.1.45:10809'):
        self.proxy = proxy
        import os
    
    def __enter__(self):
        os.environ['HTTP_PROXY'] = self.proxy
        os.environ['HTTPS_PROXY'] = self.proxy
        print('entering proxy context', self.proxy)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb)-> None:
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        print('exit proxy context', self.proxy)    