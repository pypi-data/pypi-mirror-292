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
from collections import deque
from bstack_utils.constants import *
class bstack1l11l111l_opy_:
    def __init__(self):
        self._1llll1l1l1l_opy_ = deque()
        self._1llll11lll1_opy_ = {}
        self._1llll1l111l_opy_ = False
    def bstack1llll11l1l1_opy_(self, test_name, bstack1llll1l1l11_opy_):
        bstack1llll11ll11_opy_ = self._1llll11lll1_opy_.get(test_name, {})
        return bstack1llll11ll11_opy_.get(bstack1llll1l1l11_opy_, 0)
    def bstack1llll1l1lll_opy_(self, test_name, bstack1llll1l1l11_opy_):
        bstack1llll11llll_opy_ = self.bstack1llll11l1l1_opy_(test_name, bstack1llll1l1l11_opy_)
        self.bstack1llll11l1ll_opy_(test_name, bstack1llll1l1l11_opy_)
        return bstack1llll11llll_opy_
    def bstack1llll11l1ll_opy_(self, test_name, bstack1llll1l1l11_opy_):
        if test_name not in self._1llll11lll1_opy_:
            self._1llll11lll1_opy_[test_name] = {}
        bstack1llll11ll11_opy_ = self._1llll11lll1_opy_[test_name]
        bstack1llll11llll_opy_ = bstack1llll11ll11_opy_.get(bstack1llll1l1l11_opy_, 0)
        bstack1llll11ll11_opy_[bstack1llll1l1l11_opy_] = bstack1llll11llll_opy_ + 1
    def bstack1ll1111ll1_opy_(self, bstack1llll1l1111_opy_, bstack1llll1ll111_opy_):
        bstack1llll1l11ll_opy_ = self.bstack1llll1l1lll_opy_(bstack1llll1l1111_opy_, bstack1llll1ll111_opy_)
        bstack1llll11ll1l_opy_ = bstack11l111ll11_opy_[bstack1llll1ll111_opy_]
        bstack1llll1l11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠢࡼࡿ࠰ࡿࢂ࠳ࡻࡾࠤᓈ").format(bstack1llll1l1111_opy_, bstack1llll11ll1l_opy_, bstack1llll1l11ll_opy_)
        self._1llll1l1l1l_opy_.append(bstack1llll1l11l1_opy_)
    def bstack11l1ll11_opy_(self):
        return len(self._1llll1l1l1l_opy_) == 0
    def bstack1l1llll11_opy_(self):
        bstack1llll1l1ll1_opy_ = self._1llll1l1l1l_opy_.popleft()
        return bstack1llll1l1ll1_opy_
    def capturing(self):
        return self._1llll1l111l_opy_
    def bstack111l1llll_opy_(self):
        self._1llll1l111l_opy_ = True
    def bstack111lllll_opy_(self):
        self._1llll1l111l_opy_ = False