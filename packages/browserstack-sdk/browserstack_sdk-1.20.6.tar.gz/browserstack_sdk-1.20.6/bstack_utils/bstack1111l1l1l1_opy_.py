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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111l1lll11_opy_
from browserstack_sdk.bstack1llll111_opy_ import bstack111ll1l1_opy_
def _1111l11l11_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack1111l11ll1_opy_:
    def __init__(self, handler):
        self._1111l111l1_opy_ = {}
        self._1111l1111l_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack111ll1l1_opy_.version()
        if bstack111l1lll11_opy_(pytest_version, bstack1l1l1l1_opy_ (u"ࠤ࠻࠲࠶࠴࠱ࠣᏇ")) >= 0:
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭Ꮘ")] = Module._register_setup_function_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᏉ")] = Module._register_setup_module_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᏊ")] = Class._register_setup_class_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᏋ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᏌ"))
            Module._register_setup_module_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᏍ"))
            Class._register_setup_class_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᏎ"))
            Class._register_setup_method_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᏏ"))
        else:
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᏐ")] = Module._inject_setup_function_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭Ꮡ")] = Module._inject_setup_module_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭Ꮢ")] = Class._inject_setup_class_fixture
            self._1111l111l1_opy_[bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᏓ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠨࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᏔ"))
            Module._inject_setup_module_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠩࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᏕ"))
            Class._inject_setup_class_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠪࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᏖ"))
            Class._inject_setup_method_fixture = self.bstack1111l11111_opy_(bstack1l1l1l1_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᏗ"))
    def bstack1111l11l1l_opy_(self, bstack1111l1l11l_opy_, hook_type):
        meth = getattr(bstack1111l1l11l_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._1111l1111l_opy_[hook_type] = meth
            setattr(bstack1111l1l11l_opy_, hook_type, self.bstack1111l1ll11_opy_(hook_type))
    def bstack1111l1lll1_opy_(self, instance, bstack1111l1l1ll_opy_):
        if bstack1111l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠧ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣᏘ"):
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠨࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠢᏙ"))
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࠦᏚ"))
        if bstack1111l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠣ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠤᏛ"):
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠤࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠣᏜ"))
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠧᏝ"))
        if bstack1111l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠦࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠦᏞ"):
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠥᏟ"))
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠢᏠ"))
        if bstack1111l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣᏡ"):
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟࡮ࡧࡷ࡬ࡴࡪࠢᏢ"))
            self.bstack1111l11l1l_opy_(instance.obj, bstack1l1l1l1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲ࡫ࡴࡩࡱࡧࠦᏣ"))
    @staticmethod
    def bstack1111l1l111_opy_(hook_type, func, args):
        if hook_type in [bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩᏤ"), bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭Ꮵ")]:
            _1111l11l11_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack1111l1ll11_opy_(self, hook_type):
        def bstack1111l111ll_opy_(arg=None):
            self.handler(hook_type, bstack1l1l1l1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬᏦ"))
            result = None
            exception = None
            try:
                self.bstack1111l1l111_opy_(hook_type, self._1111l1111l_opy_[hook_type], (arg,))
                result = Result(result=bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭Ꮷ"))
            except Exception as e:
                result = Result(result=bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᏨ"), exception=e)
                self.handler(hook_type, bstack1l1l1l1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᏩ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1l1l1l1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨᏪ"), result)
        def bstack1111l1ll1l_opy_(this, arg=None):
            self.handler(hook_type, bstack1l1l1l1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪᏫ"))
            result = None
            exception = None
            try:
                self.bstack1111l1l111_opy_(hook_type, self._1111l1111l_opy_[hook_type], (this, arg))
                result = Result(result=bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫᏬ"))
            except Exception as e:
                result = Result(result=bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᏭ"), exception=e)
                self.handler(hook_type, bstack1l1l1l1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᏮ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1l1l1l1_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭Ꮿ"), result)
        if hook_type in [bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟࡮ࡧࡷ࡬ࡴࡪࠧᏰ"), bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲ࡫ࡴࡩࡱࡧࠫᏱ")]:
            return bstack1111l1ll1l_opy_
        return bstack1111l111ll_opy_
    def bstack1111l11111_opy_(self, bstack1111l1l1ll_opy_):
        def bstack1111l11lll_opy_(this, *args, **kwargs):
            self.bstack1111l1lll1_opy_(this, bstack1111l1l1ll_opy_)
            self._1111l111l1_opy_[bstack1111l1l1ll_opy_](this, *args, **kwargs)
        return bstack1111l11lll_opy_