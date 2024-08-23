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
import datetime
import threading
from bstack_utils.helper import bstack11l1lll1l1_opy_, bstack111111lll_opy_, get_host_info, bstack111ll1l1l1_opy_, \
 bstack111ll1ll1_opy_, bstack1l111l1ll1_opy_, bstack11ll1l11ll_opy_, bstack1111ll1111_opy_
import bstack_utils.bstack1llll11l11_opy_ as bstack1l11lll1l_opy_
from bstack_utils.bstack1l1lll11ll_opy_ import bstack1ll11l1lll_opy_
from bstack_utils.percy import bstack1l11llll11_opy_
from bstack_utils.config import Config
bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
logger = logging.getLogger(__name__)
percy = bstack1l11llll11_opy_()
@bstack11ll1l11ll_opy_(class_method=False)
def bstack1ll1llll111_opy_(bs_config, bstack11lll1ll_opy_):
  try:
    data = {
        bstack1l1l1l1_opy_ (u"ࠪࡪࡴࡸ࡭ࡢࡶࠪᙽ"): bstack1l1l1l1_opy_ (u"ࠫ࡯ࡹ࡯࡯ࠩᙾ"),
        bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡥ࡮ࡢ࡯ࡨࠫᙿ"): bs_config.get(bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ "), bstack1l1l1l1_opy_ (u"ࠧࠨᚁ")),
        bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᚂ"): bs_config.get(bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᚃ"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᚄ"): bs_config.get(bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᚅ")),
        bstack1l1l1l1_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᚆ"): bs_config.get(bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡉ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩᚇ"), bstack1l1l1l1_opy_ (u"ࠧࠨᚈ")),
        bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᚉ"): datetime.datetime.now().isoformat() + bstack1l1l1l1_opy_ (u"ࠩ࡝ࠫᚊ"),
        bstack1l1l1l1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᚋ"): bstack111ll1l1l1_opy_(bs_config),
        bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵࡳࡵࡡ࡬ࡲ࡫ࡵࠧᚌ"): get_host_info(),
        bstack1l1l1l1_opy_ (u"ࠬࡩࡩࡠ࡫ࡱࡪࡴ࠭ᚍ"): bstack111111lll_opy_(),
        bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤࡸࡵ࡯ࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᚎ"): os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ᚏ")),
        bstack1l1l1l1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹ࡟ࡳࡧࡵࡹࡳ࠭ᚐ"): os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔࠧᚑ"), False),
        bstack1l1l1l1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࡣࡨࡵ࡮ࡵࡴࡲࡰࠬᚒ"): bstack11l1lll1l1_opy_(),
        bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚓ"): bstack1ll1ll1ll11_opy_(),
        bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡦࡨࡸࡦ࡯࡬ࡴࠩᚔ"): bstack1ll1ll11l11_opy_(bstack11lll1ll_opy_),
        bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺ࡟࡮ࡣࡳࠫᚕ"): bstack1l1l1l11ll_opy_(bs_config, bstack11lll1ll_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡹࡸ࡫ࡤࠨᚖ"), bstack1l1l1l1_opy_ (u"ࠨࠩᚗ"))),
        bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᚘ"): bstack111ll1ll1_opy_(bs_config),
    }
    return data
  except Exception as error:
    logger.error(bstack1l1l1l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡱࡣࡼࡰࡴࡧࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࠡࡽࢀࠦᚙ").format(str(error)))
    return None
def bstack1ll1ll11l11_opy_(framework):
  return {
    bstack1l1l1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡎࡢ࡯ࡨࠫᚚ"): framework.get(bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪ࠭᚛"), bstack1l1l1l1_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠭᚜")),
    bstack1l1l1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪ᚝"): framework.get(bstack1l1l1l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᚞")),
    bstack1l1l1l1_opy_ (u"ࠩࡶࡨࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᚟"): framework.get(bstack1l1l1l1_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᚠ")),
    bstack1l1l1l1_opy_ (u"ࠫࡱࡧ࡮ࡨࡷࡤ࡫ࡪ࠭ᚡ"): bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬᚢ"),
    bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ᚣ"): framework.get(bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᚤ"))
  }
