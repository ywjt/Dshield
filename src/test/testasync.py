import time
import sys
sys.path.append("..")
from lib import async


class foo:
    @async
    def foo(self,x,y):
        c = 0
        while c < 5:
            c = c + 1
        print x,y
        time.sleep(1)


if __name__ == '__main__':
    foo().foo(456,789)
    foo().foo(123,y=345)