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
import re
from bstack_utils.bstack11l1ll1l1_opy_ import bstack1lll1lllll1_opy_
def bstack1lll1lll1l1_opy_(fixture_name):
    if fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᓯ")):
        return bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ᓰ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᓱ")):
        return bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳࡭ࡰࡦࡸࡰࡪ࠭ᓲ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᓳ")):
        return bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ᓴ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᓵ")):
        return bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭ᓶ")
def bstack1llll111111_opy_(fixture_name):
    return bool(re.match(bstack1l1l1l1_opy_ (u"ࠬࡤ࡟ࡹࡷࡱ࡭ࡹࡥࠨࡴࡧࡷࡹࡵࢂࡴࡦࡣࡵࡨࡴࡽ࡮ࠪࡡࠫࡪࡺࡴࡣࡵ࡫ࡲࡲࢁࡳ࡯ࡥࡷ࡯ࡩ࠮ࡥࡦࡪࡺࡷࡹࡷ࡫࡟࠯ࠬࠪᓷ"), fixture_name))
def bstack1lll1llllll_opy_(fixture_name):
    return bool(re.match(bstack1l1l1l1_opy_ (u"࠭࡞ࡠࡺࡸࡲ࡮ࡺ࡟ࠩࡵࡨࡸࡺࡶࡼࡵࡧࡤࡶࡩࡵࡷ࡯ࠫࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧᓸ"), fixture_name))
def bstack1lll1lll111_opy_(fixture_name):
    return bool(re.match(bstack1l1l1l1_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧᓹ"), fixture_name))
def bstack1lll1llll1l_opy_(fixture_name):
    if fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᓺ")):
        return bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪᓻ"), bstack1l1l1l1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨᓼ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᓽ")):
        return bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱ࡲࡵࡤࡶ࡮ࡨࠫᓾ"), bstack1l1l1l1_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪᓿ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᔀ")):
        return bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰ࠰ࡪࡺࡴࡣࡵ࡫ࡲࡲࠬᔁ"), bstack1l1l1l1_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ᔂ")
    elif fixture_name.startswith(bstack1l1l1l1_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᔃ")):
        return bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭ᔄ"), bstack1l1l1l1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨᔅ")
    return None, None
def bstack1lll1ll1ll1_opy_(hook_name):
    if hook_name in [bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬᔆ"), bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩᔇ")]:
        return hook_name.capitalize()
    return hook_name
def bstack1lll1llll11_opy_(hook_name):
    if hook_name in [bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩᔈ"), bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨᔉ")]:
        return bstack1l1l1l1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨᔊ")
    elif hook_name in [bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠪᔋ"), bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪᔌ")]:
        return bstack1l1l1l1_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪᔍ")
    elif hook_name in [bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࠫᔎ"), bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪᔏ")]:
        return bstack1l1l1l1_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ᔐ")
    elif hook_name in [bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬᔑ"), bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠬᔒ")]:
        return bstack1l1l1l1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨᔓ")
    return hook_name
def bstack1llll11111l_opy_(node, scenario):
    if hasattr(node, bstack1l1l1l1_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨᔔ")):
        parts = node.nodeid.rsplit(bstack1l1l1l1_opy_ (u"ࠢ࡜ࠤᔕ"))
        params = parts[-1]
        return bstack1l1l1l1_opy_ (u"ࠣࡽࢀࠤࡠࢁࡽࠣᔖ").format(scenario.name, params)
    return scenario.name
def bstack1lll1lll11l_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack1l1l1l1_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᔗ")):
            examples = list(node.callspec.params[bstack1l1l1l1_opy_ (u"ࠪࡣࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡧࡻࡥࡲࡶ࡬ࡦࠩᔘ")].values())
        return examples
    except:
        return []
def bstack1lll1ll1lll_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1lll1lll1ll_opy_(report):
    try:
        status = bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᔙ")
        if report.passed or (report.failed and hasattr(report, bstack1l1l1l1_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢᔚ"))):
            status = bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᔛ")
        elif report.skipped:
            status = bstack1l1l1l1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨᔜ")
        bstack1lll1lllll1_opy_(status)
    except:
        pass
def bstack1ll1l1lll_opy_(status):
    try:
        bstack1lll1ll1l1l_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᔝ")
        if status == bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᔞ"):
            bstack1lll1ll1l1l_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᔟ")
        elif status == bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬᔠ"):
            bstack1lll1ll1l1l_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ᔡ")
        bstack1lll1lllll1_opy_(bstack1lll1ll1l1l_opy_)
    except:
        pass
def bstack1llll1111l1_opy_(item=None, report=None, summary=None, extra=None):
    return