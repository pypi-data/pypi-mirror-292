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
class bstack111l1l111_opy_:
    def __init__(self, handler):
        self._1lll1l11l1l_opy_ = None
        self.handler = handler
        self._1lll1l11lll_opy_ = self.bstack1lll1l11ll1_opy_()
        self.patch()
    def patch(self):
        self._1lll1l11l1l_opy_ = self._1lll1l11lll_opy_.execute
        self._1lll1l11lll_opy_.execute = self.bstack1lll1l1l111_opy_()
    def bstack1lll1l1l111_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1l1l1l1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࠨᔢ"), driver_command, None, this, args)
            response = self._1lll1l11l1l_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1l1l1l1_opy_ (u"ࠢࡢࡨࡷࡩࡷࠨᔣ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1lll1l11lll_opy_.execute = self._1lll1l11l1l_opy_
    @staticmethod
    def bstack1lll1l11ll1_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver