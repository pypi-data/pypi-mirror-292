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
import atexit
import datetime
import inspect
import logging
import os
import signal
import sys
import threading
from uuid import uuid4
from bstack_utils.percy_sdk import PercySDK
import tempfile
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack111lll11l_opy_, bstack1ll111llll_opy_, update, bstack1lll11lll_opy_,
                                       bstack11lll1ll1_opy_, bstack1111l1ll_opy_, bstack11llllll_opy_, bstack1lllll11l_opy_,
                                       bstack1ll11l1ll1_opy_, bstack1l1l111ll_opy_, bstack1lll11ll_opy_, bstack11l11llll_opy_,
                                       bstack1ll11l1l_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack111l11ll_opy_)
from browserstack_sdk.bstack1llll111_opy_ import bstack111ll1l1_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1lll1111ll_opy_
from bstack_utils.capture import bstack1l1111llll_opy_
from bstack_utils.config import Config
from bstack_utils.constants import bstack1l1l1l1l1l_opy_, bstack1l11ll11ll_opy_, bstack1l1llll1l1_opy_, \
    bstack1l111l1l_opy_
from bstack_utils.helper import bstack1l111l1ll1_opy_, bstack111l111l11_opy_, bstack11llll11l1_opy_, bstack1lll11llll_opy_, bstack111lll1l11_opy_, bstack1ll1l11lll_opy_, \
    bstack111l11ll1l_opy_, \
    bstack111ll1ll11_opy_, bstack1l1l1111_opy_, bstack11lll1l1_opy_, bstack1111ll1l1l_opy_, bstack1llll1111_opy_, Notset, \
    bstack1l11lll11_opy_, bstack111ll1llll_opy_, bstack111lll11ll_opy_, Result, bstack111l1l1111_opy_, bstack111l1l1l11_opy_, bstack11ll1l11ll_opy_, \
    bstack111l1111_opy_, bstack11ll1l1ll_opy_, bstack1l1111ll_opy_, bstack1111lllll1_opy_
from bstack_utils.bstack1111l1l1l1_opy_ import bstack1111l11ll1_opy_
from bstack_utils.messages import bstack11l11111_opy_, bstack1ll1l1111_opy_, bstack1llllll111_opy_, bstack1ll11ll1l1_opy_, bstack1lll1lll1_opy_, \
    bstack1ll1lll1l1_opy_, bstack1l11ll1ll1_opy_, bstack1l1lll1111_opy_, bstack111ll1lll_opy_, bstack11l111111_opy_, \
    bstack1l11ll111l_opy_, bstack1ll11l11ll_opy_
from bstack_utils.proxy import bstack111l1ll1_opy_, bstack1l1l1lll1_opy_
from bstack_utils.bstack11l1l1ll1_opy_ import bstack1llll1111l1_opy_, bstack1lll1ll1ll1_opy_, bstack1lll1llll11_opy_, bstack1lll1llllll_opy_, \
    bstack1lll1lll111_opy_, bstack1llll11111l_opy_, bstack1lll1ll1lll_opy_, bstack1ll1l1lll_opy_, bstack1lll1lll1ll_opy_
from bstack_utils.bstack1ll1ll1ll_opy_ import bstack111l1l111_opy_
from bstack_utils.bstack11l1ll1l1_opy_ import bstack1lll1ll11l_opy_, bstack1l1l11l11_opy_, bstack1l111llll_opy_, \
    bstack1l1l1lll11_opy_, bstack11llll11l_opy_
from bstack_utils.bstack1l111l11l1_opy_ import bstack11llll1lll_opy_
from bstack_utils.bstack1l1lll11ll_opy_ import bstack1ll11l1lll_opy_
import bstack_utils.bstack1llll11l11_opy_ as bstack1l11lll1l_opy_
from bstack_utils.bstack111lll1l1_opy_ import bstack11l1l11l1_opy_
from bstack_utils.bstack1ll1ll1l11_opy_ import bstack1ll1ll1l11_opy_
bstack11l11l1l_opy_ = None
bstack1l11ll11_opy_ = None
bstack111l11l1_opy_ = None
bstack1llllllll_opy_ = None
bstack1ll111l1_opy_ = None
bstack11111ll1_opy_ = None
bstack1l1ll1ll1l_opy_ = None
bstack11l1l1l11_opy_ = None
bstack1llll11l1_opy_ = None
bstack11111lll1_opy_ = None
bstack1l1llll1l_opy_ = None
bstack11l1lll1l_opy_ = None
bstack1ll1l1ll11_opy_ = None
bstack111lll1ll_opy_ = bstack1l1l1l1_opy_ (u"ࠬ࠭ᛚ")
CONFIG = {}
bstack1l1l1ll111_opy_ = False
bstack1ll11l11l1_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠧᛛ")
bstack1ll1lll111_opy_ = bstack1l1l1l1_opy_ (u"ࠧࠨᛜ")
bstack11ll11lll_opy_ = False
bstack1ll111111_opy_ = []
bstack11111l11_opy_ = bstack1l1l1l1l1l_opy_
bstack1ll11llll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨᛝ")
bstack1ll1l1l1111_opy_ = False
bstack11ll11ll_opy_ = {}
bstack111lll11_opy_ = False
logger = bstack1lll1111ll_opy_.get_logger(__name__, bstack11111l11_opy_)
store = {
    bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭ᛞ"): []
}
bstack1ll11llll11_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_11ll1ll1l1_opy_ = {}
current_test_uuid = None
def bstack1ll111ll1l_opy_(page, bstack1ll1l1l11l_opy_):
    try:
        page.evaluate(bstack1l1l1l1_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦᛟ"),
                      bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨᛠ") + json.dumps(
                          bstack1ll1l1l11l_opy_) + bstack1l1l1l1_opy_ (u"ࠧࢃࡽࠣᛡ"))
    except Exception as e:
        print(bstack1l1l1l1_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀࠦᛢ"), e)
def bstack1111l1111_opy_(page, message, level):
    try:
        page.evaluate(bstack1l1l1l1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣᛣ"), bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ᛤ") + json.dumps(
            message) + bstack1l1l1l1_opy_ (u"ࠩ࠯ࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠬᛥ") + json.dumps(level) + bstack1l1l1l1_opy_ (u"ࠪࢁࢂ࠭ᛦ"))
    except Exception as e:
        print(bstack1l1l1l1_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࢀࢃࠢᛧ"), e)
def pytest_configure(config):
    bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
    config.args = bstack1ll11l1lll_opy_.bstack1ll1ll1111l_opy_(config.args)
    bstack1l111l111_opy_.bstack1ll1l1l1l_opy_(bstack1l1111ll_opy_(config.getoption(bstack1l1l1l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩᛨ"))))
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    bstack1ll1l1l1ll1_opy_ = item.config.getoption(bstack1l1l1l1_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨᛩ"))
    plugins = item.config.getoption(bstack1l1l1l1_opy_ (u"ࠢࡱ࡮ࡸ࡫࡮ࡴࡳࠣᛪ"))
    report = outcome.get_result()
    bstack1ll1l1111ll_opy_(item, call, report)
    if bstack1l1l1l1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡰ࡭ࡷࡪ࡭ࡳࠨ᛫") not in plugins or bstack1llll1111_opy_():
        return
    summary = []
    driver = getattr(item, bstack1l1l1l1_opy_ (u"ࠤࡢࡨࡷ࡯ࡶࡦࡴࠥ᛬"), None)
    page = getattr(item, bstack1l1l1l1_opy_ (u"ࠥࡣࡵࡧࡧࡦࠤ᛭"), None)
    try:
        if (driver == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None):
        bstack1ll1l111111_opy_(item, report, summary, bstack1ll1l1l1ll1_opy_)
    if (page is not None):
        bstack1ll1l111l11_opy_(item, report, summary, bstack1ll1l1l1ll1_opy_)
def bstack1ll1l111111_opy_(item, report, summary, bstack1ll1l1l1ll1_opy_):
    if report.when == bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪᛮ") and report.skipped:
        bstack1lll1lll1ll_opy_(report)
    if report.when in [bstack1l1l1l1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᛯ"), bstack1l1l1l1_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࠣᛰ")]:
        return
    if not bstack111lll1l11_opy_():
        return
    try:
        if (str(bstack1ll1l1l1ll1_opy_).lower() != bstack1l1l1l1_opy_ (u"ࠧࡵࡴࡸࡩࠬᛱ")):
            item._driver.execute_script(
                bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭ᛲ") + json.dumps(
                    report.nodeid) + bstack1l1l1l1_opy_ (u"ࠩࢀࢁࠬᛳ"))
        os.environ[bstack1l1l1l1_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖࡢࡘࡊ࡙ࡔࡠࡐࡄࡑࡊ࠭ᛴ")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack1l1l1l1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࡀࠠࡼ࠲ࢀࠦᛵ").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1l1l1_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢᛶ")))
    bstack1111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࠢᛷ")
    bstack1lll1lll1ll_opy_(report)
    if not passed:
        try:
            bstack1111l1l1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1l1l1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢᛸ").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1111l1l1_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack1l1l1l1_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ᛹")))
        bstack1111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠤࠥ᛺")
        if not passed:
            try:
                bstack1111l1l1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1l1l1_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡸࡥࡢࡵࡲࡲ࠿ࠦࡻ࠱ࡿࠥ᛻").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1111l1l1_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡥࡣࡷࡥࠧࡀࠠࠨ᛼")
                    + json.dumps(bstack1l1l1l1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠦࠨ᛽"))
                    + bstack1l1l1l1_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࠤ᛾")
                )
            else:
                item._driver.execute_script(
                    bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡩࡧࡴࡢࠤ࠽ࠤࠬ᛿")
                    + json.dumps(str(bstack1111l1l1_opy_))
                    + bstack1l1l1l1_opy_ (u"ࠣ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࠦᜀ")
                )
        except Exception as e:
            summary.append(bstack1l1l1l1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡢࡰࡱࡳࡹࡧࡴࡦ࠼ࠣࡿ࠵ࢃࠢᜁ").format(e))
def bstack1ll1l111l1l_opy_(test_name, error_message):
    try:
        bstack1ll1l1lll11_opy_ = []
        bstack1l1l1l11l_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᜂ"), bstack1l1l1l1_opy_ (u"ࠫ࠵࠭ᜃ"))
        bstack1lll1ll11_opy_ = {bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᜄ"): test_name, bstack1l1l1l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᜅ"): error_message, bstack1l1l1l1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᜆ"): bstack1l1l1l11l_opy_}
        bstack1ll1l111ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠨࡲࡺࡣࡵࡿࡴࡦࡵࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ᜇ"))
        if os.path.exists(bstack1ll1l111ll1_opy_):
            with open(bstack1ll1l111ll1_opy_) as f:
                bstack1ll1l1lll11_opy_ = json.load(f)
        bstack1ll1l1lll11_opy_.append(bstack1lll1ll11_opy_)
        with open(bstack1ll1l111ll1_opy_, bstack1l1l1l1_opy_ (u"ࠩࡺࠫᜈ")) as f:
            json.dump(bstack1ll1l1lll11_opy_, f)
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡥࡳࡵ࡬ࡷࡹ࡯࡮ࡨࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡰࡺࡶࡨࡷࡹࠦࡥࡳࡴࡲࡶࡸࡀࠠࠨᜉ") + str(e))
def bstack1ll1l111l11_opy_(item, report, summary, bstack1ll1l1l1ll1_opy_):
    if report.when in [bstack1l1l1l1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥᜊ"), bstack1l1l1l1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᜋ")]:
        return
    if (str(bstack1ll1l1l1ll1_opy_).lower() != bstack1l1l1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫᜌ")):
        bstack1ll111ll1l_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1l1l1_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤᜍ")))
    bstack1111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠣࠤᜎ")
    bstack1lll1lll1ll_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1111l1l1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1l1l1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡷ࡫ࡡࡴࡱࡱ࠾ࠥࢁ࠰ࡾࠤᜏ").format(e)
                )
        try:
            if passed:
                bstack11llll11l_opy_(getattr(item, bstack1l1l1l1_opy_ (u"ࠪࡣࡵࡧࡧࡦࠩᜐ"), None), bstack1l1l1l1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦᜑ"))
            else:
                error_message = bstack1l1l1l1_opy_ (u"ࠬ࠭ᜒ")
                if bstack1111l1l1_opy_:
                    bstack1111l1111_opy_(item._page, str(bstack1111l1l1_opy_), bstack1l1l1l1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧᜓ"))
                    bstack11llll11l_opy_(getattr(item, bstack1l1l1l1_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ᜔࠭"), None), bstack1l1l1l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤ᜕ࠣ"), str(bstack1111l1l1_opy_))
                    error_message = str(bstack1111l1l1_opy_)
                else:
                    bstack11llll11l_opy_(getattr(item, bstack1l1l1l1_opy_ (u"ࠩࡢࡴࡦ࡭ࡥࠨ᜖"), None), bstack1l1l1l1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ᜗"))
                bstack1ll1l111l1l_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack1l1l1l1_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡩࡧࡴࡦࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀ࠶ࡽࠣ᜘").format(e))
try:
    from typing import Generator
    import pytest_playwright.pytest_playwright as p
    @pytest.fixture
    def page(context: BrowserContext, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
        page = context.new_page()
        request.node._page = page
        yield page
except:
    pass
def pytest_addoption(parser):
    parser.addoption(bstack1l1l1l1_opy_ (u"ࠧ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ᜙"), default=bstack1l1l1l1_opy_ (u"ࠨࡆࡢ࡮ࡶࡩࠧ᜚"), help=bstack1l1l1l1_opy_ (u"ࠢࡂࡷࡷࡳࡲࡧࡴࡪࡥࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠨ᜛"))
    parser.addoption(bstack1l1l1l1_opy_ (u"ࠣ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ᜜"), default=bstack1l1l1l1_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ᜝"), help=bstack1l1l1l1_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡨࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠤ᜞"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1l1l1l1_opy_ (u"ࠦ࠲࠳ࡤࡳ࡫ࡹࡩࡷࠨᜟ"), action=bstack1l1l1l1_opy_ (u"ࠧࡹࡴࡰࡴࡨࠦᜠ"), default=bstack1l1l1l1_opy_ (u"ࠨࡣࡩࡴࡲࡱࡪࠨᜡ"),
                         help=bstack1l1l1l1_opy_ (u"ࠢࡅࡴ࡬ࡺࡪࡸࠠࡵࡱࠣࡶࡺࡴࠠࡵࡧࡶࡸࡸࠨᜢ"))
def bstack11lllll1ll_opy_(log):
    if not (log[bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᜣ")] and log[bstack1l1l1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᜤ")].strip()):
        return
    active = bstack11ll1lllll_opy_()
    log = {
        bstack1l1l1l1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᜥ"): log[bstack1l1l1l1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪᜦ")],
        bstack1l1l1l1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨᜧ"): bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"࡚࠭ࠨᜨ"),
        bstack1l1l1l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᜩ"): log[bstack1l1l1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᜪ")],
    }
    if active:
        if active[bstack1l1l1l1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧᜫ")] == bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨᜬ"):
            log[bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᜭ")] = active[bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᜮ")]
        elif active[bstack1l1l1l1_opy_ (u"࠭ࡴࡺࡲࡨࠫᜯ")] == bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࠬᜰ"):
            log[bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᜱ")] = active[bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩᜲ")]
    bstack11l1l11l1_opy_.bstack1ll1l1111l_opy_([log])
def bstack11ll1lllll_opy_():
    if len(store[bstack1l1l1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧᜳ")]) > 0 and store[bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ᜴")][-1]:
        return {
            bstack1l1l1l1_opy_ (u"ࠬࡺࡹࡱࡧࠪ᜵"): bstack1l1l1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ᜶"),
            bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ᜷"): store[bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ᜸")][-1]
        }
    if store.get(bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭᜹"), None):
        return {
            bstack1l1l1l1_opy_ (u"ࠪࡸࡾࡶࡥࠨ᜺"): bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࠩ᜻"),
            bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ᜼"): store[bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ᜽")]
        }
    return None
bstack11llll1l11_opy_ = bstack1l1111llll_opy_(bstack11lllll1ll_opy_)
def pytest_runtest_call(item):
    try:
        global CONFIG
        global bstack1ll1l1l1111_opy_
        item._1ll1l1111l1_opy_ = True
        bstack1l1lllll1l_opy_ = bstack1l11lll1l_opy_.bstack1lllllll1l_opy_(bstack111ll1ll11_opy_(item.own_markers))
        item._a11y_test_case = bstack1l1lllll1l_opy_
        if bstack1ll1l1l1111_opy_:
            driver = getattr(item, bstack1l1l1l1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ᜾"), None)
            item._a11y_started = bstack1l11lll1l_opy_.bstack1ll11ll11l_opy_(driver, bstack1l1lllll1l_opy_)
        if not bstack11l1l11l1_opy_.on() or bstack1ll11llll1l_opy_ != bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ᜿"):
            return
        global current_test_uuid, bstack11llll1l11_opy_
        bstack11llll1l11_opy_.start()
        bstack11lll1l1l1_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᝀ"): uuid4().__str__(),
            bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᝁ"): bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"ࠫ࡟࠭ᝂ")
        }
        current_test_uuid = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪᝃ")]
        store[bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪᝄ")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬᝅ")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _11ll1ll1l1_opy_[item.nodeid] = {**_11ll1ll1l1_opy_[item.nodeid], **bstack11lll1l1l1_opy_}
        bstack1ll1l11l111_opy_(item, _11ll1ll1l1_opy_[item.nodeid], bstack1l1l1l1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩᝆ"))
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡦࡥࡱࡲ࠺ࠡࡽࢀࠫᝇ"), str(err))
def pytest_runtest_setup(item):
    global bstack1ll11llll11_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack1111ll1l1l_opy_():
        atexit.register(bstack1llll1ll1_opy_)
        if not bstack1ll11llll11_opy_:
            try:
                bstack1ll1l11111l_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack1111lllll1_opy_():
                    bstack1ll1l11111l_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1ll1l11111l_opy_:
                    signal.signal(s, bstack1ll1l11lll1_opy_)
                bstack1ll11llll11_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack1l1l1l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡸࡥࡨ࡫ࡶࡸࡪࡸࠠࡴ࡫ࡪࡲࡦࡲࠠࡩࡣࡱࡨࡱ࡫ࡲࡴ࠼ࠣࠦᝈ") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1llll1111l1_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫᝉ")
    try:
        if not bstack11l1l11l1_opy_.on():
            return
        bstack11llll1l11_opy_.start()
        uuid = uuid4().__str__()
        bstack11lll1l1l1_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪᝊ"): uuid,
            bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪᝋ"): bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"࡛ࠧࠩᝌ"),
            bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ᝍ"): bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧᝎ"),
            bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭ᝏ"): bstack1l1l1l1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩᝐ"),
            bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨᝑ"): bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬᝒ")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫᝓ")] = item
        store[bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ᝔")] = [uuid]
        if not _11ll1ll1l1_opy_.get(item.nodeid, None):
            _11ll1ll1l1_opy_[item.nodeid] = {bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ᝕"): [], bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡾࡴࡶࡴࡨࡷࠬ᝖"): []}
        _11ll1ll1l1_opy_[item.nodeid][bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ᝗")].append(bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪ᝘")])
        _11ll1ll1l1_opy_[item.nodeid + bstack1l1l1l1_opy_ (u"࠭࠭ࡴࡧࡷࡹࡵ࠭᝙")] = bstack11lll1l1l1_opy_
        bstack1ll1l1l1l1l_opy_(item, bstack11lll1l1l1_opy_, bstack1l1l1l1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ᝚"))
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡳࡷࡱࡸࡪࡹࡴࡠࡵࡨࡸࡺࡶ࠺ࠡࡽࢀࠫ᝛"), str(err))
def pytest_runtest_teardown(item):
    try:
        global bstack11ll11ll_opy_
        bstack1l1l1l11l_opy_ = 0
        if bstack11ll11lll_opy_ is True:
            bstack1l1l1l11l_opy_ = int(os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ᝜")))
        if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᝝"), False):
            if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡆࡥࡵࡺࡵࡳࡧࡐࡳࡩ࡫ࠧ᝞"), bstack1l1l1l1_opy_ (u"ࠧࡧࡵࡵࡱࠥ᝟")) == bstack1l1l1l1_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣᝠ"):
                bstack1ll1l11l1ll_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᝡ"), None)
                bstack1l1ll1l111_opy_ = bstack1ll1l11l1ll_opy_ + bstack1l1l1l1_opy_ (u"ࠣ࠯ࡷࡩࡸࡺࡣࡢࡵࡨࠦᝢ")
                driver = getattr(item, bstack1l1l1l1_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪᝣ"), None)
                bstack1lll1ll111_opy_ = item.get(bstack1l1l1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨᝤ")) or bstack1l1l1l1_opy_ (u"ࠫࠬᝥ")
                bstack111l111l1_opy_ = item.get(bstack1l1l1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪᝦ")) or bstack1l1l1l1_opy_ (u"࠭ࠧᝧ")
                PercySDK.screenshot(driver, bstack1l1ll1l111_opy_, bstack1lll1ll111_opy_=bstack1lll1ll111_opy_, bstack111l111l1_opy_=bstack111l111l1_opy_, bstack11l1lll11_opy_=bstack1l1l1l11l_opy_)
        if getattr(item, bstack1l1l1l1_opy_ (u"ࠧࡠࡣ࠴࠵ࡾࡥࡳࡵࡣࡵࡸࡪࡪࠧᝨ"), False):
            bstack111ll1l1_opy_.bstack1l1l11l1l_opy_(getattr(item, bstack1l1l1l1_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩᝩ"), None), bstack11ll11ll_opy_, logger, item)
        if not bstack11l1l11l1_opy_.on():
            return
        bstack11lll1l1l1_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᝪ"): uuid4().__str__(),
            bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᝫ"): bstack11llll11l1_opy_().isoformat() + bstack1l1l1l1_opy_ (u"ࠫ࡟࠭ᝬ"),
            bstack1l1l1l1_opy_ (u"ࠬࡺࡹࡱࡧࠪ᝭"): bstack1l1l1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫᝮ"),
            bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪᝯ"): bstack1l1l1l1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬᝰ"),
            bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟࡯ࡣࡰࡩࠬ᝱"): bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬᝲ")
        }
        _11ll1ll1l1_opy_[item.nodeid + bstack1l1l1l1_opy_ (u"ࠫ࠲ࡺࡥࡢࡴࡧࡳࡼࡴࠧᝳ")] = bstack11lll1l1l1_opy_
        bstack1ll1l1l1l1l_opy_(item, bstack11lll1l1l1_opy_, bstack1l1l1l1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭᝴"))
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡸࡵ࡯ࡶࡨࡷࡹࡥࡴࡦࡣࡵࡨࡴࡽ࡮࠻ࠢࡾࢁࠬ᝵"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if not bstack11l1l11l1_opy_.on():
        yield
        return
    start_time = datetime.datetime.now()
    if bstack1lll1llllll_opy_(fixturedef.argname):
        store[bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠ࡯ࡲࡨࡺࡲࡥࡠ࡫ࡷࡩࡲ࠭᝶")] = request.node
    elif bstack1lll1lll111_opy_(fixturedef.argname):
        store[bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡦࡰࡦࡹࡳࡠ࡫ࡷࡩࡲ࠭᝷")] = request.node
    outcome = yield
    try:
        fixture = {
            bstack1l1l1l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ᝸"): fixturedef.argname,
            bstack1l1l1l1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ᝹"): bstack111l11ll1l_opy_(outcome),
            bstack1l1l1l1_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭᝺"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ᝻")]
        if not _11ll1ll1l1_opy_.get(current_test_item.nodeid, None):
            _11ll1ll1l1_opy_[current_test_item.nodeid] = {bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ᝼"): []}
        _11ll1ll1l1_opy_[current_test_item.nodeid][bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡻࡸࡺࡸࡥࡴࠩ᝽")].append(fixture)
    except Exception as err:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡵࡨࡸࡺࡶ࠺ࠡࡽࢀࠫ᝾"), str(err))
if bstack1llll1111_opy_() and bstack11l1l11l1_opy_.on():
    def pytest_bdd_before_step(request, step):
        try:
            _11ll1ll1l1_opy_[request.node.nodeid][bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ᝿")].bstack1lll1l11111_opy_(id(step))
        except Exception as err:
            print(bstack1l1l1l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳ࠾ࠥࢁࡽࠨក"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        try:
            _11ll1ll1l1_opy_[request.node.nodeid][bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧខ")].bstack1l111l111l_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack1l1l1l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡵࡷࡩࡵࡥࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠩគ"), str(err))
    def pytest_bdd_after_step(request, step):
        try:
            bstack1l111l11l1_opy_: bstack11llll1lll_opy_ = _11ll1ll1l1_opy_[request.node.nodeid][bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩឃ")]
            bstack1l111l11l1_opy_.bstack1l111l111l_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack1l1l1l1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡷࡹ࡫ࡰࡠࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫង"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1ll11llll1l_opy_
        try:
            if not bstack11l1l11l1_opy_.on() or bstack1ll11llll1l_opy_ != bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠬច"):
                return
            global bstack11llll1l11_opy_
            bstack11llll1l11_opy_.start()
            driver = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨឆ"), None)
            if not _11ll1ll1l1_opy_.get(request.node.nodeid, None):
                _11ll1ll1l1_opy_[request.node.nodeid] = {}
            bstack1l111l11l1_opy_ = bstack11llll1lll_opy_.bstack1lll111llll_opy_(
                scenario, feature, request.node,
                name=bstack1llll11111l_opy_(request.node, scenario),
                bstack11lll1llll_opy_=bstack1ll1l11lll_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack1l1l1l1_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶ࠰ࡧࡺࡩࡵ࡮ࡤࡨࡶࠬជ"),
                tags=bstack1lll1ll1lll_opy_(feature, scenario),
                bstack11llll111l_opy_=bstack11l1l11l1_opy_.bstack1l111l1111_opy_(driver) if driver and driver.session_id else {}
            )
            _11ll1ll1l1_opy_[request.node.nodeid][bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧឈ")] = bstack1l111l11l1_opy_
            bstack1ll1l11l1l1_opy_(bstack1l111l11l1_opy_.uuid)
            bstack11l1l11l1_opy_.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ញ"), bstack1l111l11l1_opy_)
        except Exception as err:
            print(bstack1l1l1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲ࠾ࠥࢁࡽࠨដ"), str(err))
def bstack1ll11lll1ll_opy_(bstack1ll11llllll_opy_):
    if bstack1ll11llllll_opy_ in store[bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫឋ")]:
        store[bstack1l1l1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬឌ")].remove(bstack1ll11llllll_opy_)
def bstack1ll1l11l1l1_opy_(bstack1ll1l11ll11_opy_):
    store[bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭ឍ")] = bstack1ll1l11ll11_opy_
    threading.current_thread().current_test_uuid = bstack1ll1l11ll11_opy_
@bstack11l1l11l1_opy_.bstack1lll11111ll_opy_
def bstack1ll1l1111ll_opy_(item, call, report):
    global bstack1ll11llll1l_opy_
    bstack1111lll1l_opy_ = bstack1ll1l11lll_opy_()
    if hasattr(report, bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡵࡰࠨណ")):
        bstack1111lll1l_opy_ = bstack111l1l1111_opy_(report.stop)
    elif hasattr(report, bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࠪត")):
        bstack1111lll1l_opy_ = bstack111l1l1111_opy_(report.start)
    try:
        if getattr(report, bstack1l1l1l1_opy_ (u"ࠬࡽࡨࡦࡰࠪថ"), bstack1l1l1l1_opy_ (u"࠭ࠧទ")) == bstack1l1l1l1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬធ"):
            bstack11llll1l11_opy_.reset()
        if getattr(report, bstack1l1l1l1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭ន"), bstack1l1l1l1_opy_ (u"ࠩࠪប")) == bstack1l1l1l1_opy_ (u"ࠪࡧࡦࡲ࡬ࠨផ"):
            if bstack1ll11llll1l_opy_ == bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫព"):
                _11ll1ll1l1_opy_[item.nodeid][bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪភ")] = bstack1111lll1l_opy_
                bstack1ll1l11l111_opy_(item, _11ll1ll1l1_opy_[item.nodeid], bstack1l1l1l1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨម"), report, call)
                store[bstack1l1l1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫយ")] = None
            elif bstack1ll11llll1l_opy_ == bstack1l1l1l1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧរ"):
                bstack1l111l11l1_opy_ = _11ll1ll1l1_opy_[item.nodeid][bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬល")]
                bstack1l111l11l1_opy_.set(hooks=_11ll1ll1l1_opy_[item.nodeid].get(bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩវ"), []))
                exception, bstack1l1111ll11_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack1l1111ll11_opy_ = [call.excinfo.exconly(), getattr(report, bstack1l1l1l1_opy_ (u"ࠫࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠪឝ"), bstack1l1l1l1_opy_ (u"ࠬ࠭ឞ"))]
                bstack1l111l11l1_opy_.stop(time=bstack1111lll1l_opy_, result=Result(result=getattr(report, bstack1l1l1l1_opy_ (u"࠭࡯ࡶࡶࡦࡳࡲ࡫ࠧស"), bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧហ")), exception=exception, bstack1l1111ll11_opy_=bstack1l1111ll11_opy_))
                bstack11l1l11l1_opy_.bstack11lll11l1l_opy_(bstack1l1l1l1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪឡ"), _11ll1ll1l1_opy_[item.nodeid][bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬអ")])
        elif getattr(report, bstack1l1l1l1_opy_ (u"ࠪࡻ࡭࡫࡮ࠨឣ"), bstack1l1l1l1_opy_ (u"ࠫࠬឤ")) in [bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫឥ"), bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨឦ")]:
            bstack11llll1l1l_opy_ = item.nodeid + bstack1l1l1l1_opy_ (u"ࠧ࠮ࠩឧ") + getattr(report, bstack1l1l1l1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭ឨ"), bstack1l1l1l1_opy_ (u"ࠩࠪឩ"))
            if getattr(report, bstack1l1l1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫឪ"), False):
                hook_type = bstack1l1l1l1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩឫ") if getattr(report, bstack1l1l1l1_opy_ (u"ࠬࡽࡨࡦࡰࠪឬ"), bstack1l1l1l1_opy_ (u"࠭ࠧឭ")) == bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ឮ") else bstack1l1l1l1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬឯ")
                _11ll1ll1l1_opy_[bstack11llll1l1l_opy_] = {
                    bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧឰ"): uuid4().__str__(),
                    bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧឱ"): bstack1111lll1l_opy_,
                    bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧឲ"): hook_type
                }
            _11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪឳ")] = bstack1111lll1l_opy_
            bstack1ll11lll1ll_opy_(_11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ឴")])
            bstack1ll1l1l1l1l_opy_(item, _11ll1ll1l1_opy_[bstack11llll1l1l_opy_], bstack1l1l1l1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ឵"), report, call)
            if getattr(report, bstack1l1l1l1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭ា"), bstack1l1l1l1_opy_ (u"ࠩࠪិ")) == bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩី"):
                if getattr(report, bstack1l1l1l1_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬឹ"), bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬឺ")) == bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ុ"):
                    bstack11lll1l1l1_opy_ = {
                        bstack1l1l1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬូ"): uuid4().__str__(),
                        bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬួ"): bstack1ll1l11lll_opy_(),
                        bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧើ"): bstack1ll1l11lll_opy_()
                    }
                    _11ll1ll1l1_opy_[item.nodeid] = {**_11ll1ll1l1_opy_[item.nodeid], **bstack11lll1l1l1_opy_}
                    bstack1ll1l11l111_opy_(item, _11ll1ll1l1_opy_[item.nodeid], bstack1l1l1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫឿ"))
                    bstack1ll1l11l111_opy_(item, _11ll1ll1l1_opy_[item.nodeid], bstack1l1l1l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ៀ"), report, call)
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡼࡿࠪេ"), str(err))
def bstack1ll1l11ll1l_opy_(test, bstack11lll1l1l1_opy_, result=None, call=None, bstack1ll111l1l1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack1l111l11l1_opy_ = {
        bstack1l1l1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫែ"): bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬៃ")],
        bstack1l1l1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭ោ"): bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺࠧៅ"),
        bstack1l1l1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨំ"): test.name,
        bstack1l1l1l1_opy_ (u"ࠫࡧࡵࡤࡺࠩះ"): {
            bstack1l1l1l1_opy_ (u"ࠬࡲࡡ࡯ࡩࠪៈ"): bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭៉"),
            bstack1l1l1l1_opy_ (u"ࠧࡤࡱࡧࡩࠬ៊"): inspect.getsource(test.obj)
        },
        bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ់"): test.name,
        bstack1l1l1l1_opy_ (u"ࠩࡶࡧࡴࡶࡥࠨ៌"): test.name,
        bstack1l1l1l1_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ៍"): bstack1ll11l1lll_opy_.bstack11ll1ll11l_opy_(test),
        bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ៎"): file_path,
        bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧ៏"): file_path,
        bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭័"): bstack1l1l1l1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ៑"),
        bstack1l1l1l1_opy_ (u"ࠨࡸࡦࡣ࡫࡯࡬ࡦࡲࡤࡸ࡭្࠭"): file_path,
        bstack1l1l1l1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭៓"): bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ។")],
        bstack1l1l1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ៕"): bstack1l1l1l1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ៖"),
        bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡘࡥࡳࡷࡱࡔࡦࡸࡡ࡮ࠩៗ"): {
            bstack1l1l1l1_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥ࡮ࡢ࡯ࡨࠫ៘"): test.nodeid
        },
        bstack1l1l1l1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭៙"): bstack111ll1ll11_opy_(test.own_markers)
    }
    if bstack1ll111l1l1_opy_ in [bstack1l1l1l1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ៚"), bstack1l1l1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ៛")]:
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡲ࡫ࡴࡢࠩៜ")] = {
            bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ៝"): bstack11lll1l1l1_opy_.get(bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ៞"), [])
        }
    if bstack1ll111l1l1_opy_ == bstack1l1l1l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨ៟"):
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ០")] = bstack1l1l1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ១")
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ២")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ៣")]
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ៤")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ៥")]
    if result:
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ៦")] = result.outcome
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ៧")] = result.duration * 1000
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ៨")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ៩")]
        if result.failed:
            bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ៪")] = bstack11l1l11l1_opy_.bstack11ll1111l1_opy_(call.excinfo.typename)
            bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭៫")] = bstack11l1l11l1_opy_.bstack1lll111111l_opy_(call.excinfo, result)
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ៬")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭៭")]
    if outcome:
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ៮")] = bstack111l11ll1l_opy_(outcome)
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ៯")] = 0
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ៰")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ៱")]
        if bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ៲")] == bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭៳"):
            bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭៴")] = bstack1l1l1l1_opy_ (u"ࠨࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠩ៵")  # bstack1ll1l1l11l1_opy_
            bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ៶")] = [{bstack1l1l1l1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭៷"): [bstack1l1l1l1_opy_ (u"ࠫࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠨ៸")]}]
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ៹")] = bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ៺")]
    return bstack1l111l11l1_opy_
def bstack1ll1l1lll1l_opy_(test, bstack1l1111l1ll_opy_, bstack1ll111l1l1_opy_, result, call, outcome, bstack1ll1l1ll111_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ៻")]
    hook_name = bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ៼")]
    hook_data = {
        bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ៽"): bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ៾")],
        bstack1l1l1l1_opy_ (u"ࠫࡹࡿࡰࡦࠩ៿"): bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ᠀"),
        bstack1l1l1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ᠁"): bstack1l1l1l1_opy_ (u"ࠧࡼࡿࠪ᠂").format(bstack1lll1ll1ll1_opy_(hook_name)),
        bstack1l1l1l1_opy_ (u"ࠨࡤࡲࡨࡾ࠭᠃"): {
            bstack1l1l1l1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ᠄"): bstack1l1l1l1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ᠅"),
            bstack1l1l1l1_opy_ (u"ࠫࡨࡵࡤࡦࠩ᠆"): None
        },
        bstack1l1l1l1_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫ᠇"): test.name,
        bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭᠈"): bstack1ll11l1lll_opy_.bstack11ll1ll11l_opy_(test, hook_name),
        bstack1l1l1l1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ᠉"): file_path,
        bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ᠊"): file_path,
        bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ᠋"): bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ᠌"),
        bstack1l1l1l1_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩ᠍"): file_path,
        bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ᠎"): bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ᠏")],
        bstack1l1l1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ᠐"): bstack1l1l1l1_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ᠑") if bstack1ll11llll1l_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭᠒") else bstack1l1l1l1_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶࠪ᠓"),
        bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ᠔"): hook_type
    }
    bstack1ll1l11llll_opy_ = bstack11ll1ll111_opy_(_11ll1ll1l1_opy_.get(test.nodeid, None))
    if bstack1ll1l11llll_opy_:
        hook_data[bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡪࡦࠪ᠕")] = bstack1ll1l11llll_opy_
    if result:
        hook_data[bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭᠖")] = result.outcome
        hook_data[bstack1l1l1l1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨ᠗")] = result.duration * 1000
        hook_data[bstack1l1l1l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭᠘")] = bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ᠙")]
        if result.failed:
            hook_data[bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ᠚")] = bstack11l1l11l1_opy_.bstack11ll1111l1_opy_(call.excinfo.typename)
            hook_data[bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ᠛")] = bstack11l1l11l1_opy_.bstack1lll111111l_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ᠜")] = bstack111l11ll1l_opy_(outcome)
        hook_data[bstack1l1l1l1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ᠝")] = 100
        hook_data[bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ᠞")] = bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭᠟")]
        if hook_data[bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᠠ")] == bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᠡ"):
            hook_data[bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪᠢ")] = bstack1l1l1l1_opy_ (u"࡛ࠬ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷ࠭ᠣ")  # bstack1ll1l1l11l1_opy_
            hook_data[bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧᠤ")] = [{bstack1l1l1l1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪᠥ"): [bstack1l1l1l1_opy_ (u"ࠨࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠬᠦ")]}]
    if bstack1ll1l1ll111_opy_:
        hook_data[bstack1l1l1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᠧ")] = bstack1ll1l1ll111_opy_.result
        hook_data[bstack1l1l1l1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫᠨ")] = bstack111ll1llll_opy_(bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨᠩ")], bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᠪ")])
        hook_data[bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫᠫ")] = bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᠬ")]
        if hook_data[bstack1l1l1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨᠭ")] == bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᠮ"):
            hook_data[bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩᠯ")] = bstack11l1l11l1_opy_.bstack11ll1111l1_opy_(bstack1ll1l1ll111_opy_.exception_type)
            hook_data[bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬᠰ")] = [{bstack1l1l1l1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨᠱ"): bstack111lll11ll_opy_(bstack1ll1l1ll111_opy_.exception)}]
    return hook_data
def bstack1ll1l11l111_opy_(test, bstack11lll1l1l1_opy_, bstack1ll111l1l1_opy_, result=None, call=None, outcome=None):
    bstack1l111l11l1_opy_ = bstack1ll1l11ll1l_opy_(test, bstack11lll1l1l1_opy_, result, call, bstack1ll111l1l1_opy_, outcome)
    driver = getattr(test, bstack1l1l1l1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧᠲ"), None)
    if bstack1ll111l1l1_opy_ == bstack1l1l1l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨᠳ") and driver:
        bstack1l111l11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡸࡪ࡭ࡲࡢࡶ࡬ࡳࡳࡹࠧᠴ")] = bstack11l1l11l1_opy_.bstack1l111l1111_opy_(driver)
    if bstack1ll111l1l1_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪᠵ"):
        bstack1ll111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬᠶ")
    bstack11llllllll_opy_ = {
        bstack1l1l1l1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨᠷ"): bstack1ll111l1l1_opy_,
        bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧᠸ"): bstack1l111l11l1_opy_
    }
    bstack11l1l11l1_opy_.bstack11ll1llll1_opy_(bstack11llllllll_opy_)
def bstack1ll1l1l1l1l_opy_(test, bstack11lll1l1l1_opy_, bstack1ll111l1l1_opy_, result=None, call=None, outcome=None, bstack1ll1l1ll111_opy_=None):
    hook_data = bstack1ll1l1lll1l_opy_(test, bstack11lll1l1l1_opy_, bstack1ll111l1l1_opy_, result, call, outcome, bstack1ll1l1ll111_opy_)
    bstack11llllllll_opy_ = {
        bstack1l1l1l1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪᠹ"): bstack1ll111l1l1_opy_,
        bstack1l1l1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࠩᠺ"): hook_data
    }
    bstack11l1l11l1_opy_.bstack11ll1llll1_opy_(bstack11llllllll_opy_)
def bstack11ll1ll111_opy_(bstack11lll1l1l1_opy_):
    if not bstack11lll1l1l1_opy_:
        return None
    if bstack11lll1l1l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫᠻ"), None):
        return getattr(bstack11lll1l1l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬᠼ")], bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᠽ"), None)
    return bstack11lll1l1l1_opy_.get(bstack1l1l1l1_opy_ (u"ࠫࡺࡻࡩࡥࠩᠾ"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    yield
    try:
        if not bstack11l1l11l1_opy_.on():
            return
        places = [bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫᠿ"), bstack1l1l1l1_opy_ (u"࠭ࡣࡢ࡮࡯ࠫᡀ"), bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩᡁ")]
        bstack1l1111111l_opy_ = []
        for bstack1ll1l1ll1ll_opy_ in places:
            records = caplog.get_records(bstack1ll1l1ll1ll_opy_)
            bstack1ll1l1l11ll_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᡂ") if bstack1ll1l1ll1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡦࡥࡱࡲࠧᡃ") else bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᡄ")
            bstack1ll11lllll1_opy_ = request.node.nodeid + (bstack1l1l1l1_opy_ (u"ࠫࠬᡅ") if bstack1ll1l1ll1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠬࡩࡡ࡭࡮ࠪᡆ") else bstack1l1l1l1_opy_ (u"࠭࠭ࠨᡇ") + bstack1ll1l1ll1ll_opy_)
            bstack1ll1l11ll11_opy_ = bstack11ll1ll111_opy_(_11ll1ll1l1_opy_.get(bstack1ll11lllll1_opy_, None))
            if not bstack1ll1l11ll11_opy_:
                continue
            for record in records:
                if bstack111l1l1l11_opy_(record.message):
                    continue
                bstack1l1111111l_opy_.append({
                    bstack1l1l1l1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪᡈ"): bstack111l111l11_opy_(record.created).isoformat() + bstack1l1l1l1_opy_ (u"ࠨ࡜ࠪᡉ"),
                    bstack1l1l1l1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨᡊ"): record.levelname,
                    bstack1l1l1l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᡋ"): record.message,
                    bstack1ll1l1l11ll_opy_: bstack1ll1l11ll11_opy_
                })
        if len(bstack1l1111111l_opy_) > 0:
            bstack11l1l11l1_opy_.bstack1ll1l1111l_opy_(bstack1l1111111l_opy_)
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡪࡩ࡯࡯ࡦࡢࡪ࡮ࡾࡴࡶࡴࡨ࠾ࠥࢁࡽࠨᡌ"), str(err))
def bstack1l1111ll1_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack111lll11_opy_
    bstack1l1l11l111_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬ࡯ࡳࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩᡍ"), None) and bstack1l111l1ll1_opy_(
            threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬᡎ"), None)
    bstack1l11l111_opy_ = getattr(driver, bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧᡏ"), None) != None and getattr(driver, bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨᡐ"), None) == True
    if sequence == bstack1l1l1l1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩᡑ") and driver != None:
      if not bstack111lll11_opy_ and bstack111lll1l11_opy_() and bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᡒ") in CONFIG and CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᡓ")] == True and bstack1ll1ll1l11_opy_.bstack1l1l11l11l_opy_(driver_command) and (bstack1l11l111_opy_ or bstack1l1l11l111_opy_) and not bstack111l11ll_opy_(args):
        try:
          bstack111lll11_opy_ = True
          logger.debug(bstack1l1l1l1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧᡔ").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡩࡷ࡬࡯ࡳ࡯ࠣࡷࡨࡧ࡮ࠡࡽࢀࠫᡕ").format(str(err)))
        bstack111lll11_opy_ = False
    if sequence == bstack1l1l1l1_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᡖ"):
        if driver_command == bstack1l1l1l1_opy_ (u"ࠨࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠬᡗ"):
            bstack11l1l11l1_opy_.bstack1ll1lllll1_opy_({
                bstack1l1l1l1_opy_ (u"ࠩ࡬ࡱࡦ࡭ࡥࠨᡘ"): response[bstack1l1l1l1_opy_ (u"ࠪࡺࡦࡲࡵࡦࠩᡙ")],
                bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᡚ"): store[bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩᡛ")]
            })
def bstack1llll1ll1_opy_():
    global bstack1ll111111_opy_
    bstack1lll1111ll_opy_.bstack11l1l11ll_opy_()
    logging.shutdown()
    bstack11l1l11l1_opy_.bstack11lll1l11l_opy_()
    for driver in bstack1ll111111_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1ll1l11lll1_opy_(*args):
    global bstack1ll111111_opy_
    bstack11l1l11l1_opy_.bstack11lll1l11l_opy_()
    for driver in bstack1ll111111_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack11ll1ll1_opy_(self, *args, **kwargs):
    bstack1ll1lll11_opy_ = bstack11l11l1l_opy_(self, *args, **kwargs)
    bstack11l1l11l1_opy_.bstack1111l111l_opy_(self)
    return bstack1ll1lll11_opy_
def bstack11l11lll1_opy_(framework_name):
    global bstack111lll1ll_opy_
    global bstack1ll1ll111l_opy_
    bstack111lll1ll_opy_ = framework_name
    logger.info(bstack1ll11l11ll_opy_.format(bstack111lll1ll_opy_.split(bstack1l1l1l1_opy_ (u"࠭࠭ࠨᡜ"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack111lll1l11_opy_():
            Service.start = bstack11llllll_opy_
            Service.stop = bstack1lllll11l_opy_
            webdriver.Remote.__init__ = bstack1l11ll1l_opy_
            webdriver.Remote.get = bstack1l11l11l1l_opy_
            if not isinstance(os.getenv(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡂࡔࡄࡐࡑࡋࡌࠨᡝ")), str):
                return
            WebDriver.close = bstack1ll11l1ll1_opy_
            WebDriver.quit = bstack1111ll1ll_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        if not bstack111lll1l11_opy_() and bstack11l1l11l1_opy_.on():
            webdriver.Remote.__init__ = bstack11ll1ll1_opy_
        bstack1ll1ll111l_opy_ = True
    except Exception as e:
        pass
    bstack1ll1lllll_opy_()
    if os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡕࡈࡐࡊࡔࡉࡖࡏࡢࡓࡗࡥࡐࡍࡃ࡜࡛ࡗࡏࡇࡉࡖࡢࡍࡓ࡙ࡔࡂࡎࡏࡉࡉ࠭ᡞ")):
        bstack1ll1ll111l_opy_ = eval(os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧᡟ")))
    if not bstack1ll1ll111l_opy_:
        bstack1lll11ll_opy_(bstack1l1l1l1_opy_ (u"ࠥࡔࡦࡩ࡫ࡢࡩࡨࡷࠥࡴ࡯ࡵࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠧᡠ"), bstack1l11ll111l_opy_)
    if bstack1l1l1l1ll1_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            RemoteConnection._get_proxy_url = bstack1ll11111ll_opy_
        except Exception as e:
            logger.error(bstack1ll1lll1l1_opy_.format(str(e)))
    if bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᡡ") in str(framework_name).lower():
        if not bstack111lll1l11_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack11lll1ll1_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1111l1ll_opy_
            Config.getoption = bstack1l111lll_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l1l1lll_opy_
        except Exception as e:
            pass
def bstack1111ll1ll_opy_(self):
    global bstack111lll1ll_opy_
    global bstack11ll1l1l_opy_
    global bstack1l11ll11_opy_
    try:
        if bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬᡢ") in bstack111lll1ll_opy_ and self.session_id != None and bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡗࡹࡧࡴࡶࡵࠪᡣ"), bstack1l1l1l1_opy_ (u"ࠧࠨᡤ")) != bstack1l1l1l1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩᡥ"):
            bstack1l1ll1ll1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᡦ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᡧ")
            bstack11ll1l1ll_opy_(logger, True)
            if self != None:
                bstack1l1l1lll11_opy_(self, bstack1l1ll1ll1_opy_, bstack1l1l1l1_opy_ (u"ࠫ࠱ࠦࠧᡨ").join(threading.current_thread().bstackTestErrorMessages))
        item = store.get(bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩᡩ"), None)
        if item is not None and bstack1ll1l1l1111_opy_:
            bstack111ll1l1_opy_.bstack1l1l11l1l_opy_(self, bstack11ll11ll_opy_, logger, item)
        threading.current_thread().testStatus = bstack1l1l1l1_opy_ (u"࠭ࠧᡪ")
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡳࡡࡳ࡭࡬ࡲ࡬ࠦࡳࡵࡣࡷࡹࡸࡀࠠࠣᡫ") + str(e))
    bstack1l11ll11_opy_(self)
    self.session_id = None
def bstack1l11ll1l_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack11ll1l1l_opy_
    global bstack11l1l11l_opy_
    global bstack11ll11lll_opy_
    global bstack111lll1ll_opy_
    global bstack11l11l1l_opy_
    global bstack1ll111111_opy_
    global bstack1ll11l11l1_opy_
    global bstack1ll1lll111_opy_
    global bstack1ll1l1l1111_opy_
    global bstack11ll11ll_opy_
    CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᡬ")] = str(bstack111lll1ll_opy_) + str(__version__)
    command_executor = bstack11lll1l1_opy_(bstack1ll11l11l1_opy_)
    logger.debug(bstack1ll11ll1l1_opy_.format(command_executor))
    proxy = bstack1ll11l1l_opy_(CONFIG, proxy)
    bstack1l1l1l11l_opy_ = 0
    try:
        if bstack11ll11lll_opy_ is True:
            bstack1l1l1l11l_opy_ = int(os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩᡭ")))
    except:
        bstack1l1l1l11l_opy_ = 0
    bstack1l11lllll_opy_ = bstack111lll11l_opy_(CONFIG, bstack1l1l1l11l_opy_)
    logger.debug(bstack1l1lll1111_opy_.format(str(bstack1l11lllll_opy_)))
    bstack11ll11ll_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᡮ"))[bstack1l1l1l11l_opy_]
    if bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨᡯ") in CONFIG and CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩᡰ")]:
        bstack1l111llll_opy_(bstack1l11lllll_opy_, bstack1ll1lll111_opy_)
    if bstack1l11lll1l_opy_.bstack1ll1llllll_opy_(CONFIG, bstack1l1l1l11l_opy_) and bstack1l11lll1l_opy_.bstack1ll1lll1l_opy_(bstack1l11lllll_opy_, options, desired_capabilities):
        bstack1ll1l1l1111_opy_ = True
        bstack1l11lll1l_opy_.set_capabilities(bstack1l11lllll_opy_, CONFIG)
    if desired_capabilities:
        bstack1l11llll_opy_ = bstack1ll111llll_opy_(desired_capabilities)
        bstack1l11llll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᡱ")] = bstack1l11lll11_opy_(CONFIG)
        bstack1l1111l1l_opy_ = bstack111lll11l_opy_(bstack1l11llll_opy_)
        if bstack1l1111l1l_opy_:
            bstack1l11lllll_opy_ = update(bstack1l1111l1l_opy_, bstack1l11lllll_opy_)
        desired_capabilities = None
    if options:
        bstack1l1l111ll_opy_(options, bstack1l11lllll_opy_)
    if not options:
        options = bstack1lll11lll_opy_(bstack1l11lllll_opy_)
    if proxy and bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧᡲ")):
        options.proxy(proxy)
    if options and bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧᡳ")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1l1l1111_opy_() < version.parse(bstack1l1l1l1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᡴ")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack1l11lllll_opy_)
    logger.info(bstack1llllll111_opy_)
    if bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠪ࠸࠳࠷࠰࠯࠲ࠪᡵ")):
        bstack11l11l1l_opy_(self, command_executor=command_executor,
                  options=options, keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪᡶ")):
        bstack11l11l1l_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities, options=options,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠬ࠸࠮࠶࠵࠱࠴ࠬᡷ")):
        bstack11l11l1l_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    else:
        bstack11l11l1l_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  browser_profile=browser_profile, proxy=proxy,
                  keep_alive=keep_alive)
    try:
        bstack1llll1lll_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠧᡸ")
        if bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠧ࠵࠰࠳࠲࠵ࡨ࠱ࠨ᡹")):
            bstack1llll1lll_opy_ = self.caps.get(bstack1l1l1l1_opy_ (u"ࠣࡱࡳࡸ࡮ࡳࡡ࡭ࡊࡸࡦ࡚ࡸ࡬ࠣ᡺"))
        else:
            bstack1llll1lll_opy_ = self.capabilities.get(bstack1l1l1l1_opy_ (u"ࠤࡲࡴࡹ࡯࡭ࡢ࡮ࡋࡹࡧ࡛ࡲ࡭ࠤ᡻"))
        if bstack1llll1lll_opy_:
            bstack111l1111_opy_(bstack1llll1lll_opy_)
            if bstack1l1l1111_opy_() <= version.parse(bstack1l1l1l1_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪ᡼")):
                self.command_executor._url = bstack1l1l1l1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧ᡽") + bstack1ll11l11l1_opy_ + bstack1l1l1l1_opy_ (u"ࠧࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠤ᡾")
            else:
                self.command_executor._url = bstack1l1l1l1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣ᡿") + bstack1llll1lll_opy_ + bstack1l1l1l1_opy_ (u"ࠢ࠰ࡹࡧ࠳࡭ࡻࡢࠣᢀ")
            logger.debug(bstack1ll1l1111_opy_.format(bstack1llll1lll_opy_))
        else:
            logger.debug(bstack11l11111_opy_.format(bstack1l1l1l1_opy_ (u"ࠣࡑࡳࡸ࡮ࡳࡡ࡭ࠢࡋࡹࡧࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠤᢁ")))
    except Exception as e:
        logger.debug(bstack11l11111_opy_.format(e))
    bstack11ll1l1l_opy_ = self.session_id
    if bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩᢂ") in bstack111lll1ll_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack1l1l1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧᢃ"), None)
        if item:
            bstack1ll1l1l1lll_opy_ = getattr(item, bstack1l1l1l1_opy_ (u"ࠫࡤࡺࡥࡴࡶࡢࡧࡦࡹࡥࡠࡵࡷࡥࡷࡺࡥࡥࠩᢄ"), False)
            if not getattr(item, bstack1l1l1l1_opy_ (u"ࠬࡥࡤࡳ࡫ࡹࡩࡷ࠭ᢅ"), None) and bstack1ll1l1l1lll_opy_:
                setattr(store[bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪᢆ")], bstack1l1l1l1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨᢇ"), self)
        bstack11l1l11l1_opy_.bstack1111l111l_opy_(self)
    bstack1ll111111_opy_.append(self)
    if bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᢈ") in CONFIG and bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᢉ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᢊ")][bstack1l1l1l11l_opy_]:
        bstack11l1l11l_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᢋ")][bstack1l1l1l11l_opy_][bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᢌ")]
    logger.debug(bstack11l111111_opy_.format(bstack11ll1l1l_opy_))
def bstack1l11l11l1l_opy_(self, url):
    global bstack1llll11l1_opy_
    global CONFIG
    try:
        bstack1l1l11l11_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack111ll1lll_opy_.format(str(err)))
    try:
        bstack1llll11l1_opy_(self, url)
    except Exception as e:
        try:
            bstack11l1lllll_opy_ = str(e)
            if any(err_msg in bstack11l1lllll_opy_ for err_msg in bstack1l1llll1l1_opy_):
                bstack1l1l11l11_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack111ll1lll_opy_.format(str(err)))
        raise e
def bstack1l11ll1111_opy_(item, when):
    global bstack11l1lll1l_opy_
    try:
        bstack11l1lll1l_opy_(item, when)
    except Exception as e:
        pass
def bstack1l1l1lll_opy_(item, call, rep):
    global bstack1ll1l1ll11_opy_
    global bstack1ll111111_opy_
    name = bstack1l1l1l1_opy_ (u"࠭ࠧᢍ")
    try:
        if rep.when == bstack1l1l1l1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬᢎ"):
            bstack11ll1l1l_opy_ = threading.current_thread().bstackSessionId
            bstack1ll1l1l1ll1_opy_ = item.config.getoption(bstack1l1l1l1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᢏ"))
            try:
                if (str(bstack1ll1l1l1ll1_opy_).lower() != bstack1l1l1l1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧᢐ")):
                    name = str(rep.nodeid)
                    bstack1l11l1ll11_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫᢑ"), name, bstack1l1l1l1_opy_ (u"ࠫࠬᢒ"), bstack1l1l1l1_opy_ (u"ࠬ࠭ᢓ"), bstack1l1l1l1_opy_ (u"࠭ࠧᢔ"), bstack1l1l1l1_opy_ (u"ࠧࠨᢕ"))
                    os.environ[bstack1l1l1l1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫᢖ")] = name
                    for driver in bstack1ll111111_opy_:
                        if bstack11ll1l1l_opy_ == driver.session_id:
                            driver.execute_script(bstack1l11l1ll11_opy_)
            except Exception as e:
                logger.debug(bstack1l1l1l1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩᢗ").format(str(e)))
            try:
                bstack1ll1l1lll_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack1l1l1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫᢘ"):
                    status = bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᢙ") if rep.outcome.lower() == bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᢚ") else bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᢛ")
                    reason = bstack1l1l1l1_opy_ (u"ࠧࠨᢜ")
                    if status == bstack1l1l1l1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᢝ"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack1l1l1l1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧᢞ") if status == bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᢟ") else bstack1l1l1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᢠ")
                    data = name + bstack1l1l1l1_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧᢡ") if status == bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᢢ") else name + bstack1l1l1l1_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠢࠢࠪᢣ") + reason
                    bstack11l1111l1_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪᢤ"), bstack1l1l1l1_opy_ (u"ࠩࠪᢥ"), bstack1l1l1l1_opy_ (u"ࠪࠫᢦ"), bstack1l1l1l1_opy_ (u"ࠫࠬᢧ"), level, data)
                    for driver in bstack1ll111111_opy_:
                        if bstack11ll1l1l_opy_ == driver.session_id:
                            driver.execute_script(bstack11l1111l1_opy_)
            except Exception as e:
                logger.debug(bstack1l1l1l1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡳࡳࡺࡥࡹࡶࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩᢨ").format(str(e)))
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼࡿᢩࠪ").format(str(e)))
    bstack1ll1l1ll11_opy_(item, call, rep)
notset = Notset()
def bstack1l111lll_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack1l1llll1l_opy_
    if str(name).lower() == bstack1l1l1l1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧᢪ"):
        return bstack1l1l1l1_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢ᢫")
    else:
        return bstack1l1llll1l_opy_(self, name, default, skip)
def bstack1ll11111ll_opy_(self):
    global CONFIG
    global bstack1l1ll1ll1l_opy_
    try:
        proxy = bstack111l1ll1_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack1l1l1l1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ᢬")):
                proxies = bstack1l1l1lll1_opy_(proxy, bstack11lll1l1_opy_())
                if len(proxies) > 0:
                    protocol, bstack1ll1ll1ll1_opy_ = proxies.popitem()
                    if bstack1l1l1l1_opy_ (u"ࠥ࠾࠴࠵ࠢ᢭") in bstack1ll1ll1ll1_opy_:
                        return bstack1ll1ll1ll1_opy_
                    else:
                        return bstack1l1l1l1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧ᢮") + bstack1ll1ll1ll1_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack1l1l1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡲࡵࡳࡽࡿࠠࡶࡴ࡯ࠤ࠿ࠦࡻࡾࠤ᢯").format(str(e)))
    return bstack1l1ll1ll1l_opy_(self)
