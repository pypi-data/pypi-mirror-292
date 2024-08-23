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
import os
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack11l11ll1l_opy_ = {}
        bstack1l111l1l11_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨൊ"), bstack1l1l1l1_opy_ (u"ࠨࠩോ"))
        if not bstack1l111l1l11_opy_:
            return bstack11l11ll1l_opy_
        try:
            bstack1l111l1l1l_opy_ = json.loads(bstack1l111l1l11_opy_)
            if bstack1l1l1l1_opy_ (u"ࠤࡲࡷࠧൌ") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠥࡳࡸࠨ്")] = bstack1l111l1l1l_opy_[bstack1l1l1l1_opy_ (u"ࠦࡴࡹࠢൎ")]
            if bstack1l1l1l1_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ൏") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ൐") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠢࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠥ൑")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ൒"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠤࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠧ൓")))
            if bstack1l1l1l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࠦൔ") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤൕ") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠥൖ")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࠢൗ"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧ൘")))
            if bstack1l1l1l1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ൙") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ൚") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦ൛")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ൜"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨ൝")))
            if bstack1l1l1l1_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨ൞") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦൟ") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠧൠ")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࠤൡ"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠢൢ")))
            if bstack1l1l1l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨൣ") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦ൤") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ൥")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤ൦"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠢ൧")))
            if bstack1l1l1l1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ൨") in bstack1l111l1l1l_opy_ or bstack1l1l1l1_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧ൩") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨ൪")] = bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣ൫"), bstack1l111l1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ൬")))
            if bstack1l1l1l1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠤ൭") in bstack1l111l1l1l_opy_:
                bstack11l11ll1l_opy_[bstack1l1l1l1_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠥ൮")] = bstack1l111l1l1l_opy_[bstack1l1l1l1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦ൯")]
        except Exception as error:
            logger.error(bstack1l1l1l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡥࡹࡧ࠺ࠡࠤ൰") +  str(error))
        return bstack11l11ll1l_opy_