def bstack1l1l1l11ll_opy_(bs_config, framework):
  bstack1111l1ll1_opy_ = False
  bstack1l111ll11_opy_ = False
  if bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴࠬᚥ") in bs_config:
    bstack1111l1ll1_opy_ = True
  else:
    bstack1l111ll11_opy_ = True
  bstack11lllll11_opy_ = {
    bstack1l1l1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩᚦ"): bstack1ll11l1lll_opy_.bstack1ll1ll11l1l_opy_(bs_config, framework),
    bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᚧ"): bstack1l11lll1l_opy_.bstack11l1l1ll11_opy_(bs_config),
    bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᚨ"): bs_config.get(bstack1l1l1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᚩ"), False),
    bstack1l1l1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨᚪ"): bstack1l111ll11_opy_,
    bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᚫ"): bstack1111l1ll1_opy_
  }
  return bstack11lllll11_opy_
@bstack11ll1l11ll_opy_(class_method=False)
def bstack1ll1ll1ll11_opy_():
  try:
    bstack1ll1ll11lll_opy_ = json.loads(os.getenv(bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᚬ"), bstack1l1l1l1_opy_ (u"ࠩࡾࢁࠬᚭ")))
    return {
        bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡴࡪࡰࡪࡷࠬᚮ"): bstack1ll1ll11lll_opy_
    }
  except Exception as error:
    logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡣࡳࡧࡤࡸ࡮ࡴࡧࠡࡩࡨࡸࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠠࡧࡱࡵࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࠠࡼࡿࠥᚯ").format(str(error)))
    return {}
def bstack1ll1lll1lll_opy_(array, bstack1ll1ll1l1ll_opy_, bstack1ll1ll1l111_opy_):
  result = {}
  for o in array:
    key = o[bstack1ll1ll1l1ll_opy_]
    result[key] = o[bstack1ll1ll1l111_opy_]
  return result
def bstack1ll1lll11l1_opy_(bstack1ll111l1l1_opy_=bstack1l1l1l1_opy_ (u"ࠬ࠭ᚰ")):
  bstack1ll1ll1l1l1_opy_ = bstack1l11lll1l_opy_.on()
  bstack1ll1ll1l11l_opy_ = bstack1ll11l1lll_opy_.on()
  bstack1ll1ll1ll1l_opy_ = percy.bstack1111111l1l_opy_()
  if bstack1ll1ll1ll1l_opy_ and not bstack1ll1ll1l11l_opy_ and not bstack1ll1ll1l1l1_opy_:
    return bstack1ll111l1l1_opy_ not in [bstack1l1l1l1_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪᚱ"), bstack1l1l1l1_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫᚲ")]
  elif bstack1ll1ll1l1l1_opy_ and not bstack1ll1ll1l11l_opy_:
    return bstack1ll111l1l1_opy_ not in [bstack1l1l1l1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩᚳ"), bstack1l1l1l1_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫᚴ"), bstack1l1l1l1_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧᚵ")]
  return bstack1ll1ll1l1l1_opy_ or bstack1ll1ll1l11l_opy_ or bstack1ll1ll1ll1l_opy_
@bstack11ll1l11ll_opy_(class_method=False)
def bstack1ll1llll1ll_opy_(bstack1ll111l1l1_opy_, test=None):
  bstack1ll1ll11ll1_opy_ = bstack1l11lll1l_opy_.on()
  if not bstack1ll1ll11ll1_opy_ or bstack1ll111l1l1_opy_ not in [bstack1l1l1l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ᚶ")] or test == None:
    return None
  return {
    bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᚷ"): bstack1ll1ll11ll1_opy_ and bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬᚸ"), None) == True and bstack1l11lll1l_opy_.bstack1lllllll1l_opy_(test[bstack1l1l1l1_opy_ (u"ࠧࡵࡣࡪࡷࠬᚹ")])
  }