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
import re
bstack1ll111l1ll_opy_ = {
	bstack1l1l1l1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ༭"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡶࠬ༮"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ༯"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡮ࡩࡾ࠭༰"),
  bstack1l1l1l1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧ༱"): bstack1l1l1l1_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ༲"),
  bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭༳"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡢࡻ࠸ࡩࠧ༴"),
  bstack1l1l1l1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ༵࠭"): bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࠪ༶"),
  bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ༷࠭"): bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࠪ༸"),
  bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧ༹ࠪ"): bstack1l1l1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ༺"),
  bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡥࡹ࡬࠭༻"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡥࡧࡥࡹ࡬࠭༼"),
  bstack1l1l1l1_opy_ (u"ࠩࡦࡳࡳࡹ࡯࡭ࡧࡏࡳ࡬ࡹࠧ༽"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡳࡹ࡯࡭ࡧࠪ༾"),
  bstack1l1l1l1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࠩ༿"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࠩཀ"),
  bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲࡒ࡯ࡨࡵࠪཁ"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡱࡲ࡬ࡹࡲࡒ࡯ࡨࡵࠪག"),
  bstack1l1l1l1_opy_ (u"ࠨࡸ࡬ࡨࡪࡵࠧགྷ"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡸ࡬ࡨࡪࡵࠧང"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡑࡵࡧࡴࠩཅ"): bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡪࡲࡥ࡯࡫ࡸࡱࡑࡵࡧࡴࠩཆ"),
  bstack1l1l1l1_opy_ (u"ࠬࡺࡥ࡭ࡧࡰࡩࡹࡸࡹࡍࡱࡪࡷࠬཇ"): bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡺࡥ࡭ࡧࡰࡩࡹࡸࡹࡍࡱࡪࡷࠬ཈"),
  bstack1l1l1l1_opy_ (u"ࠧࡨࡧࡲࡐࡴࡩࡡࡵ࡫ࡲࡲࠬཉ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡨࡧࡲࡐࡴࡩࡡࡵ࡫ࡲࡲࠬཊ"),
  bstack1l1l1l1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡺࡰࡰࡨࠫཋ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷ࡭ࡲ࡫ࡺࡰࡰࡨࠫཌ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ཌྷ"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧཎ"),
  bstack1l1l1l1_opy_ (u"࠭࡭ࡢࡵ࡮ࡇࡴࡳ࡭ࡢࡰࡧࡷࠬཏ"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡭ࡢࡵ࡮ࡇࡴࡳ࡭ࡢࡰࡧࡷࠬཐ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࡰࡪ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ད"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡫ࡧࡰࡪ࡚ࡩ࡮ࡧࡲࡹࡹ࠭དྷ"),
  bstack1l1l1l1_opy_ (u"ࠪࡱࡦࡹ࡫ࡃࡣࡶ࡭ࡨࡇࡵࡵࡪࠪན"): bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡱࡦࡹ࡫ࡃࡣࡶ࡭ࡨࡇࡵࡵࡪࠪཔ"),
  bstack1l1l1l1_opy_ (u"ࠬࡹࡥ࡯ࡦࡎࡩࡾࡹࠧཕ"): bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡹࡥ࡯ࡦࡎࡩࡾࡹࠧབ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳ࡜ࡧࡩࡵࠩབྷ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡷࡷࡳ࡜ࡧࡩࡵࠩམ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡸࡺࡳࠨཙ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡫ࡳࡸࡺࡳࠨཚ"),
  bstack1l1l1l1_opy_ (u"ࠫࡧ࡬ࡣࡢࡥ࡫ࡩࠬཛ"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧ࡬ࡣࡢࡥ࡫ࡩࠬཛྷ"),
  bstack1l1l1l1_opy_ (u"࠭ࡷࡴࡎࡲࡧࡦࡲࡓࡶࡲࡳࡳࡷࡺࠧཝ"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡷࡴࡎࡲࡧࡦࡲࡓࡶࡲࡳࡳࡷࡺࠧཞ"),
  bstack1l1l1l1_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡅࡲࡶࡸࡘࡥࡴࡶࡵ࡭ࡨࡺࡩࡰࡰࡶࠫཟ"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡦ࡬ࡷࡦࡨ࡬ࡦࡅࡲࡶࡸࡘࡥࡴࡶࡵ࡭ࡨࡺࡩࡰࡰࡶࠫའ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧཡ"): bstack1l1l1l1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫར"),
  bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡢ࡮ࡐࡳࡧ࡯࡬ࡦࠩལ"): bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡣ࡯ࡣࡲࡵࡢࡪ࡮ࡨࠫཤ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴࠧཥ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡲࡳ࡭ࡺࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨས"),
  bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡐࡨࡸࡼࡵࡲ࡬ࠩཧ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡹࡸࡺ࡯࡮ࡐࡨࡸࡼࡵࡲ࡬ࠩཨ"),
  bstack1l1l1l1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡕࡸ࡯ࡧ࡫࡯ࡩࠬཀྵ"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡳ࡫ࡴࡸࡱࡵ࡯ࡕࡸ࡯ࡧ࡫࡯ࡩࠬཪ"),
  bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹࡏ࡮ࡴࡧࡦࡹࡷ࡫ࡃࡦࡴࡷࡷࠬཫ"): bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡓࡴ࡮ࡆࡩࡷࡺࡳࠨཬ"),
  bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ཭"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ཮"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ཯"): bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡴࡻࡲࡤࡧࠪ཰"),
  bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸཱࠧ"): bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸིࠧ"),
  bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡶࡸࡓࡧ࡭ࡦཱིࠩ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡩࡱࡶࡸࡓࡧ࡭ࡦུࠩ"),
  bstack1l1l1l1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡕ࡬ࡱཱུࠬ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡨࡲࡦࡨ࡬ࡦࡕ࡬ࡱࠬྲྀ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡯࡭ࡐࡲࡷ࡭ࡴࡴࡳࠨཷ"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡸ࡯࡭ࡐࡲࡷ࡭ࡴࡴࡳࠨླྀ"),
  bstack1l1l1l1_opy_ (u"࠭ࡵࡱ࡮ࡲࡥࡩࡓࡥࡥ࡫ࡤࠫཹ"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡱ࡮ࡲࡥࡩࡓࡥࡥ࡫ࡤེࠫ")
}
bstack11l111l1l1_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠨࡱࡶཻࠫ"),
  bstack1l1l1l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲོࠬ"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲཽࠬ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩཾ"),
  bstack1l1l1l1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩཿ"),
  bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧྀࠪ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴཱྀࠧ"),
]
bstack1l1lll1l1l_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪྂ"): [bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡔࡁࡎࡇࠪྃ"), bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡘࡗࡊࡘ࡟ࡏࡃࡐࡉ྄ࠬ")],
  bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ྅"): bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨ྆"),
  bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ྇"): bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡔࡁࡎࡇࠪྈ"),
  bstack1l1l1l1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ྉ"): bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡕࡓࡏࡋࡃࡕࡡࡑࡅࡒࡋࠧྊ"),
  bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬྋ"): bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ྌ"),
  bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬྍ"): bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡁࡓࡃࡏࡐࡊࡒࡓࡠࡒࡈࡖࡤࡖࡌࡂࡖࡉࡓࡗࡓࠧྎ"),
  bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫྏ"): bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑ࠭ྐ"),
  bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸ࠭ྑ"): bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࡠࡖࡈࡗ࡙࡙ࠧྒ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࠨྒྷ"): [bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡖࡐࡠࡋࡇࠫྔ"), bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡐࡑࠩྕ")],
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩྖ"): bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡔࡆࡎࡣࡑࡕࡇࡍࡇ࡙ࡉࡑ࠭ྗ"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭྘"): bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ྙ"),
  bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨྚ"): bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡒࡆࡘࡋࡒࡗࡃࡅࡍࡑࡏࡔ࡚ࠩྛ")
}
bstack1lll111111_opy_ = {
  bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨྜ"): [bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࡣࡳࡧ࡭ࡦࠩྜྷ"), bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡶࡓࡧ࡭ࡦࠩྞ")],
  bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬྟ"): [bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴࡡ࡮ࡩࡾ࠭ྠ"), bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ྡ")],
  bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨྡྷ"): bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨྣ"),
  bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬྤ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬྥ"),
  bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫྦ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫྦྷ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫྨ"): [bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡵࡶࡰࠨྩ"), bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬྪ")],
  bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫྫ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱ࠭ྫྷ"),
  bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸ࠭ྭ"): bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸ࠭ྮ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࠨྯ"): bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࠨྰ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨྱ"): bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨྲ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬླ"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬྴ")
}
bstack111111ll_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ྵ"): bstack1l1l1l1_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨྶ"),
  bstack1l1l1l1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴࠧྷ"): [bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨྸ"), bstack1l1l1l1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡡࡹࡩࡷࡹࡩࡰࡰࠪྐྵ")],
  bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ྺ"): bstack1l1l1l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧྻ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧྼ"): bstack1l1l1l1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ྽"),
  bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ྾"): [bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ྿"), bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡰࡤࡱࡪ࠭࿀")],
  bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ࿁"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫ࿂"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧ࿃"): bstack1l1l1l1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡡࡰࡳࡧ࡯࡬ࡦࠩ࿄"),
  bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬ࿅"): [bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱ࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࿆࠭"), bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ࿇")],
  bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡶࡴࡊࡰࡶࡩࡨࡻࡲࡦࡅࡨࡶࡹࡹࠧ࿈"): [bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡰࡵࡕࡶࡰࡈ࡫ࡲࡵࡵࠪ࿉"), bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡖࡷࡱࡉࡥࡳࡶࠪ࿊")]
}
bstack1llll1ll1l_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࿋"),
  bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡨࡧࡏࡳࡦࡪࡓࡵࡴࡤࡸࡪ࡭ࡹࠨ࿌"),
  bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬ࿍"),
  bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷ࡛࡮ࡴࡤࡰࡹࡕࡩࡨࡺࠧ࿎"),
  bstack1l1l1l1_opy_ (u"ࠨࡶ࡬ࡱࡪࡵࡵࡵࡵࠪ࿏"),
  bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡷ࡯ࡣࡵࡈ࡬ࡰࡪࡏ࡮ࡵࡧࡵࡥࡨࡺࡡࡣ࡫࡯࡭ࡹࡿࠧ࿐"),
  bstack1l1l1l1_opy_ (u"ࠪࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡖࡲࡰ࡯ࡳࡸࡇ࡫ࡨࡢࡸ࡬ࡳࡷ࠭࿑"),
  bstack1l1l1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ࿒"),
  bstack1l1l1l1_opy_ (u"ࠬࡳ࡯ࡻ࠼ࡩ࡭ࡷ࡫ࡦࡰࡺࡒࡴࡹ࡯࡯࡯ࡵࠪ࿓"),
  bstack1l1l1l1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ࿔"),
  bstack1l1l1l1_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭࿕"),
  bstack1l1l1l1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ࿖"),
]
bstack11llll1ll_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭࿗"),
  bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ࿘"),
  bstack1l1l1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ࿙"),
  bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ࿚"),
  bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ࿛"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩ࿜"),
  bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ࿝"),
  bstack1l1l1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭࿞"),
  bstack1l1l1l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭࿟"),
  bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩ࿠"),
  bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࿡"),
  bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡜ࡡࡳ࡫ࡤࡦࡱ࡫ࡳࠨ࿢"),
  bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡔࡢࡩࠪ࿣"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ࿤"),
  bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫ࿥"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧ࿦"),
  bstack1l1l1l1_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠳ࠪ࿧"),
  bstack1l1l1l1_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠵ࠫ࿨"),
  bstack1l1l1l1_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠷ࠬ࿩"),
  bstack1l1l1l1_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠹࠭࿪"),
  bstack1l1l1l1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠻ࠧ࿫"),
  bstack1l1l1l1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠶ࠨ࿬"),
  bstack1l1l1l1_opy_ (u"ࠪࡇ࡚࡙ࡔࡐࡏࡢࡘࡆࡍ࡟࠸ࠩ࿭"),
  bstack1l1l1l1_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠺ࠪ࿮"),
  bstack1l1l1l1_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠼ࠫ࿯"),
  bstack1l1l1l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ࿰"),
  bstack1l1l1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭࿱"),
  bstack1l1l1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫ࿲"),
  bstack1l1l1l1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫ࿳")
]
bstack11l111lll1_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠪࡹࡵࡲ࡯ࡢࡦࡐࡩࡩ࡯ࡡࠨ࿴"),
  bstack1l1l1l1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭࿵"),
  bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ࿶"),
  bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ࿷"),
  bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡕࡸࡩࡰࡴ࡬ࡸࡾ࠭࿸"),
  bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࿹"),
  bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡕࡣࡪࠫ࿺"),
  bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࿻"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭࿼"),
  bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ࿽"),
  bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ࿾"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭࿿"),
  bstack1l1l1l1_opy_ (u"ࠨࡱࡶࠫက"),
  bstack1l1l1l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬခ"),
  bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡹࡴࡴࠩဂ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ဃ"),
  bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡨ࡫ࡲࡲࠬင"),
  bstack1l1l1l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨစ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡮ࡣࡦ࡬࡮ࡴࡥࠨဆ"),
  bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡷࡴࡲࡵࡵ࡫ࡲࡲࠬဇ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡬ࡨࡱ࡫ࡔࡪ࡯ࡨࡳࡺࡺࠧဈ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧဉ"),
  bstack1l1l1l1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱࠪည"),
  bstack1l1l1l1_opy_ (u"ࠬࡴ࡯ࡑࡣࡪࡩࡑࡵࡡࡥࡖ࡬ࡱࡪࡵࡵࡵࠩဋ"),
  bstack1l1l1l1_opy_ (u"࠭ࡢࡧࡥࡤࡧ࡭࡫ࠧဌ"),
  bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡥࡹ࡬࠭ဍ"),
  bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡔࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬဎ"),
  bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡕࡨࡲࡩࡑࡥࡺࡵࠪဏ"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧတ"),
  bstack1l1l1l1_opy_ (u"ࠫࡳࡵࡐࡪࡲࡨࡰ࡮ࡴࡥࠨထ"),
  bstack1l1l1l1_opy_ (u"ࠬࡩࡨࡦࡥ࡮࡙ࡗࡒࠧဒ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨဓ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡃࡰࡱ࡮࡭ࡪࡹࠧန"),
  bstack1l1l1l1_opy_ (u"ࠨࡥࡤࡴࡹࡻࡲࡦࡅࡵࡥࡸ࡮ࠧပ"),
  bstack1l1l1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ဖ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪဗ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡗࡧࡵࡷ࡮ࡵ࡮ࠨဘ"),
  bstack1l1l1l1_opy_ (u"ࠬࡴ࡯ࡃ࡮ࡤࡲࡰࡖ࡯࡭࡮࡬ࡲ࡬࠭မ"),
  bstack1l1l1l1_opy_ (u"࠭࡭ࡢࡵ࡮ࡗࡪࡴࡤࡌࡧࡼࡷࠬယ"),
  bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡌࡰࡩࡶࠫရ"),
  bstack1l1l1l1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡊࡦࠪလ"),
  bstack1l1l1l1_opy_ (u"ࠩࡧࡩࡩ࡯ࡣࡢࡶࡨࡨࡉ࡫ࡶࡪࡥࡨࠫဝ"),
  bstack1l1l1l1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡓࡥࡷࡧ࡭ࡴࠩသ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵ࡮࡯࡯ࡧࡑࡹࡲࡨࡥࡳࠩဟ"),
  bstack1l1l1l1_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡒ࡯ࡨࡵࠪဠ"),
  bstack1l1l1l1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡓࡵࡺࡩࡰࡰࡶࠫအ"),
  bstack1l1l1l1_opy_ (u"ࠧࡤࡱࡱࡷࡴࡲࡥࡍࡱࡪࡷࠬဢ"),
  bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨဣ"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭ဤ"),
  bstack1l1l1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡅ࡭ࡴࡳࡥࡵࡴ࡬ࡧࠬဥ"),
  bstack1l1l1l1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱ࡙࠶ࠬဦ"),
  bstack1l1l1l1_opy_ (u"ࠬࡳࡩࡥࡕࡨࡷࡸ࡯࡯࡯ࡋࡱࡷࡹࡧ࡬࡭ࡃࡳࡴࡸ࠭ဧ"),
  bstack1l1l1l1_opy_ (u"࠭ࡥࡴࡲࡵࡩࡸࡹ࡯ࡔࡧࡵࡺࡪࡸࠧဨ"),
  bstack1l1l1l1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭ဩ"),
  bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡆࡨࡵ࠭ဪ"),
  bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩါ"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡾࡴࡣࡕ࡫ࡰࡩ࡜࡯ࡴࡩࡐࡗࡔࠬာ"),
  bstack1l1l1l1_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩိ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡭ࡰࡴࡎࡲࡧࡦࡺࡩࡰࡰࠪီ"),
  bstack1l1l1l1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡐࡳࡱࡩ࡭ࡱ࡫ࠧု"),
  bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧူ"),
  bstack1l1l1l1_opy_ (u"ࠨࡨࡲࡶࡨ࡫ࡃࡩࡣࡱ࡫ࡪࡐࡡࡳࠩေ"),
  bstack1l1l1l1_opy_ (u"ࠩࡻࡱࡸࡐࡡࡳࠩဲ"),
  bstack1l1l1l1_opy_ (u"ࠪࡼࡲࡾࡊࡢࡴࠪဳ"),
  bstack1l1l1l1_opy_ (u"ࠫࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪဴ"),
  bstack1l1l1l1_opy_ (u"ࠬࡳࡡࡴ࡭ࡅࡥࡸ࡯ࡣࡂࡷࡷ࡬ࠬဵ"),
  bstack1l1l1l1_opy_ (u"࠭ࡷࡴࡎࡲࡧࡦࡲࡓࡶࡲࡳࡳࡷࡺࠧံ"),
  bstack1l1l1l1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵ့ࠪ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴ࡛࡫ࡲࡴ࡫ࡲࡲࠬး"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡰࡵࡋࡱࡷࡪࡩࡵࡳࡧࡆࡩࡷࡺࡳࠨ္"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡹࡩࡨࡰࡄࡴࡵ်࠭"),
  bstack1l1l1l1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡩ࡮ࡣࡷ࡭ࡴࡴࡳࠨျ"),
  bstack1l1l1l1_opy_ (u"ࠬࡩࡡ࡯ࡣࡵࡽࠬြ"),
  bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧွ"),
  bstack1l1l1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧှ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡫ࡨࠫဿ"),
  bstack1l1l1l1_opy_ (u"ࠩࡨࡨ࡬࡫ࠧ၀"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪ၁"),
  bstack1l1l1l1_opy_ (u"ࠫࡶࡻࡥࡶࡧࠪ၂"),
  bstack1l1l1l1_opy_ (u"ࠬ࡯࡮ࡵࡧࡵࡲࡦࡲࠧ၃"),
  bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲࡖࡸࡴࡸࡥࡄࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠧ၄"),
  bstack1l1l1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡃࡢ࡯ࡨࡶࡦࡏ࡭ࡢࡩࡨࡍࡳࡰࡥࡤࡶ࡬ࡳࡳ࠭၅"),
  bstack1l1l1l1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸࡋࡸࡤ࡮ࡸࡨࡪࡎ࡯ࡴࡶࡶࠫ၆"),
  bstack1l1l1l1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࡉ࡯ࡥ࡯ࡹࡩ࡫ࡈࡰࡵࡷࡷࠬ၇"),
  bstack1l1l1l1_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡄࡴࡵ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧ၈"),
  bstack1l1l1l1_opy_ (u"ࠫࡷ࡫ࡳࡦࡴࡹࡩࡉ࡫ࡶࡪࡥࡨࠫ၉"),
  bstack1l1l1l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ၊"),
  bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡰࡧࡏࡪࡿࡳࠨ။"),
  bstack1l1l1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡐࡢࡵࡶࡧࡴࡪࡥࠨ၌"),
  bstack1l1l1l1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡊࡱࡶࡈࡪࡼࡩࡤࡧࡖࡩࡹࡺࡩ࡯ࡩࡶࠫ၍"),
  bstack1l1l1l1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡃࡸࡨ࡮ࡵࡉ࡯࡬ࡨࡧࡹ࡯࡯࡯ࠩ၎"),
  bstack1l1l1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡄࡴࡵࡲࡥࡑࡣࡼࠫ၏"),
  bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬၐ"),
  bstack1l1l1l1_opy_ (u"ࠬࡽࡤࡪࡱࡖࡩࡷࡼࡩࡤࡧࠪၑ"),
  bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨၒ"),
  bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡄࡴࡲࡷࡸ࡙ࡩࡵࡧࡗࡶࡦࡩ࡫ࡪࡰࡪࠫၓ"),
  bstack1l1l1l1_opy_ (u"ࠨࡪ࡬࡫࡭ࡉ࡯࡯ࡶࡵࡥࡸࡺࠧၔ"),
  bstack1l1l1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡒࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࡸ࠭ၕ"),
  bstack1l1l1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡖ࡭ࡲ࠭ၖ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡯࡭ࡐࡲࡷ࡭ࡴࡴࡳࠨၗ"),
  bstack1l1l1l1_opy_ (u"ࠬࡸࡥ࡮ࡱࡹࡩࡎࡕࡓࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࡑࡵࡣࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠪၘ"),
  bstack1l1l1l1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨၙ"),
  bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩၚ"),
  bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪၛ"),
  bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨၜ"),
  bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬၝ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡧࡦࡎࡲࡥࡩ࡙ࡴࡳࡣࡷࡩ࡬ࡿࠧၞ"),
  bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫၟ"),
  bstack1l1l1l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡳࡺࡺࡳࠨၠ"),
  bstack1l1l1l1_opy_ (u"ࠧࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡓࡶࡴࡳࡰࡵࡄࡨ࡬ࡦࡼࡩࡰࡴࠪၡ")
]
bstack1l1lll1ll1_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠨࡸࠪၢ"): bstack1l1l1l1_opy_ (u"ࠩࡹࠫၣ"),
  bstack1l1l1l1_opy_ (u"ࠪࡪࠬၤ"): bstack1l1l1l1_opy_ (u"ࠫ࡫࠭ၥ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡬࡯ࡳࡥࡨࠫၦ"): bstack1l1l1l1_opy_ (u"࠭ࡦࡰࡴࡦࡩࠬၧ"),
  bstack1l1l1l1_opy_ (u"ࠧࡰࡰ࡯ࡽࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ၨ"): bstack1l1l1l1_opy_ (u"ࠨࡱࡱࡰࡾࡇࡵࡵࡱࡰࡥࡹ࡫ࠧၩ"),
  bstack1l1l1l1_opy_ (u"ࠩࡩࡳࡷࡩࡥ࡭ࡱࡦࡥࡱ࠭ၪ"): bstack1l1l1l1_opy_ (u"ࠪࡪࡴࡸࡣࡦ࡮ࡲࡧࡦࡲࠧၫ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻ࡫ࡳࡸࡺࠧၬ"): bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡌࡴࡹࡴࠨၭ"),
  bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡵࡵࡲࡵࠩၮ"): bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪၯ"),
  bstack1l1l1l1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫၰ"): bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬၱ"),
  bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡲࡤࡷࡸ࠭ၲ"): bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧၳ"),
  bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡪࡲࡷࡹ࠭ၴ"): bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡋࡳࡸࡺࠧၵ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡴࡸࡴࠨၶ"): bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡵࡲࡵࠩၷ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡻࡳࡦࡴࠪၸ"): bstack1l1l1l1_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬၹ"),
  bstack1l1l1l1_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡷࡶࡩࡷ࠭ၺ"): bstack1l1l1l1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡘࡷࡪࡸࠧၻ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡳࡥࡸࡹࠧၼ"): bstack1l1l1l1_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩၽ"),
  bstack1l1l1l1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡶࡡࡴࡵࠪၾ"): bstack1l1l1l1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡐࡢࡵࡶࠫၿ"),
  bstack1l1l1l1_opy_ (u"ࠪࡦ࡮ࡴࡡࡳࡻࡳࡥࡹ࡮ࠧႀ"): bstack1l1l1l1_opy_ (u"ࠫࡧ࡯࡮ࡢࡴࡼࡴࡦࡺࡨࠨႁ"),
  bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡤࡨ࡬ࡰࡪ࠭ႂ"): bstack1l1l1l1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩႃ"),
  bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡦ࠱࡫࡯࡬ࡦࠩႄ"): bstack1l1l1l1_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫႅ"),
  bstack1l1l1l1_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬႆ"): bstack1l1l1l1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭ႇ"),
  bstack1l1l1l1_opy_ (u"ࠫࡱࡵࡧࡧ࡫࡯ࡩࠬႈ"): bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡨࡨ࡬ࡰࡪ࠭ႉ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨႊ"): bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩႋ"),
}
bstack11l1111l11_opy_ = bstack1l1l1l1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡪ࡭ࡹ࡮ࡵࡣ࠰ࡦࡳࡲ࠵ࡰࡦࡴࡦࡽ࠴ࡩ࡬ࡪ࠱ࡵࡩࡱ࡫ࡡࡴࡧࡶ࠳ࡱࡧࡴࡦࡵࡷ࠳ࡩࡵࡷ࡯࡮ࡲࡥࡩࠨႌ")
bstack11l111l111_opy_ = bstack1l1l1l1_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠱࡫ࡩࡦࡲࡴࡩࡥ࡫ࡩࡨࡱႍࠢ")
bstack111l1l1l_opy_ = bstack1l1l1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳࡭ࡻࡢ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡼࡪ࠯ࡩࡷࡥࠫႎ")
bstack1l11l1llll_opy_ = bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱ࠼࠲࠳࡭ࡻࡢ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠧႏ")
bstack1llllll1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡨࡶࡤ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵࡮ࡦࡺࡷࡣ࡭ࡻࡢࡴࠩ႐")
bstack11l11l1111_opy_ = {
  bstack1l1l1l1_opy_ (u"࠭ࡣࡳ࡫ࡷ࡭ࡨࡧ࡬ࠨ႑"): 50,
  bstack1l1l1l1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭႒"): 40,
  bstack1l1l1l1_opy_ (u"ࠨࡹࡤࡶࡳ࡯࡮ࡨࠩ႓"): 30,
  bstack1l1l1l1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ႔"): 20,
  bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩ႕"): 10
}
bstack1l1l1l1l1l_opy_ = bstack11l11l1111_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡮ࡴࡦࡰࠩ႖")]
bstack1llllll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠲ࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࠫ႗")
bstack111l1l11_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲ࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࠫ႘")
bstack1111lll1_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴࠭႙")
bstack1l111l1l_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧႚ")
bstack1lll1lll1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶࠣࡥࡳࡪࠠࡱࡻࡷࡩࡸࡺ࠭ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡳࡥࡨࡱࡡࡨࡧࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷࠤࡵࡿࡴࡦࡵࡷ࠱ࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡦࠧႛ")
bstack11l1111l1l_opy_ = [bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫႜ"), bstack1l1l1l1_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫႝ")]
bstack11l111l11l_opy_ = [bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨ႞"), bstack1l1l1l1_opy_ (u"࡙࠭ࡐࡗࡕࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠨ႟")]
bstack11l11lll_opy_ = re.compile(bstack1l1l1l1_opy_ (u"ࠧ࡟࡝࡟ࡠࡼ࠳࡝ࠬ࠼࠱࠮ࠩ࠭Ⴀ"))
bstack1l1lllllll_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡓࡧ࡭ࡦࠩႡ"),
  bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫႢ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧႣ"),
  bstack1l1l1l1_opy_ (u"ࠫࡳ࡫ࡷࡄࡱࡰࡱࡦࡴࡤࡕ࡫ࡰࡩࡴࡻࡴࠨႤ"),
  bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱࠩႥ"),
  bstack1l1l1l1_opy_ (u"࠭ࡵࡥ࡫ࡧࠫႦ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࠩႧ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡥࠨႨ"),
  bstack1l1l1l1_opy_ (u"ࠩࡲࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧႩ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡺࡺ࡯ࡘࡧࡥࡺ࡮࡫ࡷࠨႪ"),
  bstack1l1l1l1_opy_ (u"ࠫࡳࡵࡒࡦࡵࡨࡸࠬႫ"), bstack1l1l1l1_opy_ (u"ࠬ࡬ࡵ࡭࡮ࡕࡩࡸ࡫ࡴࠨႬ"),
  bstack1l1l1l1_opy_ (u"࠭ࡣ࡭ࡧࡤࡶࡘࡿࡳࡵࡧࡰࡊ࡮ࡲࡥࡴࠩႭ"),
  bstack1l1l1l1_opy_ (u"ࠧࡦࡸࡨࡲࡹ࡚ࡩ࡮࡫ࡱ࡫ࡸ࠭Ⴎ"),
  bstack1l1l1l1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡑࡧࡵࡪࡴࡸ࡭ࡢࡰࡦࡩࡑࡵࡧࡨ࡫ࡱ࡫ࠬႯ"),
  bstack1l1l1l1_opy_ (u"ࠩࡲࡸ࡭࡫ࡲࡂࡲࡳࡷࠬႰ"),
  bstack1l1l1l1_opy_ (u"ࠪࡴࡷ࡯࡮ࡵࡒࡤ࡫ࡪ࡙࡯ࡶࡴࡦࡩࡔࡴࡆࡪࡰࡧࡊࡦ࡯࡬ࡶࡴࡨࠫႱ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࡂࡥࡷ࡭ࡻ࡯ࡴࡺࠩႲ"), bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱࡒࡤࡧࡰࡧࡧࡦࠩႳ"), bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲ࡚ࡥ࡮ࡺࡁࡤࡶ࡬ࡺ࡮ࡺࡹࠨႴ"), bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳ࡛ࡦ࡯ࡴࡑࡣࡦ࡯ࡦ࡭ࡥࠨႵ"), bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴ࡜ࡧࡩࡵࡆࡸࡶࡦࡺࡩࡰࡰࠪႶ"),
  bstack1l1l1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡔࡨࡥࡩࡿࡔࡪ࡯ࡨࡳࡺࡺࠧႷ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡖࡨࡷࡹࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠧႸ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡈࡵࡶࡦࡴࡤ࡫ࡪ࠭Ⴙ"), bstack1l1l1l1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡉ࡯ࡷࡧࡵࡥ࡬࡫ࡅ࡯ࡦࡌࡲࡹ࡫࡮ࡵࠩႺ"),
  bstack1l1l1l1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡄࡦࡸ࡬ࡧࡪࡘࡥࡢࡦࡼࡘ࡮ࡳࡥࡰࡷࡷࠫႻ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡦࡥࡔࡴࡸࡴࠨႼ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡆࡨࡺ࡮ࡩࡥࡔࡱࡦ࡯ࡪࡺࠧႽ"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡌࡲࡸࡺࡡ࡭࡮ࡗ࡭ࡲ࡫࡯ࡶࡶࠪႾ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡍࡳࡹࡴࡢ࡮࡯ࡔࡦࡺࡨࠨႿ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡼࡤࠨჀ"), bstack1l1l1l1_opy_ (u"ࠬࡧࡶࡥࡎࡤࡹࡳࡩࡨࡕ࡫ࡰࡩࡴࡻࡴࠨჁ"), bstack1l1l1l1_opy_ (u"࠭ࡡࡷࡦࡕࡩࡦࡪࡹࡕ࡫ࡰࡩࡴࡻࡴࠨჂ"), bstack1l1l1l1_opy_ (u"ࠧࡢࡸࡧࡅࡷ࡭ࡳࠨჃ"),
  bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡐ࡫ࡹࡴࡶࡲࡶࡪ࠭Ⴤ"), bstack1l1l1l1_opy_ (u"ࠩ࡮ࡩࡾࡹࡴࡰࡴࡨࡔࡦࡺࡨࠨჅ"), bstack1l1l1l1_opy_ (u"ࠪ࡯ࡪࡿࡳࡵࡱࡵࡩࡕࡧࡳࡴࡹࡲࡶࡩ࠭჆"),
  bstack1l1l1l1_opy_ (u"ࠫࡰ࡫ࡹࡂ࡮࡬ࡥࡸ࠭Ⴧ"), bstack1l1l1l1_opy_ (u"ࠬࡱࡥࡺࡒࡤࡷࡸࡽ࡯ࡳࡦࠪ჈"),
  bstack1l1l1l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡊࡾࡥࡤࡷࡷࡥࡧࡲࡥࠨ჉"), bstack1l1l1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡇࡲࡨࡵࠪ჊"), bstack1l1l1l1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡅࡹࡧࡦࡹࡹࡧࡢ࡭ࡧࡇ࡭ࡷ࠭჋"), bstack1l1l1l1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡄࡪࡵࡳࡲ࡫ࡍࡢࡲࡳ࡭ࡳ࡭ࡆࡪ࡮ࡨࠫ჌"), bstack1l1l1l1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡗࡶࡩࡘࡿࡳࡵࡧࡰࡉࡽ࡫ࡣࡶࡶࡤࡦࡱ࡫ࠧჍ"),
  bstack1l1l1l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡓࡳࡷࡺࠧ჎"), bstack1l1l1l1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡔࡴࡸࡴࡴࠩ჏"),
  bstack1l1l1l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡉ࡯ࡳࡢࡤ࡯ࡩࡇࡻࡩ࡭ࡦࡆ࡬ࡪࡩ࡫ࠨა"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳ࡜࡫ࡢࡷ࡫ࡨࡻ࡙࡯࡭ࡦࡱࡸࡸࠬბ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡸࡪࡴࡴࡂࡥࡷ࡭ࡴࡴࠧგ"), bstack1l1l1l1_opy_ (u"ࠩ࡬ࡲࡹ࡫࡮ࡵࡅࡤࡸࡪ࡭࡯ࡳࡻࠪდ"), bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳࡺࡥ࡯ࡶࡉࡰࡦ࡭ࡳࠨე"), bstack1l1l1l1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡥࡱࡏ࡮ࡵࡧࡱࡸࡆࡸࡧࡶ࡯ࡨࡲࡹࡹࠧვ"),
  bstack1l1l1l1_opy_ (u"ࠬࡪ࡯࡯ࡶࡖࡸࡴࡶࡁࡱࡲࡒࡲࡗ࡫ࡳࡦࡶࠪზ"),
  bstack1l1l1l1_opy_ (u"࠭ࡵ࡯࡫ࡦࡳࡩ࡫ࡋࡦࡻࡥࡳࡦࡸࡤࠨთ"), bstack1l1l1l1_opy_ (u"ࠧࡳࡧࡶࡩࡹࡑࡥࡺࡤࡲࡥࡷࡪࠧი"),
  bstack1l1l1l1_opy_ (u"ࠨࡰࡲࡗ࡮࡭࡮ࠨკ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡬࡫ࡳࡵࡲࡦࡗࡱ࡭ࡲࡶ࡯ࡳࡶࡤࡲࡹ࡜ࡩࡦࡹࡶࠫლ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡳࡪࡲࡰ࡫ࡧ࡛ࡦࡺࡣࡩࡧࡵࡷࠬმ"),
  bstack1l1l1l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫნ"),
  bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡤࡴࡨࡥࡹ࡫ࡃࡩࡴࡲࡱࡪࡊࡲࡪࡸࡨࡶࡘ࡫ࡳࡴ࡫ࡲࡲࡸ࠭ო"),
  bstack1l1l1l1_opy_ (u"࠭࡮ࡢࡶ࡬ࡺࡪ࡝ࡥࡣࡕࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠬპ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡔࡥࡵࡩࡪࡴࡳࡩࡱࡷࡔࡦࡺࡨࠨჟ"),
  bstack1l1l1l1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡕࡳࡩࡪࡪࠧრ"),
  bstack1l1l1l1_opy_ (u"ࠩࡪࡴࡸࡋ࡮ࡢࡤ࡯ࡩࡩ࠭ს"),
  bstack1l1l1l1_opy_ (u"ࠪ࡭ࡸࡎࡥࡢࡦ࡯ࡩࡸࡹࠧტ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡪࡢࡆࡺࡨࡧ࡙࡯࡭ࡦࡱࡸࡸࠬუ"),
  bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡩࡘࡩࡲࡪࡲࡷࠫფ"),
  bstack1l1l1l1_opy_ (u"࠭ࡳ࡬࡫ࡳࡈࡪࡼࡩࡤࡧࡌࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠪქ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳࡌࡸࡡ࡯ࡶࡓࡩࡷࡳࡩࡴࡵ࡬ࡳࡳࡹࠧღ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡐࡤࡸࡺࡸࡡ࡭ࡑࡵ࡭ࡪࡴࡴࡢࡶ࡬ࡳࡳ࠭ყ"),
  bstack1l1l1l1_opy_ (u"ࠩࡶࡽࡸࡺࡥ࡮ࡒࡲࡶࡹ࠭შ"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡳ࡯ࡵࡧࡄࡨࡧࡎ࡯ࡴࡶࠪჩ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡗࡱࡰࡴࡩ࡫ࠨც"), bstack1l1l1l1_opy_ (u"ࠬࡻ࡮࡭ࡱࡦ࡯࡙ࡿࡰࡦࠩძ"), bstack1l1l1l1_opy_ (u"࠭ࡵ࡯࡮ࡲࡧࡰࡑࡥࡺࠩწ"),
  bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳࡑࡧࡵ࡯ࡥ࡫ࠫჭ"),
  bstack1l1l1l1_opy_ (u"ࠨࡵ࡮࡭ࡵࡒ࡯ࡨࡥࡤࡸࡈࡧࡰࡵࡷࡵࡩࠬხ"),
  bstack1l1l1l1_opy_ (u"ࠩࡸࡲ࡮ࡴࡳࡵࡣ࡯ࡰࡔࡺࡨࡦࡴࡓࡥࡨࡱࡡࡨࡧࡶࠫჯ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨ࡛࡮ࡴࡤࡰࡹࡄࡲ࡮ࡳࡡࡵ࡫ࡲࡲࠬჰ"),
  bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡗࡳࡴࡲࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨჱ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡫࡮ࡧࡱࡵࡧࡪࡇࡰࡱࡋࡱࡷࡹࡧ࡬࡭ࠩჲ"),
  bstack1l1l1l1_opy_ (u"࠭ࡥ࡯ࡵࡸࡶࡪ࡝ࡥࡣࡸ࡬ࡩࡼࡹࡈࡢࡸࡨࡔࡦ࡭ࡥࡴࠩჳ"), bstack1l1l1l1_opy_ (u"ࠧࡸࡧࡥࡺ࡮࡫ࡷࡅࡧࡹࡸࡴࡵ࡬ࡴࡒࡲࡶࡹ࠭ჴ"), bstack1l1l1l1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡘࡧࡥࡺ࡮࡫ࡷࡅࡧࡷࡥ࡮ࡲࡳࡄࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠫჵ"),
  bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡲࡵࡴࡦࡃࡳࡴࡸࡉࡡࡤࡪࡨࡐ࡮ࡳࡩࡵࠩჶ"),
  bstack1l1l1l1_opy_ (u"ࠪࡧࡦࡲࡥ࡯ࡦࡤࡶࡋࡵࡲ࡮ࡣࡷࠫჷ"),
  bstack1l1l1l1_opy_ (u"ࠫࡧࡻ࡮ࡥ࡮ࡨࡍࡩ࠭ჸ"),
  bstack1l1l1l1_opy_ (u"ࠬࡲࡡࡶࡰࡦ࡬࡙࡯࡭ࡦࡱࡸࡸࠬჹ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࡔࡧࡵࡺ࡮ࡩࡥࡴࡇࡱࡥࡧࡲࡥࡥࠩჺ"), bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࡕࡨࡶࡻ࡯ࡣࡦࡵࡄࡹࡹ࡮࡯ࡳ࡫ࡽࡩࡩ࠭჻"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡇࡣࡤࡧࡳࡸࡆࡲࡥࡳࡶࡶࠫჼ"), bstack1l1l1l1_opy_ (u"ࠩࡤࡹࡹࡵࡄࡪࡵࡰ࡭ࡸࡹࡁ࡭ࡧࡵࡸࡸ࠭ჽ"),
  bstack1l1l1l1_opy_ (u"ࠪࡲࡦࡺࡩࡷࡧࡌࡲࡸࡺࡲࡶ࡯ࡨࡲࡹࡹࡌࡪࡤࠪჾ"),
  bstack1l1l1l1_opy_ (u"ࠫࡳࡧࡴࡪࡸࡨ࡛ࡪࡨࡔࡢࡲࠪჿ"),
  bstack1l1l1l1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࡎࡴࡩࡵ࡫ࡤࡰ࡚ࡸ࡬ࠨᄀ"), bstack1l1l1l1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡇ࡬࡭ࡱࡺࡔࡴࡶࡵࡱࡵࠪᄁ"), bstack1l1l1l1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡉࡨࡰࡲࡶࡪࡌࡲࡢࡷࡧ࡛ࡦࡸ࡮ࡪࡰࡪࠫᄂ"), bstack1l1l1l1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡐࡲࡨࡲࡑ࡯࡮࡬ࡵࡌࡲࡇࡧࡣ࡬ࡩࡵࡳࡺࡴࡤࠨᄃ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡮ࡩࡪࡶࡋࡦࡻࡆ࡬ࡦ࡯࡮ࡴࠩᄄ"),
  bstack1l1l1l1_opy_ (u"ࠪࡰࡴࡩࡡ࡭࡫ࡽࡥࡧࡲࡥࡔࡶࡵ࡭ࡳ࡭ࡳࡅ࡫ࡵࠫᄅ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡤࡧࡶࡷࡆࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᄆ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡯࡮ࡵࡧࡵࡏࡪࡿࡄࡦ࡮ࡤࡽࠬᄇ"),
  bstack1l1l1l1_opy_ (u"࠭ࡳࡩࡱࡺࡍࡔ࡙ࡌࡰࡩࠪᄈ"),
  bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡱࡨࡐ࡫ࡹࡔࡶࡵࡥࡹ࡫ࡧࡺࠩᄉ"),
  bstack1l1l1l1_opy_ (u"ࠨࡹࡨࡦࡰ࡯ࡴࡓࡧࡶࡴࡴࡴࡳࡦࡖ࡬ࡱࡪࡵࡵࡵࠩᄊ"), bstack1l1l1l1_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࡝ࡡࡪࡶࡗ࡭ࡲ࡫࡯ࡶࡶࠪᄋ"),
  bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡳ࡯ࡵࡧࡇࡩࡧࡻࡧࡑࡴࡲࡼࡾ࠭ᄌ"),
  bstack1l1l1l1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡅࡸࡿ࡮ࡤࡇࡻࡩࡨࡻࡴࡦࡈࡵࡳࡲࡎࡴࡵࡲࡶࠫᄍ"),
  bstack1l1l1l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡏࡳ࡬ࡉࡡࡱࡶࡸࡶࡪ࠭ᄎ"),
  bstack1l1l1l1_opy_ (u"࠭ࡷࡦࡤ࡮࡭ࡹࡊࡥࡣࡷࡪࡔࡷࡵࡸࡺࡒࡲࡶࡹ࠭ᄏ"),
  bstack1l1l1l1_opy_ (u"ࠧࡧࡷ࡯ࡰࡈࡵ࡮ࡵࡧࡻࡸࡑ࡯ࡳࡵࠩᄐ"),
  bstack1l1l1l1_opy_ (u"ࠨࡹࡤ࡭ࡹࡌ࡯ࡳࡃࡳࡴࡘࡩࡲࡪࡲࡷࠫᄑ"),
  bstack1l1l1l1_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࡆࡳࡳࡴࡥࡤࡶࡕࡩࡹࡸࡩࡦࡵࠪᄒ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶࡎࡢ࡯ࡨࠫᄓ"),
  bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡗࡘࡒࡃࡦࡴࡷࠫᄔ"),
  bstack1l1l1l1_opy_ (u"ࠬࡺࡡࡱ࡙࡬ࡸ࡭࡙ࡨࡰࡴࡷࡔࡷ࡫ࡳࡴࡆࡸࡶࡦࡺࡩࡰࡰࠪᄕ"),
  bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡣ࡯ࡩࡋࡧࡣࡵࡱࡵࠫᄖ"),
  bstack1l1l1l1_opy_ (u"ࠧࡸࡦࡤࡐࡴࡩࡡ࡭ࡒࡲࡶࡹ࠭ᄗ"),
  bstack1l1l1l1_opy_ (u"ࠨࡵ࡫ࡳࡼ࡞ࡣࡰࡦࡨࡐࡴ࡭ࠧᄘ"),
  bstack1l1l1l1_opy_ (u"ࠩ࡬ࡳࡸࡏ࡮ࡴࡶࡤࡰࡱࡖࡡࡶࡵࡨࠫᄙ"),
  bstack1l1l1l1_opy_ (u"ࠪࡼࡨࡵࡤࡦࡅࡲࡲ࡫࡯ࡧࡇ࡫࡯ࡩࠬᄚ"),
  bstack1l1l1l1_opy_ (u"ࠫࡰ࡫ࡹࡤࡪࡤ࡭ࡳࡖࡡࡴࡵࡺࡳࡷࡪࠧᄛ"),
  bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡒࡵࡩࡧࡻࡩ࡭ࡶ࡚ࡈࡆ࠭ᄜ"),
  bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡧࡹࡩࡳࡺࡗࡅࡃࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠧᄝ"),
  bstack1l1l1l1_opy_ (u"ࠧࡸࡧࡥࡈࡷ࡯ࡶࡦࡴࡄ࡫ࡪࡴࡴࡖࡴ࡯ࠫᄞ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡭ࡨࡽࡨ࡮ࡡࡪࡰࡓࡥࡹ࡮ࠧᄟ"),
  bstack1l1l1l1_opy_ (u"ࠩࡸࡷࡪࡔࡥࡸ࡙ࡇࡅࠬᄠ"),
  bstack1l1l1l1_opy_ (u"ࠪࡻࡩࡧࡌࡢࡷࡱࡧ࡭࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᄡ"), bstack1l1l1l1_opy_ (u"ࠫࡼࡪࡡࡄࡱࡱࡲࡪࡩࡴࡪࡱࡱࡘ࡮ࡳࡥࡰࡷࡷࠫᄢ"),
  bstack1l1l1l1_opy_ (u"ࠬࡾࡣࡰࡦࡨࡓࡷ࡭ࡉࡥࠩᄣ"), bstack1l1l1l1_opy_ (u"࠭ࡸࡤࡱࡧࡩࡘ࡯ࡧ࡯࡫ࡱ࡫ࡎࡪࠧᄤ"),
  bstack1l1l1l1_opy_ (u"ࠧࡶࡲࡧࡥࡹ࡫ࡤࡘࡆࡄࡆࡺࡴࡤ࡭ࡧࡌࡨࠬᄥ"),
  bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡷࡪࡺࡏ࡯ࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡷࡺࡏ࡯࡮ࡼࠫᄦ"),
  bstack1l1l1l1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡗ࡭ࡲ࡫࡯ࡶࡶࡶࠫᄧ"),
  bstack1l1l1l1_opy_ (u"ࠪࡻࡩࡧࡓࡵࡣࡵࡸࡺࡶࡒࡦࡶࡵ࡭ࡪࡹࠧᄨ"), bstack1l1l1l1_opy_ (u"ࠫࡼࡪࡡࡔࡶࡤࡶࡹࡻࡰࡓࡧࡷࡶࡾࡏ࡮ࡵࡧࡵࡺࡦࡲࠧᄩ"),
  bstack1l1l1l1_opy_ (u"ࠬࡩ࡯࡯ࡰࡨࡧࡹࡎࡡࡳࡦࡺࡥࡷ࡫ࡋࡦࡻࡥࡳࡦࡸࡤࠨᄪ"),
  bstack1l1l1l1_opy_ (u"࠭࡭ࡢࡺࡗࡽࡵ࡯࡮ࡨࡈࡵࡩࡶࡻࡥ࡯ࡥࡼࠫᄫ"),
  bstack1l1l1l1_opy_ (u"ࠧࡴ࡫ࡰࡴࡱ࡫ࡉࡴࡘ࡬ࡷ࡮ࡨ࡬ࡦࡅ࡫ࡩࡨࡱࠧᄬ"),
  bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡈࡧࡲࡵࡪࡤ࡫ࡪ࡙ࡳ࡭ࠩᄭ"),
  bstack1l1l1l1_opy_ (u"ࠩࡶ࡬ࡴࡻ࡬ࡥࡗࡶࡩࡘ࡯࡮ࡨ࡮ࡨࡸࡴࡴࡔࡦࡵࡷࡑࡦࡴࡡࡨࡧࡵࠫᄮ"),
  bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡋ࡚ࡈࡕ࠭ᄯ"),
  bstack1l1l1l1_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡗࡳࡺࡩࡨࡊࡦࡈࡲࡷࡵ࡬࡭ࠩᄰ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡯ࡧ࡯ࡱࡵࡩࡍ࡯ࡤࡥࡧࡱࡅࡵ࡯ࡐࡰ࡮࡬ࡧࡾࡋࡲࡳࡱࡵࠫᄱ"),
  bstack1l1l1l1_opy_ (u"࠭࡭ࡰࡥ࡮ࡐࡴࡩࡡࡵ࡫ࡲࡲࡆࡶࡰࠨᄲ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡪࡧࡦࡺࡆࡰࡴࡰࡥࡹ࠭ᄳ"), bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲ࡫ࡨࡧࡴࡇ࡫࡯ࡸࡪࡸࡓࡱࡧࡦࡷࠬᄴ"),
  bstack1l1l1l1_opy_ (u"ࠩࡤࡰࡱࡵࡷࡅࡧ࡯ࡥࡾࡇࡤࡣࠩᄵ"),
  bstack1l1l1l1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡍࡩࡒ࡯ࡤࡣࡷࡳࡷࡇࡵࡵࡱࡦࡳࡲࡶ࡬ࡦࡶ࡬ࡳࡳ࠭ᄶ")
]
bstack1l11l1l11_opy_ = bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠯ࡦࡰࡴࡻࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡹࡵࡲ࡯ࡢࡦࠪᄷ")
bstack1ll1l1l11_opy_ = [bstack1l1l1l1_opy_ (u"ࠬ࠴ࡡࡱ࡭ࠪᄸ"), bstack1l1l1l1_opy_ (u"࠭࠮ࡢࡣࡥࠫᄹ"), bstack1l1l1l1_opy_ (u"ࠧ࠯࡫ࡳࡥࠬᄺ")]
bstack1lll111ll1_opy_ = [bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࠫᄻ"), bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡹ࡮ࠧᄼ"), bstack1l1l1l1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭ᄽ"), bstack1l1l1l1_opy_ (u"ࠫࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦࠪᄾ")]
bstack11111111l_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᄿ"): bstack1l1l1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᅀ"),
  bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨᅁ"): bstack1l1l1l1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭ᅂ"),
  bstack1l1l1l1_opy_ (u"ࠩࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᅃ"): bstack1l1l1l1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫᅄ"),
  bstack1l1l1l1_opy_ (u"ࠫ࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᅅ"): bstack1l1l1l1_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫᅆ"),
  bstack1l1l1l1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡕࡰࡵ࡫ࡲࡲࡸ࠭ᅇ"): bstack1l1l1l1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯࠮ࡰࡲࡷ࡭ࡴࡴࡳࠨᅈ")
}
bstack1l1l11ll11_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᅉ"),
  bstack1l1l1l1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧᅊ"),
  bstack1l1l1l1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫᅋ"),
  bstack1l1l1l1_opy_ (u"ࠫࡸ࡫࠺ࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᅌ"),
  bstack1l1l1l1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᅍ"),
]
bstack11l1111ll_opy_ = bstack11llll1ll_opy_ + bstack11l111lll1_opy_ + bstack1l1lllllll_opy_
bstack1l11l1l11l_opy_ = [
  bstack1l1l1l1_opy_ (u"࠭࡞࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶࠧࠫᅎ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡟ࡤࡶ࠱ࡱࡵࡣࡢ࡮࠱ࡧࡴࡳࠤࠨᅏ"),
  bstack1l1l1l1_opy_ (u"ࠨࡠ࠴࠶࠼࠴ࠧᅐ"),
  bstack1l1l1l1_opy_ (u"ࠩࡡ࠵࠵࠴ࠧᅑ"),
  bstack1l1l1l1_opy_ (u"ࠪࡢ࠶࠽࠲࠯࠳࡞࠺࠲࠿࡝࠯ࠩᅒ"),
  bstack1l1l1l1_opy_ (u"ࠫࡣ࠷࠷࠳࠰࠵࡟࠵࠳࠹࡞࠰ࠪᅓ"),
  bstack1l1l1l1_opy_ (u"ࠬࡤ࠱࠸࠴࠱࠷ࡠ࠶࠭࠲࡟࠱ࠫᅔ"),
  bstack1l1l1l1_opy_ (u"࠭࡞࠲࠻࠵࠲࠶࠼࠸࠯ࠩᅕ")
]
bstack11l111l1ll_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨᅖ")
bstack1l1ll11111_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡵࡧ࡯࠴ࡼ࠱࠰ࡧࡹࡩࡳࡺࠧᅗ")
bstack1ll111l111_opy_ = [ bstack1l1l1l1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᅘ") ]
bstack11ll1ll1l_opy_ = [ bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩᅙ") ]
bstack1l111111l_opy_ = [ bstack1l1l1l1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᅚ") ]
bstack1111l1lll_opy_ = bstack1l1l1l1_opy_ (u"࡙ࠬࡄࡌࡕࡨࡸࡺࡶࠧᅛ")
bstack1l1ll11l1l_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡓࡅࡍࡗࡩࡸࡺࡁࡵࡶࡨࡱࡵࡺࡥࡥࠩᅜ")
bstack1llll1l11l_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡔࡆࡎࡘࡪࡹࡴࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠫᅝ")
bstack1l11ll11ll_opy_ = bstack1l1l1l1_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࠧᅞ")
bstack1l1llll1l1_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠩࡈࡖࡗࡥࡆࡂࡋࡏࡉࡉ࠭ᅟ"),
  bstack1l1l1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪᅠ"),
  bstack1l1l1l1_opy_ (u"ࠫࡊࡘࡒࡠࡄࡏࡓࡈࡑࡅࡅࡡࡅ࡝ࡤࡉࡌࡊࡇࡑࡘࠬᅡ"),
  bstack1l1l1l1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡉ࡙࡝ࡏࡓࡍࡢࡇࡍࡇࡎࡈࡇࡇࠫᅢ"),
  bstack1l1l1l1_opy_ (u"࠭ࡅࡓࡔࡢࡗࡔࡉࡋࡆࡖࡢࡒࡔ࡚࡟ࡄࡑࡑࡒࡊࡉࡔࡆࡆࠪᅣ"),
  bstack1l1l1l1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡅࡏࡓࡘࡋࡄࠨᅤ"),
  bstack1l1l1l1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡕࡉࡘࡋࡔࠨᅥ"),
  bstack1l1l1l1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡖࡊࡌࡕࡔࡇࡇࠫᅦ"),
  bstack1l1l1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡆࡈࡏࡓࡖࡈࡈࠬᅧ"),
  bstack1l1l1l1_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬᅨ"),
  bstack1l1l1l1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡏࡑࡗࡣࡗࡋࡓࡐࡎ࡙ࡉࡉ࠭ᅩ"),
  bstack1l1l1l1_opy_ (u"࠭ࡅࡓࡔࡢࡅࡉࡊࡒࡆࡕࡖࡣࡎࡔࡖࡂࡎࡌࡈࠬᅪ"),
  bstack1l1l1l1_opy_ (u"ࠧࡆࡔࡕࡣࡆࡊࡄࡓࡇࡖࡗࡤ࡛ࡎࡓࡇࡄࡇࡍࡇࡂࡍࡇࠪᅫ"),
  bstack1l1l1l1_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡕࡏࡐࡈࡐࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩᅬ"),
  bstack1l1l1l1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡘࡎࡓࡅࡅࡡࡒ࡙࡙࠭ᅭ"),
  bstack1l1l1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡘࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪᅮ"),
  bstack1l1l1l1_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐ࡙࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡍࡕࡓࡕࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧᅯ"),
  bstack1l1l1l1_opy_ (u"ࠬࡋࡒࡓࡡࡓࡖࡔ࡞࡙ࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬᅰ"),
  bstack1l1l1l1_opy_ (u"࠭ࡅࡓࡔࡢࡒࡆࡓࡅࡠࡐࡒࡘࡤࡘࡅࡔࡑࡏ࡚ࡊࡊࠧᅱ"),
  bstack1l1l1l1_opy_ (u"ࠧࡆࡔࡕࡣࡓࡇࡍࡆࡡࡕࡉࡘࡕࡌࡖࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ᅲ"),
  bstack1l1l1l1_opy_ (u"ࠨࡇࡕࡖࡤࡓࡁࡏࡆࡄࡘࡔࡘ࡙ࡠࡒࡕࡓ࡝࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧᅳ"),
]
bstack1lllll1l11_opy_ = bstack1l1l1l1_opy_ (u"ࠩ࠱࠳ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡥࡷࡺࡩࡧࡣࡦࡸࡸ࠵ࠧᅴ")
bstack1l11111ll_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠪࢂࠬᅵ")), bstack1l1l1l1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᅶ"), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡴࡶࡤࡧࡰ࠳ࡣࡰࡰࡩ࡭࡬࠴ࡪࡴࡱࡱࠫᅷ"))
bstack11l1llll11_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡥࡵ࡯ࠧᅸ")
bstack11l11l11l1_opy_ = [ bstack1l1l1l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧᅹ"), bstack1l1l1l1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧᅺ"), bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨᅻ") ]
bstack1l1llll111_opy_ = [ bstack1l1l1l1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪᅼ"), bstack1l1l1l1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᅽ"), bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫᅾ") ]
bstack11llll1ll1_opy_ = {
  bstack1l1l1l1_opy_ (u"࠭ࡐࡂࡕࡖࠫᅿ"): bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᆀ"),
  bstack1l1l1l1_opy_ (u"ࠨࡈࡄࡍࡑ࠭ᆁ"): bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᆂ"),
  bstack1l1l1l1_opy_ (u"ࠪࡗࡐࡏࡐࠨᆃ"): bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬᆄ")
}
bstack1ll1ll1l1l_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡥࡵࠤᆅ"),
  bstack1l1l1l1_opy_ (u"ࠨࡧࡰࡄࡤࡧࡰࠨᆆ"),
  bstack1l1l1l1_opy_ (u"ࠢࡨࡱࡉࡳࡷࡽࡡࡳࡦࠥᆇ"),
  bstack1l1l1l1_opy_ (u"ࠣࡴࡨࡪࡷ࡫ࡳࡩࠤᆈ"),
  bstack1l1l1l1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴࠣᆉ"),
  bstack1l1l1l1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᆊ"),
  bstack1l1l1l1_opy_ (u"ࠦࡸࡻࡢ࡮࡫ࡷࡉࡱ࡫࡭ࡦࡰࡷࠦᆋ"),
  bstack1l1l1l1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡇ࡯ࡩࡲ࡫࡮ࡵࠤᆌ"),
  bstack1l1l1l1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡄࡧࡹ࡯ࡶࡦࡇ࡯ࡩࡲ࡫࡮ࡵࠤᆍ"),
  bstack1l1l1l1_opy_ (u"ࠢࡤ࡮ࡨࡥࡷࡋ࡬ࡦ࡯ࡨࡲࡹࠨᆎ"),
  bstack1l1l1l1_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࡴࠤᆏ"),
  bstack1l1l1l1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࡖࡧࡷ࡯ࡰࡵࠤᆐ"),
  bstack1l1l1l1_opy_ (u"ࠥࡩࡽ࡫ࡣࡶࡶࡨࡅࡸࡿ࡮ࡤࡕࡦࡶ࡮ࡶࡴࠣᆑ"),
  bstack1l1l1l1_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥᆒ"),
  bstack1l1l1l1_opy_ (u"ࠧࡷࡵࡪࡶࠥᆓ"),
  bstack1l1l1l1_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳࡔࡰࡷࡦ࡬ࡆࡩࡴࡪࡱࡱࠦᆔ"),
  bstack1l1l1l1_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡎࡷ࡯ࡸ࡮࡚࡯ࡶࡥ࡫ࠦᆕ"),
  bstack1l1l1l1_opy_ (u"ࠣࡵ࡫ࡥࡰ࡫ࠢᆖ"),
  bstack1l1l1l1_opy_ (u"ࠤࡦࡰࡴࡹࡥࡂࡲࡳࠦᆗ")
]
bstack11l1111lll_opy_ = [
  bstack1l1l1l1_opy_ (u"ࠥࡧࡱ࡯ࡣ࡬ࠤᆘ"),
  bstack1l1l1l1_opy_ (u"ࠦࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠣᆙ"),
  bstack1l1l1l1_opy_ (u"ࠧࡧࡵࡵࡱࠥᆚ"),
  bstack1l1l1l1_opy_ (u"ࠨ࡭ࡢࡰࡸࡥࡱࠨᆛ"),
  bstack1l1l1l1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤᆜ")
]
bstack1l1l1l1l11_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢᆝ"): [bstack1l1l1l1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴࠣᆞ")],
  bstack1l1l1l1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᆟ"): [bstack1l1l1l1_opy_ (u"ࠦࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠣᆠ")],
  bstack1l1l1l1_opy_ (u"ࠧࡧࡵࡵࡱࠥᆡ"): [bstack1l1l1l1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡈࡰࡪࡳࡥ࡯ࡶࠥᆢ"), bstack1l1l1l1_opy_ (u"ࠢࡴࡧࡱࡨࡐ࡫ࡹࡴࡖࡲࡅࡨࡺࡩࡷࡧࡈࡰࡪࡳࡥ࡯ࡶࠥᆣ"), bstack1l1l1l1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᆤ"), bstack1l1l1l1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࡆ࡮ࡨࡱࡪࡴࡴࠣᆥ")],
  bstack1l1l1l1_opy_ (u"ࠥࡱࡦࡴࡵࡢ࡮ࠥᆦ"): [bstack1l1l1l1_opy_ (u"ࠦࡲࡧ࡮ࡶࡣ࡯ࠦᆧ")],
  bstack1l1l1l1_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢᆨ"): [bstack1l1l1l1_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣᆩ")],
}
bstack11l111ll11_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨᆪ"): bstack1l1l1l1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢᆫ"),
  bstack1l1l1l1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨᆬ"): bstack1l1l1l1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᆭ"),
  bstack1l1l1l1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡆ࡮ࡨࡱࡪࡴࡴࠣᆮ"): bstack1l1l1l1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࠢᆯ"),
  bstack1l1l1l1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡄࡧࡹ࡯ࡶࡦࡇ࡯ࡩࡲ࡫࡮ࡵࠤᆰ"): bstack1l1l1l1_opy_ (u"ࠢࡴࡧࡱࡨࡐ࡫ࡹࡴࠤᆱ"),
  bstack1l1l1l1_opy_ (u"ࠣࡶࡨࡷࡹࡩࡡࡴࡧࠥᆲ"): bstack1l1l1l1_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦᆳ")
}
bstack11lllll11l_opy_ = {
  bstack1l1l1l1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧᆴ"): bstack1l1l1l1_opy_ (u"ࠫࡘࡻࡩࡵࡧࠣࡗࡪࡺࡵࡱࠩᆵ"),
  bstack1l1l1l1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨᆶ"): bstack1l1l1l1_opy_ (u"࠭ࡓࡶ࡫ࡷࡩ࡚ࠥࡥࡢࡴࡧࡳࡼࡴࠧᆷ"),
  bstack1l1l1l1_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬᆸ"): bstack1l1l1l1_opy_ (u"ࠨࡖࡨࡷࡹࠦࡓࡦࡶࡸࡴࠬᆹ"),
  bstack1l1l1l1_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ᆺ"): bstack1l1l1l1_opy_ (u"ࠪࡘࡪࡹࡴࠡࡖࡨࡥࡷࡪ࡯ࡸࡰࠪᆻ")
}
bstack11l111llll_opy_ = 65536
bstack11l1111ll1_opy_ = bstack1l1l1l1_opy_ (u"ࠫ࠳࠴࠮࡜ࡖࡕ࡙ࡓࡉࡁࡕࡇࡇࡡࠬᆼ")
bstack11l11l111l_opy_ = [
      bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᆽ"), bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᆾ"), bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᆿ"), bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬᇀ"), bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠫᇁ"),
      bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᇂ"), bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧᇃ"), bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᇄ"), bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡥࡸࡹࠧᇅ"),
      bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࡒࡦࡳࡥࠨᇆ"), bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᇇ"), bstack1l1l1l1_opy_ (u"ࠩࡤࡹࡹ࡮ࡔࡰ࡭ࡨࡲࠬᇈ")
    ]
