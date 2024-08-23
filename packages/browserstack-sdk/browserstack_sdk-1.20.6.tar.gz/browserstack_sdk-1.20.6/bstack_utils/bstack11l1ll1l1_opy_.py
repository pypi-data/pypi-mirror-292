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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.helper import bstack1111lll111_opy_, bstack1l111lll11_opy_, bstack1l111l1ll1_opy_, bstack1ll1ll1l_opy_, \
    bstack111lll1lll_opy_
def bstack1llll1ll1_opy_(bstack1lll1l111l1_opy_):
    for driver in bstack1lll1l111l1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1l1l1lll11_opy_(driver, status, reason=bstack1l1l1l1_opy_ (u"ࠨࠩᔤ")):
    bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
    if bstack1l111l111_opy_.bstack11ll1l11l1_opy_():
        return
    bstack1l11l1ll11_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬᔥ"), bstack1l1l1l1_opy_ (u"ࠪࠫᔦ"), status, reason, bstack1l1l1l1_opy_ (u"ࠫࠬᔧ"), bstack1l1l1l1_opy_ (u"ࠬ࠭ᔨ"))
    driver.execute_script(bstack1l11l1ll11_opy_)
def bstack11llll11l_opy_(page, status, reason=bstack1l1l1l1_opy_ (u"࠭ࠧᔩ")):
    try:
        if page is None:
            return
        bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
        if bstack1l111l111_opy_.bstack11ll1l11l1_opy_():
            return
        bstack1l11l1ll11_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪᔪ"), bstack1l1l1l1_opy_ (u"ࠨࠩᔫ"), status, reason, bstack1l1l1l1_opy_ (u"ࠩࠪᔬ"), bstack1l1l1l1_opy_ (u"ࠪࠫᔭ"))
        page.evaluate(bstack1l1l1l1_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧᔮ"), bstack1l11l1ll11_opy_)
    except Exception as e:
        print(bstack1l1l1l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡼࡿࠥᔯ"), e)
def bstack1lll1ll11l_opy_(type, name, status, reason, bstack11ll1l1l1_opy_, bstack11111ll11_opy_):
    bstack1l1ll111ll_opy_ = {
        bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ᔰ"): type,
        bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᔱ"): {}
    }
    if type == bstack1l1l1l1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪᔲ"):
        bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬᔳ")][bstack1l1l1l1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᔴ")] = bstack11ll1l1l1_opy_
        bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᔵ")][bstack1l1l1l1_opy_ (u"ࠬࡪࡡࡵࡣࠪᔶ")] = json.dumps(str(bstack11111ll11_opy_))
    if type == bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᔷ"):
        bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᔸ")][bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᔹ")] = name
    if type == bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬᔺ"):
        bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ᔻ")][bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᔼ")] = status
        if status == bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᔽ") and str(reason) != bstack1l1l1l1_opy_ (u"ࠨࠢᔾ"):
            bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᔿ")][bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨᕀ")] = json.dumps(str(reason))
    bstack1l111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧᕁ").format(json.dumps(bstack1l1ll111ll_opy_))
    return bstack1l111l1l1_opy_
def bstack1l1l11l11_opy_(url, config, logger, bstack1l1lllll11_opy_=False):
    hostname = bstack1l111lll11_opy_(url)
    is_private = bstack1ll1ll1l_opy_(hostname)
    try:
        if is_private or bstack1l1lllll11_opy_:
            file_path = bstack1111lll111_opy_(bstack1l1l1l1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᕂ"), bstack1l1l1l1_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪᕃ"), logger)
            if os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪᕄ")) and eval(
                    os.environ.get(bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࡣࡓࡕࡔࡠࡕࡈࡘࡤࡋࡒࡓࡑࡕࠫᕅ"))):
                return
            if (bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫᕆ") in config and not config[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬᕇ")]):
                os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧᕈ")] = str(True)
                bstack1lll1l11l11_opy_ = {bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬᕉ"): hostname}
                bstack111lll1lll_opy_(bstack1l1l1l1_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪᕊ"), bstack1l1l1l1_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪᕋ"), bstack1lll1l11l11_opy_, logger)
    except Exception as e:
        pass
def bstack1l111llll_opy_(caps, bstack1lll1l1111l_opy_):
    if bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᕌ") in caps:
        caps[bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᕍ")][bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧᕎ")] = True
        if bstack1lll1l1111l_opy_:
            caps[bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᕏ")][bstack1l1l1l1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᕐ")] = bstack1lll1l1111l_opy_
    else:
        caps[bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩᕑ")] = True
        if bstack1lll1l1111l_opy_:
            caps[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᕒ")] = bstack1lll1l1111l_opy_
def bstack1lll1lllll1_opy_(bstack11ll1lll11_opy_):
    bstack1lll1l111ll_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡗࡹࡧࡴࡶࡵࠪᕓ"), bstack1l1l1l1_opy_ (u"ࠧࠨᕔ"))
    if bstack1lll1l111ll_opy_ == bstack1l1l1l1_opy_ (u"ࠨࠩᕕ") or bstack1lll1l111ll_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪᕖ"):
        threading.current_thread().testStatus = bstack11ll1lll11_opy_
    else:
        if bstack11ll1lll11_opy_ == bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᕗ"):
            threading.current_thread().testStatus = bstack11ll1lll11_opy_