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
import requests
import logging
import threading
from urllib.parse import urlparse
from bstack_utils.constants import bstack11l1llll11_opy_ as bstack11l1l11l1l_opy_
from bstack_utils.bstack1ll1ll1l11_opy_ import bstack1ll1ll1l11_opy_
from bstack_utils.helper import bstack1ll1l11lll_opy_, bstack11llll11l1_opy_, bstack111ll1ll1_opy_, bstack11l1ll111l_opy_, bstack11l1ll11ll_opy_, bstack111111lll_opy_, get_host_info, bstack11l1lll1l1_opy_, bstack1l1111lll_opy_, bstack11ll1l11ll_opy_
from browserstack_sdk._version import __version__
logger = logging.getLogger(__name__)
@bstack11ll1l11ll_opy_(class_method=False)
def _11l1l1l111_opy_(driver, bstack1ll1l111l1_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack1l1l1l1_opy_ (u"ࠧࡰࡵࡢࡲࡦࡳࡥࠨ๢"): caps.get(bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧ๣"), None),
        bstack1l1l1l1_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭๤"): bstack1ll1l111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭๥"), None),
        bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧࠪ๦"): caps.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ๧"), None),
        bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ๨"): caps.get(bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ๩"), None)
    }
  except Exception as error:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩ࡫ࡴࡢ࡫࡯ࡷࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳࠢ࠽ࠤࠬ๪") + str(error))
  return response
def on():
    if os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ๫"), None) is None or os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ๬")] == bstack1l1l1l1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ๭"):
        return False
    return True
def bstack11l1l1ll11_opy_(config):
  return config.get(bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ๮"), False) or any([p.get(bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭๯"), False) == True for p in config.get(bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ๰"), [])])
def bstack1ll1llllll_opy_(config, bstack1l1l1l11l_opy_):
  try:
    if not bstack111ll1ll1_opy_(config):
      return False
    bstack11l1l111ll_opy_ = config.get(bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ๱"), False)
    if int(bstack1l1l1l11l_opy_) < len(config.get(bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ๲"), [])) and config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭๳")][bstack1l1l1l11l_opy_]:
      bstack11l1lll111_opy_ = config[bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ๴")][bstack1l1l1l11l_opy_].get(bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ๵"), None)
    else:
      bstack11l1lll111_opy_ = config.get(bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭๶"), None)
    if bstack11l1lll111_opy_ != None:
      bstack11l1l111ll_opy_ = bstack11l1lll111_opy_
    bstack11l1lll1ll_opy_ = os.getenv(bstack1l1l1l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ๷")) is not None and len(os.getenv(bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭๸"))) > 0 and os.getenv(bstack1l1l1l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ๹")) != bstack1l1l1l1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ๺")
    return bstack11l1l111ll_opy_ and bstack11l1lll1ll_opy_
  except Exception as error:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡺࡪࡸࡩࡧࡻ࡬ࡲ࡬ࠦࡴࡩࡧࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡪࡹࡳࡪࡱࡱࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡ࠼ࠣࠫ๻") + str(error))
  return False
def bstack1lllllll1l_opy_(test_tags):
  bstack11l1l1111l_opy_ = os.getenv(bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭๼"))
  if bstack11l1l1111l_opy_ is None:
    return True
  bstack11l1l1111l_opy_ = json.loads(bstack11l1l1111l_opy_)
  try:
    include_tags = bstack11l1l1111l_opy_[bstack1l1l1l1_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ๽")] if bstack1l1l1l1_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ๾") in bstack11l1l1111l_opy_ and isinstance(bstack11l1l1111l_opy_[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭๿")], list) else []
    exclude_tags = bstack11l1l1111l_opy_[bstack1l1l1l1_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ຀")] if bstack1l1l1l1_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨກ") in bstack11l1l1111l_opy_ and isinstance(bstack11l1l1111l_opy_[bstack1l1l1l1_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩຂ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡺࡦࡲࡩࡥࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡥࡤࡲࡳ࡯࡮ࡨ࠰ࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠤࠧ຃") + str(error))
  return False
def bstack11l1lllll1_opy_(config, bstack11l1ll1ll1_opy_, bstack11l1ll11l1_opy_, bstack11l1lll11l_opy_):
  bstack11l1l111l1_opy_ = bstack11l1ll111l_opy_(config)
  bstack11l11lllll_opy_ = bstack11l1ll11ll_opy_(config)
  if bstack11l1l111l1_opy_ is None or bstack11l11lllll_opy_ is None:
    logger.error(bstack1l1l1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡴࡸࡲࠥ࡬࡯ࡳࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࠿ࠦࡍࡪࡵࡶ࡭ࡳ࡭ࠠࡢࡷࡷ࡬ࡪࡴࡴࡪࡥࡤࡸ࡮ࡵ࡮ࠡࡶࡲ࡯ࡪࡴࠧຄ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ຅"), bstack1l1l1l1_opy_ (u"ࠨࡽࢀࠫຆ")))
    data = {
        bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧງ"): config[bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨຈ")],
        bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧຉ"): config.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨຊ"), os.path.basename(os.getcwd())),
        bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸ࡙࡯࡭ࡦࠩ຋"): bstack1ll1l11lll_opy_(),
        bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬຌ"): config.get(bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫຍ"), bstack1l1l1l1_opy_ (u"ࠩࠪຎ")),
        bstack1l1l1l1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪຏ"): {
            bstack1l1l1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡎࡢ࡯ࡨࠫຐ"): bstack11l1ll1ll1_opy_,
            bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨຑ"): bstack11l1ll11l1_opy_,
            bstack1l1l1l1_opy_ (u"࠭ࡳࡥ࡭࡙ࡩࡷࡹࡩࡰࡰࠪຒ"): __version__,
            bstack1l1l1l1_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࠩຓ"): bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨດ"),
            bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩຕ"): bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࠬຖ"),
            bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮࡚ࡪࡸࡳࡪࡱࡱࠫທ"): bstack11l1lll11l_opy_
        },
        bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠧຘ"): settings,
        bstack1l1l1l1_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࡃࡰࡰࡷࡶࡴࡲࠧນ"): bstack11l1lll1l1_opy_(),
        bstack1l1l1l1_opy_ (u"ࠧࡤ࡫ࡌࡲ࡫ࡵࠧບ"): bstack111111lll_opy_(),
        bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡷࡹࡏ࡮ࡧࡱࠪປ"): get_host_info(),
        bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫຜ"): bstack111ll1ll1_opy_(config)
    }
    headers = {
        bstack1l1l1l1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩຝ"): bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧພ"),
    }
    config = {
        bstack1l1l1l1_opy_ (u"ࠬࡧࡵࡵࡪࠪຟ"): (bstack11l1l111l1_opy_, bstack11l11lllll_opy_),
        bstack1l1l1l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧຠ"): headers
    }
    response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠧࡑࡑࡖࡘࠬມ"), bstack11l1l11l1l_opy_ + bstack1l1l1l1_opy_ (u"ࠨ࠱ࡹ࠶࠴ࡺࡥࡴࡶࡢࡶࡺࡴࡳࠨຢ"), data, config)
    bstack11l1l1l1l1_opy_ = response.json()
    if bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪຣ")]:
      parsed = json.loads(os.getenv(bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ຤"), bstack1l1l1l1_opy_ (u"ࠫࢀࢃࠧລ")))
      parsed[bstack1l1l1l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭຦")] = bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡤࡢࡶࡤࠫວ")][bstack1l1l1l1_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨຨ")]
      os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩຩ")] = json.dumps(parsed)
      bstack1ll1ll1l11_opy_.bstack11l1l11111_opy_(bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡧࡥࡹࡧࠧສ")][bstack1l1l1l1_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫຫ")])
      bstack1ll1ll1l11_opy_.bstack11l1l11lll_opy_(bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡩࡧࡴࡢࠩຬ")][bstack1l1l1l1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧອ")])
      bstack1ll1ll1l11_opy_.store()
      return bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡤࡢࡶࡤࠫຮ")][bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡔࡰ࡭ࡨࡲࠬຯ")], bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭ະ")][bstack1l1l1l1_opy_ (u"ࠩ࡬ࡨࠬັ")]
    else:
      logger.error(bstack1l1l1l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡸࡵ࡯ࡰ࡬ࡲ࡬ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠼ࠣࠫາ") + bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬຳ")])
      if bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ິ")] == bstack1l1l1l1_opy_ (u"࠭ࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡱࡣࡶࡷࡪࡪ࠮ࠨີ"):
        for bstack11l1l1l1ll_opy_ in bstack11l1l1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧຶ")]:
          logger.error(bstack11l1l1l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩື")])
      return None, None
  except Exception as error:
    logger.error(bstack1l1l1l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡷࡻ࡮ࠡࡨࡲࡶࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ຸࠢࠥ") +  str(error))
    return None, None
def bstack11l1l1lll1_opy_():
  if os.getenv(bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨູ")) is None:
    return {
        bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶ຺ࠫ"): bstack1l1l1l1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫົ"),
        bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧຼ"): bstack1l1l1l1_opy_ (u"ࠧࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡪࡤࡨࠥ࡬ࡡࡪ࡮ࡨࡨ࠳࠭ຽ")
    }
  data = {bstack1l1l1l1_opy_ (u"ࠨࡧࡱࡨ࡙࡯࡭ࡦࠩ຾"): bstack1ll1l11lll_opy_()}
  headers = {
      bstack1l1l1l1_opy_ (u"ࠩࡄࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ຿"): bstack1l1l1l1_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࠫເ") + os.getenv(bstack1l1l1l1_opy_ (u"ࠦࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠤແ")),
      bstack1l1l1l1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫໂ"): bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩໃ")
  }
  response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠧࡑࡗࡗࠫໄ"), bstack11l1l11l1l_opy_ + bstack1l1l1l1_opy_ (u"ࠨ࠱ࡷࡩࡸࡺ࡟ࡳࡷࡱࡷ࠴ࡹࡴࡰࡲࠪ໅"), data, { bstack1l1l1l1_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪໆ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack1l1l1l1_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡔࡦࡵࡷࠤࡗࡻ࡮ࠡ࡯ࡤࡶࡰ࡫ࡤࠡࡣࡶࠤࡨࡵ࡭ࡱ࡮ࡨࡸࡪࡪࠠࡢࡶࠣࠦ໇") + bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"ࠫ࡟່࠭"))
      return {bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷ້ࠬ"): bstack1l1l1l1_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹ໊ࠧ"), bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ໋"): bstack1l1l1l1_opy_ (u"ࠨࠩ໌")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack1l1l1l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡯࡯࡯ࠢࡲࡪࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡖࡨࡷࡹࠦࡒࡶࡰ࠽ࠤࠧໍ") + str(error))
    return {
        bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ໎"): bstack1l1l1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ໏"),
        bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭໐"): str(error)
    }
