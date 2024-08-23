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
import logging
import os
import threading
from bstack_utils.helper import bstack1l1111ll_opy_
from bstack_utils.constants import bstack11l11l11l1_opy_
logger = logging.getLogger(__name__)
class bstack1ll11l1lll_opy_:
    bstack1lll1l1l11l_opy_ = None
    @classmethod
    def bstack11l111l1_opy_(cls):
        if cls.on():
            print(
                bstack1l1l1l1_opy_ (u"ࠨࡘ࡬ࡷ࡮ࡺࠠࡩࡶࡷࡴࡸࡀ࠯࠰ࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃࠠࡵࡱࠣࡺ࡮࡫ࡷࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡳࡳࡷࡺࠬࠡ࡫ࡱࡷ࡮࡭ࡨࡵࡵ࠯ࠤࡦࡴࡤࠡ࡯ࡤࡲࡾࠦ࡭ࡰࡴࡨࠤࡩ࡫ࡢࡶࡩࡪ࡭ࡳ࡭ࠠࡪࡰࡩࡳࡷࡳࡡࡵ࡫ࡲࡲࠥࡧ࡬࡭ࠢࡤࡸࠥࡵ࡮ࡦࠢࡳࡰࡦࡩࡥࠢ࡞ࡱࠫᚺ").format(os.environ[bstack1l1l1l1_opy_ (u"ࠤࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡎࡁࡔࡊࡈࡈࡤࡏࡄࠣᚻ")]))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡋ࡙ࡗࠫᚼ"), None) is None or os.environ[bstack1l1l1l1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡌ࡚ࡘࠬᚽ")] == bstack1l1l1l1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥᚾ"):
            return False
        return True
    @classmethod
    def bstack1ll1ll11l1l_opy_(cls, bs_config, framework=bstack1l1l1l1_opy_ (u"ࠨࠢᚿ")):
        bstack1ll1ll111ll_opy_ = framework in bstack11l11l11l1_opy_
        return bstack1l1111ll_opy_(bs_config.get(bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᛀ"), bstack1ll1ll111ll_opy_))
    @classmethod
    def bstack1ll1l1lllll_opy_(cls, framework):
        return framework in bstack11l11l11l1_opy_
    @classmethod
    def bstack1ll1lll1l1l_opy_(cls, bs_config, framework):
        return cls.bstack1ll1ll11l1l_opy_(bs_config, framework) is True and cls.bstack1ll1l1lllll_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬᛁ"), None)
    @staticmethod
    def bstack11ll1lllll_opy_():
        if getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭ᛂ"), None):
            return {
                bstack1l1l1l1_opy_ (u"ࠪࡸࡾࡶࡥࠨᛃ"): bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࠩᛄ"),
                bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᛅ"): getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪᛆ"), None)
            }
        if getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫᛇ"), None):
            return {
                bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ᛈ"): bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧᛉ"),
                bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᛊ"): getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨᛋ"), None)
            }
        return None
    @staticmethod
    def bstack1ll1l1llll1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1ll11l1lll_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack11ll1ll11l_opy_(test, hook_name=None):
        bstack1ll1ll111l1_opy_ = test.parent
        if hook_name in [bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪᛌ"), bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧᛍ"), bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭ᛎ"), bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪᛏ")]:
            bstack1ll1ll111l1_opy_ = test
        scope = []
        while bstack1ll1ll111l1_opy_ is not None:
            scope.append(bstack1ll1ll111l1_opy_.name)
            bstack1ll1ll111l1_opy_ = bstack1ll1ll111l1_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1ll1ll11111_opy_(hook_type):
        if hook_type == bstack1l1l1l1_opy_ (u"ࠤࡅࡉࡋࡕࡒࡆࡡࡈࡅࡈࡎࠢᛐ"):
            return bstack1l1l1l1_opy_ (u"ࠥࡗࡪࡺࡵࡱࠢ࡫ࡳࡴࡱࠢᛑ")
        elif hook_type == bstack1l1l1l1_opy_ (u"ࠦࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠣᛒ"):
            return bstack1l1l1l1_opy_ (u"࡚ࠧࡥࡢࡴࡧࡳࡼࡴࠠࡩࡱࡲ࡯ࠧᛓ")
    @staticmethod
    def bstack1ll1ll1111l_opy_(bstack1llllll1ll_opy_):
        try:
            if not bstack1ll11l1lll_opy_.on():
                return bstack1llllll1ll_opy_
            if os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࠦᛔ"), None) == bstack1l1l1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧᛕ"):
                tests = os.environ.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠧᛖ"), None)
                if tests is None or tests == bstack1l1l1l1_opy_ (u"ࠤࡱࡹࡱࡲࠢᛗ"):
                    return bstack1llllll1ll_opy_
                bstack1llllll1ll_opy_ = tests.split(bstack1l1l1l1_opy_ (u"ࠪ࠰ࠬᛘ"))
                return bstack1llllll1ll_opy_
        except Exception as exc:
            print(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡶࡪࡸࡵ࡯ࠢ࡫ࡥࡳࡪ࡬ࡦࡴ࠽ࠤࠧᛙ"), str(exc))
        return bstack1llllll1ll_opy_