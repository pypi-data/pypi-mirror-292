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
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack11lll1ll11_opy_ import RobotHandler
from bstack_utils.capture import bstack1l1111llll_opy_
from bstack_utils.bstack1l111l11l1_opy_ import bstack11lllll1l1_opy_, bstack11lll1l111_opy_, bstack11llll1lll_opy_
from bstack_utils.bstack1l1lll11ll_opy_ import bstack1ll11l1lll_opy_
from bstack_utils.bstack111lll1l1_opy_ import bstack11l1l11l1_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1l111l1ll1_opy_, bstack1ll1l11lll_opy_, Result, \
    bstack11ll1l11ll_opy_, bstack11llll11l1_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    store = {
        bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ൱"): [],
        bstack1l1l1l1_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫ൲"): [],
        bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪ൳"): []
    }
    bstack11ll1lll1l_opy_ = []
    bstack1l111l11ll_opy_ = []
    @staticmethod
    def bstack11lllll1ll_opy_(log):
        if not (log[bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ൴")] and log[bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ൵")].strip()):
            return
        active = bstack1ll11l1lll_opy_.bstack11ll1lllll_opy_()
        log = {
            bstack1l1l1l1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ൶"): log[bstack1l1l1l1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ൷")],
            bstack1l1l1l1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ൸"): bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"ࠬࡠࠧ൹"),
            bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧൺ"): log[bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨൻ")],
        }
        if active:
            if active[bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ർ")] == bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧൽ"):
                log[bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪൾ")] = active[bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫൿ")]
            elif active[bstack1l1l1l1_opy_ (u"ࠬࡺࡹࡱࡧࠪ඀")] == bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࠫඁ"):
                log[bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧං")] = active[bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨඃ")]
        bstack11l1l11l1_opy_.bstack1ll1l1111l_opy_([log])
    def __init__(self):
        self.messages = Messages()
        self._1l1111l1l1_opy_ = None
        self._11lll1l1ll_opy_ = None
        self._11ll1ll1l1_opy_ = OrderedDict()
        self.bstack11llll1l11_opy_ = bstack1l1111llll_opy_(self.bstack11lllll1ll_opy_)
    @bstack11ll1l11ll_opy_(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack11llll1111_opy_()
        if not self._11ll1ll1l1_opy_.get(attrs.get(bstack1l1l1l1_opy_ (u"ࠩ࡬ࡨࠬ඄")), None):
            self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠪ࡭ࡩ࠭අ"))] = {}
        bstack11llll11ll_opy_ = bstack11llll1lll_opy_(
                bstack11lll1ll1l_opy_=attrs.get(bstack1l1l1l1_opy_ (u"ࠫ࡮ࡪࠧආ")),
                name=name,
                bstack11lll1llll_opy_=bstack1ll1l11lll_opy_(),
                file_path=os.path.relpath(attrs[bstack1l1l1l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬඇ")], start=os.getcwd()) if attrs.get(bstack1l1l1l1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ඈ")) != bstack1l1l1l1_opy_ (u"ࠧࠨඉ") else bstack1l1l1l1_opy_ (u"ࠨࠩඊ"),
                framework=bstack1l1l1l1_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨඋ")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack1l1l1l1_opy_ (u"ࠪ࡭ࡩ࠭ඌ"), None)
        self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠫ࡮ࡪࠧඍ"))][bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨඎ")] = bstack11llll11ll_opy_
    @bstack11ll1l11ll_opy_(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack1l11111l1l_opy_()
        self._11lll11l11_opy_(messages)
        for bstack1l11111lll_opy_ in self.bstack11ll1lll1l_opy_:
            bstack1l11111lll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨඏ")][bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭ඐ")].extend(self.store[bstack1l1l1l1_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬ࡠࡪࡲࡳࡰࡹࠧඑ")])
            bstack11l1l11l1_opy_.bstack11ll1llll1_opy_(bstack1l11111lll_opy_)
        self.bstack11ll1lll1l_opy_ = []
        self.store[bstack1l1l1l1_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨඒ")] = []
    @bstack11ll1l11ll_opy_(class_method=True)
    def start_test(self, name, attrs):
        self.bstack11llll1l11_opy_.start()
        if not self._11ll1ll1l1_opy_.get(attrs.get(bstack1l1l1l1_opy_ (u"ࠪ࡭ࡩ࠭ඓ")), None):
            self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠫ࡮ࡪࠧඔ"))] = {}
        driver = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫඕ"), None)
        bstack1l111l11l1_opy_ = bstack11llll1lll_opy_(
            bstack11lll1ll1l_opy_=attrs.get(bstack1l1l1l1_opy_ (u"࠭ࡩࡥࠩඖ")),
            name=name,
            bstack11lll1llll_opy_=bstack1ll1l11lll_opy_(),
            file_path=os.path.relpath(attrs[bstack1l1l1l1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ඗")], start=os.getcwd()),
            scope=RobotHandler.bstack11ll1ll11l_opy_(attrs.get(bstack1l1l1l1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ඘"), None)),
            framework=bstack1l1l1l1_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨ඙"),
            tags=attrs[bstack1l1l1l1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨක")],
            hooks=self.store[bstack1l1l1l1_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪඛ")],
            bstack11llll111l_opy_=bstack11l1l11l1_opy_.bstack1l111l1111_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack1l1l1l1_opy_ (u"ࠧࢁࡽࠡ࡞ࡱࠤࢀࢃࠢග").format(bstack1l1l1l1_opy_ (u"ࠨࠠࠣඝ").join(attrs[bstack1l1l1l1_opy_ (u"ࠧࡵࡣࡪࡷࠬඞ")]), name) if attrs[bstack1l1l1l1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ඟ")] else name
        )
        self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠩ࡬ࡨࠬච"))][bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ඡ")] = bstack1l111l11l1_opy_
        threading.current_thread().current_test_uuid = bstack1l111l11l1_opy_.bstack1l1111l111_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack1l1l1l1_opy_ (u"ࠫ࡮ࡪࠧජ"), None)
        self.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ඣ"), bstack1l111l11l1_opy_)
    @bstack11ll1l11ll_opy_(class_method=True)
    def end_test(self, name, attrs):
        self.bstack11llll1l11_opy_.reset()
        bstack11ll1lll11_opy_ = bstack11llll1ll1_opy_.get(attrs.get(bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ඤ")), bstack1l1l1l1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨඥ"))
        self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࠫඦ"))][bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬට")].stop(time=bstack1ll1l11lll_opy_(), duration=int(attrs.get(bstack1l1l1l1_opy_ (u"ࠪࡩࡱࡧࡰࡴࡧࡧࡸ࡮ࡳࡥࠨඨ"), bstack1l1l1l1_opy_ (u"ࠫ࠵࠭ඩ"))), result=Result(result=bstack11ll1lll11_opy_, exception=attrs.get(bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ඪ")), bstack1l1111ll11_opy_=[attrs.get(bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧණ"))]))
        self.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩඬ"), self._11ll1ll1l1_opy_[attrs.get(bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࠫත"))][bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬථ")], True)
        self.store[bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹࠧද")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @bstack11ll1l11ll_opy_(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack11llll1111_opy_()
        current_test_id = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡩ࠭ධ"), None)
        bstack11lll11ll1_opy_ = current_test_id if bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡪࠧන"), None) else bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡴࡷ࡬ࡸࡪࡥࡩࡥࠩ඲"), None)
        if attrs.get(bstack1l1l1l1_opy_ (u"ࠧࡵࡻࡳࡩࠬඳ"), bstack1l1l1l1_opy_ (u"ࠨࠩප")).lower() in [bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨඵ"), bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬබ")]:
            hook_type = bstack11lll11lll_opy_(attrs.get(bstack1l1l1l1_opy_ (u"ࠫࡹࡿࡰࡦࠩභ")), bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩම"), None))
            hook_name = bstack1l1l1l1_opy_ (u"࠭ࡻࡾࠩඹ").format(attrs.get(bstack1l1l1l1_opy_ (u"ࠧ࡬ࡹࡱࡥࡲ࡫ࠧය"), bstack1l1l1l1_opy_ (u"ࠨࠩර")))
            if hook_type in [bstack1l1l1l1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭඼"), bstack1l1l1l1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭ල")]:
                hook_name = bstack1l1l1l1_opy_ (u"ࠫࡠࢁࡽ࡞ࠢࡾࢁࠬ඾").format(bstack11lllll11l_opy_.get(hook_type), attrs.get(bstack1l1l1l1_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ඿"), bstack1l1l1l1_opy_ (u"࠭ࠧව")))
            bstack1l1111l1ll_opy_ = bstack11lll1l111_opy_(
                bstack11lll1ll1l_opy_=bstack11lll11ll1_opy_ + bstack1l1l1l1_opy_ (u"ࠧ࠮ࠩශ") + attrs.get(bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ෂ"), bstack1l1l1l1_opy_ (u"ࠩࠪස")).lower(),
                name=hook_name,
                bstack11lll1llll_opy_=bstack1ll1l11lll_opy_(),
                file_path=os.path.relpath(attrs.get(bstack1l1l1l1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪහ")), start=os.getcwd()),
                framework=bstack1l1l1l1_opy_ (u"ࠫࡗࡵࡢࡰࡶࠪළ"),
                tags=attrs[bstack1l1l1l1_opy_ (u"ࠬࡺࡡࡨࡵࠪෆ")],
                scope=RobotHandler.bstack11ll1ll11l_opy_(attrs.get(bstack1l1l1l1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭෇"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack1l1111l1ll_opy_.bstack1l1111l111_opy_()
            threading.current_thread().current_hook_id = bstack11lll11ll1_opy_ + bstack1l1l1l1_opy_ (u"ࠧ࠮ࠩ෈") + attrs.get(bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭෉"), bstack1l1l1l1_opy_ (u"්ࠩࠪ")).lower()
            self.store[bstack1l1l1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ෋")] = [bstack1l1111l1ll_opy_.bstack1l1111l111_opy_()]
            if bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ෌"), None):
                self.store[bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩ෍")].append(bstack1l1111l1ll_opy_.bstack1l1111l111_opy_())
            else:
                self.store[bstack1l1l1l1_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬ෎")].append(bstack1l1111l1ll_opy_.bstack1l1111l111_opy_())
            if bstack11lll11ll1_opy_:
                self._11ll1ll1l1_opy_[bstack11lll11ll1_opy_ + bstack1l1l1l1_opy_ (u"ࠧ࠮ࠩා") + attrs.get(bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ැ"), bstack1l1l1l1_opy_ (u"ࠩࠪෑ")).lower()] = { bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ි"): bstack1l1111l1ll_opy_ }
            bstack11l1l11l1_opy_.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬී"), bstack1l1111l1ll_opy_)
        else:
            bstack1l1111lll1_opy_ = {
                bstack1l1l1l1_opy_ (u"ࠬ࡯ࡤࠨු"): uuid4().__str__(),
                bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡺࡷࠫ෕"): bstack1l1l1l1_opy_ (u"ࠧࡼࡿࠣࡿࢂ࠭ූ").format(attrs.get(bstack1l1l1l1_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨ෗")), attrs.get(bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧෘ"), bstack1l1l1l1_opy_ (u"ࠪࠫෙ"))) if attrs.get(bstack1l1l1l1_opy_ (u"ࠫࡦࡸࡧࡴࠩේ"), []) else attrs.get(bstack1l1l1l1_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬෛ")),
                bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡧࡳࡣࡦࡸࡧࡶ࡯ࡨࡲࡹ࠭ො"): attrs.get(bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬෝ"), []),
                bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬෞ"): bstack1ll1l11lll_opy_(),
                bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩෟ"): bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ෠"),
                bstack1l1l1l1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ෡"): attrs.get(bstack1l1l1l1_opy_ (u"ࠬࡪ࡯ࡤࠩ෢"), bstack1l1l1l1_opy_ (u"࠭ࠧ෣"))
            }
            if attrs.get(bstack1l1l1l1_opy_ (u"ࠧ࡭࡫ࡥࡲࡦࡳࡥࠨ෤"), bstack1l1l1l1_opy_ (u"ࠨࠩ෥")) != bstack1l1l1l1_opy_ (u"ࠩࠪ෦"):
                bstack1l1111lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫ෧")] = attrs.get(bstack1l1l1l1_opy_ (u"ࠫࡱ࡯ࡢ࡯ࡣࡰࡩࠬ෨"))
            if not self.bstack1l111l11ll_opy_:
                self._11ll1ll1l1_opy_[self._11lll11111_opy_()][bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ෩")].add_step(bstack1l1111lll1_opy_)
                threading.current_thread().current_step_uuid = bstack1l1111lll1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡩࡥࠩ෪")]
            self.bstack1l111l11ll_opy_.append(bstack1l1111lll1_opy_)
    @bstack11ll1l11ll_opy_(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack1l11111l1l_opy_()
        self._11lll11l11_opy_(messages)
        current_test_id = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡥࠩ෫"), None)
        bstack11lll11ll1_opy_ = current_test_id if current_test_id else bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡶࡹ࡮ࡺࡥࡠ࡫ࡧࠫ෬"), None)
        bstack11ll1l1ll1_opy_ = bstack11llll1ll1_opy_.get(attrs.get(bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ෭")), bstack1l1l1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ෮"))
        bstack1l111111ll_opy_ = attrs.get(bstack1l1l1l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ෯"))
        if bstack11ll1l1ll1_opy_ != bstack1l1l1l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭෰") and not attrs.get(bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ෱")) and self._1l1111l1l1_opy_:
            bstack1l111111ll_opy_ = self._1l1111l1l1_opy_
        bstack11lll111ll_opy_ = Result(result=bstack11ll1l1ll1_opy_, exception=bstack1l111111ll_opy_, bstack1l1111ll11_opy_=[bstack1l111111ll_opy_])
        if attrs.get(bstack1l1l1l1_opy_ (u"ࠧࡵࡻࡳࡩࠬෲ"), bstack1l1l1l1_opy_ (u"ࠨࠩෳ")).lower() in [bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ෴"), bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ෵")]:
            bstack11lll11ll1_opy_ = current_test_id if current_test_id else bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡵࡪࡶࡨࡣ࡮ࡪࠧ෶"), None)
            if bstack11lll11ll1_opy_:
                bstack11llll1l1l_opy_ = bstack11lll11ll1_opy_ + bstack1l1l1l1_opy_ (u"ࠧ࠳ࠢ෷") + attrs.get(bstack1l1l1l1_opy_ (u"࠭ࡴࡺࡲࡨࠫ෸"), bstack1l1l1l1_opy_ (u"ࠧࠨ෹")).lower()
                self._11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ෺")].stop(time=bstack1ll1l11lll_opy_(), duration=int(attrs.get(bstack1l1l1l1_opy_ (u"ࠩࡨࡰࡦࡶࡳࡦࡦࡷ࡭ࡲ࡫ࠧ෻"), bstack1l1l1l1_opy_ (u"ࠪ࠴ࠬ෼"))), result=bstack11lll111ll_opy_)
                bstack11l1l11l1_opy_.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭෽"), self._11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ෾")])
        else:
            bstack11lll11ll1_opy_ = current_test_id if current_test_id else bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤ࡯ࡤࠨ෿"), None)
            if bstack11lll11ll1_opy_ and len(self.bstack1l111l11ll_opy_) == 1:
                current_step_uuid = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡷࡩࡵࡥࡵࡶ࡫ࡧࠫ฀"), None)
                self._11ll1ll1l1_opy_[bstack11lll11ll1_opy_][bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫก")].bstack1l111l111l_opy_(current_step_uuid, duration=int(attrs.get(bstack1l1l1l1_opy_ (u"ࠩࡨࡰࡦࡶࡳࡦࡦࡷ࡭ࡲ࡫ࠧข"), bstack1l1l1l1_opy_ (u"ࠪ࠴ࠬฃ"))), result=bstack11lll111ll_opy_)
            else:
                self.bstack1l11111l11_opy_(attrs)
            self.bstack1l111l11ll_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺ࡭࡭ࠩค"), bstack1l1l1l1_opy_ (u"ࠬࡴ࡯ࠨฅ")) == bstack1l1l1l1_opy_ (u"࠭ࡹࡦࡵࠪฆ"):
                return
            self.messages.push(message)
            bstack1l1111111l_opy_ = []
            if bstack1ll11l1lll_opy_.bstack11ll1lllll_opy_():
                bstack1l1111111l_opy_.append({
                    bstack1l1l1l1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪง"): bstack1ll1l11lll_opy_(),
                    bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩจ"): message.get(bstack1l1l1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪฉ")),
                    bstack1l1l1l1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩช"): message.get(bstack1l1l1l1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪซ")),
                    **bstack1ll11l1lll_opy_.bstack11ll1lllll_opy_()
                })
                if len(bstack1l1111111l_opy_) > 0:
                    bstack11l1l11l1_opy_.bstack1ll1l1111l_opy_(bstack1l1111111l_opy_)
        except Exception as err:
            pass
    def close(self):
        bstack11l1l11l1_opy_.bstack11lll1l11l_opy_()
    def bstack1l11111l11_opy_(self, bstack1l111111l1_opy_):
        if not bstack1ll11l1lll_opy_.bstack11ll1lllll_opy_():
            return
        kwname = bstack1l1l1l1_opy_ (u"ࠬࢁࡽࠡࡽࢀࠫฌ").format(bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"࠭࡫ࡸࡰࡤࡱࡪ࠭ญ")), bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬฎ"), bstack1l1l1l1_opy_ (u"ࠨࠩฏ"))) if bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧฐ"), []) else bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪฑ"))
        error_message = bstack1l1l1l1_opy_ (u"ࠦࡰࡽ࡮ࡢ࡯ࡨ࠾ࠥࡢࠢࡼ࠲ࢀࡠࠧࠦࡼࠡࡵࡷࡥࡹࡻࡳ࠻ࠢ࡟ࠦࢀ࠷ࡽ࡝ࠤࠣࢀࠥ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢ࡟ࠦࢀ࠸ࡽ࡝ࠤࠥฒ").format(kwname, bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬณ")), str(bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧด"))))
        bstack11lllllll1_opy_ = bstack1l1l1l1_opy_ (u"ࠢ࡬ࡹࡱࡥࡲ࡫࠺ࠡ࡞ࠥࡿ࠵ࢃ࡜ࠣࠢࡿࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࡢࠢࡼ࠳ࢀࡠࠧࠨต").format(kwname, bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨถ")))
        bstack11llllll1l_opy_ = error_message if bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪท")) else bstack11lllllll1_opy_
        bstack11lll1lll1_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ธ"): self.bstack1l111l11ll_opy_[-1].get(bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨน"), bstack1ll1l11lll_opy_()),
            bstack1l1l1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭บ"): bstack11llllll1l_opy_,
            bstack1l1l1l1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬป"): bstack1l1l1l1_opy_ (u"ࠧࡆࡔࡕࡓࡗ࠭ผ") if bstack1l111111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨฝ")) == bstack1l1l1l1_opy_ (u"ࠩࡉࡅࡎࡒࠧพ") else bstack1l1l1l1_opy_ (u"ࠪࡍࡓࡌࡏࠨฟ"),
            **bstack1ll11l1lll_opy_.bstack11ll1lllll_opy_()
        }
        bstack11l1l11l1_opy_.bstack1ll1l1111l_opy_([bstack11lll1lll1_opy_])
    def _11lll11111_opy_(self):
        for bstack11lll1ll1l_opy_ in reversed(self._11ll1ll1l1_opy_):
            bstack11ll1ll1ll_opy_ = bstack11lll1ll1l_opy_
            data = self._11ll1ll1l1_opy_[bstack11lll1ll1l_opy_][bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧภ")]
            if isinstance(data, bstack11lll1l111_opy_):
                if not bstack1l1l1l1_opy_ (u"ࠬࡋࡁࡄࡊࠪม") in data.bstack1l1111ll1l_opy_():
                    return bstack11ll1ll1ll_opy_
            else:
                return bstack11ll1ll1ll_opy_
    def _11lll11l11_opy_(self, messages):
        try:
            bstack11llllll11_opy_ = BuiltIn().get_variable_value(bstack1l1l1l1_opy_ (u"ࠨࠤࡼࡎࡒࡋࠥࡒࡅࡗࡇࡏࢁࠧย")) in (bstack11ll1l1l1l_opy_.DEBUG, bstack11ll1l1l1l_opy_.TRACE)
            for message, bstack11lll111l1_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨร"))
                level = message.get(bstack1l1l1l1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧฤ"))
                if level == bstack11ll1l1l1l_opy_.FAIL:
                    self._1l1111l1l1_opy_ = name or self._1l1111l1l1_opy_
                    self._11lll1l1ll_opy_ = bstack11lll111l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠤࡰࡩࡸࡹࡡࡨࡧࠥล")) if bstack11llllll11_opy_ and bstack11lll111l1_opy_ else self._11lll1l1ll_opy_
        except:
            pass
    @classmethod
    def bstack11lll11l1l_opy_(self, event: str, bstack11ll1l1lll_opy_: bstack11lllll1l1_opy_, bstack11lllll111_opy_=False):
        if event == bstack1l1l1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬฦ"):
            bstack11ll1l1lll_opy_.set(hooks=self.store[bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࠨว")])
        if event == bstack1l1l1l1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭ศ"):
            event = bstack1l1l1l1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨษ")
        if bstack11lllll111_opy_:
            bstack11llllllll_opy_ = {
                bstack1l1l1l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫส"): event,
                bstack11ll1l1lll_opy_.bstack1l11111ll1_opy_(): bstack11ll1l1lll_opy_.bstack11ll1l1l11_opy_(event)
            }
            self.bstack11ll1lll1l_opy_.append(bstack11llllllll_opy_)
        else:
            bstack11l1l11l1_opy_.bstack11lll11l1l_opy_(event, bstack11ll1l1lll_opy_)
class Messages:
    def __init__(self):
        self._11lll1111l_opy_ = []
    def bstack11llll1111_opy_(self):
        self._11lll1111l_opy_.append([])
    def bstack1l11111l1l_opy_(self):
        return self._11lll1111l_opy_.pop() if self._11lll1111l_opy_ else list()
    def push(self, message):
        self._11lll1111l_opy_[-1].append(message) if self._11lll1111l_opy_ else self._11lll1111l_opy_.append([message])
class bstack11ll1l1l1l_opy_:
    FAIL = bstack1l1l1l1_opy_ (u"ࠨࡈࡄࡍࡑ࠭ห")
    ERROR = bstack1l1l1l1_opy_ (u"ࠩࡈࡖࡗࡕࡒࠨฬ")
    WARNING = bstack1l1l1l1_opy_ (u"࡛ࠪࡆࡘࡎࠨอ")
    bstack1l1111l11l_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡎࡔࡆࡐࠩฮ")
    DEBUG = bstack1l1l1l1_opy_ (u"ࠬࡊࡅࡃࡗࡊࠫฯ")
    TRACE = bstack1l1l1l1_opy_ (u"࠭ࡔࡓࡃࡆࡉࠬะ")
    bstack1l11111111_opy_ = [FAIL, ERROR]
def bstack11ll1ll111_opy_(bstack11lll1l1l1_opy_):
    if not bstack11lll1l1l1_opy_:
        return None
    if bstack11lll1l1l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪั"), None):
        return getattr(bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫา")], bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧำ"), None)
    return bstack11lll1l1l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨิ"), None)
def bstack11lll11lll_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪี"), bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧึ")]:
        return
    if hook_type.lower() == bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬื"):
        if current_test_uuid is None:
            return bstack1l1l1l1_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏุࠫ")
        else:
            return bstack1l1l1l1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍู࠭")
    elif hook_type.lower() == bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱฺࠫ"):
        if current_test_uuid is None:
            return bstack1l1l1l1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭฻")
        else:
            return bstack1l1l1l1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ฼")