bstack11l111ll1l_opy_= {
  bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧᇉ"): bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨᇊ"),
  bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩᇋ"): bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪᇌ"),
  bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ᇍ"): bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬᇎ"),
  bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᇏ"): bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᇐ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᇑ"): bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᇒ"),
  bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᇓ"): bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᇔ"),
  bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫᇕ"): bstack1l1l1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬᇖ"),
  bstack1l1l1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧᇗ"): bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨᇘ"),
  bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᇙ"): bstack1l1l1l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩᇚ"),
  bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬᇛ"): bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸ࠭ᇜ"),
  bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ᇝ"): bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᇞ"),
  bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᇟ"): bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᇠ"),
  bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡜ࡡࡳ࡫ࡤࡦࡱ࡫ࡳࠨᇡ"): bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠩᇢ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᇣ"): bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᇤ"),
  bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᇥ"): bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᇦ"),
  bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩᇧ"): bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡴࡸࡲ࡙࡫ࡳࡵࡵࠪᇨ"),
  bstack1l1l1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᇩ"): bstack1l1l1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧᇪ"),
  bstack1l1l1l1_opy_ (u"ࠩࡳࡩࡷࡩࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᇫ"): bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᇬ"),
  bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡆࡥࡵࡺࡵࡳࡧࡐࡳࡩ࡫ࠧᇭ"): bstack1l1l1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨᇮ"),
  bstack1l1l1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨᇯ"): bstack1l1l1l1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩᇰ"),
  bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᇱ"): bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᇲ"),
  bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᇳ"): bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᇴ"),
  bstack1l1l1l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩᇵ"): bstack1l1l1l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᇶ"),
  bstack1l1l1l1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࡓࡵࡺࡩࡰࡰࡶࠫᇷ"): bstack1l1l1l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬᇸ"),
  bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠩᇹ"): bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡕࡨࡸࡹ࡯࡮ࡨࡵࠪᇺ")
}