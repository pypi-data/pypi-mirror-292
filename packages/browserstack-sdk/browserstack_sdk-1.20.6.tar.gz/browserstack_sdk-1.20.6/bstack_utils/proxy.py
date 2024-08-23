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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111111ll1l_opy_
bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
def bstack1llll11l11l_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1llll11l111_opy_(bstack1llll111ll1_opy_, bstack1llll111l1l_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1llll111ll1_opy_):
        with open(bstack1llll111ll1_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1llll11l11l_opy_(bstack1llll111ll1_opy_):
        pac = get_pac(url=bstack1llll111ll1_opy_)
    else:
        raise Exception(bstack1l1l1l1_opy_ (u"ࠨࡒࡤࡧࠥ࡬ࡩ࡭ࡧࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠾ࠥࢁࡽࠨᓉ").format(bstack1llll111ll1_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack1l1l1l1_opy_ (u"ࠤ࠻࠲࠽࠴࠸࠯࠺ࠥᓊ"), 80))
        bstack1llll1111ll_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1llll1111ll_opy_ = bstack1l1l1l1_opy_ (u"ࠪ࠴࠳࠶࠮࠱࠰࠳ࠫᓋ")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1llll111l1l_opy_, bstack1llll1111ll_opy_)
    return proxy_url
def bstack1lll11l1_opy_(config):
    return bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧᓌ") in config or bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩᓍ") in config
def bstack111l1ll1_opy_(config):
    if not bstack1lll11l1_opy_(config):
        return
    if config.get(bstack1l1l1l1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᓎ")):
        return config.get(bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᓏ"))
    if config.get(bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬᓐ")):
        return config.get(bstack1l1l1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ᓑ"))
def bstack11l111lll_opy_(config, bstack1llll111l1l_opy_):
    proxy = bstack111l1ll1_opy_(config)
    proxies = {}
    if config.get(bstack1l1l1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭ᓒ")) or config.get(bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨᓓ")):
        if proxy.endswith(bstack1l1l1l1_opy_ (u"ࠬ࠴ࡰࡢࡥࠪᓔ")):
            proxies = bstack1l1l1lll1_opy_(proxy, bstack1llll111l1l_opy_)
        else:
            proxies = {
                bstack1l1l1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᓕ"): proxy
            }
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧᓖ"), proxies)
    return proxies
def bstack1l1l1lll1_opy_(bstack1llll111ll1_opy_, bstack1llll111l1l_opy_):
    proxies = {}
    global bstack1llll111lll_opy_
    if bstack1l1l1l1_opy_ (u"ࠨࡒࡄࡇࡤࡖࡒࡐ࡚࡜ࠫᓗ") in globals():
        return bstack1llll111lll_opy_
    try:
        proxy = bstack1llll11l111_opy_(bstack1llll111ll1_opy_, bstack1llll111l1l_opy_)
        if bstack1l1l1l1_opy_ (u"ࠤࡇࡍࡗࡋࡃࡕࠤᓘ") in proxy:
            proxies = {}
        elif bstack1l1l1l1_opy_ (u"ࠥࡌ࡙࡚ࡐࠣᓙ") in proxy or bstack1l1l1l1_opy_ (u"ࠦࡍ࡚ࡔࡑࡕࠥᓚ") in proxy or bstack1l1l1l1_opy_ (u"࡙ࠧࡏࡄࡍࡖࠦᓛ") in proxy:
            bstack1llll111l11_opy_ = proxy.split(bstack1l1l1l1_opy_ (u"ࠨࠠࠣᓜ"))
            if bstack1l1l1l1_opy_ (u"ࠢ࠻࠱࠲ࠦᓝ") in bstack1l1l1l1_opy_ (u"ࠣࠤᓞ").join(bstack1llll111l11_opy_[1:]):
                proxies = {
                    bstack1l1l1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨᓟ"): bstack1l1l1l1_opy_ (u"ࠥࠦᓠ").join(bstack1llll111l11_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᓡ"): str(bstack1llll111l11_opy_[0]).lower() + bstack1l1l1l1_opy_ (u"ࠧࡀ࠯࠰ࠤᓢ") + bstack1l1l1l1_opy_ (u"ࠨࠢᓣ").join(bstack1llll111l11_opy_[1:])
                }
        elif bstack1l1l1l1_opy_ (u"ࠢࡑࡔࡒ࡜࡞ࠨᓤ") in proxy:
            bstack1llll111l11_opy_ = proxy.split(bstack1l1l1l1_opy_ (u"ࠣࠢࠥᓥ"))
            if bstack1l1l1l1_opy_ (u"ࠤ࠽࠳࠴ࠨᓦ") in bstack1l1l1l1_opy_ (u"ࠥࠦᓧ").join(bstack1llll111l11_opy_[1:]):
                proxies = {
                    bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᓨ"): bstack1l1l1l1_opy_ (u"ࠧࠨᓩ").join(bstack1llll111l11_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᓪ"): bstack1l1l1l1_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣᓫ") + bstack1l1l1l1_opy_ (u"ࠣࠤᓬ").join(bstack1llll111l11_opy_[1:])
                }
        else:
            proxies = {
                bstack1l1l1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨᓭ"): proxy
            }
    except Exception as e:
        print(bstack1l1l1l1_opy_ (u"ࠥࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠢᓮ"), bstack111111ll1l_opy_.format(bstack1llll111ll1_opy_, str(e)))
    bstack1llll111lll_opy_ = proxies
    return proxies