def bstack1ll1lll1l_opy_(caps, options, desired_capabilities={}):
  try:
    bstack11l1llll1l_opy_ = caps.get(bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ໑"), {}).get(bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ໒"), caps.get(bstack1l1l1l1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ໓"), bstack1l1l1l1_opy_ (u"ࠩࠪ໔")))
    if bstack11l1llll1l_opy_:
      logger.warn(bstack1l1l1l1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡈࡪࡹ࡫ࡵࡱࡳࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢ໕"))
      return False
    if options:
      bstack11l1ll1l1l_opy_ = options.to_capabilities()
    elif desired_capabilities:
      bstack11l1ll1l1l_opy_ = desired_capabilities
    else:
      bstack11l1ll1l1l_opy_ = {}
    browser = caps.get(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ໖"), bstack1l1l1l1_opy_ (u"ࠬ࠭໗")).lower() or bstack11l1ll1l1l_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ໘"), bstack1l1l1l1_opy_ (u"ࠧࠨ໙")).lower()
    if browser != bstack1l1l1l1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨ໚"):
      logger.warn(bstack1l1l1l1_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧ໛"))
      return False
    browser_version = caps.get(bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫໜ")) or caps.get(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ໝ")) or bstack11l1ll1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ໞ")) or bstack11l1ll1l1l_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧໟ"), {}).get(bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ໠")) or bstack11l1ll1l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ໡"), {}).get(bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫ໢"))
    if browser_version and browser_version != bstack1l1l1l1_opy_ (u"ࠪࡰࡦࡺࡥࡴࡶࠪ໣") and int(browser_version.split(bstack1l1l1l1_opy_ (u"ࠫ࠳࠭໤"))[0]) <= 94:
      logger.warn(bstack1l1l1l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡨࡴࡨࡥࡹ࡫ࡲࠡࡶ࡫ࡥࡳࠦ࠹࠵࠰ࠥ໥"))
      return False
    if not options is None:
      bstack11l1ll1l11_opy_ = bstack11l1ll1l1l_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ໦"), {})
      if bstack1l1l1l1_opy_ (u"ࠧ࠮࠯࡫ࡩࡦࡪ࡬ࡦࡵࡶࠫ໧") in bstack11l1ll1l11_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭໨"), []):
        logger.warn(bstack1l1l1l1_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡳࡵࡴࠡࡴࡸࡲࠥࡵ࡮ࠡ࡮ࡨ࡫ࡦࡩࡹࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠢࡖࡻ࡮ࡺࡣࡩࠢࡷࡳࠥࡴࡥࡸࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦࠢࡲࡶࠥࡧࡶࡰ࡫ࡧࠤࡺࡹࡩ࡯ࡩࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠦ໩"))
        return False
    return True
  except Exception as error:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡹࡥࡱ࡯ࡤࡢࡶࡨࠤࡦ࠷࠱ࡺࠢࡶࡹࡵࡶ࡯ࡳࡶࠣ࠾ࠧ໪") + str(error))
    return False
def set_capabilities(caps, config):
  try:
    bstack11l1ll1111_opy_ = config.get(bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ໫"), {})
    bstack11l1ll1111_opy_[bstack1l1l1l1_opy_ (u"ࠬࡧࡵࡵࡪࡗࡳࡰ࡫࡮ࠨ໬")] = os.getenv(bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ໭"))
    bstack11l1l1l11l_opy_ = json.loads(os.getenv(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ໮"), bstack1l1l1l1_opy_ (u"ࠨࡽࢀࠫ໯"))).get(bstack1l1l1l1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ໰"))
    caps[bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ໱")] = True
    if bstack1l1l1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ໲") in caps:
      caps[bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭໳")][bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭໴")] = bstack11l1ll1111_opy_
      caps[bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ໵")][bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ໶")][bstack1l1l1l1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ໷")] = bstack11l1l1l11l_opy_
    else:
      caps[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ໸")] = bstack11l1ll1111_opy_
      caps[bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ໹")][bstack1l1l1l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭໺")] = bstack11l1l1l11l_opy_
  except Exception as error:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠳ࠦࡅࡳࡴࡲࡶ࠿ࠦࠢ໻") +  str(error))
def bstack1ll11ll11l_opy_(driver, bstack11l1l1llll_opy_):
  try:
    setattr(driver, bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧ໼"), True)
    session = driver.session_id
    if session:
      bstack11l1l1ll1l_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11l1l1ll1l_opy_ = False
      bstack11l1l1ll1l_opy_ = url.scheme in [bstack1l1l1l1_opy_ (u"ࠣࡪࡷࡸࡵࠨ໽"), bstack1l1l1l1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳࠣ໾")]
      if bstack11l1l1ll1l_opy_:
        if bstack11l1l1llll_opy_:
          logger.info(bstack1l1l1l1_opy_ (u"ࠥࡗࡪࡺࡵࡱࠢࡩࡳࡷࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡴࡦࡵࡷ࡭ࡳ࡭ࠠࡩࡣࡶࠤࡸࡺࡡࡳࡶࡨࡨ࠳ࠦࡁࡶࡶࡲࡱࡦࡺࡥࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤࡪࡾࡥࡤࡷࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡨࡥࡨ࡫ࡱࠤࡲࡵ࡭ࡦࡰࡷࡥࡷ࡯࡬ࡺ࠰ࠥ໿"))
      return bstack11l1l1llll_opy_
  except Exception as e:
    logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡧࡲࡵ࡫ࡱ࡫ࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࡹ࡮ࡩࡴࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢༀ") + str(e))
    return False
def bstack11llll111_opy_(driver, class_name, name, module_name, path, bstack1ll1l111l1_opy_):
  try:
    bstack11l1l11l11_opy_ = {
        bstack1l1l1l1_opy_ (u"ࠬࡺࡨࡕࡧࡶࡸࡗࡻ࡮ࡖࡷ࡬ࡨࠬ༁"): threading.current_thread().current_test_uuid,
        bstack1l1l1l1_opy_ (u"࠭ࡴࡩࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫ༂"): os.environ.get(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ༃"), bstack1l1l1l1_opy_ (u"ࠨࠩ༄")),
        bstack1l1l1l1_opy_ (u"ࠩࡷ࡬ࡏࡽࡴࡕࡱ࡮ࡩࡳ࠭༅"): os.environ.get(bstack1l1l1l1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ༆"), bstack1l1l1l1_opy_ (u"ࠫࠬ༇"))
    }
    logger.debug(bstack1l1l1l1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡣࡹ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠨ༈"))
    logger.debug(driver.execute_async_script(bstack1ll1ll1l11_opy_.perform_scan, {bstack1l1l1l1_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࠨ༉"): name}))
    logger.debug(driver.execute_async_script(bstack1ll1ll1l11_opy_.bstack11l1l11ll1_opy_, bstack11l1l11l11_opy_))
    logger.info(bstack1l1l1l1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠥ༊"))
  except Exception as bstack11l1ll1lll_opy_:
    logger.error(bstack1l1l1l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥ་") + str(path) + bstack1l1l1l1_opy_ (u"ࠤࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠦ༌") + str(bstack11l1ll1lll_opy_))