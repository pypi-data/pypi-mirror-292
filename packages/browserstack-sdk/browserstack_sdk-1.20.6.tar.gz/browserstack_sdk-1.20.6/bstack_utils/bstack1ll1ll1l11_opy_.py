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
class bstack11l11ll11l_opy_(object):
  bstack1l11lllll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠪࢂࠬ།")), bstack1l1l1l1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ༎"))
  bstack11l11lll11_opy_ = os.path.join(bstack1l11lllll1_opy_, bstack1l1l1l1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹ࠮࡫ࡵࡲࡲࠬ༏"))
  bstack11l11ll1ll_opy_ = None
  perform_scan = None
  bstack1l1l11ll_opy_ = None
  bstack11ll1l11l_opy_ = None
  bstack11l1l11ll1_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1l1l1l1_opy_ (u"࠭ࡩ࡯ࡵࡷࡥࡳࡩࡥࠨ༐")):
      cls.instance = super(bstack11l11ll11l_opy_, cls).__new__(cls)
      cls.instance.bstack11l11lll1l_opy_()
    return cls.instance
  def bstack11l11lll1l_opy_(self):
    try:
      with open(self.bstack11l11lll11_opy_, bstack1l1l1l1_opy_ (u"ࠧࡳࠩ༑")) as bstack1l11ll11l_opy_:
        bstack11l11llll1_opy_ = bstack1l11ll11l_opy_.read()
        data = json.loads(bstack11l11llll1_opy_)
        if bstack1l1l1l1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪ༒") in data:
          self.bstack11l1l11lll_opy_(data[bstack1l1l1l1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫ༓")])
        if bstack1l1l1l1_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫ༔") in data:
          self.bstack11l1l11111_opy_(data[bstack1l1l1l1_opy_ (u"ࠫࡸࡩࡲࡪࡲࡷࡷࠬ༕")])
    except:
      pass
  def bstack11l1l11111_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts[bstack1l1l1l1_opy_ (u"ࠬࡹࡣࡢࡰࠪ༖")]
      self.bstack1l1l11ll_opy_ = scripts[bstack1l1l1l1_opy_ (u"࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠪ༗")]
      self.bstack11ll1l11l_opy_ = scripts[bstack1l1l1l1_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼ༘ࠫ")]
      self.bstack11l1l11ll1_opy_ = scripts[bstack1l1l1l1_opy_ (u"ࠨࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸ༙࠭")]
  def bstack11l1l11lll_opy_(self, bstack11l11ll1ll_opy_):
    if bstack11l11ll1ll_opy_ != None and len(bstack11l11ll1ll_opy_) != 0:
      self.bstack11l11ll1ll_opy_ = bstack11l11ll1ll_opy_
  def store(self):
    try:
      with open(self.bstack11l11lll11_opy_, bstack1l1l1l1_opy_ (u"ࠩࡺࠫ༚")) as file:
        json.dump({
          bstack1l1l1l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡷࠧ༛"): self.bstack11l11ll1ll_opy_,
          bstack1l1l1l1_opy_ (u"ࠦࡸࡩࡲࡪࡲࡷࡷࠧ༜"): {
            bstack1l1l1l1_opy_ (u"ࠧࡹࡣࡢࡰࠥ༝"): self.perform_scan,
            bstack1l1l1l1_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠥ༞"): self.bstack1l1l11ll_opy_,
            bstack1l1l1l1_opy_ (u"ࠢࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠦ༟"): self.bstack11ll1l11l_opy_,
            bstack1l1l1l1_opy_ (u"ࠣࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸࠨ༠"): self.bstack11l1l11ll1_opy_
          }
        }, file)
    except:
      pass
  def bstack1l1l11l11l_opy_(self, bstack11l11ll1l1_opy_):
    try:
      return any(command.get(bstack1l1l1l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ༡")) == bstack11l11ll1l1_opy_ for command in self.bstack11l11ll1ll_opy_)
    except:
      return False
bstack1ll1ll1l11_opy_ = bstack11l11ll11l_opy_()