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
import json
import logging
import os
import datetime
import threading
from bstack_utils.helper import bstack11l1ll111l_opy_, bstack11l1ll11ll_opy_, bstack1l1111lll_opy_, bstack11ll1l11ll_opy_, bstack111llll111_opy_, bstack111l1lllll_opy_, bstack1111ll1111_opy_
from bstack_utils.bstack1lll1l1l11l_opy_ import bstack1lll1l1l1ll_opy_
import bstack_utils.bstack11111l11l_opy_ as bstack1111ll11l_opy_
from bstack_utils.bstack1l1lll11ll_opy_ import bstack1ll11l1lll_opy_
import bstack_utils.bstack1llll11l11_opy_ as bstack1l11lll1l_opy_
from bstack_utils.bstack1ll1ll1l11_opy_ import bstack1ll1ll1l11_opy_
from bstack_utils.bstack1l111l11l1_opy_ import bstack11lllll1l1_opy_
bstack1ll1llll1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡨࡵ࡬࡭ࡧࡦࡸࡴࡸ࠭ࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪᖖ")
logger = logging.getLogger(__name__)
class bstack11l1l11l1_opy_:
    bstack1lll1l1l11l_opy_ = None
    bs_config = None
    bstack11lll1ll_opy_ = None
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def launch(cls, bs_config, bstack11lll1ll_opy_):
        cls.bs_config = bs_config
        cls.bstack11lll1ll_opy_ = bstack11lll1ll_opy_
        try:
            cls.bstack1ll1lll1ll1_opy_()
            bstack11l1l111l1_opy_ = bstack11l1ll111l_opy_(bs_config)
            bstack11l11lllll_opy_ = bstack11l1ll11ll_opy_(bs_config)
            data = bstack1111ll11l_opy_.bstack1ll1llll111_opy_(bs_config, bstack11lll1ll_opy_)
            config = {
                bstack1l1l1l1_opy_ (u"ࠫࡦࡻࡴࡩࠩᖗ"): (bstack11l1l111l1_opy_, bstack11l11lllll_opy_),
                bstack1l1l1l1_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᖘ"): cls.default_headers()
            }
            response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"࠭ࡐࡐࡕࡗࠫᖙ"), cls.request_url(bstack1l1l1l1_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠸࠯ࡣࡷ࡬ࡰࡩࡹࠧᖚ")), data, config)
            if response.status_code != 200:
                bstack1ll1ll1lll1_opy_ = response.json()
                if bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᖛ")] == False:
                    cls.bstack1ll1lllll11_opy_(bstack1ll1ll1lll1_opy_)
                    return
                cls.bstack1lll111ll1l_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᖜ")])
                cls.bstack1lll1111lll_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᖝ")])
                return None
            bstack1lll111l111_opy_ = cls.bstack1ll1llllll1_opy_(response)
            return bstack1lll111l111_opy_
        except Exception as error:
            logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡣࡳࡧࡤࡸ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡧࡱࡵࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࡻࡾࠤᖞ").format(str(error)))
            return None
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def stop(cls, bstack1lll111l1l1_opy_=None):
        if not bstack1ll11l1lll_opy_.on() and not bstack1l11lll1l_opy_.on():
            return
        if os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭ᖟ")) == bstack1l1l1l1_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦᖠ") or os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᖡ")) == bstack1l1l1l1_opy_ (u"ࠣࡰࡸࡰࡱࠨᖢ"):
            logger.error(bstack1l1l1l1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡷࡳࡵࠦࡢࡶ࡫࡯ࡨࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡗࡩࡸࡺࡈࡶࡤ࠽ࠤࡒ࡯ࡳࡴ࡫ࡱ࡫ࠥࡧࡵࡵࡪࡨࡲࡹ࡯ࡣࡢࡶ࡬ࡳࡳࠦࡴࡰ࡭ࡨࡲࠬᖣ"))
            return {
                bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪᖤ"): bstack1l1l1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᖥ"),
                bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᖦ"): bstack1l1l1l1_opy_ (u"࠭ࡔࡰ࡭ࡨࡲ࠴ࡨࡵࡪ࡮ࡧࡍࡉࠦࡩࡴࠢࡸࡲࡩ࡫ࡦࡪࡰࡨࡨ࠱ࠦࡢࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠ࡮࡫ࡪ࡬ࡹࠦࡨࡢࡸࡨࠤ࡫ࡧࡩ࡭ࡧࡧࠫᖧ")
            }
        try:
            cls.bstack1lll1l1l11l_opy_.shutdown()
            data = {
                bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᖨ"): datetime.datetime.now().isoformat() + bstack1l1l1l1_opy_ (u"ࠨ࡜ࠪᖩ")
            }
            if not bstack1lll111l1l1_opy_ is None:
                data[bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡲ࡫ࡴࡢࡦࡤࡸࡦ࠭ᖪ")] = [{
                    bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪᖫ"): bstack1l1l1l1_opy_ (u"ࠫࡺࡹࡥࡳࡡ࡮࡭ࡱࡲࡥࡥࠩᖬ"),
                    bstack1l1l1l1_opy_ (u"ࠬࡹࡩࡨࡰࡤࡰࠬᖭ"): bstack1lll111l1l1_opy_
                }]
            config = {
                bstack1l1l1l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧᖮ"): cls.default_headers()
            }
            bstack1111ll1l11_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡹࡵࡰࠨᖯ").format(os.environ[bstack1l1l1l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨᖰ")])
            bstack1ll1ll1llll_opy_ = cls.request_url(bstack1111ll1l11_opy_)
            response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠩࡓ࡙࡙࠭ᖱ"), bstack1ll1ll1llll_opy_, data, config)
            if not response.ok:
                raise Exception(bstack1l1l1l1_opy_ (u"ࠥࡗࡹࡵࡰࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡱࡳࡹࠦ࡯࡬ࠤᖲ"))
        except Exception as error:
            logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࡀࠠࠣᖳ") + str(error))
            return {
                bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬᖴ"): bstack1l1l1l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᖵ"),
                bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᖶ"): str(error)
            }
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1ll1llllll1_opy_(cls, response):
        bstack1ll1ll1lll1_opy_ = response.json()
        bstack1lll111l111_opy_ = {}
        if bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨ࡬ࡺࡸࠬᖷ")) is None:
            os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᖸ")] = bstack1l1l1l1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨᖹ")
        else:
            os.environ[bstack1l1l1l1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬᖺ")] = bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠬࡰࡷࡵࠩᖻ"), bstack1l1l1l1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫᖼ"))
        os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᖽ")] = bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪᖾ"), bstack1l1l1l1_opy_ (u"ࠩࡱࡹࡱࡲࠧᖿ"))
        if bstack1ll11l1lll_opy_.bstack1ll1lll1l1l_opy_(cls.bs_config, cls.bstack11lll1ll_opy_.get(bstack1l1l1l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡵࡴࡧࡧࠫᗀ"), bstack1l1l1l1_opy_ (u"ࠫࠬᗁ"))) is True:
            bstack1ll1lllll1l_opy_, bstack1ll1lll111l_opy_, bstack1lll1111ll1_opy_ = cls.bstack1ll1lll1l11_opy_(bstack1ll1ll1lll1_opy_)
            if bstack1ll1lllll1l_opy_ != None and bstack1ll1lll111l_opy_ != None:
                bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬᗂ")] = {
                    bstack1l1l1l1_opy_ (u"࠭ࡪࡸࡶࡢࡸࡴࡱࡥ࡯ࠩᗃ"): bstack1ll1lllll1l_opy_,
                    bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩᗄ"): bstack1ll1lll111l_opy_,
                    bstack1l1l1l1_opy_ (u"ࠨࡣ࡯ࡰࡴࡽ࡟ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬᗅ"): bstack1lll1111ll1_opy_
                }
            else:
                bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᗆ")] = {}
        else:
            bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᗇ")] = {}
        if bstack1l11lll1l_opy_.bstack11l1l1ll11_opy_(cls.bs_config) is True:
            bstack1ll1lll11ll_opy_, bstack1ll1lll111l_opy_ = cls.bstack1lll11111l1_opy_(bstack1ll1ll1lll1_opy_)
            if bstack1ll1lll11ll_opy_ != None and bstack1ll1lll111l_opy_ != None:
                bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᗈ")] = {
                    bstack1l1l1l1_opy_ (u"ࠬࡧࡵࡵࡪࡢࡸࡴࡱࡥ࡯ࠩᗉ"): bstack1ll1lll11ll_opy_,
                    bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨᗊ"): bstack1ll1lll111l_opy_,
                }
            else:
                bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᗋ")] = {}
        else:
            bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᗌ")] = {}
        if bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᗍ")].get(bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬᗎ")) != None or bstack1lll111l111_opy_[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᗏ")].get(bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧᗐ")) != None:
            cls.bstack1lll111ll11_opy_(bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡪࡸࡶࠪᗑ")), bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩᗒ")))
        return bstack1lll111l111_opy_
    @classmethod
    def bstack1ll1lll1l11_opy_(cls, bstack1ll1ll1lll1_opy_):
        if bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨᗓ")) == None:
            cls.bstack1lll111ll1l_opy_()
            return [None, None, None]
        if bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᗔ")][bstack1l1l1l1_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫᗕ")] != True:
            cls.bstack1lll111ll1l_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᗖ")])
            return [None, None, None]
        logger.debug(bstack1l1l1l1_opy_ (u"࡚ࠬࡥࡴࡶࠣࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠢࠩᗗ"))
        os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡆࡓࡒࡖࡌࡆࡖࡈࡈࠬᗘ")] = bstack1l1l1l1_opy_ (u"ࠧࡵࡴࡸࡩࠬᗙ")
        if bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨ࡬ࡺࡸࠬᗚ")):
            os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡊࡘࡖࠪᗛ")] = bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪ࡮ࡼࡺࠧᗜ")]
            os.environ[bstack1l1l1l1_opy_ (u"ࠫࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࡡࡉࡓࡗࡥࡃࡓࡃࡖࡌࡤࡘࡅࡑࡑࡕࡘࡎࡔࡇࠨᗝ")] = json.dumps({
                bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡴࡱࡥࡲ࡫ࠧᗞ"): bstack11l1ll111l_opy_(cls.bs_config),
                bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡻࡴࡸࡤࠨᗟ"): bstack11l1ll11ll_opy_(cls.bs_config)
            })
        if bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩᗠ")):
            os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧᗡ")] = bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫᗢ")]
        if bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᗣ")].get(bstack1l1l1l1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬᗤ"), {}).get(bstack1l1l1l1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩᗥ")):
            os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧᗦ")] = str(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᗧ")][bstack1l1l1l1_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩᗨ")][bstack1l1l1l1_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭ᗩ")])
        return [bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪ࡮ࡼࡺࠧᗪ")], bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ᗫ")], os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭ᗬ")]]
    @classmethod
    def bstack1lll11111l1_opy_(cls, bstack1ll1ll1lll1_opy_):
        if bstack1ll1ll1lll1_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᗭ")) == None:
            cls.bstack1lll1111lll_opy_()
            return [None, None]
        if bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᗮ")][bstack1l1l1l1_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᗯ")] != True:
            cls.bstack1lll1111lll_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᗰ")])
            return [None, None]
        if bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᗱ")].get(bstack1l1l1l1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬᗲ")):
            logger.debug(bstack1l1l1l1_opy_ (u"࡚ࠬࡥࡴࡶࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠢࠩᗳ"))
            parsed = json.loads(os.getenv(bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᗴ"), bstack1l1l1l1_opy_ (u"ࠧࡼࡿࠪᗵ")))
            capabilities = bstack1111ll11l_opy_.bstack1ll1lll1lll_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᗶ")][bstack1l1l1l1_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪᗷ")][bstack1l1l1l1_opy_ (u"ࠪࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᗸ")], bstack1l1l1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᗹ"), bstack1l1l1l1_opy_ (u"ࠬࡼࡡ࡭ࡷࡨࠫᗺ"))
            bstack1ll1lll11ll_opy_ = capabilities[bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࡚࡯࡬ࡧࡱࠫᗻ")]
            os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᗼ")] = bstack1ll1lll11ll_opy_
            parsed[bstack1l1l1l1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᗽ")] = capabilities[bstack1l1l1l1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᗾ")]
            os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᗿ")] = json.dumps(parsed)
            scripts = bstack1111ll11l_opy_.bstack1ll1lll1lll_opy_(bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᘀ")][bstack1l1l1l1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ᘁ")][bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧᘂ")], bstack1l1l1l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᘃ"), bstack1l1l1l1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࠩᘄ"))
            bstack1ll1ll1l11_opy_.bstack11l1l11111_opy_(scripts)
            commands = bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᘅ")][bstack1l1l1l1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫᘆ")][bstack1l1l1l1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࡚࡯ࡘࡴࡤࡴࠬᘇ")].get(bstack1l1l1l1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧᘈ"))
            bstack1ll1ll1l11_opy_.bstack11l1l11lll_opy_(commands)
            bstack1ll1ll1l11_opy_.store()
        return [bstack1ll1lll11ll_opy_, bstack1ll1ll1lll1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨᘉ")]]
    @classmethod
    def bstack1lll111ll1l_opy_(cls, response=None):
        os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᘊ")] = bstack1l1l1l1_opy_ (u"ࠨࡰࡸࡰࡱ࠭ᘋ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡉࡏࡎࡒࡏࡉ࡙ࡋࡄࠨᘌ")] = bstack1l1l1l1_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩᘍ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬᘎ")] = bstack1l1l1l1_opy_ (u"ࠬࡴࡵ࡭࡮ࠪᘏ")
        os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡎ࡜࡚ࠧᘐ")] = bstack1l1l1l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬᘑ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧᘒ")] = bstack1l1l1l1_opy_ (u"ࠤࡱࡹࡱࡲࠢᘓ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫᘔ")] = bstack1l1l1l1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤᘕ")
        cls.bstack1ll1lllll11_opy_(response, bstack1l1l1l1_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧᘖ"))
        return [None, None, None]
    @classmethod
    def bstack1lll1111lll_opy_(cls, response=None):
        os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᘗ")] = bstack1l1l1l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬᘘ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᘙ")] = bstack1l1l1l1_opy_ (u"ࠩࡱࡹࡱࡲࠧᘚ")
        os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫᘛ")] = bstack1l1l1l1_opy_ (u"ࠫࡳࡻ࡬࡭ࠩᘜ")
        cls.bstack1ll1lllll11_opy_(response, bstack1l1l1l1_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠧᘝ"))
        return [None, None, None]
    @classmethod
    def bstack1lll111ll11_opy_(cls, bstack1lll111l11l_opy_, bstack1ll1lll111l_opy_):
        os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧᘞ")] = bstack1lll111l11l_opy_
        os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᘟ")] = bstack1ll1lll111l_opy_
    @classmethod
    def bstack1ll1lllll11_opy_(cls, response=None, product=bstack1l1l1l1_opy_ (u"ࠣࠤᘠ")):
        if response == None:
            logger.error(product + bstack1l1l1l1_opy_ (u"ࠤࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠦᘡ"))
        for error in response[bstack1l1l1l1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪᘢ")]:
            bstack1111lll1l1_opy_ = error[bstack1l1l1l1_opy_ (u"ࠫࡰ࡫ࡹࠨᘣ")]
            error_message = error[bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᘤ")]
            if error_message:
                if bstack1111lll1l1_opy_ == bstack1l1l1l1_opy_ (u"ࠨࡅࡓࡔࡒࡖࡤࡇࡃࡄࡇࡖࡗࡤࡊࡅࡏࡋࡈࡈࠧᘥ"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack1l1l1l1_opy_ (u"ࠢࡅࡣࡷࡥࠥࡻࡰ࡭ࡱࡤࡨࠥࡺ࡯ࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࠣᘦ") + product + bstack1l1l1l1_opy_ (u"ࠣࠢࡩࡥ࡮ࡲࡥࡥࠢࡧࡹࡪࠦࡴࡰࠢࡶࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠨᘧ"))
    @classmethod
    def bstack1ll1lll1ll1_opy_(cls):
        if cls.bstack1lll1l1l11l_opy_ is not None:
            return
        cls.bstack1lll1l1l11l_opy_ = bstack1lll1l1l1ll_opy_(cls.bstack1lll1111l11_opy_)
        cls.bstack1lll1l1l11l_opy_.start()
    @classmethod
    def bstack11lll1l11l_opy_(cls):
        if cls.bstack1lll1l1l11l_opy_ is None:
            return
        cls.bstack1lll1l1l11l_opy_.shutdown()
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1lll1111l11_opy_(cls, bstack11ll1l1lll_opy_, bstack1ll1lll1111_opy_=bstack1l1l1l1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨᘨ")):
        config = {
            bstack1l1l1l1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫᘩ"): cls.default_headers()
        }
        response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠫࡕࡕࡓࡕࠩᘪ"), cls.request_url(bstack1ll1lll1111_opy_), bstack11ll1l1lll_opy_, config)
        bstack11l1l1l1l1_opy_ = response.json()
    @classmethod
    def bstack11ll1llll1_opy_(cls, bstack11ll1l1lll_opy_, bstack1ll1lll1111_opy_=bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫᘫ")):
        if not bstack1111ll11l_opy_.bstack1ll1lll11l1_opy_(bstack11ll1l1lll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪᘬ")]):
            return
        bstack11lllll11_opy_ = bstack1111ll11l_opy_.bstack1ll1llll1ll_opy_(bstack11ll1l1lll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫᘭ")], bstack11ll1l1lll_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪᘮ")))
        if bstack11lllll11_opy_ != None:
            bstack11ll1l1lll_opy_[bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࡢࡱࡦࡶࠧᘯ")] = bstack11lllll11_opy_
        if bstack1ll1lll1111_opy_ == bstack1l1l1l1_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡦࡺࡣࡩࠩᘰ"):
            cls.bstack1ll1lll1ll1_opy_()
            cls.bstack1lll1l1l11l_opy_.add(bstack11ll1l1lll_opy_)
        elif bstack1ll1lll1111_opy_ == bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩᘱ"):
            cls.bstack1lll1111l11_opy_([bstack11ll1l1lll_opy_], bstack1ll1lll1111_opy_)
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1ll1l1111l_opy_(cls, bstack1l1111111l_opy_):
        bstack1ll1llll11l_opy_ = []
        for log in bstack1l1111111l_opy_:
            bstack1lll1111l1l_opy_ = {
                bstack1l1l1l1_opy_ (u"ࠬࡱࡩ࡯ࡦࠪᘲ"): bstack1l1l1l1_opy_ (u"࠭ࡔࡆࡕࡗࡣࡑࡕࡇࠨᘳ"),
                bstack1l1l1l1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ᘴ"): log[bstack1l1l1l1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧᘵ")],
                bstack1l1l1l1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬᘶ"): log[bstack1l1l1l1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ᘷ")],
                bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡡࡵࡩࡸࡶ࡯࡯ࡵࡨࠫᘸ"): {},
                bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᘹ"): log[bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᘺ")],
            }
            if bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᘻ") in log:
                bstack1lll1111l1l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᘼ")] = log[bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩᘽ")]
            elif bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᘾ") in log:
                bstack1lll1111l1l_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᘿ")] = log[bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᙀ")]
            bstack1ll1llll11l_opy_.append(bstack1lll1111l1l_opy_)
        cls.bstack11ll1llll1_opy_({
            bstack1l1l1l1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪᙁ"): bstack1l1l1l1_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫᙂ"),
            bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭ᙃ"): bstack1ll1llll11l_opy_
        })
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1ll1lllllll_opy_(cls, steps):
        bstack1lll111l1ll_opy_ = []
        for step in steps:
            bstack1lll1111111_opy_ = {
                bstack1l1l1l1_opy_ (u"ࠩ࡮࡭ࡳࡪࠧᙄ"): bstack1l1l1l1_opy_ (u"ࠪࡘࡊ࡙ࡔࡠࡕࡗࡉࡕ࠭ᙅ"),
                bstack1l1l1l1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪᙆ"): step[bstack1l1l1l1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫᙇ")],
                bstack1l1l1l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩᙈ"): step[bstack1l1l1l1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪᙉ")],
                bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᙊ"): step[bstack1l1l1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᙋ")],
                bstack1l1l1l1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࠬᙌ"): step[bstack1l1l1l1_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭ᙍ")]
            }
            if bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᙎ") in step:
                bstack1lll1111111_opy_[bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ᙏ")] = step[bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᙐ")]
            elif bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᙑ") in step:
                bstack1lll1111111_opy_[bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩᙒ")] = step[bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᙓ")]
            bstack1lll111l1ll_opy_.append(bstack1lll1111111_opy_)
        cls.bstack11ll1llll1_opy_({
            bstack1l1l1l1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨᙔ"): bstack1l1l1l1_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩᙕ"),
            bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡩࡶࠫᙖ"): bstack1lll111l1ll_opy_
        })
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1ll1lllll1_opy_(cls, screenshot):
        cls.bstack11ll1llll1_opy_({
            bstack1l1l1l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫᙗ"): bstack1l1l1l1_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬᙘ"),
            bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳ࡬ࡹࠧᙙ"): [{
                bstack1l1l1l1_opy_ (u"ࠪ࡯࡮ࡴࡤࠨᙚ"): bstack1l1l1l1_opy_ (u"࡙ࠫࡋࡓࡕࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࠭ᙛ"),
                bstack1l1l1l1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨᙜ"): datetime.datetime.utcnow().isoformat() + bstack1l1l1l1_opy_ (u"࡚࠭ࠨᙝ"),
                bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᙞ"): screenshot[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡰࡥ࡬࡫ࠧᙟ")],
                bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩᙠ"): screenshot[bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᙡ")]
            }]
        }, bstack1ll1lll1111_opy_=bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩᙢ"))
    @classmethod
    @bstack11ll1l11ll_opy_(class_method=True)
    def bstack1111l111l_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack11ll1llll1_opy_({
            bstack1l1l1l1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩᙣ"): bstack1l1l1l1_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪᙤ"),
            bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩᙥ"): {
                bstack1l1l1l1_opy_ (u"ࠣࡷࡸ࡭ࡩࠨᙦ"): cls.current_test_uuid(),
                bstack1l1l1l1_opy_ (u"ࠤ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠣᙧ"): cls.bstack1l111l1111_opy_(driver)
            }
        })
    @classmethod
    def bstack11lll11l1l_opy_(cls, event: str, bstack11ll1l1lll_opy_: bstack11lllll1l1_opy_):
        bstack11llllllll_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧᙨ"): event,
            bstack11ll1l1lll_opy_.bstack1l11111ll1_opy_(): bstack11ll1l1lll_opy_.bstack11ll1l1l11_opy_(event)
        }
        cls.bstack11ll1llll1_opy_(bstack11llllllll_opy_)
    @classmethod
    def on(cls):
        if (os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡌ࡚ࡘࠬᙩ"), None) is None or os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡍ࡛࡙࠭ᙪ")] == bstack1l1l1l1_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦᙫ")) and (os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᙬ"), None) is None or os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭᙭")] == bstack1l1l1l1_opy_ (u"ࠤࡱࡹࡱࡲࠢ᙮")):
            return False
        return True
    @staticmethod
    def bstack1lll11111ll_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11l1l11l1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack1l1l1l1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩᙯ"): bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧᙰ"),
            bstack1l1l1l1_opy_ (u"ࠬ࡞࠭ࡃࡕࡗࡅࡈࡑ࠭ࡕࡇࡖࡘࡔࡖࡓࠨᙱ"): bstack1l1l1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫᙲ")
        }
        if os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨᙳ"), None):
            headers[bstack1l1l1l1_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨᙴ")] = bstack1l1l1l1_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬᙵ").format(os.environ[bstack1l1l1l1_opy_ (u"ࠥࡆࡘࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠦᙶ")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack1l1l1l1_opy_ (u"ࠫࢀࢃ࠯ࡼࡿࠪᙷ").format(bstack1ll1llll1l1_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩᙸ"), None)
    @staticmethod
    def bstack1l111l1111_opy_(driver):
        return {
            bstack111llll111_opy_(): bstack111l1lllll_opy_(driver)
        }
    @staticmethod
    def bstack1lll111111l_opy_(exception_info, report):
        return [{bstack1l1l1l1_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩᙹ"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack11ll1111l1_opy_(typename):
        if bstack1l1l1l1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᙺ") in typename:
            return bstack1l1l1l1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤᙻ")
        return bstack1l1l1l1_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᙼ")