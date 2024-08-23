# coding: UTF-8
import sys
bstack11lll1l_opy_ = sys.version_info [0] == 2
bstack1lll1ll_opy_ = 2048
bstack111lll1_opy_ = 7
def bstack1l1l1l1_opy_ (bstack11l1l1l_opy_):
    global bstack1l1l_opy_
    bstack11l1_opy_ = ord (bstack11l1l1l_opy_ [-1])
    bstack1l11ll_opy_ = bstack11l1l1l_opy_ [:-1]
    bstack1ll1l_opy_ = bstack11l1_opy_ % len (bstack1l11ll_opy_)
    bstack11111ll_opy_ = bstack1l11ll_opy_ [:bstack1ll1l_opy_] + bstack1l11ll_opy_ [bstack1ll1l_opy_:]
    if bstack11lll1l_opy_:
        bstack11ll111_opy_ = unicode () .join ([unichr (ord (char) - bstack1lll1ll_opy_ - (bstack11lll_opy_ + bstack11l1_opy_) % bstack111lll1_opy_) for bstack11lll_opy_, char in enumerate (bstack11111ll_opy_)])
    else:
        bstack11ll111_opy_ = str () .join ([chr (ord (char) - bstack1lll1ll_opy_ - (bstack11lll_opy_ + bstack11l1_opy_) % bstack111lll1_opy_) for bstack11lll_opy_, char in enumerate (bstack11111ll_opy_)])
    return eval (bstack11ll111_opy_)
import threading
bstack1lll1l1ll1l_opy_ = 1000
bstack1lll1l1ll11_opy_ = 5
bstack1lll1l1lll1_opy_ = 30
bstack1lll1ll111l_opy_ = 2
class bstack1lll1l1l1ll_opy_:
    def __init__(self, handler, bstack1lll1l1l1l1_opy_=bstack1lll1l1ll1l_opy_, bstack1lll1ll11ll_opy_=bstack1lll1l1ll11_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lll1l1l1l1_opy_ = bstack1lll1l1l1l1_opy_
        self.bstack1lll1ll11ll_opy_ = bstack1lll1ll11ll_opy_
        self.lock = threading.Lock()
        self.timer = None
    def start(self):
        if not self.timer:
            self.bstack1lll1l1llll_opy_()
    def bstack1lll1l1llll_opy_(self):
        self.timer = threading.Timer(self.bstack1lll1ll11ll_opy_, self.bstack1lll1ll1l11_opy_)
        self.timer.start()
    def bstack1lll1ll1111_opy_(self):
        self.timer.cancel()
    def bstack1lll1ll11l1_opy_(self):
        self.bstack1lll1ll1111_opy_()
        self.bstack1lll1l1llll_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lll1l1l1l1_opy_:
                t = threading.Thread(target=self.bstack1lll1ll1l11_opy_)
                t.start()
                self.bstack1lll1ll11l1_opy_()
    def bstack1lll1ll1l11_opy_(self):
        if len(self.queue) <= 0:
            return
        data = self.queue[:self.bstack1lll1l1l1l1_opy_]
        del self.queue[:self.bstack1lll1l1l1l1_opy_]
        self.handler(data)
    def shutdown(self):
        self.bstack1lll1ll1111_opy_()
        while len(self.queue) > 0:
            self.bstack1lll1ll1l11_opy_()