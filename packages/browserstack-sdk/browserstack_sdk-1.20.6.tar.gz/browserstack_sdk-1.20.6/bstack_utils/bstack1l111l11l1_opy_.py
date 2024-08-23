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
from uuid import uuid4
from bstack_utils.helper import bstack1ll1l11lll_opy_, bstack111ll1llll_opy_
from bstack_utils.bstack11l1l1ll1_opy_ import bstack1lll1lll11l_opy_
class bstack11lllll1l1_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, bstack11lll1llll_opy_=None, framework=None, tags=[], scope=[], bstack1lll11llll1_opy_=None, bstack1lll11l11l1_opy_=True, bstack1lll11lll11_opy_=None, bstack1ll111l1l1_opy_=None, result=None, duration=None, bstack11lll1ll1l_opy_=None, meta={}):
        self.bstack11lll1ll1l_opy_ = bstack11lll1ll1l_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1lll11l11l1_opy_:
            self.uuid = uuid4().__str__()
        self.bstack11lll1llll_opy_ = bstack11lll1llll_opy_
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1lll11llll1_opy_ = bstack1lll11llll1_opy_
        self.bstack1lll11lll11_opy_ = bstack1lll11lll11_opy_
        self.bstack1ll111l1l1_opy_ = bstack1ll111l1l1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
    def bstack1l1111l111_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack1lll111lll1_opy_(self):
        bstack1lll11ll11l_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧᕘ"): bstack1lll11ll11l_opy_,
            bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧᕙ"): bstack1lll11ll11l_opy_,
            bstack1l1l1l1_opy_ (u"࠭ࡶࡤࡡࡩ࡭ࡱ࡫ࡰࡢࡶ࡫ࠫᕚ"): bstack1lll11ll11l_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1l1l1l1_opy_ (u"ࠢࡖࡰࡨࡼࡵ࡫ࡣࡵࡧࡧࠤࡦࡸࡧࡶ࡯ࡨࡲࡹࡀࠠࠣᕛ") + key)
            setattr(self, key, val)
    def bstack1lll11l1ll1_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᕜ"): self.name,
            bstack1l1l1l1_opy_ (u"ࠩࡥࡳࡩࡿࠧᕝ"): {
                bstack1l1l1l1_opy_ (u"ࠪࡰࡦࡴࡧࠨᕞ"): bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫᕟ"),
                bstack1l1l1l1_opy_ (u"ࠬࡩ࡯ࡥࡧࠪᕠ"): self.code
            },
            bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭ᕡ"): self.scope,
            bstack1l1l1l1_opy_ (u"ࠧࡵࡣࡪࡷࠬᕢ"): self.tags,
            bstack1l1l1l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫᕣ"): self.framework,
            bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᕤ"): self.bstack11lll1llll_opy_
        }
    def bstack1lll11ll1ll_opy_(self):
        return {
         bstack1l1l1l1_opy_ (u"ࠪࡱࡪࡺࡡࠨᕥ"): self.meta
        }
    def bstack1lll11lllll_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡖࡪࡸࡵ࡯ࡒࡤࡶࡦࡳࠧᕦ"): {
                bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡣࡳࡧ࡭ࡦࠩᕧ"): self.bstack1lll11llll1_opy_
            }
        }
    def bstack1lll11l111l_opy_(self, bstack1lll11lll1l_opy_, details):
        step = next(filter(lambda st: st[bstack1l1l1l1_opy_ (u"࠭ࡩࡥࠩᕨ")] == bstack1lll11lll1l_opy_, self.meta[bstack1l1l1l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᕩ")]), None)
        step.update(details)
    def bstack1lll1l11111_opy_(self, bstack1lll11lll1l_opy_):
        step = next(filter(lambda st: st[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࠫᕪ")] == bstack1lll11lll1l_opy_, self.meta[bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᕫ")]), None)
        step.update({
            bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᕬ"): bstack1ll1l11lll_opy_()
        })
    def bstack1l111l111l_opy_(self, bstack1lll11lll1l_opy_, result, duration=None):
        bstack1lll11lll11_opy_ = bstack1ll1l11lll_opy_()
        if bstack1lll11lll1l_opy_ is not None and self.meta.get(bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᕭ")):
            step = next(filter(lambda st: st[bstack1l1l1l1_opy_ (u"ࠬ࡯ࡤࠨᕮ")] == bstack1lll11lll1l_opy_, self.meta[bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᕯ")]), None)
            step.update({
                bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᕰ"): bstack1lll11lll11_opy_,
                bstack1l1l1l1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪᕱ"): duration if duration else bstack111ll1llll_opy_(step[bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᕲ")], bstack1lll11lll11_opy_),
                bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪᕳ"): result.result,
                bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬᕴ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1lll11l1l1l_opy_):
        if self.meta.get(bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᕵ")):
            self.meta[bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᕶ")].append(bstack1lll11l1l1l_opy_)
        else:
            self.meta[bstack1l1l1l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᕷ")] = [ bstack1lll11l1l1l_opy_ ]
    def bstack1lll11ll1l1_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᕸ"): self.bstack1l1111l111_opy_(),
            **self.bstack1lll11l1ll1_opy_(),
            **self.bstack1lll111lll1_opy_(),
            **self.bstack1lll11ll1ll_opy_()
        }
    def bstack1lll11ll111_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧᕹ"): self.bstack1lll11lll11_opy_,
            bstack1l1l1l1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫᕺ"): self.duration,
            bstack1l1l1l1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫᕻ"): self.result.result
        }
        if data[bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᕼ")] == bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᕽ"):
            data[bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭ᕾ")] = self.result.bstack11ll1111l1_opy_()
            data[bstack1l1l1l1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᕿ")] = [{bstack1l1l1l1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᖀ"): self.result.bstack11l1111111_opy_()}]
        return data
    def bstack1lll11l1111_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᖁ"): self.bstack1l1111l111_opy_(),
            **self.bstack1lll11l1ll1_opy_(),
            **self.bstack1lll111lll1_opy_(),
            **self.bstack1lll11ll111_opy_(),
            **self.bstack1lll11ll1ll_opy_()
        }
    def bstack11ll1l1l11_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1l1l1l1_opy_ (u"ࠫࡘࡺࡡࡳࡶࡨࡨࠬᖂ") in event:
            return self.bstack1lll11ll1l1_opy_()
        elif bstack1l1l1l1_opy_ (u"ࠬࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧᖃ") in event:
            return self.bstack1lll11l1111_opy_()
    def bstack1l11111ll1_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1lll11lll11_opy_ = time if time else bstack1ll1l11lll_opy_()
        self.duration = duration if duration else bstack111ll1llll_opy_(self.bstack11lll1llll_opy_, self.bstack1lll11lll11_opy_)
        if result:
            self.result = result
class bstack11llll1lll_opy_(bstack11lllll1l1_opy_):
    def __init__(self, hooks=[], bstack11llll111l_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack11llll111l_opy_ = bstack11llll111l_opy_
        super().__init__(*args, **kwargs, bstack1ll111l1l1_opy_=bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࠫᖄ"))
    @classmethod
    def bstack1lll111llll_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1l1l1l1_opy_ (u"ࠧࡪࡦࠪᖅ"): id(step),
                bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡼࡹ࠭ᖆ"): step.name,
                bstack1l1l1l1_opy_ (u"ࠩ࡮ࡩࡾࡽ࡯ࡳࡦࠪᖇ"): step.keyword,
            })
        return bstack11llll1lll_opy_(
            **kwargs,
            meta={
                bstack1l1l1l1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࠫᖈ"): {
                    bstack1l1l1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᖉ"): feature.name,
                    bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡵࡪࠪᖊ"): feature.filename,
                    bstack1l1l1l1_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫᖋ"): feature.description
                },
                bstack1l1l1l1_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩᖌ"): {
                    bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᖍ"): scenario.name
                },
                bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᖎ"): steps,
                bstack1l1l1l1_opy_ (u"ࠪࡩࡽࡧ࡭ࡱ࡮ࡨࡷࠬᖏ"): bstack1lll1lll11l_opy_(test)
            }
        )
    def bstack1lll11l1lll_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪᖐ"): self.hooks
        }
    def bstack1lll11l11ll_opy_(self):
        if self.bstack11llll111l_opy_:
            return {
                bstack1l1l1l1_opy_ (u"ࠬ࡯࡮ࡵࡧࡪࡶࡦࡺࡩࡰࡰࡶࠫᖑ"): self.bstack11llll111l_opy_
            }
        return {}
    def bstack1lll11l1111_opy_(self):
        return {
            **super().bstack1lll11l1111_opy_(),
            **self.bstack1lll11l1lll_opy_()
        }
    def bstack1lll11ll1l1_opy_(self):
        return {
            **super().bstack1lll11ll1l1_opy_(),
            **self.bstack1lll11l11ll_opy_()
        }
    def bstack1l11111ll1_opy_(self):
        return bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨᖒ")
class bstack11lll1l111_opy_(bstack11lllll1l1_opy_):
    def __init__(self, hook_type, *args, **kwargs):
        self.hook_type = hook_type
        super().__init__(*args, **kwargs, bstack1ll111l1l1_opy_=bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࠬᖓ"))
    def bstack1l1111ll1l_opy_(self):
        return self.hook_type
    def bstack1lll11l1l11_opy_(self):
        return {
            bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡴࡺࡲࡨࠫᖔ"): self.hook_type
        }
    def bstack1lll11l1111_opy_(self):
        return {
            **super().bstack1lll11l1111_opy_(),
            **self.bstack1lll11l1l11_opy_()
        }
    def bstack1lll11ll1l1_opy_(self):
        return {
            **super().bstack1lll11ll1l1_opy_(),
            **self.bstack1lll11l1l11_opy_()
        }
    def bstack1l11111ll1_opy_(self):
        return bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫᖕ")