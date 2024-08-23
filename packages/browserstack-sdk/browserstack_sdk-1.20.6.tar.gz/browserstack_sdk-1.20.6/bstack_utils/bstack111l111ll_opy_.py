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
from browserstack_sdk.bstack1llll111_opy_ import bstack111ll1l1_opy_
from browserstack_sdk.bstack11lll1ll11_opy_ import RobotHandler
def bstack1lll111lll_opy_(framework):
    if framework.lower() == bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᇻ"):
        return bstack111ll1l1_opy_.version()
    elif framework.lower() == bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᇼ"):
        return RobotHandler.version()
    elif framework.lower() == bstack1l1l1l1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ᇽ"):
        import behave
        return behave.__version__
    else:
        return bstack1l1l1l1_opy_ (u"ࠧࡶࡰ࡮ࡲࡴࡽ࡮ࠨᇾ")