def bstack1l1l1l1ll1_opy_():
    return (bstack1l1l1l1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᢰ") in CONFIG or bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫᢱ") in CONFIG) and bstack1lll11llll_opy_() and bstack1l1l1111_opy_() >= version.parse(
        bstack1l11ll11ll_opy_)
def bstack1l1lll111_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack11l1l11l_opy_
    global bstack11ll11lll_opy_
    global bstack111lll1ll_opy_
    CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᢲ")] = str(bstack111lll1ll_opy_) + str(__version__)
    bstack1l1l1l11l_opy_ = 0
    try:
        if bstack11ll11lll_opy_ is True:
            bstack1l1l1l11l_opy_ = int(os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩᢳ")))
    except:
        bstack1l1l1l11l_opy_ = 0
    CONFIG[bstack1l1l1l1_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᢴ")] = True
    bstack1l11lllll_opy_ = bstack111lll11l_opy_(CONFIG, bstack1l1l1l11l_opy_)
    logger.debug(bstack1l1lll1111_opy_.format(str(bstack1l11lllll_opy_)))
    if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨᢵ")):
        bstack1l111llll_opy_(bstack1l11lllll_opy_, bstack1ll1lll111_opy_)
    if bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᢶ") in CONFIG and bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫᢷ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪᢸ")][bstack1l1l1l11l_opy_]:
        bstack11l1l11l_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᢹ")][bstack1l1l1l11l_opy_][bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᢺ")]
    import urllib
    import json
    bstack11l1l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠬᢻ") + urllib.parse.quote(json.dumps(bstack1l11lllll_opy_))
    browser = self.connect(bstack11l1l1l1_opy_)
    return browser
def bstack1ll1lllll_opy_():
    global bstack1ll1ll111l_opy_
    global bstack111lll1ll_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1l11l1111l_opy_
        if not bstack111lll1l11_opy_():
            global bstack1ll1111111_opy_
            if not bstack1ll1111111_opy_:
                from bstack_utils.helper import bstack11lll111_opy_, bstack11l1ll111_opy_
                bstack1ll1111111_opy_ = bstack11lll111_opy_()
                bstack11l1ll111_opy_(bstack111lll1ll_opy_)
            BrowserType.connect = bstack1l11l1111l_opy_
            return
        BrowserType.launch = bstack1l1lll111_opy_
        bstack1ll1ll111l_opy_ = True
    except Exception as e:
        pass
def bstack1ll1l1l1l11_opy_():
    global CONFIG
    global bstack1l1l1ll111_opy_
    global bstack1ll11l11l1_opy_
    global bstack1ll1lll111_opy_
    global bstack11ll11lll_opy_
    global bstack11111l11_opy_
    CONFIG = json.loads(os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠪᢼ")))
    bstack1l1l1ll111_opy_ = eval(os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ᢽ")))
    bstack1ll11l11l1_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡎࡕࡃࡡࡘࡖࡑ࠭ᢾ"))
    bstack11l11llll_opy_(CONFIG, bstack1l1l1ll111_opy_)
    bstack11111l11_opy_ = bstack1lll1111ll_opy_.bstack11l1l1l1l_opy_(CONFIG, bstack11111l11_opy_)
    global bstack11l11l1l_opy_
    global bstack1l11ll11_opy_
    global bstack111l11l1_opy_
    global bstack1llllllll_opy_
    global bstack1ll111l1_opy_
    global bstack11111ll1_opy_
    global bstack11l1l1l11_opy_
    global bstack1llll11l1_opy_
    global bstack1l1ll1ll1l_opy_
    global bstack1l1llll1l_opy_
    global bstack11l1lll1l_opy_
    global bstack1ll1l1ll11_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack11l11l1l_opy_ = webdriver.Remote.__init__
        bstack1l11ll11_opy_ = WebDriver.quit
        bstack11l1l1l11_opy_ = WebDriver.close
        bstack1llll11l1_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᢿ") in CONFIG or bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬᣀ") in CONFIG) and bstack1lll11llll_opy_():
        if bstack1l1l1111_opy_() < version.parse(bstack1l11ll11ll_opy_):
            logger.error(bstack1l11ll1ll1_opy_.format(bstack1l1l1111_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                bstack1l1ll1ll1l_opy_ = RemoteConnection._get_proxy_url
            except Exception as e:
                logger.error(bstack1ll1lll1l1_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack1l1llll1l_opy_ = Config.getoption
        from _pytest import runner
        bstack11l1lll1l_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack1lll1lll1_opy_)
    try:
        from pytest_bdd import reporting
        bstack1ll1l1ll11_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡱࠣࡶࡺࡴࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹ࡫ࡳࡵࡵࠪᣁ"))
    bstack1ll1lll111_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧᣂ"), {}).get(bstack1l1l1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᣃ"))
    bstack11ll11lll_opy_ = True
    bstack11l11lll1_opy_(bstack1l111l1l_opy_)
if (bstack1111ll1l1l_opy_()):
    bstack1ll1l1l1l11_opy_()
@bstack11ll1l11ll_opy_(class_method=False)
def bstack1ll1l1ll11l_opy_(hook_name, event, bstack1ll1l111lll_opy_=None):
    if hook_name not in [bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ᣄ"), bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠪᣅ"), bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭ᣆ"), bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪᣇ"), bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧᣈ"), bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠫᣉ"), bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠪᣊ"), bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡧࡷ࡬ࡴࡪࠧᣋ")]:
        return
    node = store[bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪᣌ")]
    if hook_name in [bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭ᣍ"), bstack1l1l1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪᣎ")]:
        node = store[bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡱࡴࡪࡵ࡭ࡧࡢ࡭ࡹ࡫࡭ࠨᣏ")]
    elif hook_name in [bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡦࡰࡦࡹࡳࠨᣐ"), bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠬᣑ")]:
        node = store[bstack1l1l1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡣ࡭ࡣࡶࡷࡤ࡯ࡴࡦ࡯ࠪᣒ")]
    if event == bstack1l1l1l1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪ࠭ᣓ"):
        hook_type = bstack1lll1llll11_opy_(hook_name)
        uuid = uuid4().__str__()
        bstack1l1111l1ll_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬᣔ"): uuid,
            bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᣕ"): bstack1ll1l11lll_opy_(),
            bstack1l1l1l1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧᣖ"): bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨᣗ"),
            bstack1l1l1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧᣘ"): hook_type,
            bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨᣙ"): hook_name
        }
        store[bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪᣚ")].append(uuid)
        bstack1ll1l1l111l_opy_ = node.nodeid
        if hook_type == bstack1l1l1l1_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬᣛ"):
            if not _11ll1ll1l1_opy_.get(bstack1ll1l1l111l_opy_, None):
                _11ll1ll1l1_opy_[bstack1ll1l1l111l_opy_] = {bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧᣜ"): []}
            _11ll1ll1l1_opy_[bstack1ll1l1l111l_opy_][bstack1l1l1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨᣝ")].append(bstack1l1111l1ll_opy_[bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᣞ")])
        _11ll1ll1l1_opy_[bstack1ll1l1l111l_opy_ + bstack1l1l1l1_opy_ (u"ࠫ࠲࠭ᣟ") + hook_name] = bstack1l1111l1ll_opy_
        bstack1ll1l1l1l1l_opy_(node, bstack1l1111l1ll_opy_, bstack1l1l1l1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ᣠ"))
    elif event == bstack1l1l1l1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᣡ"):
        bstack11llll1l1l_opy_ = node.nodeid + bstack1l1l1l1_opy_ (u"ࠧ࠮ࠩᣢ") + hook_name
        _11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᣣ")] = bstack1ll1l11lll_opy_()
        bstack1ll11lll1ll_opy_(_11ll1ll1l1_opy_[bstack11llll1l1l_opy_][bstack1l1l1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᣤ")])
        bstack1ll1l1l1l1l_opy_(node, _11ll1ll1l1_opy_[bstack11llll1l1l_opy_], bstack1l1l1l1_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬᣥ"), bstack1ll1l1ll111_opy_=bstack1ll1l111lll_opy_)
def bstack1ll1l1ll1l1_opy_():
    global bstack1ll11llll1l_opy_
    if bstack1llll1111_opy_():
        bstack1ll11llll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨᣦ")
    else:
        bstack1ll11llll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬᣧ")
@bstack11l1l11l1_opy_.bstack1lll11111ll_opy_
def bstack1ll1l11l11l_opy_():
    bstack1ll1l1ll1l1_opy_()
    if bstack1lll11llll_opy_():
        bstack111l1l111_opy_(bstack1l1111ll1_opy_)
    try:
        bstack1111l11ll1_opy_(bstack1ll1l1ll11l_opy_)
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࡶࠤࡵࡧࡴࡤࡪ࠽ࠤࢀࢃࠢᣨ").format(e))
bstack1ll1l11l11l_opy_()