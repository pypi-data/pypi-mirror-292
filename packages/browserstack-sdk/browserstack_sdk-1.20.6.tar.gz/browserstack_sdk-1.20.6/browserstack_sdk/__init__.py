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
import os
import signal
import sys
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
import multiprocessing
import traceback
import copy
import tempfile
from packaging import version
from uuid import uuid4
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from bstack_utils.constants import *
from bstack_utils.percy import *
from browserstack_sdk.bstack1lll1l1l11_opy_ import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack111ll1111_opy_ import bstack1l11l111l_opy_
import time
import requests
def bstack1l1111l1_opy_():
  global CONFIG
  headers = {
        bstack1l1l1l1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack11l111lll_opy_(CONFIG, bstack1llllll1l1_opy_)
  try:
    response = requests.get(bstack1llllll1l1_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1l11llll1_opy_ = response.json()[bstack1l1l1l1_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1llll11l_opy_.format(response.json()))
      return bstack1l11llll1_opy_
    else:
      logger.debug(bstack1l111ll1_opy_.format(bstack1l1l1l1_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack1l111ll1_opy_.format(e))
def bstack11lll1l1l_opy_(hub_url):
  global CONFIG
  url = bstack1l1l1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack1l1l1l1_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack1l1l1l1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack11l111lll_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1l1lll11l_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1l111l1lll_opy_.format(hub_url, e))
def bstack1l11llll1l_opy_():
  try:
    global bstack1ll11l11l1_opy_
    bstack1l11llll1_opy_ = bstack1l1111l1_opy_()
    bstack111l1l11l_opy_ = []
    results = []
    for bstack1l1lll111l_opy_ in bstack1l11llll1_opy_:
      bstack111l1l11l_opy_.append(bstack1ll1ll1lll_opy_(target=bstack11lll1l1l_opy_,args=(bstack1l1lll111l_opy_,)))
    for t in bstack111l1l11l_opy_:
      t.start()
    for t in bstack111l1l11l_opy_:
      results.append(t.join())
    bstack1llll111l1_opy_ = {}
    for item in results:
      hub_url = item[bstack1l1l1l1_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬࡾ")]
      latency = item[bstack1l1l1l1_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭ࡿ")]
      bstack1llll111l1_opy_[hub_url] = latency
    bstack111l1ll1l_opy_ = min(bstack1llll111l1_opy_, key= lambda x: bstack1llll111l1_opy_[x])
    bstack1ll11l11l1_opy_ = bstack111l1ll1l_opy_
    logger.debug(bstack111l11l1l_opy_.format(bstack111l1ll1l_opy_))
  except Exception as e:
    logger.debug(bstack1llll11ll1_opy_.format(e))
from bstack_utils.messages import *
from bstack_utils import bstack1lll1111ll_opy_
from bstack_utils.config import Config
from bstack_utils.helper import bstack11ll111l_opy_, bstack1l1111lll_opy_, bstack1l1ll1l11l_opy_, bstack1l111l1ll1_opy_, bstack111ll1ll1_opy_, \
  Notset, bstack1l11lll11_opy_, \
  bstack1lll1l111_opy_, bstack1ll1l1l1l1_opy_, bstack1l1ll1l1_opy_, bstack111111lll_opy_, bstack1llll1111_opy_, bstack1lll11llll_opy_, \
  bstack1l11ll1l1l_opy_, \
  bstack1lllll1l1l_opy_, bstack11111111_opy_, bstack111l1111_opy_, bstack1ll1l1ll1l_opy_, \
  bstack11ll1l1ll_opy_, bstack1111l1l1l_opy_, bstack1l1111ll_opy_, bstack11111l1ll_opy_
from bstack_utils.bstack111l111ll_opy_ import bstack1lll111lll_opy_
from bstack_utils.bstack1ll1ll1ll_opy_ import bstack111l1l111_opy_
from bstack_utils.bstack11l1ll1l1_opy_ import bstack1l1l1lll11_opy_, bstack11llll11l_opy_
from bstack_utils.bstack111lll1l1_opy_ import bstack11l1l11l1_opy_
from bstack_utils.bstack1l1lll11ll_opy_ import bstack1ll11l1lll_opy_
from bstack_utils.bstack1ll1ll1l11_opy_ import bstack1ll1ll1l11_opy_
from bstack_utils.proxy import bstack1l1l1lll1_opy_, bstack11l111lll_opy_, bstack111l1ll1_opy_, bstack1lll11l1_opy_
import bstack_utils.bstack1llll11l11_opy_ as bstack1l11lll1l_opy_
from browserstack_sdk.bstack1llll111_opy_ import *
from browserstack_sdk.bstack1lll11l11_opy_ import *
from bstack_utils.bstack11l1l1ll1_opy_ import bstack1ll1l1lll_opy_
import bstack_utils.bstack11111l11l_opy_ as bstack1111ll11l_opy_
bstack1lll1lllll_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠠࠡ࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳࠦࠠࡪࡨࠫࡴࡦ࡭ࡥࠡ࠿ࡀࡁࠥࡼ࡯ࡪࡦࠣ࠴࠮ࠦࡻ࡝ࡰࠣࠤࠥࡺࡲࡺࡽ࡟ࡲࠥࡩ࡯࡯ࡵࡷࠤ࡫ࡹࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࡠࠬ࡬ࡳ࡝ࠩࠬ࠿ࡡࡴࠠࠡࠢࠣࠤ࡫ࡹ࠮ࡢࡲࡳࡩࡳࡪࡆࡪ࡮ࡨࡗࡾࡴࡣࠩࡤࡶࡸࡦࡩ࡫ࡠࡲࡤࡸ࡭࠲ࠠࡋࡕࡒࡒ࠳ࡹࡴࡳ࡫ࡱ࡫࡮࡬ࡹࠩࡲࡢ࡭ࡳࡪࡥࡹࠫࠣ࠯ࠥࠨ࠺ࠣࠢ࠮ࠤࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡐࡓࡐࡐ࠱ࡴࡦࡸࡳࡦࠪࠫࡥࡼࡧࡩࡵࠢࡱࡩࡼࡖࡡࡨࡧ࠵࠲ࡪࡼࡡ࡭ࡷࡤࡸࡪ࠮ࠢࠩࠫࠣࡁࡃࠦࡻࡾࠤ࠯ࠤࡡ࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡧࡦࡶࡖࡩࡸࡹࡩࡰࡰࡇࡩࡹࡧࡩ࡭ࡵࠥࢁࡡ࠭ࠩࠪࠫ࡞ࠦ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠢ࡞ࠫࠣ࠯ࠥࠨࠬ࡝࡞ࡱࠦ࠮ࡢ࡮ࠡࠢࠣࠤࢂࡩࡡࡵࡥ࡫ࠬࡪࡾࠩࡼ࡞ࡱࠤࠥࠦࠠࡾ࡞ࡱࠤࠥࢃ࡜࡯ࠢࠣ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴࠭ࢀ")
bstack1lll11ll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠧ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡶࡡࡵࡪࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠹࡝࡝ࡰࡦࡳࡳࡹࡴࠡࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠳ࡠࡠࡳࡩ࡯࡯ࡵࡷࠤࡵࡥࡩ࡯ࡦࡨࡼࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠳࡟࡟ࡲࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡸࡲࡩࡤࡧࠫ࠴࠱ࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠴ࠫ࡟ࡲࡨࡵ࡮ࡴࡶࠣ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫ࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤࠬ࠿ࡡࡴࡩ࡮ࡲࡲࡶࡹࡥࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶ࠷ࡣࡧࡹࡴࡢࡥ࡮࠲ࡨ࡮ࡲࡰ࡯࡬ࡹࡲ࠴࡬ࡢࡷࡱࡧ࡭ࠦ࠽ࠡࡣࡶࡽࡳࡩࠠࠩ࡮ࡤࡹࡳࡩࡨࡐࡲࡷ࡭ࡴࡴࡳࠪࠢࡀࡂࠥࢁ࡜࡯࡮ࡨࡸࠥࡩࡡࡱࡵ࠾ࡠࡳࡺࡲࡺࠢࡾࡠࡳࡩࡡࡱࡵࠣࡁࠥࡐࡓࡐࡐ࠱ࡴࡦࡸࡳࡦࠪࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠩ࡝ࡰࠣࠤࢂࠦࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࠢࡾࡠࡳࠦࠠࠡࠢࢀࡠࡳࠦࠠࡳࡧࡷࡹࡷࡴࠠࡢࡹࡤ࡭ࡹࠦࡩ࡮ࡲࡲࡶࡹࡥࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶ࠷ࡣࡧࡹࡴࡢࡥ࡮࠲ࡨ࡮ࡲࡰ࡯࡬ࡹࡲ࠴ࡣࡰࡰࡱࡩࡨࡺࠨࡼ࡞ࡱࠤࠥࠦࠠࡸࡵࡈࡲࡩࡶ࡯ࡪࡰࡷ࠾ࠥࡦࡷࡴࡵ࠽࠳࠴ࡩࡤࡱ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡁࡦࡥࡵࡹ࠽ࠥࡽࡨࡲࡨࡵࡤࡦࡗࡕࡍࡈࡵ࡭ࡱࡱࡱࡩࡳࡺࠨࡋࡕࡒࡒ࠳ࡹࡴࡳ࡫ࡱ࡫࡮࡬ࡹࠩࡥࡤࡴࡸ࠯ࠩࡾࡢ࠯ࡠࡳࠦࠠࠡࠢ࠱࠲࠳ࡲࡡࡶࡰࡦ࡬ࡔࡶࡴࡪࡱࡱࡷࡡࡴࠠࠡࡿࠬࡠࡳࢃ࡜࡯࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳ࠭ࢁ")
from ._version import __version__
bstack1l1l1111ll_opy_ = None
CONFIG = {}
bstack1lll11ll11_opy_ = {}
bstack1ll1llll1l_opy_ = {}
bstack11ll1l1l_opy_ = None
bstack1111ll1l1_opy_ = None
bstack11l1l11l_opy_ = None
bstack111lll1l_opy_ = -1
bstack1lllll111_opy_ = 0
bstack11111l11_opy_ = bstack1l1l1l1l1l_opy_
bstack1llll11111_opy_ = 1
bstack11ll11lll_opy_ = False
bstack1ll1l11l11_opy_ = False
bstack111lll1ll_opy_ = bstack1l1l1l1_opy_ (u"ࠨࠩࢂ")
bstack1ll1lll111_opy_ = bstack1l1l1l1_opy_ (u"ࠩࠪࢃ")
bstack1l1l1ll111_opy_ = False
bstack1l1l11l1l1_opy_ = True
bstack11111lll_opy_ = bstack1l1l1l1_opy_ (u"ࠪࠫࢄ")
bstack1ll111111_opy_ = []
bstack1ll11l11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࠬࢅ")
bstack1ll1ll111l_opy_ = False
bstack11l1l111l_opy_ = None
bstack1l1l1111l_opy_ = None
bstack1lll1l1ll_opy_ = None
bstack1lll1ll1ll_opy_ = -1
bstack111llll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠬࢄࠧࢆ")), bstack1l1l1l1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ࢇ"), bstack1l1l1l1_opy_ (u"ࠧ࠯ࡴࡲࡦࡴࡺ࠭ࡳࡧࡳࡳࡷࡺ࠭ࡩࡧ࡯ࡴࡪࡸ࠮࡫ࡵࡲࡲࠬ࢈"))
bstack1111l111_opy_ = 0
bstack1ll1l1lll1_opy_ = 0
bstack1l1l1llll1_opy_ = []
bstack1l1l11ll1l_opy_ = []
bstack1ll11llll1_opy_ = []
bstack1l11l11l_opy_ = []
bstack11lll1l11_opy_ = bstack1l1l1l1_opy_ (u"ࠨࠩࢉ")
bstack111lllll1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࠪࢊ")
bstack1lllll11ll_opy_ = False
bstack11lllll1_opy_ = False
bstack11ll11ll_opy_ = {}
bstack11l11l1l_opy_ = None
bstack1l11ll11_opy_ = None
bstack1l1l1l1l1_opy_ = None
bstack1l1l1l111l_opy_ = None
bstack11lllllll_opy_ = None
bstack1l11lll11l_opy_ = None
bstack111l11l1_opy_ = None
bstack1llllllll_opy_ = None
bstack1l111ll1ll_opy_ = None
bstack1ll111l1_opy_ = None
bstack11111ll1_opy_ = None
bstack1l1ll1ll1l_opy_ = None
bstack11l1l1l11_opy_ = None
bstack1llll11l1_opy_ = None
bstack11111lll1_opy_ = None
bstack1l1llll1l_opy_ = None
bstack11l1lll1l_opy_ = None
bstack1lll111l1_opy_ = None
bstack1ll1l1ll11_opy_ = None
bstack1l1l1ll1l1_opy_ = None
bstack111ll11l1_opy_ = None
bstack1ll1111111_opy_ = None
bstack111lll11_opy_ = False
bstack1ll111l11_opy_ = bstack1l1l1l1_opy_ (u"ࠥࠦࢋ")
logger = bstack1lll1111ll_opy_.get_logger(__name__, bstack11111l11_opy_)
bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
percy = bstack1l11llll11_opy_()
bstack1l11l11l11_opy_ = bstack1l11l111l_opy_()
def bstack1l111111_opy_():
  global CONFIG
  global bstack1lllll11ll_opy_
  global bstack1l111l111_opy_
  bstack1lll11l1l_opy_ = bstack1ll11111l_opy_(CONFIG)
  if bstack111ll1ll1_opy_(CONFIG):
    if (bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ࢌ") in bstack1lll11l1l_opy_ and str(bstack1lll11l1l_opy_[bstack1l1l1l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࢍ")]).lower() == bstack1l1l1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫࢎ")):
      bstack1lllll11ll_opy_ = True
    bstack1l111l111_opy_.bstack1ll1l1l1l_opy_(bstack1lll11l1l_opy_.get(bstack1l1l1l1_opy_ (u"ࠧࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫ࢏"), False))
  else:
    bstack1lllll11ll_opy_ = True
    bstack1l111l111_opy_.bstack1ll1l1l1l_opy_(True)
def bstack1ll1l11ll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1l1l1111_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll11lll11_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack1l1l1l1_opy_ (u"ࠣ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡥࡲࡲ࡫࡯ࡧࡧ࡫࡯ࡩࠧ࢐") == args[i].lower() or bstack1l1l1l1_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡴࡦࡪࡩࠥ࢑") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack11111lll_opy_
      bstack11111lll_opy_ += bstack1l1l1l1_opy_ (u"ࠪ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠠࠨ࢒") + path
      return path
  return None
bstack1ll11ll1l_opy_ = re.compile(bstack1l1l1l1_opy_ (u"ࡶࠧ࠴ࠪࡀ࡞ࠧࡿ࠭࠴ࠪࡀࠫࢀ࠲࠯ࡅࠢ࢓"))
def bstack1l11l1ll1_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1ll11ll1l_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack1l1l1l1_opy_ (u"ࠧࠪࡻࠣ࢔") + group + bstack1l1l1l1_opy_ (u"ࠨࡽࠣ࢕"), os.environ.get(group))
  return value
def bstack1l1l1ll1l_opy_():
  bstack1ll11ll1_opy_ = bstack1ll11lll11_opy_()
  if bstack1ll11ll1_opy_ and os.path.exists(os.path.abspath(bstack1ll11ll1_opy_)):
    fileName = bstack1ll11ll1_opy_
  if bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ࢖") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࢗ")])) and not bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡱ࡫ࡎࡢ࡯ࡨࠫ࢘") in locals():
    fileName = os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࡡࡉࡍࡑࡋ࢙ࠧ")]
  if bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡐࡤࡱࡪ࢚࠭") in locals():
    bstack111111_opy_ = os.path.abspath(fileName)
  else:
    bstack111111_opy_ = bstack1l1l1l1_opy_ (u"࢛ࠬ࠭")
  bstack1111lll11_opy_ = os.getcwd()
  bstack11ll1l111_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩ࢜")
  bstack1lll11111_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹࡢ࡯࡯ࠫ࢝")
  while (not os.path.exists(bstack111111_opy_)) and bstack1111lll11_opy_ != bstack1l1l1l1_opy_ (u"ࠣࠤ࢞"):
    bstack111111_opy_ = os.path.join(bstack1111lll11_opy_, bstack11ll1l111_opy_)
    if not os.path.exists(bstack111111_opy_):
      bstack111111_opy_ = os.path.join(bstack1111lll11_opy_, bstack1lll11111_opy_)
    if bstack1111lll11_opy_ != os.path.dirname(bstack1111lll11_opy_):
      bstack1111lll11_opy_ = os.path.dirname(bstack1111lll11_opy_)
    else:
      bstack1111lll11_opy_ = bstack1l1l1l1_opy_ (u"ࠤࠥ࢟")
  if not os.path.exists(bstack111111_opy_):
    bstack1ll1lll1ll_opy_(
      bstack1llll1l1_opy_.format(os.getcwd()))
  try:
    with open(bstack111111_opy_, bstack1l1l1l1_opy_ (u"ࠪࡶࠬࢠ")) as stream:
      yaml.add_implicit_resolver(bstack1l1l1l1_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࢡ"), bstack1ll11ll1l_opy_)
      yaml.add_constructor(bstack1l1l1l1_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࢢ"), bstack1l11l1ll1_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      return config
  except:
    with open(bstack111111_opy_, bstack1l1l1l1_opy_ (u"࠭ࡲࠨࢣ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1ll1lll1ll_opy_(bstack1l1111l11_opy_.format(str(exc)))
def bstack1l111ll1l_opy_(config):
  bstack1l11lll1l1_opy_ = bstack1l111lll1l_opy_(config)
  for option in list(bstack1l11lll1l1_opy_):
    if option.lower() in bstack1l1lll1ll1_opy_ and option != bstack1l1lll1ll1_opy_[option.lower()]:
      bstack1l11lll1l1_opy_[bstack1l1lll1ll1_opy_[option.lower()]] = bstack1l11lll1l1_opy_[option]
      del bstack1l11lll1l1_opy_[option]
  return config
def bstack1l11ll11l1_opy_():
  global bstack1ll1llll1l_opy_
  for key, bstack1l1l111ll1_opy_ in bstack1l1lll1l1l_opy_.items():
    if isinstance(bstack1l1l111ll1_opy_, list):
      for var in bstack1l1l111ll1_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack1ll1llll1l_opy_[key] = os.environ[var]
          break
    elif bstack1l1l111ll1_opy_ in os.environ and os.environ[bstack1l1l111ll1_opy_] and str(os.environ[bstack1l1l111ll1_opy_]).strip():
      bstack1ll1llll1l_opy_[key] = os.environ[bstack1l1l111ll1_opy_]
  if bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩࢤ") in os.environ:
    bstack1ll1llll1l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࢥ")] = {}
    bstack1ll1llll1l_opy_[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")][bstack1l1l1l1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࢧ")] = os.environ[bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ࢨ")]
def bstack1ll1l1l1ll_opy_():
  global bstack1lll11ll11_opy_
  global bstack11111lll_opy_
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) and bstack1l1l1l1_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨࢩ").lower() == val.lower():
      bstack1lll11ll11_opy_[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢪ")] = {}
      bstack1lll11ll11_opy_[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࢫ")][bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࢬ")] = sys.argv[idx + 1]
      del sys.argv[idx:idx + 2]
      break
  for key, bstack1ll1111l1_opy_ in bstack1lll111111_opy_.items():
    if isinstance(bstack1ll1111l1_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1ll1111l1_opy_:
          if idx < len(sys.argv) and bstack1l1l1l1_opy_ (u"ࠩ࠰࠱ࠬࢭ") + var.lower() == val.lower() and not key in bstack1lll11ll11_opy_:
            bstack1lll11ll11_opy_[key] = sys.argv[idx + 1]
            bstack11111lll_opy_ += bstack1l1l1l1_opy_ (u"ࠪࠤ࠲࠳ࠧࢮ") + var + bstack1l1l1l1_opy_ (u"ࠫࠥ࠭ࢯ") + sys.argv[idx + 1]
            del sys.argv[idx:idx + 2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx < len(sys.argv) and bstack1l1l1l1_opy_ (u"ࠬ࠳࠭ࠨࢰ") + bstack1ll1111l1_opy_.lower() == val.lower() and not key in bstack1lll11ll11_opy_:
          bstack1lll11ll11_opy_[key] = sys.argv[idx + 1]
          bstack11111lll_opy_ += bstack1l1l1l1_opy_ (u"࠭ࠠ࠮࠯ࠪࢱ") + bstack1ll1111l1_opy_ + bstack1l1l1l1_opy_ (u"ࠧࠡࠩࢲ") + sys.argv[idx + 1]
          del sys.argv[idx:idx + 2]
def bstack1ll111llll_opy_(config):
  bstack1l11ll1l1_opy_ = config.keys()
  for bstack11111l1l1_opy_, bstack1l1ll1ll11_opy_ in bstack1ll111l1ll_opy_.items():
    if bstack1l1ll1ll11_opy_ in bstack1l11ll1l1_opy_:
      config[bstack11111l1l1_opy_] = config[bstack1l1ll1ll11_opy_]
      del config[bstack1l1ll1ll11_opy_]
  for bstack11111l1l1_opy_, bstack1l1ll1ll11_opy_ in bstack111111ll_opy_.items():
    if isinstance(bstack1l1ll1ll11_opy_, list):
      for bstack1ll1l1ll1_opy_ in bstack1l1ll1ll11_opy_:
        if bstack1ll1l1ll1_opy_ in bstack1l11ll1l1_opy_:
          config[bstack11111l1l1_opy_] = config[bstack1ll1l1ll1_opy_]
          del config[bstack1ll1l1ll1_opy_]
          break
    elif bstack1l1ll1ll11_opy_ in bstack1l11ll1l1_opy_:
      config[bstack11111l1l1_opy_] = config[bstack1l1ll1ll11_opy_]
      del config[bstack1l1ll1ll11_opy_]
  for bstack1ll1l1ll1_opy_ in list(config):
    for bstack11lll11ll_opy_ in bstack11l1111ll_opy_:
      if bstack1ll1l1ll1_opy_.lower() == bstack11lll11ll_opy_.lower() and bstack1ll1l1ll1_opy_ != bstack11lll11ll_opy_:
        config[bstack11lll11ll_opy_] = config[bstack1ll1l1ll1_opy_]
        del config[bstack1ll1l1ll1_opy_]
  bstack1l1ll111_opy_ = [{}]
  if not config.get(bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫࢳ")):
    config[bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢴ")] = [{}]
  bstack1l1ll111_opy_ = config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࢵ")]
  for platform in bstack1l1ll111_opy_:
    for bstack1ll1l1ll1_opy_ in list(platform):
      for bstack11lll11ll_opy_ in bstack11l1111ll_opy_:
        if bstack1ll1l1ll1_opy_.lower() == bstack11lll11ll_opy_.lower() and bstack1ll1l1ll1_opy_ != bstack11lll11ll_opy_:
          platform[bstack11lll11ll_opy_] = platform[bstack1ll1l1ll1_opy_]
          del platform[bstack1ll1l1ll1_opy_]
  for bstack11111l1l1_opy_, bstack1l1ll1ll11_opy_ in bstack111111ll_opy_.items():
    for platform in bstack1l1ll111_opy_:
      if isinstance(bstack1l1ll1ll11_opy_, list):
        for bstack1ll1l1ll1_opy_ in bstack1l1ll1ll11_opy_:
          if bstack1ll1l1ll1_opy_ in platform:
            platform[bstack11111l1l1_opy_] = platform[bstack1ll1l1ll1_opy_]
            del platform[bstack1ll1l1ll1_opy_]
            break
      elif bstack1l1ll1ll11_opy_ in platform:
        platform[bstack11111l1l1_opy_] = platform[bstack1l1ll1ll11_opy_]
        del platform[bstack1l1ll1ll11_opy_]
  for bstack1l1ll11lll_opy_ in bstack11111111l_opy_:
    if bstack1l1ll11lll_opy_ in config:
      if not bstack11111111l_opy_[bstack1l1ll11lll_opy_] in config:
        config[bstack11111111l_opy_[bstack1l1ll11lll_opy_]] = {}
      config[bstack11111111l_opy_[bstack1l1ll11lll_opy_]].update(config[bstack1l1ll11lll_opy_])
      del config[bstack1l1ll11lll_opy_]
  for platform in bstack1l1ll111_opy_:
    for bstack1l1ll11lll_opy_ in bstack11111111l_opy_:
      if bstack1l1ll11lll_opy_ in list(platform):
        if not bstack11111111l_opy_[bstack1l1ll11lll_opy_] in platform:
          platform[bstack11111111l_opy_[bstack1l1ll11lll_opy_]] = {}
        platform[bstack11111111l_opy_[bstack1l1ll11lll_opy_]].update(platform[bstack1l1ll11lll_opy_])
        del platform[bstack1l1ll11lll_opy_]
  config = bstack1l111ll1l_opy_(config)
  return config
def bstack1l1ll11ll_opy_(config):
  global bstack1ll1lll111_opy_
  if bstack111ll1ll1_opy_(config) and bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨࢶ") in config and str(config[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩࢷ")]).lower() != bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࢸ"):
    if not bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࢹ") in config:
      config[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࢺ")] = {}
    if not config[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢻ")].get(bstack1l1l1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧࢼ")) and not bstack1l1l1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢽ") in config[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢾ")]:
      bstack1ll1l11lll_opy_ = datetime.datetime.now()
      bstack11l11l11_opy_ = bstack1ll1l11lll_opy_.strftime(bstack1l1l1l1_opy_ (u"࠭ࠥࡥࡡࠨࡦࡤࠫࡈࠦࡏࠪࢿ"))
      hostname = socket.gethostname()
      bstack1l111llll1_opy_ = bstack1l1l1l1_opy_ (u"ࠧࠨࣀ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1l1l1l1_opy_ (u"ࠨࡽࢀࡣࢀࢃ࡟ࡼࡿࠪࣁ").format(bstack11l11l11_opy_, hostname, bstack1l111llll1_opy_)
      config[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࣂ")][bstack1l1l1l1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࣃ")] = identifier
    bstack1ll1lll111_opy_ = config[bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨࣄ")].get(bstack1l1l1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣅ"))
  return config
def bstack1lll111l_opy_():
  bstack1ll11111_opy_ =  bstack111111lll_opy_()[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠬࣆ")]
  return bstack1ll11111_opy_ if bstack1ll11111_opy_ else -1
def bstack1l1l1l1ll_opy_(bstack1ll11111_opy_):
  global CONFIG
  if not bstack1l1l1l1_opy_ (u"ࠧࠥࡽࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࡾࠩࣇ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࣈ")]:
    return
  CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࣉ")] = CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ࣊")].replace(
    bstack1l1l1l1_opy_ (u"ࠫࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭࣋"),
    str(bstack1ll11111_opy_)
  )
def bstack1l1l1l1l_opy_():
  global CONFIG
  if not bstack1l1l1l1_opy_ (u"ࠬࠪࡻࡅࡃࡗࡉࡤ࡚ࡉࡎࡇࢀࠫ࣌") in CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣍")]:
    return
  bstack1ll1l11lll_opy_ = datetime.datetime.now()
  bstack11l11l11_opy_ = bstack1ll1l11lll_opy_.strftime(bstack1l1l1l1_opy_ (u"ࠧࠦࡦ࠰ࠩࡧ࠳ࠥࡉ࠼ࠨࡑࠬ࣎"))
  CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴ࣏ࠪ")] = CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵ࣐ࠫ")].replace(
    bstack1l1l1l1_opy_ (u"ࠪࠨࢀࡊࡁࡕࡇࡢࡘࡎࡓࡅࡾ࣑ࠩ"),
    bstack11l11l11_opy_
  )
def bstack1llll1llll_opy_():
  global CONFIG
  if bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࣒࠭") in CONFIG and not bool(CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸ࣓ࠧ")]):
    del CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨࣔ")]
    return
  if not bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࣕ") in CONFIG:
    CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࣖ")] = bstack1l1l1l1_opy_ (u"ࠩࠦࠨࢀࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࢁࠬࣗ")
  if bstack1l1l1l1_opy_ (u"ࠪࠨࢀࡊࡁࡕࡇࡢࡘࡎࡓࡅࡾࠩࣘ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࣙ")]:
    bstack1l1l1l1l_opy_()
    os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩࣚ")] = CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨࣛ")]
  if not bstack1l1l1l1_opy_ (u"ࠧࠥࡽࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࡾࠩࣜ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࣝ")]:
    return
  bstack1ll11111_opy_ = bstack1l1l1l1_opy_ (u"ࠩࠪࣞ")
  bstack1l1lll1lll_opy_ = bstack1lll111l_opy_()
  if bstack1l1lll1lll_opy_ != -1:
    bstack1ll11111_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡇࡎࠦࠧࣟ") + str(bstack1l1lll1lll_opy_)
  if bstack1ll11111_opy_ == bstack1l1l1l1_opy_ (u"ࠫࠬ࣠"):
    bstack1l11l11ll1_opy_ = bstack1l11l1lll1_opy_(CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ࣡")])
    if bstack1l11l11ll1_opy_ != -1:
      bstack1ll11111_opy_ = str(bstack1l11l11ll1_opy_)
  if bstack1ll11111_opy_:
    bstack1l1l1l1ll_opy_(bstack1ll11111_opy_)
    os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪ࣢")] = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࣣࠩ")]
def bstack1lllll1l1_opy_(bstack1l1l111l11_opy_, bstack1lll1l111l_opy_, path):
  bstack11l1llll1_opy_ = {
    bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࣤ"): bstack1lll1l111l_opy_
  }
  if os.path.exists(path):
    bstack1ll11llll_opy_ = json.load(open(path, bstack1l1l1l1_opy_ (u"ࠩࡵࡦࠬࣥ")))
  else:
    bstack1ll11llll_opy_ = {}
  bstack1ll11llll_opy_[bstack1l1l111l11_opy_] = bstack11l1llll1_opy_
  with open(path, bstack1l1l1l1_opy_ (u"ࠥࡻ࠰ࠨࣦ")) as outfile:
    json.dump(bstack1ll11llll_opy_, outfile)
def bstack1l11l1lll1_opy_(bstack1l1l111l11_opy_):
  bstack1l1l111l11_opy_ = str(bstack1l1l111l11_opy_)
  bstack1l11lllll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭ࣧ")), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬࣨ"))
  try:
    if not os.path.exists(bstack1l11lllll1_opy_):
      os.makedirs(bstack1l11lllll1_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"࠭ࡾࠨࣩ")), bstack1l1l1l1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ࣪"), bstack1l1l1l1_opy_ (u"ࠨ࠰ࡥࡹ࡮ࡲࡤ࠮ࡰࡤࡱࡪ࠳ࡣࡢࡥ࡫ࡩ࠳ࡰࡳࡰࡰࠪ࣫"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1l1l1l1_opy_ (u"ࠩࡺࠫ࣬")):
        pass
      with open(file_path, bstack1l1l1l1_opy_ (u"ࠥࡻ࠰ࠨ࣭")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1l1l1l1_opy_ (u"ࠫࡷ࣮࠭")) as bstack1l11ll11l_opy_:
      bstack11ll111l1_opy_ = json.load(bstack1l11ll11l_opy_)
    if bstack1l1l111l11_opy_ in bstack11ll111l1_opy_:
      bstack1ll1ll1111_opy_ = bstack11ll111l1_opy_[bstack1l1l111l11_opy_][bstack1l1l1l1_opy_ (u"ࠬ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ࣯ࠩ")]
      bstack11111ll1l_opy_ = int(bstack1ll1ll1111_opy_) + 1
      bstack1lllll1l1_opy_(bstack1l1l111l11_opy_, bstack11111ll1l_opy_, file_path)
      return bstack11111ll1l_opy_
    else:
      bstack1lllll1l1_opy_(bstack1l1l111l11_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack11ll11ll1_opy_.format(str(e)))
    return -1
def bstack1ll11lll1_opy_(config):
  if not config[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࣰ")] or not config[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࣱࠪ")]:
    return True
  else:
    return False
def bstack1l11l1111_opy_(config, index=0):
  global bstack1l1l1ll111_opy_
  bstack1l1l1ll1ll_opy_ = {}
  caps = bstack11llll1ll_opy_ + bstack1llll1ll1l_opy_
  if bstack1l1l1ll111_opy_:
    caps += bstack1l1lllllll_opy_
  for key in config:
    if key in caps + [bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣲࠫ")]:
      continue
    bstack1l1l1ll1ll_opy_[key] = config[key]
  if bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࣳ") in config:
    for bstack1l11111l1_opy_ in config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣴ")][index]:
      if bstack1l11111l1_opy_ in caps:
        continue
      bstack1l1l1ll1ll_opy_[bstack1l11111l1_opy_] = config[bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧࣵ")][index][bstack1l11111l1_opy_]
  bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࣶࠧ")] = socket.gethostname()
  if bstack1l1l1l1_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧࣷ") in bstack1l1l1ll1ll_opy_:
    del (bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨࣸ")])
  return bstack1l1l1ll1ll_opy_
def bstack1l11llllll_opy_(config):
  global bstack1l1l1ll111_opy_
  bstack111111ll1_opy_ = {}
  caps = bstack1llll1ll1l_opy_
  if bstack1l1l1ll111_opy_:
    caps += bstack1l1lllllll_opy_
  for key in caps:
    if key in config:
      bstack111111ll1_opy_[key] = config[key]
  return bstack111111ll1_opy_
def bstack111l1lll_opy_(bstack1l1l1ll1ll_opy_, bstack111111ll1_opy_):
  bstack11llll11_opy_ = {}
  for key in bstack1l1l1ll1ll_opy_.keys():
    if key in bstack1ll111l1ll_opy_:
      bstack11llll11_opy_[bstack1ll111l1ll_opy_[key]] = bstack1l1l1ll1ll_opy_[key]
    else:
      bstack11llll11_opy_[key] = bstack1l1l1ll1ll_opy_[key]
  for key in bstack111111ll1_opy_:
    if key in bstack1ll111l1ll_opy_:
      bstack11llll11_opy_[bstack1ll111l1ll_opy_[key]] = bstack111111ll1_opy_[key]
    else:
      bstack11llll11_opy_[key] = bstack111111ll1_opy_[key]
  return bstack11llll11_opy_
def bstack111lll11l_opy_(config, index=0):
  global bstack1l1l1ll111_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1ll11l111l_opy_ = bstack11ll111l_opy_(bstack11l11lll_opy_, config, logger)
  bstack111111ll1_opy_ = bstack1l11llllll_opy_(config)
  bstack111l11111_opy_ = bstack1llll1ll1l_opy_
  bstack111l11111_opy_ += bstack1l1l11ll11_opy_
  bstack111111ll1_opy_ = update(bstack111111ll1_opy_, bstack1ll11l111l_opy_)
  if bstack1l1l1ll111_opy_:
    bstack111l11111_opy_ += bstack1l1lllllll_opy_
  if bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ") in config:
    if bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࣺࠧ") in config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")][index]:
      caps[bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩࣼ")] = config[bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨࣽ")][index][bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫࣾ")]
    if bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨࣿ") in config[bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫऀ")][index]:
      caps[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪँ")] = str(config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ं")][index][bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬः")])
    bstack1l11l111l1_opy_ = bstack11ll111l_opy_(bstack11l11lll_opy_, config[bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨऄ")][index], logger)
    bstack111l11111_opy_ += list(bstack1l11l111l1_opy_.keys())
    for bstack1l1l111111_opy_ in bstack111l11111_opy_:
      if bstack1l1l111111_opy_ in config[bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩअ")][index]:
        if bstack1l1l111111_opy_ == bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩआ"):
          try:
            bstack1l11l111l1_opy_[bstack1l1l111111_opy_] = str(config[bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫइ")][index][bstack1l1l111111_opy_] * 1.0)
          except:
            bstack1l11l111l1_opy_[bstack1l1l111111_opy_] = str(config[bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬई")][index][bstack1l1l111111_opy_])
        else:
          bstack1l11l111l1_opy_[bstack1l1l111111_opy_] = config[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭उ")][index][bstack1l1l111111_opy_]
        del (config[bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧऊ")][index][bstack1l1l111111_opy_])
    bstack111111ll1_opy_ = update(bstack111111ll1_opy_, bstack1l11l111l1_opy_)
  bstack1l1l1ll1ll_opy_ = bstack1l11l1111_opy_(config, index)
  for bstack1ll1l1ll1_opy_ in bstack1llll1ll1l_opy_ + list(bstack1ll11l111l_opy_.keys()):
    if bstack1ll1l1ll1_opy_ in bstack1l1l1ll1ll_opy_:
      bstack111111ll1_opy_[bstack1ll1l1ll1_opy_] = bstack1l1l1ll1ll_opy_[bstack1ll1l1ll1_opy_]
      del (bstack1l1l1ll1ll_opy_[bstack1ll1l1ll1_opy_])
  if bstack1l11lll11_opy_(config):
    bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬऋ")] = True
    caps.update(bstack111111ll1_opy_)
    caps[bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧऌ")] = bstack1l1l1ll1ll_opy_
  else:
    bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧऍ")] = False
    caps.update(bstack111l1lll_opy_(bstack1l1l1ll1ll_opy_, bstack111111ll1_opy_))
    if bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ऎ") in caps:
      caps[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪए")] = caps[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨऐ")]
      del (caps[bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩऑ")])
    if bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ऒ") in caps:
      caps[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨओ")] = caps[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨऔ")]
      del (caps[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩक")])
  return caps
def bstack11lll1l1_opy_():
  global bstack1ll11l11l1_opy_
  if bstack1l1l1111_opy_() <= version.parse(bstack1l1l1l1_opy_ (u"ࠩ࠶࠲࠶࠹࠮࠱ࠩख")):
    if bstack1ll11l11l1_opy_ != bstack1l1l1l1_opy_ (u"ࠪࠫग"):
      return bstack1l1l1l1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧघ") + bstack1ll11l11l1_opy_ + bstack1l1l1l1_opy_ (u"ࠧࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠤङ")
    return bstack1l11l1llll_opy_
  if bstack1ll11l11l1_opy_ != bstack1l1l1l1_opy_ (u"࠭ࠧच"):
    return bstack1l1l1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤछ") + bstack1ll11l11l1_opy_ + bstack1l1l1l1_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤज")
  return bstack111l1l1l_opy_
def bstack1llll11l1l_opy_(options):
  return hasattr(options, bstack1l1l1l1_opy_ (u"ࠩࡶࡩࡹࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵࡻࠪझ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1lll1lll1l_opy_(options, bstack1l1l11111_opy_):
  for bstack1l11l1l1l_opy_ in bstack1l1l11111_opy_:
    if bstack1l11l1l1l_opy_ in [bstack1l1l1l1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨञ"), bstack1l1l1l1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨट")]:
      continue
    if bstack1l11l1l1l_opy_ in options._experimental_options:
      options._experimental_options[bstack1l11l1l1l_opy_] = update(options._experimental_options[bstack1l11l1l1l_opy_],
                                                         bstack1l1l11111_opy_[bstack1l11l1l1l_opy_])
    else:
      options.add_experimental_option(bstack1l11l1l1l_opy_, bstack1l1l11111_opy_[bstack1l11l1l1l_opy_])
  if bstack1l1l1l1_opy_ (u"ࠬࡧࡲࡨࡵࠪठ") in bstack1l1l11111_opy_:
    for arg in bstack1l1l11111_opy_[bstack1l1l1l1_opy_ (u"࠭ࡡࡳࡩࡶࠫड")]:
      options.add_argument(arg)
    del (bstack1l1l11111_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬढ")])
  if bstack1l1l1l1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬण") in bstack1l1l11111_opy_:
    for ext in bstack1l1l11111_opy_[bstack1l1l1l1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭त")]:
      options.add_extension(ext)
    del (bstack1l1l11111_opy_[bstack1l1l1l1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧथ")])
def bstack1l11l1l111_opy_(options, bstack1lll1ll1l1_opy_):
  if bstack1l1l1l1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪद") in bstack1lll1ll1l1_opy_:
    for bstack11ll11111_opy_ in bstack1lll1ll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫध")]:
      if bstack11ll11111_opy_ in options._preferences:
        options._preferences[bstack11ll11111_opy_] = update(options._preferences[bstack11ll11111_opy_], bstack1lll1ll1l1_opy_[bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬन")][bstack11ll11111_opy_])
      else:
        options.set_preference(bstack11ll11111_opy_, bstack1lll1ll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ऩ")][bstack11ll11111_opy_])
  if bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭प") in bstack1lll1ll1l1_opy_:
    for arg in bstack1lll1ll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧफ")]:
      options.add_argument(arg)
def bstack1l1ll1lll_opy_(options, bstack1ll1ll11l1_opy_):
  if bstack1l1l1l1_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࠫब") in bstack1ll1ll11l1_opy_:
    options.use_webview(bool(bstack1ll1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࠬभ")]))
  bstack1lll1lll1l_opy_(options, bstack1ll1ll11l1_opy_)
def bstack111l11l11_opy_(options, bstack1ll111lll1_opy_):
  for bstack11ll11l11_opy_ in bstack1ll111lll1_opy_:
    if bstack11ll11l11_opy_ in [bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡤࡪࡱࡳࡱࡵࡧࡺࡒࡵࡩࡻ࡯ࡥࡸࠩम"), bstack1l1l1l1_opy_ (u"࠭ࡡࡳࡩࡶࠫय")]:
      continue
    options.set_capability(bstack11ll11l11_opy_, bstack1ll111lll1_opy_[bstack11ll11l11_opy_])
  if bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬर") in bstack1ll111lll1_opy_:
    for arg in bstack1ll111lll1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ऱ")]:
      options.add_argument(arg)
  if bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡨ࡮࡮ࡰ࡮ࡲ࡫ࡾࡖࡲࡦࡸ࡬ࡩࡼ࠭ल") in bstack1ll111lll1_opy_:
    options.bstack1ll11l1l11_opy_(bool(bstack1ll111lll1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧळ")]))
def bstack111l1lll1_opy_(options, bstack1lllll111l_opy_):
  for bstack111ll11l_opy_ in bstack1lllll111l_opy_:
    if bstack111ll11l_opy_ in [bstack1l1l1l1_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨऴ"), bstack1l1l1l1_opy_ (u"ࠬࡧࡲࡨࡵࠪव")]:
      continue
    options._options[bstack111ll11l_opy_] = bstack1lllll111l_opy_[bstack111ll11l_opy_]
  if bstack1l1l1l1_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪश") in bstack1lllll111l_opy_:
    for bstack1l111ll11l_opy_ in bstack1lllll111l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡦࡧ࡭ࡹ࡯࡯࡯ࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫष")]:
      options.bstack111ll1l11_opy_(
        bstack1l111ll11l_opy_, bstack1lllll111l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬस")][bstack1l111ll11l_opy_])
  if bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧह") in bstack1lllll111l_opy_:
    for arg in bstack1lllll111l_opy_[bstack1l1l1l1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨऺ")]:
      options.add_argument(arg)
def bstack1ll11ll11_opy_(options, caps):
  if not hasattr(options, bstack1l1l1l1_opy_ (u"ࠫࡐࡋ࡙ࠨऻ")):
    return
  if options.KEY == bstack1l1l1l1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵ़ࠪ") and options.KEY in caps:
    bstack1lll1lll1l_opy_(options, caps[bstack1l1l1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫऽ")])
  elif options.KEY == bstack1l1l1l1_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬा") and options.KEY in caps:
    bstack1l11l1l111_opy_(options, caps[bstack1l1l1l1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭ि")])
  elif options.KEY == bstack1l1l1l1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪी") and options.KEY in caps:
    bstack111l11l11_opy_(options, caps[bstack1l1l1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫु")])
  elif options.KEY == bstack1l1l1l1_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬू") and options.KEY in caps:
    bstack1l1ll1lll_opy_(options, caps[bstack1l1l1l1_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ृ")])
  elif options.KEY == bstack1l1l1l1_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬॄ") and options.KEY in caps:
    bstack111l1lll1_opy_(options, caps[bstack1l1l1l1_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ॅ")])
def bstack1lll11lll_opy_(caps):
  global bstack1l1l1ll111_opy_
  if isinstance(os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩॆ")), str):
    bstack1l1l1ll111_opy_ = eval(os.getenv(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪे")))
  if bstack1l1l1ll111_opy_:
    if bstack1ll1l11ll_opy_() < version.parse(bstack1l1l1l1_opy_ (u"ࠪ࠶࠳࠹࠮࠱ࠩै")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1l1l1l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫॉ")
    if bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪॊ") in caps:
      browser = caps[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫो")]
    elif bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨौ") in caps:
      browser = caps[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳ्ࠩ")]
    browser = str(browser).lower()
    if browser == bstack1l1l1l1_opy_ (u"ࠩ࡬ࡴ࡭ࡵ࡮ࡦࠩॎ") or browser == bstack1l1l1l1_opy_ (u"ࠪ࡭ࡵࡧࡤࠨॏ"):
      browser = bstack1l1l1l1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࠫॐ")
    if browser == bstack1l1l1l1_opy_ (u"ࠬࡹࡡ࡮ࡵࡸࡲ࡬࠭॑"):
      browser = bstack1l1l1l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ॒࠭")
    if browser not in [bstack1l1l1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧ॓"), bstack1l1l1l1_opy_ (u"ࠨࡧࡧ࡫ࡪ࠭॔"), bstack1l1l1l1_opy_ (u"ࠩ࡬ࡩࠬॕ"), bstack1l1l1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪॖ"), bstack1l1l1l1_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬॗ")]:
      return None
    try:
      package = bstack1l1l1l1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࢂ࠴࡯ࡱࡶ࡬ࡳࡳࡹࠧक़").format(browser)
      name = bstack1l1l1l1_opy_ (u"࠭ࡏࡱࡶ࡬ࡳࡳࡹࠧख़")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1llll11l1l_opy_(options):
        return None
      for bstack1ll1l1ll1_opy_ in caps.keys():
        options.set_capability(bstack1ll1l1ll1_opy_, caps[bstack1ll1l1ll1_opy_])
      bstack1ll11ll11_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1l1l111ll_opy_(options, bstack1l11lllll_opy_):
  if not bstack1llll11l1l_opy_(options):
    return
  for bstack1ll1l1ll1_opy_ in bstack1l11lllll_opy_.keys():
    if bstack1ll1l1ll1_opy_ in bstack1l1l11ll11_opy_:
      continue
    if bstack1ll1l1ll1_opy_ in options._caps and type(options._caps[bstack1ll1l1ll1_opy_]) in [dict, list]:
      options._caps[bstack1ll1l1ll1_opy_] = update(options._caps[bstack1ll1l1ll1_opy_], bstack1l11lllll_opy_[bstack1ll1l1ll1_opy_])
    else:
      options.set_capability(bstack1ll1l1ll1_opy_, bstack1l11lllll_opy_[bstack1ll1l1ll1_opy_])
  bstack1ll11ll11_opy_(options, bstack1l11lllll_opy_)
  if bstack1l1l1l1_opy_ (u"ࠧ࡮ࡱࡽ࠾ࡩ࡫ࡢࡶࡩࡪࡩࡷࡇࡤࡥࡴࡨࡷࡸ࠭ग़") in options._caps:
    if options._caps[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ज़")] and options._caps[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧड़")].lower() != bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫढ़"):
      del options._caps[bstack1l1l1l1_opy_ (u"ࠫࡲࡵࡺ࠻ࡦࡨࡦࡺ࡭ࡧࡦࡴࡄࡨࡩࡸࡥࡴࡵࠪफ़")]
def bstack1l11l111ll_opy_(proxy_config):
  if bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩय़") in proxy_config:
    proxy_config[bstack1l1l1l1_opy_ (u"࠭ࡳࡴ࡮ࡓࡶࡴࡾࡹࠨॠ")] = proxy_config[bstack1l1l1l1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫॡ")]
    del (proxy_config[bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬॢ")])
  if bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬॣ") in proxy_config and proxy_config[bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡖࡼࡴࡪ࠭।")].lower() != bstack1l1l1l1_opy_ (u"ࠫࡩ࡯ࡲࡦࡥࡷࠫ॥"):
    proxy_config[bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡘࡾࡶࡥࠨ०")] = bstack1l1l1l1_opy_ (u"࠭࡭ࡢࡰࡸࡥࡱ࠭१")
  if bstack1l1l1l1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡇࡵࡵࡱࡦࡳࡳ࡬ࡩࡨࡗࡵࡰࠬ२") in proxy_config:
    proxy_config[bstack1l1l1l1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫ३")] = bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡨ࠭४")
  return proxy_config
def bstack1ll11l1l_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ५") in config:
    return proxy
  config[bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪ६")] = bstack1l11l111ll_opy_(config[bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ७")])
  if proxy == None:
    proxy = Proxy(config[bstack1l1l1l1_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬ८")])
  return proxy
def bstack1ll11111ll_opy_(self):
  global CONFIG
  global bstack1l1ll1ll1l_opy_
  try:
    proxy = bstack111l1ll1_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1l1l1l1_opy_ (u"ࠧ࠯ࡲࡤࡧࠬ९")):
        proxies = bstack1l1l1lll1_opy_(proxy, bstack11lll1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll1ll1ll1_opy_ = proxies.popitem()
          if bstack1l1l1l1_opy_ (u"ࠣ࠼࠲࠳ࠧ॰") in bstack1ll1ll1ll1_opy_:
            return bstack1ll1ll1ll1_opy_
          else:
            return bstack1l1l1l1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack1ll1ll1ll1_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1l1l1l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡰࡳࡱࡻࡽࠥࡻࡲ࡭ࠢ࠽ࠤࢀࢃࠢॲ").format(str(e)))
  return bstack1l1ll1ll1l_opy_(self)
def bstack1l1l1l1ll1_opy_():
  global CONFIG
  return bstack1lll11l1_opy_(CONFIG) and bstack1lll11llll_opy_() and bstack1l1l1111_opy_() >= version.parse(bstack1l11ll11ll_opy_)
def bstack11l1ll1ll_opy_():
  global CONFIG
  return (bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧॳ") in CONFIG or bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩॴ") in CONFIG) and bstack1l11ll1l1l_opy_()
def bstack1l111lll1l_opy_(config):
  bstack1l11lll1l1_opy_ = {}
  if bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪॵ") in config:
    bstack1l11lll1l1_opy_ = config[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫॶ")]
  if bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧॷ") in config:
    bstack1l11lll1l1_opy_ = config[bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨॸ")]
  proxy = bstack111l1ll1_opy_(config)
  if proxy:
    if proxy.endswith(bstack1l1l1l1_opy_ (u"ࠪ࠲ࡵࡧࡣࠨॹ")) and os.path.isfile(proxy):
      bstack1l11lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫ࠲ࡶࡡࡤ࠯ࡩ࡭ࡱ࡫ࠧॺ")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1l1l1l1_opy_ (u"ࠬ࠴ࡰࡢࡥࠪॻ")):
        proxies = bstack11l111lll_opy_(config, bstack11lll1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll1ll1ll1_opy_ = proxies.popitem()
          if bstack1l1l1l1_opy_ (u"ࠨ࠺࠰࠱ࠥॼ") in bstack1ll1ll1ll1_opy_:
            parsed_url = urlparse(bstack1ll1ll1ll1_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1l1l1l1_opy_ (u"ࠢ࠻࠱࠲ࠦॽ") + bstack1ll1ll1ll1_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l11lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡈࡰࡵࡷࠫॾ")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l11lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡱࡵࡸࠬॿ")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l11lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭ঀ")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l11lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧঁ")] = str(parsed_url.password)
  return bstack1l11lll1l1_opy_
def bstack1ll11111l_opy_(config):
  if bstack1l1l1l1_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪং") in config:
    return config[bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠫঃ")]
  return {}
def bstack1l111llll_opy_(caps):
  global bstack1ll1lll111_opy_
  if bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ঄") in caps:
    caps[bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩঅ")][bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࠨআ")] = True
    if bstack1ll1lll111_opy_:
      caps[bstack1l1l1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫই")][bstack1l1l1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ঈ")] = bstack1ll1lll111_opy_
  else:
    caps[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࠪউ")] = True
    if bstack1ll1lll111_opy_:
      caps[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧঊ")] = bstack1ll1lll111_opy_
def bstack11l11l11l_opy_():
  global CONFIG
  if not bstack111ll1ll1_opy_(CONFIG):
    return
  if bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫঋ") in CONFIG and bstack1l1111ll_opy_(CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬঌ")]):
    if (
      bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍") in CONFIG
      and bstack1l1111ll_opy_(CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ঎")].get(bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨএ")))
    ):
      logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡒ࡯ࡤࡣ࡯ࠤࡧ࡯࡮ࡢࡴࡼࠤࡳࡵࡴࠡࡵࡷࡥࡷࡺࡥࡥࠢࡤࡷࠥࡹ࡫ࡪࡲࡅ࡭ࡳࡧࡲࡺࡋࡱ࡭ࡹ࡯ࡡ࡭࡫ࡶࡥࡹ࡯࡯࡯ࠢ࡬ࡷࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠨঐ"))
      return
    bstack1l11lll1l1_opy_ = bstack1l111lll1l_opy_(CONFIG)
    bstack1ll1l1llll_opy_(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ঑")], bstack1l11lll1l1_opy_)
def bstack1ll1l1llll_opy_(key, bstack1l11lll1l1_opy_):
  global bstack1l1l1111ll_opy_
  logger.info(bstack1l1l1l1lll_opy_)
  try:
    bstack1l1l1111ll_opy_ = Local()
    bstack111l1ll11_opy_ = {bstack1l1l1l1_opy_ (u"ࠧ࡬ࡧࡼࠫ঒"): key}
    bstack111l1ll11_opy_.update(bstack1l11lll1l1_opy_)
    logger.debug(bstack1l1l111lll_opy_.format(str(bstack111l1ll11_opy_)))
    bstack1l1l1111ll_opy_.start(**bstack111l1ll11_opy_)
    if bstack1l1l1111ll_opy_.isRunning():
      logger.info(bstack1l1l1l11l1_opy_)
  except Exception as e:
    bstack1ll1lll1ll_opy_(bstack11l1111l_opy_.format(str(e)))
def bstack1l1llll1_opy_():
  global bstack1l1l1111ll_opy_
  if bstack1l1l1111ll_opy_.isRunning():
    logger.info(bstack1lll11l1l1_opy_)
    bstack1l1l1111ll_opy_.stop()
  bstack1l1l1111ll_opy_ = None
def bstack1l11l1ll_opy_(bstack111llllll_opy_=[]):
  global CONFIG
  bstack1ll1l1ll_opy_ = []
  bstack1lll1l1l1l_opy_ = [bstack1l1l1l1_opy_ (u"ࠨࡱࡶࠫও"), bstack1l1l1l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬঔ"), bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧক"), bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭খ"), bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪগ"), bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧঘ")]
  try:
    for err in bstack111llllll_opy_:
      bstack1l1ll11ll1_opy_ = {}
      for k in bstack1lll1l1l1l_opy_:
        val = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪঙ")][int(err[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧচ")])].get(k)
        if val:
          bstack1l1ll11ll1_opy_[k] = val
      if(err[bstack1l1l1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨছ")] != bstack1l1l1l1_opy_ (u"ࠪࠫজ")):
        bstack1l1ll11ll1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪঝ")] = {
          err[bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪঞ")]: err[bstack1l1l1l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬট")]
        }
        bstack1ll1l1ll_opy_.append(bstack1l1ll11ll1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩঠ") + str(e))
  finally:
    return bstack1ll1l1ll_opy_
def bstack11lll1111_opy_(file_name):
  bstack1ll11lllll_opy_ = []
  try:
    bstack111l11lll_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack111l11lll_opy_):
      with open(bstack111l11lll_opy_) as f:
        bstack1111llll_opy_ = json.load(f)
        bstack1ll11lllll_opy_ = bstack1111llll_opy_
      os.remove(bstack111l11lll_opy_)
    return bstack1ll11lllll_opy_
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪড") + str(e))
    return bstack1ll11lllll_opy_
def bstack1llll1ll1_opy_():
  global bstack1ll111l11_opy_
  global bstack1ll111111_opy_
  global bstack1l1l1llll1_opy_
  global bstack1l1l11ll1l_opy_
  global bstack1ll11llll1_opy_
  global bstack111lllll1_opy_
  global CONFIG
  bstack11lll11l1_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪঢ"))
  if bstack11lll11l1_opy_ in [bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩণ"), bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪত")]:
    bstack1lll111l11_opy_()
  percy.shutdown()
  if bstack1ll111l11_opy_:
    logger.warning(bstack1llll1ll11_opy_.format(str(bstack1ll111l11_opy_)))
  else:
    try:
      bstack1ll11llll_opy_ = bstack1lll1l111_opy_(bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡴࡶࡤࡧࡰ࠳ࡣࡰࡰࡩ࡭࡬࠴ࡪࡴࡱࡱࠫথ"), logger)
      if bstack1ll11llll_opy_.get(bstack1l1l1l1_opy_ (u"࠭࡮ࡶࡦࡪࡩࡤࡲ࡯ࡤࡣ࡯ࠫদ")) and bstack1ll11llll_opy_.get(bstack1l1l1l1_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬধ")).get(bstack1l1l1l1_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪন")):
        logger.warning(bstack1llll1ll11_opy_.format(str(bstack1ll11llll_opy_[bstack1l1l1l1_opy_ (u"ࠩࡱࡹࡩ࡭ࡥࡠ࡮ࡲࡧࡦࡲࠧ঩")][bstack1l1l1l1_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬপ")])))
    except Exception as e:
      logger.error(e)
  logger.info(bstack1l111lll1_opy_)
  global bstack1l1l1111ll_opy_
  if bstack1l1l1111ll_opy_:
    bstack1l1llll1_opy_()
  try:
    for driver in bstack1ll111111_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1ll11l1111_opy_)
  if bstack111lllll1_opy_ == bstack1l1l1l1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪফ"):
    bstack1ll11llll1_opy_ = bstack11lll1111_opy_(bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ব"))
  if bstack111lllll1_opy_ == bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ভ") and len(bstack1l1l11ll1l_opy_) == 0:
    bstack1l1l11ll1l_opy_ = bstack11lll1111_opy_(bstack1l1l1l1_opy_ (u"ࠧࡱࡹࡢࡴࡾࡺࡥࡴࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬম"))
    if len(bstack1l1l11ll1l_opy_) == 0:
      bstack1l1l11ll1l_opy_ = bstack11lll1111_opy_(bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡳࡴࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧয"))
  bstack1l1llllll_opy_ = bstack1l1l1l1_opy_ (u"ࠩࠪর")
  if len(bstack1l1l1llll1_opy_) > 0:
    bstack1l1llllll_opy_ = bstack1l11l1ll_opy_(bstack1l1l1llll1_opy_)
  elif len(bstack1l1l11ll1l_opy_) > 0:
    bstack1l1llllll_opy_ = bstack1l11l1ll_opy_(bstack1l1l11ll1l_opy_)
  elif len(bstack1ll11llll1_opy_) > 0:
    bstack1l1llllll_opy_ = bstack1l11l1ll_opy_(bstack1ll11llll1_opy_)
  elif len(bstack1l11l11l_opy_) > 0:
    bstack1l1llllll_opy_ = bstack1l11l1ll_opy_(bstack1l11l11l_opy_)
  if bool(bstack1l1llllll_opy_):
    bstack1l1ll1l1l1_opy_(bstack1l1llllll_opy_)
  else:
    bstack1l1ll1l1l1_opy_()
  bstack1ll1l1l1l1_opy_(bstack1l11111ll_opy_, logger)
  bstack1lll1111ll_opy_.bstack1ll1l1111l_opy_(CONFIG)
  if len(bstack1ll11llll1_opy_) > 0:
    sys.exit(len(bstack1ll11llll1_opy_))
def bstack111l1111l_opy_(bstack1llll111l_opy_, frame):
  global bstack1l111l111_opy_
  logger.error(bstack1lllll1111_opy_)
  bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡒࡴ࠭঱"), bstack1llll111l_opy_)
  if hasattr(signal, bstack1l1l1l1_opy_ (u"ࠫࡘ࡯ࡧ࡯ࡣ࡯ࡷࠬল")):
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ঳"), signal.Signals(bstack1llll111l_opy_).name)
  else:
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"࠭ࡳࡥ࡭ࡎ࡭ࡱࡲࡓࡪࡩࡱࡥࡱ࠭঴"), bstack1l1l1l1_opy_ (u"ࠧࡔࡋࡊ࡙ࡓࡑࡎࡐ࡙ࡑࠫ঵"))
  bstack11lll11l1_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡈࡕࡅࡒࡋࡗࡐࡔࡎࡣ࡚࡙ࡅࡅࠩশ"))
  if bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩষ"):
    bstack11l1l11l1_opy_.stop(bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪস")))
  bstack1llll1ll1_opy_()
  sys.exit(1)
def bstack1ll1lll1ll_opy_(err):
  logger.critical(bstack1llll1l1l1_opy_.format(str(err)))
  bstack1l1ll1l1l1_opy_(bstack1llll1l1l1_opy_.format(str(err)), True)
  atexit.unregister(bstack1llll1ll1_opy_)
  bstack1lll111l11_opy_()
  sys.exit(1)
def bstack1lll11ll_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1l1ll1l1l1_opy_(message, True)
  atexit.unregister(bstack1llll1ll1_opy_)
  bstack1lll111l11_opy_()
  sys.exit(1)
def bstack1l1l11111l_opy_():
  global CONFIG
  global bstack1lll11ll11_opy_
  global bstack1ll1llll1l_opy_
  global bstack1l1l11l1l1_opy_
  CONFIG = bstack1l1l1ll1l_opy_()
  load_dotenv(CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡪࡴࡶࡇ࡫࡯ࡩࠬহ")))
  bstack1l11ll11l1_opy_()
  bstack1ll1l1l1ll_opy_()
  CONFIG = bstack1ll111llll_opy_(CONFIG)
  update(CONFIG, bstack1ll1llll1l_opy_)
  update(CONFIG, bstack1lll11ll11_opy_)
  CONFIG = bstack1l1ll11ll_opy_(CONFIG)
  bstack1l1l11l1l1_opy_ = bstack111ll1ll1_opy_(CONFIG)
  os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨ঺")] = bstack1l1l11l1l1_opy_.__str__()
  bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ঻"), bstack1l1l11l1l1_opy_)
  if (bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧ়ࠪ") in CONFIG and bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫঽ") in bstack1lll11ll11_opy_) or (
          bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬা") in CONFIG and bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ি") not in bstack1ll1llll1l_opy_):
    if os.getenv(bstack1l1l1l1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨী")):
      CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧু")] = os.getenv(bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪূ"))
    else:
      bstack1llll1llll_opy_()
  elif (bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪৃ") not in CONFIG and bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪৄ") in CONFIG) or (
          bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ৅") in bstack1ll1llll1l_opy_ and bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭৆") not in bstack1lll11ll11_opy_):
    del (CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ে")])
  if bstack1ll11lll1_opy_(CONFIG):
    bstack1ll1lll1ll_opy_(bstack1l1l111l1_opy_)
  bstack11lll1lll_opy_()
  bstack1l1ll111l_opy_()
  if bstack1l1l1ll111_opy_:
    CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱࠩৈ")] = bstack11l11ll11_opy_(CONFIG)
    logger.info(bstack1l11l1l1_opy_.format(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲࠪ৉")]))
  if not bstack1l1l11l1l1_opy_:
    CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৊")] = [{}]
def bstack11l11llll_opy_(config, bstack111ll1ll_opy_):
  global CONFIG
  global bstack1l1l1ll111_opy_
  CONFIG = config
  bstack1l1l1ll111_opy_ = bstack111ll1ll_opy_
def bstack1l1ll111l_opy_():
  global CONFIG
  global bstack1l1l1ll111_opy_
  if bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴࠬো") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1l1llllll1_opy_)
    bstack1l1l1ll111_opy_ = True
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨৌ"), True)
def bstack11l11ll11_opy_(config):
  bstack1lll111ll_opy_ = bstack1l1l1l1_opy_ (u"্ࠪࠫ")
  app = config[bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࠨৎ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1ll1l1l11_opy_:
      if os.path.exists(app):
        bstack1lll111ll_opy_ = bstack1ll1111l1l_opy_(config, app)
      elif bstack1ll111l11l_opy_(app):
        bstack1lll111ll_opy_ = app
      else:
        bstack1ll1lll1ll_opy_(bstack1l1llll11l_opy_.format(app))
    else:
      if bstack1ll111l11l_opy_(app):
        bstack1lll111ll_opy_ = app
      elif os.path.exists(app):
        bstack1lll111ll_opy_ = bstack1ll1111l1l_opy_(app)
      else:
        bstack1ll1lll1ll_opy_(bstack1l1ll1ll_opy_)
  else:
    if len(app) > 2:
      bstack1ll1lll1ll_opy_(bstack1l111ll111_opy_)
    elif len(app) == 2:
      if bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡵࡪࠪ৏") in app and bstack1l1l1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡥࡩࡥࠩ৐") in app:
        if os.path.exists(app[bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡷ࡬ࠬ৑")]):
          bstack1lll111ll_opy_ = bstack1ll1111l1l_opy_(config, app[bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡸ࡭࠭৒")], app[bstack1l1l1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ৓")])
        else:
          bstack1ll1lll1ll_opy_(bstack1l1llll11l_opy_.format(app))
      else:
        bstack1ll1lll1ll_opy_(bstack1l111ll111_opy_)
    else:
      for key in app:
        if key in bstack1lll111ll1_opy_:
          if key == bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡺࡨࠨ৔"):
            if os.path.exists(app[key]):
              bstack1lll111ll_opy_ = bstack1ll1111l1l_opy_(config, app[key])
            else:
              bstack1ll1lll1ll_opy_(bstack1l1llll11l_opy_.format(app))
          else:
            bstack1lll111ll_opy_ = app[key]
        else:
          bstack1ll1lll1ll_opy_(bstack1lll1llll_opy_)
  return bstack1lll111ll_opy_
def bstack1ll111l11l_opy_(bstack1lll111ll_opy_):
  import re
  bstack11l11111l_opy_ = re.compile(bstack1l1l1l1_opy_ (u"ࡶࠧࡤ࡛ࡢ࠯ࡽࡅ࠲ࡠ࠰࠮࠻࡟ࡣ࠳ࡢ࠭࡞ࠬࠧࠦ৕"))
  bstack1ll111lll_opy_ = re.compile(bstack1l1l1l1_opy_ (u"ࡷࠨ࡞࡜ࡣ࠰ࡾࡆ࠳࡚࠱࠯࠼ࡠࡤ࠴࡜࠮࡟࠭࠳ࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ৖"))
  if bstack1l1l1l1_opy_ (u"࠭ࡢࡴ࠼࠲࠳ࠬৗ") in bstack1lll111ll_opy_ or re.fullmatch(bstack11l11111l_opy_, bstack1lll111ll_opy_) or re.fullmatch(bstack1ll111lll_opy_, bstack1lll111ll_opy_):
    return True
  else:
    return False
def bstack1ll1111l1l_opy_(config, path, bstack1ll111111l_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1l1l1l1_opy_ (u"ࠧࡳࡤࠪ৘")).read()).hexdigest()
  bstack11ll1111_opy_ = bstack1lll1ll1_opy_(md5_hash)
  bstack1lll111ll_opy_ = None
  if bstack11ll1111_opy_:
    logger.info(bstack1l111ll1l1_opy_.format(bstack11ll1111_opy_, md5_hash))
    return bstack11ll1111_opy_
  bstack1l1l11ll1_opy_ = MultipartEncoder(
    fields={
      bstack1l1l1l1_opy_ (u"ࠨࡨ࡬ࡰࡪ࠭৙"): (os.path.basename(path), open(os.path.abspath(path), bstack1l1l1l1_opy_ (u"ࠩࡵࡦࠬ৚")), bstack1l1l1l1_opy_ (u"ࠪࡸࡪࡾࡴ࠰ࡲ࡯ࡥ࡮ࡴࠧ৛")),
      bstack1l1l1l1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧড়"): bstack1ll111111l_opy_
    }
  )
  response = requests.post(bstack1l11l1l11_opy_, data=bstack1l1l11ll1_opy_,
                           headers={bstack1l1l1l1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫঢ়"): bstack1l1l11ll1_opy_.content_type},
                           auth=(config[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨ৞")], config[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪয়")]))
  try:
    res = json.loads(response.text)
    bstack1lll111ll_opy_ = res[bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴࡤࡻࡲ࡭ࠩৠ")]
    logger.info(bstack11llll1l1_opy_.format(bstack1lll111ll_opy_))
    bstack1l1ll1l1ll_opy_(md5_hash, bstack1lll111ll_opy_)
  except ValueError as err:
    bstack1ll1lll1ll_opy_(bstack1l1ll1111l_opy_.format(str(err)))
  return bstack1lll111ll_opy_
def bstack11lll1lll_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack1llll11111_opy_
  bstack11l11ll1l_opy_ = 1
  bstack1l1lllll1_opy_ = 1
  if bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩৡ") in CONFIG:
    bstack1l1lllll1_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪৢ")]
  else:
    bstack1l1lllll1_opy_ = bstack11l11ll1_opy_(framework_name, args) or 1
  if bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧৣ") in CONFIG:
    bstack11l11ll1l_opy_ = len(CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ৤")])
  bstack1llll11111_opy_ = int(bstack1l1lllll1_opy_) * int(bstack11l11ll1l_opy_)
def bstack11l11ll1_opy_(framework_name, args):
  if framework_name == bstack111l1l11_opy_ and args and bstack1l1l1l1_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ৥") in args:
      bstack1l11111l_opy_ = args.index(bstack1l1l1l1_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬ০"))
      return int(args[bstack1l11111l_opy_ + 1]) or 1
  return 1
def bstack1lll1ll1_opy_(md5_hash):
  bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠨࢀࠪ১")), bstack1l1l1l1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ২"), bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ৩"))
  if os.path.exists(bstack11lllll1l_opy_):
    bstack1ll111ll1_opy_ = json.load(open(bstack11lllll1l_opy_, bstack1l1l1l1_opy_ (u"ࠫࡷࡨࠧ৪")))
    if md5_hash in bstack1ll111ll1_opy_:
      bstack1l1l1lll1l_opy_ = bstack1ll111ll1_opy_[md5_hash]
      bstack1111lll1l_opy_ = datetime.datetime.now()
      bstack1ll1l111l_opy_ = datetime.datetime.strptime(bstack1l1l1lll1l_opy_[bstack1l1l1l1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ৫")], bstack1l1l1l1_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪ৬"))
      if (bstack1111lll1l_opy_ - bstack1ll1l111l_opy_).days > 30:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack1l1l1lll1l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ৭")]):
        return None
      return bstack1l1l1lll1l_opy_[bstack1l1l1l1_opy_ (u"ࠨ࡫ࡧࠫ৮")]
  else:
    return None
def bstack1l1ll1l1ll_opy_(md5_hash, bstack1lll111ll_opy_):
  bstack1l11lllll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠩࢁࠫ৯")), bstack1l1l1l1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪৰ"))
  if not os.path.exists(bstack1l11lllll1_opy_):
    os.makedirs(bstack1l11lllll1_opy_)
  bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭ৱ")), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ৲"), bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲࡘࡴࡱࡵࡡࡥࡏࡇ࠹ࡍࡧࡳࡩ࠰࡭ࡷࡴࡴࠧ৳"))
  bstack1ll1llll11_opy_ = {
    bstack1l1l1l1_opy_ (u"ࠧࡪࡦࠪ৴"): bstack1lll111ll_opy_,
    bstack1l1l1l1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ৵"): datetime.datetime.strftime(datetime.datetime.now(), bstack1l1l1l1_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭৶")),
    bstack1l1l1l1_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ৷"): str(__version__)
  }
  if os.path.exists(bstack11lllll1l_opy_):
    bstack1ll111ll1_opy_ = json.load(open(bstack11lllll1l_opy_, bstack1l1l1l1_opy_ (u"ࠫࡷࡨࠧ৸")))
  else:
    bstack1ll111ll1_opy_ = {}
  bstack1ll111ll1_opy_[md5_hash] = bstack1ll1llll11_opy_
  with open(bstack11lllll1l_opy_, bstack1l1l1l1_opy_ (u"ࠧࡽࠫࠣ৹")) as outfile:
    json.dump(bstack1ll111ll1_opy_, outfile)
def bstack11llllll_opy_(self):
  return
def bstack1lllll11l_opy_(self):
  return
def bstack1ll11l1ll1_opy_(self):
  global bstack11l1l1l11_opy_
  bstack11l1l1l11_opy_(self)
def bstack1lllll1ll_opy_():
  global bstack1lll1l1ll_opy_
  bstack1lll1l1ll_opy_ = True
def bstack1111ll1ll_opy_(self):
  global bstack111lll1ll_opy_
  global bstack11ll1l1l_opy_
  global bstack1l11ll11_opy_
  try:
    if bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭৺") in bstack111lll1ll_opy_ and self.session_id != None and bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡵࡧࡶࡸࡘࡺࡡࡵࡷࡶࠫ৻"), bstack1l1l1l1_opy_ (u"ࠨࠩৼ")) != bstack1l1l1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ৽"):
      bstack1l1ll1ll1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ৾") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ৿")
      if bstack1l1ll1ll1_opy_ == bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ਀"):
        bstack11ll1l1ll_opy_(logger)
      if self != None:
        bstack1l1l1lll11_opy_(self, bstack1l1ll1ll1_opy_, bstack1l1l1l1_opy_ (u"࠭ࠬࠡࠩਁ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack1l1l1l1_opy_ (u"ࠧࠨਂ")
    if bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨਃ") in bstack111lll1ll_opy_ and getattr(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ਄"), None):
      bstack111ll1l1_opy_.bstack1l1l11l1l_opy_(self, bstack11ll11ll_opy_, logger, wait=True)
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦਅ") + str(e))
  bstack1l11ll11_opy_(self)
  self.session_id = None
def bstack1ll111ll_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1llll1l1ll_opy_
    global bstack111lll1ll_opy_
    command_executor = kwargs.get(bstack1l1l1l1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧਆ"), bstack1l1l1l1_opy_ (u"ࠬ࠭ਇ"))
    bstack1ll1lll11l_opy_ = False
    if type(command_executor) == str and bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩਈ") in command_executor:
      bstack1ll1lll11l_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪਉ") in str(getattr(command_executor, bstack1l1l1l1_opy_ (u"ࠨࡡࡸࡶࡱ࠭ਊ"), bstack1l1l1l1_opy_ (u"ࠩࠪ਋"))):
      bstack1ll1lll11l_opy_ = True
    else:
      return bstack11l11l1l_opy_(self, *args, **kwargs)
    if bstack1ll1lll11l_opy_:
      if kwargs.get(bstack1l1l1l1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ਌")):
        kwargs[bstack1l1l1l1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ਍")] = bstack1llll1l1ll_opy_(kwargs[bstack1l1l1l1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭਎")], bstack111lll1ll_opy_)
      elif kwargs.get(bstack1l1l1l1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ਏ")):
        kwargs[bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧਐ")] = bstack1llll1l1ll_opy_(kwargs[bstack1l1l1l1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ਑")], bstack111lll1ll_opy_)
  except Exception as e:
    logger.error(bstack1l1l1l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤ਒").format(str(e)))
  return bstack11l11l1l_opy_(self, *args, **kwargs)
def bstack11ll1ll1_opy_(self, command_executor=bstack1l1l1l1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦਓ"), *args, **kwargs):
  bstack1ll1lll11_opy_ = bstack1ll111ll_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack1ll11l1lll_opy_.on():
    return bstack1ll1lll11_opy_
  try:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨਔ").format(str(command_executor)))
    logger.debug(bstack1l1l1l1_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧਕ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩਖ") in command_executor._url:
      bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨਗ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫਘ") in command_executor):
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪਙ"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack11l1l11l1_opy_.bstack1111l111l_opy_(self)
  return bstack1ll1lll11_opy_
def bstack111l11ll_opy_(args):
  return bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫਚ") in str(args)
def bstack1ll1111l11_opy_(self, driver_command, *args, **kwargs):
  global bstack1l1l1ll1l1_opy_
  global bstack111lll11_opy_
  bstack1l1l11l111_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨਛ"), None) and bstack1l111l1ll1_opy_(
          threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫਜ"), None)
  bstack1l11l111_opy_ = getattr(self, bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭ਝ"), None) != None and getattr(self, bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧਞ"), None) == True
  if not bstack111lll11_opy_ and bstack1l1l11l1l1_opy_ and bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨਟ") in CONFIG and CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩਠ")] == True and bstack1ll1ll1l11_opy_.bstack1l1l11l11l_opy_(driver_command) and (bstack1l11l111_opy_ or bstack1l1l11l111_opy_) and not bstack111l11ll_opy_(args):
    try:
      bstack111lll11_opy_ = True
      logger.debug(bstack1l1l1l1_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥ࡬࡯ࡳࠢࡾࢁࠬਡ").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡧࡵࡪࡴࡸ࡭ࠡࡵࡦࡥࡳࠦࡻࡾࠩਢ").format(str(err)))
    bstack111lll11_opy_ = False
  response = bstack1l1l1ll1l1_opy_(self, driver_command, *args, **kwargs)
  if bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫਣ") in str(bstack111lll1ll_opy_).lower() and bstack1ll11l1lll_opy_.on():
    try:
      if driver_command == bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪਤ"):
        bstack11l1l11l1_opy_.bstack1ll1lllll1_opy_({
            bstack1l1l1l1_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭ਥ"): response[bstack1l1l1l1_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧਦ")],
            bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩਧ"): bstack11l1l11l1_opy_.current_test_uuid() if bstack11l1l11l1_opy_.current_test_uuid() else bstack1ll11l1lll_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
def bstack1l11ll1l_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack11ll1l1l_opy_
  global bstack111lll1l_opy_
  global bstack11l1l11l_opy_
  global bstack11ll11lll_opy_
  global bstack1ll1l11l11_opy_
  global bstack111lll1ll_opy_
  global bstack11l11l1l_opy_
  global bstack1ll111111_opy_
  global bstack1lll1ll1ll_opy_
  global bstack11ll11ll_opy_
  CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬਨ")] = str(bstack111lll1ll_opy_) + str(__version__)
  command_executor = bstack11lll1l1_opy_()
  logger.debug(bstack1ll11ll1l1_opy_.format(command_executor))
  proxy = bstack1ll11l1l_opy_(CONFIG, proxy)
  bstack1l1l1l11l_opy_ = 0 if bstack111lll1l_opy_ < 0 else bstack111lll1l_opy_
  try:
    if bstack11ll11lll_opy_ is True:
      bstack1l1l1l11l_opy_ = int(multiprocessing.current_process().name)
    elif bstack1ll1l11l11_opy_ is True:
      bstack1l1l1l11l_opy_ = int(threading.current_thread().name)
  except:
    bstack1l1l1l11l_opy_ = 0
  bstack1l11lllll_opy_ = bstack111lll11l_opy_(CONFIG, bstack1l1l1l11l_opy_)
  logger.debug(bstack1l1lll1111_opy_.format(str(bstack1l11lllll_opy_)))
  if bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ਩") in CONFIG and bstack1l1111ll_opy_(CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩਪ")]):
    bstack1l111llll_opy_(bstack1l11lllll_opy_)
  if bstack1l11lll1l_opy_.bstack1ll1llllll_opy_(CONFIG, bstack1l1l1l11l_opy_) and bstack1l11lll1l_opy_.bstack1ll1lll1l_opy_(bstack1l11lllll_opy_, options, desired_capabilities):
    threading.current_thread().a11yPlatform = True
    bstack1l11lll1l_opy_.set_capabilities(bstack1l11lllll_opy_, CONFIG)
  if desired_capabilities:
    bstack1l11llll_opy_ = bstack1ll111llll_opy_(desired_capabilities)
    bstack1l11llll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ਫ")] = bstack1l11lll11_opy_(CONFIG)
    bstack1l1111l1l_opy_ = bstack111lll11l_opy_(bstack1l11llll_opy_)
    if bstack1l1111l1l_opy_:
      bstack1l11lllll_opy_ = update(bstack1l1111l1l_opy_, bstack1l11lllll_opy_)
    desired_capabilities = None
  if options:
    bstack1l1l111ll_opy_(options, bstack1l11lllll_opy_)
  if not options:
    options = bstack1lll11lll_opy_(bstack1l11lllll_opy_)
  bstack11ll11ll_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪਬ"))[bstack1l1l1l11l_opy_]
  if proxy and bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨਭ")):
    options.proxy(proxy)
  if options and bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨਮ")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1l1l1111_opy_() < version.parse(bstack1l1l1l1_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩਯ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack1l11lllll_opy_)
  logger.info(bstack1llllll111_opy_)
  if bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫਰ")):
    bstack11l11l1l_opy_(self, command_executor=command_executor,
              options=options, keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫ਱")):
    bstack11l11l1l_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities, options=options,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"࠭࠲࠯࠷࠶࠲࠵࠭ਲ")):
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
    bstack1llll1lll_opy_ = bstack1l1l1l1_opy_ (u"ࠧࠨਲ਼")
    if bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࡢ࠲ࠩ਴")):
      bstack1llll1lll_opy_ = self.caps.get(bstack1l1l1l1_opy_ (u"ࠤࡲࡴࡹ࡯࡭ࡢ࡮ࡋࡹࡧ࡛ࡲ࡭ࠤਵ"))
    else:
      bstack1llll1lll_opy_ = self.capabilities.get(bstack1l1l1l1_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥਸ਼"))
    if bstack1llll1lll_opy_:
      bstack111l1111_opy_(bstack1llll1lll_opy_)
      if bstack1l1l1111_opy_() <= version.parse(bstack1l1l1l1_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫ਷")):
        self.command_executor._url = bstack1l1l1l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨਸ") + bstack1ll11l11l1_opy_ + bstack1l1l1l1_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥਹ")
      else:
        self.command_executor._url = bstack1l1l1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤ਺") + bstack1llll1lll_opy_ + bstack1l1l1l1_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤ਻")
      logger.debug(bstack1ll1l1111_opy_.format(bstack1llll1lll_opy_))
    else:
      logger.debug(bstack11l11111_opy_.format(bstack1l1l1l1_opy_ (u"ࠤࡒࡴࡹ࡯࡭ࡢ࡮ࠣࡌࡺࡨࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦ਼ࠥ")))
  except Exception as e:
    logger.debug(bstack11l11111_opy_.format(e))
  if bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ਽") in bstack111lll1ll_opy_:
    bstack1l11l1ll1l_opy_(bstack111lll1l_opy_, bstack1lll1ll1ll_opy_)
  bstack11ll1l1l_opy_ = self.session_id
  if bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫਾ") in bstack111lll1ll_opy_ or bstack1l1l1l1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬਿ") in bstack111lll1ll_opy_ or bstack1l1l1l1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬੀ") in bstack111lll1ll_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
    bstack11l1l11l1_opy_.bstack1111l111l_opy_(self)
  bstack1ll111111_opy_.append(self)
  if bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪੁ") in CONFIG and bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ੂ") in CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ੃")][bstack1l1l1l11l_opy_]:
    bstack11l1l11l_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੄")][bstack1l1l1l11l_opy_][bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ੅")]
  logger.debug(bstack11l111111_opy_.format(bstack11ll1l1l_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack1lll11lll1_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1ll1ll111l_opy_
      if(bstack1l1l1l1_opy_ (u"ࠧ࡯࡮ࡥࡧࡻ࠲࡯ࡹࠢ੆") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"࠭ࡾࠨੇ")), bstack1l1l1l1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧੈ"), bstack1l1l1l1_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ੉")), bstack1l1l1l1_opy_ (u"ࠩࡺࠫ੊")) as fp:
          fp.write(bstack1l1l1l1_opy_ (u"ࠥࠦੋ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1l1l1l1_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨੌ")))):
          with open(args[1], bstack1l1l1l1_opy_ (u"ࠬࡸ੍ࠧ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1l1l1l1_opy_ (u"࠭ࡡࡴࡻࡱࡧࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡠࡰࡨࡻࡕࡧࡧࡦࠪࡦࡳࡳࡺࡥࡹࡶ࠯ࠤࡵࡧࡧࡦࠢࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠬ੎") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1lll1lllll_opy_)
            lines.insert(1, bstack1lll11ll1l_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1l1l1l1_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤ੏")), bstack1l1l1l1_opy_ (u"ࠨࡹࠪ੐")) as bstack111l1l1l1_opy_:
              bstack111l1l1l1_opy_.writelines(lines)
        CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫੑ")] = str(bstack111lll1ll_opy_) + str(__version__)
        bstack1l1l1l11l_opy_ = 0 if bstack111lll1l_opy_ < 0 else bstack111lll1l_opy_
        try:
          if bstack11ll11lll_opy_ is True:
            bstack1l1l1l11l_opy_ = int(multiprocessing.current_process().name)
          elif bstack1ll1l11l11_opy_ is True:
            bstack1l1l1l11l_opy_ = int(threading.current_thread().name)
        except:
          bstack1l1l1l11l_opy_ = 0
        CONFIG[bstack1l1l1l1_opy_ (u"ࠥࡹࡸ࡫ࡗ࠴ࡅࠥ੒")] = False
        CONFIG[bstack1l1l1l1_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ੓")] = True
        bstack1l11lllll_opy_ = bstack111lll11l_opy_(CONFIG, bstack1l1l1l11l_opy_)
        logger.debug(bstack1l1lll1111_opy_.format(str(bstack1l11lllll_opy_)))
        if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ੔")):
          bstack1l111llll_opy_(bstack1l11lllll_opy_)
        if bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ੕") in CONFIG and bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ੖") in CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ੗")][bstack1l1l1l11l_opy_]:
          bstack11l1l11l_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ੘")][bstack1l1l1l11l_opy_][bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨਖ਼")]
        args.append(os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭ਗ਼")), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬਜ਼"), bstack1l1l1l1_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨੜ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack1l11lllll_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1l1l1l1_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤ੝"))
      bstack1ll1ll111l_opy_ = True
      return bstack11111lll1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1l1lll111_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack111lll1l_opy_
    global bstack11l1l11l_opy_
    global bstack11ll11lll_opy_
    global bstack1ll1l11l11_opy_
    global bstack111lll1ll_opy_
    CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪਫ਼")] = str(bstack111lll1ll_opy_) + str(__version__)
    bstack1l1l1l11l_opy_ = 0 if bstack111lll1l_opy_ < 0 else bstack111lll1l_opy_
    try:
      if bstack11ll11lll_opy_ is True:
        bstack1l1l1l11l_opy_ = int(multiprocessing.current_process().name)
      elif bstack1ll1l11l11_opy_ is True:
        bstack1l1l1l11l_opy_ = int(threading.current_thread().name)
    except:
      bstack1l1l1l11l_opy_ = 0
    CONFIG[bstack1l1l1l1_opy_ (u"ࠤ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ੟")] = True
    bstack1l11lllll_opy_ = bstack111lll11l_opy_(CONFIG, bstack1l1l1l11l_opy_)
    logger.debug(bstack1l1lll1111_opy_.format(str(bstack1l11lllll_opy_)))
    if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ੠")):
      bstack1l111llll_opy_(bstack1l11lllll_opy_)
    if bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੡") in CONFIG and bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ੢") in CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ੣")][bstack1l1l1l11l_opy_]:
      bstack11l1l11l_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ੤")][bstack1l1l1l11l_opy_][bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭੥")]
    import urllib
    import json
    bstack11l1l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫ੦") + urllib.parse.quote(json.dumps(bstack1l11lllll_opy_))
    browser = self.connect(bstack11l1l1l1_opy_)
    return browser
except Exception as e:
    pass
def bstack1ll1lllll_opy_():
    global bstack1ll1ll111l_opy_
    global bstack111lll1ll_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1l11l1111l_opy_
        if not bstack1l1l11l1l1_opy_:
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
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1lll11lll1_opy_
      bstack1ll1ll111l_opy_ = True
    except Exception as e:
      pass
def bstack1ll111ll1l_opy_(context, bstack1ll1l1l11l_opy_):
  try:
    context.page.evaluate(bstack1l1l1l1_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ੧"), bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨ੨")+ json.dumps(bstack1ll1l1l11l_opy_) + bstack1l1l1l1_opy_ (u"ࠧࢃࡽࠣ੩"))
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀࠦ੪"), e)
def bstack1111l1111_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1l1l1l1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ੫"), bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭੬") + json.dumps(message) + bstack1l1l1l1_opy_ (u"ࠩ࠯ࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠬ੭") + json.dumps(level) + bstack1l1l1l1_opy_ (u"ࠪࢁࢂ࠭੮"))
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࢀࢃࠢ੯"), e)
def bstack1l11l11l1l_opy_(self, url):
  global bstack1llll11l1_opy_
  try:
    bstack1l1l11l11_opy_(url)
  except Exception as err:
    logger.debug(bstack111ll1lll_opy_.format(str(err)))
  try:
    bstack1llll11l1_opy_(self, url)
  except Exception as e:
    try:
      bstack11l1lllll_opy_ = str(e)
      if any(err_msg in bstack11l1lllll_opy_ for err_msg in bstack1l1llll1l1_opy_):
        bstack1l1l11l11_opy_(url, True)
    except Exception as err:
      logger.debug(bstack111ll1lll_opy_.format(str(err)))
    raise e
def bstack1l11l11111_opy_(self):
  global bstack1l1l1111l_opy_
  bstack1l1l1111l_opy_ = self
  return
def bstack1l11ll1l11_opy_(self):
  global bstack11l1l111l_opy_
  bstack11l1l111l_opy_ = self
  return
def bstack1l11l11l1_opy_(test_name, bstack111l11ll1_opy_):
  global CONFIG
  if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫੰ"), False):
    bstack1111ll111_opy_ = os.path.relpath(bstack111l11ll1_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1111ll111_opy_)
    bstack1l1l1111l1_opy_ = suite_name + bstack1l1l1l1_opy_ (u"ࠨ࠭ࠣੱ") + test_name
    threading.current_thread().percySessionName = bstack1l1l1111l1_opy_
def bstack1ll11111l1_opy_(self, test, *args, **kwargs):
  global bstack1l1l1l1l1_opy_
  test_name = None
  bstack111l11ll1_opy_ = None
  if test:
    test_name = str(test.name)
    bstack111l11ll1_opy_ = str(test.source)
  bstack1l11l11l1_opy_(test_name, bstack111l11ll1_opy_)
  bstack1l1l1l1l1_opy_(self, test, *args, **kwargs)
def bstack1lllll1ll1_opy_(driver, bstack1l1l1111l1_opy_):
  if not bstack1lllll11ll_opy_ and bstack1l1l1111l1_opy_:
      bstack1l1ll111ll_opy_ = {
          bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡷ࡭ࡴࡴࠧੲ"): bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩੳ"),
          bstack1l1l1l1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬੴ"): {
              bstack1l1l1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨੵ"): bstack1l1l1111l1_opy_
          }
      }
      bstack1l111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠩ੶").format(json.dumps(bstack1l1ll111ll_opy_))
      driver.execute_script(bstack1l111l1l1_opy_)
  if bstack1111ll1l1_opy_:
      bstack1lllll11l1_opy_ = {
          bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬ੷"): bstack1l1l1l1_opy_ (u"࠭ࡡ࡯ࡰࡲࡸࡦࡺࡥࠨ੸"),
          bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ੹"): {
              bstack1l1l1l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭੺"): bstack1l1l1111l1_opy_ + bstack1l1l1l1_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫ੻"),
              bstack1l1l1l1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ੼"): bstack1l1l1l1_opy_ (u"ࠫ࡮ࡴࡦࡰࠩ੽")
          }
      }
      if bstack1111ll1l1_opy_.status == bstack1l1l1l1_opy_ (u"ࠬࡖࡁࡔࡕࠪ੾"):
          bstack11ll111ll_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫ੿").format(json.dumps(bstack1lllll11l1_opy_))
          driver.execute_script(bstack11ll111ll_opy_)
          bstack1l1l1lll11_opy_(driver, bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ઀"))
      elif bstack1111ll1l1_opy_.status == bstack1l1l1l1_opy_ (u"ࠨࡈࡄࡍࡑ࠭ઁ"):
          reason = bstack1l1l1l1_opy_ (u"ࠤࠥં")
          bstack1lll1l11_opy_ = bstack1l1l1111l1_opy_ + bstack1l1l1l1_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠫઃ")
          if bstack1111ll1l1_opy_.message:
              reason = str(bstack1111ll1l1_opy_.message)
              bstack1lll1l11_opy_ = bstack1lll1l11_opy_ + bstack1l1l1l1_opy_ (u"ࠫࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠫ઄") + reason
          bstack1lllll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨઅ")] = {
              bstack1l1l1l1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬઆ"): bstack1l1l1l1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ઇ"),
              bstack1l1l1l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭ઈ"): bstack1lll1l11_opy_
          }
          bstack11ll111ll_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧઉ").format(json.dumps(bstack1lllll11l1_opy_))
          driver.execute_script(bstack11ll111ll_opy_)
          bstack1l1l1lll11_opy_(driver, bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪઊ"), reason)
          bstack1111l1l1l_opy_(reason, str(bstack1111ll1l1_opy_), str(bstack111lll1l_opy_), logger)
def bstack1llll1lll1_opy_(driver, test):
  if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪઋ"), False) and CONFIG.get(bstack1l1l1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨઌ"), bstack1l1l1l1_opy_ (u"ࠨࡡࡶࡶࡲࠦઍ")) == bstack1l1l1l1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤ઎"):
      bstack1l1ll1l111_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫએ"), None)
      bstack11ll1ll11_opy_(driver, bstack1l1ll1l111_opy_, test)
  if bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ઐ"), None) and bstack1l111l1ll1_opy_(
          threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩઑ"), None):
      logger.info(bstack1l1l1l1_opy_ (u"ࠦࡆࡻࡴࡰ࡯ࡤࡸࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡨࡼࡪࡩࡵࡵ࡫ࡲࡲࠥ࡮ࡡࡴࠢࡨࡲࡩ࡫ࡤ࠯ࠢࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡮ࡹࠠࡶࡰࡧࡩࡷࡽࡡࡺ࠰ࠣࠦ઒"))
      bstack1l11lll1l_opy_.bstack11llll111_opy_(driver, class_name=test.parent.name, name=test.name, module_name=None,
                              path=test.source, bstack1ll1l111l1_opy_=bstack11ll11ll_opy_)
def bstack1l1ll1lll1_opy_(test, bstack1l1l1111l1_opy_):
    try:
      data = {}
      if test:
        data[bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪઓ")] = bstack1l1l1111l1_opy_
      if bstack1111ll1l1_opy_:
        if bstack1111ll1l1_opy_.status == bstack1l1l1l1_opy_ (u"࠭ࡐࡂࡕࡖࠫઔ"):
          data[bstack1l1l1l1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧક")] = bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨખ")
        elif bstack1111ll1l1_opy_.status == bstack1l1l1l1_opy_ (u"ࠩࡉࡅࡎࡒࠧગ"):
          data[bstack1l1l1l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪઘ")] = bstack1l1l1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫઙ")
          if bstack1111ll1l1_opy_.message:
            data[bstack1l1l1l1_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬચ")] = str(bstack1111ll1l1_opy_.message)
      user = CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨછ")]
      key = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪજ")]
      url = bstack1l1l1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠴ࢁࡽ࠯࡬ࡶࡳࡳ࠭ઝ").format(user, key, bstack11ll1l1l_opy_)
      headers = {
        bstack1l1l1l1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨઞ"): bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ટ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack1111lllll_opy_.format(str(e)))
def bstack1lllll11_opy_(test, bstack1l1l1111l1_opy_):
  global CONFIG
  global bstack11l1l111l_opy_
  global bstack1l1l1111l_opy_
  global bstack11ll1l1l_opy_
  global bstack1111ll1l1_opy_
  global bstack11l1l11l_opy_
  global bstack1l1l1l111l_opy_
  global bstack11lllllll_opy_
  global bstack1l11lll11l_opy_
  global bstack111ll11l1_opy_
  global bstack1ll111111_opy_
  global bstack11ll11ll_opy_
  try:
    if not bstack11ll1l1l_opy_:
      with open(os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭ઠ")), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬડ"), bstack1l1l1l1_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨઢ"))) as f:
        bstack1lll111l1l_opy_ = json.loads(bstack1l1l1l1_opy_ (u"ࠢࡼࠤણ") + f.read().strip() + bstack1l1l1l1_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪત") + bstack1l1l1l1_opy_ (u"ࠤࢀࠦથ"))
        bstack11ll1l1l_opy_ = bstack1lll111l1l_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1ll111111_opy_:
    for driver in bstack1ll111111_opy_:
      if bstack11ll1l1l_opy_ == driver.session_id:
        if test:
          bstack1llll1lll1_opy_(driver, test)
        bstack1lllll1ll1_opy_(driver, bstack1l1l1111l1_opy_)
  elif bstack11ll1l1l_opy_:
    bstack1l1ll1lll1_opy_(test, bstack1l1l1111l1_opy_)
  if bstack11l1l111l_opy_:
    bstack11lllllll_opy_(bstack11l1l111l_opy_)
  if bstack1l1l1111l_opy_:
    bstack1l11lll11l_opy_(bstack1l1l1111l_opy_)
  if bstack1lll1l1ll_opy_:
    bstack111ll11l1_opy_()
def bstack1lll11111l_opy_(self, test, *args, **kwargs):
  bstack1l1l1111l1_opy_ = None
  if test:
    bstack1l1l1111l1_opy_ = str(test.name)
  bstack1lllll11_opy_(test, bstack1l1l1111l1_opy_)
  bstack1l1l1l111l_opy_(self, test, *args, **kwargs)
def bstack1l1ll1111_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack111l11l1_opy_
  global CONFIG
  global bstack1ll111111_opy_
  global bstack11ll1l1l_opy_
  bstack1ll11l1ll_opy_ = None
  try:
    if bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩદ"), None):
      try:
        if not bstack11ll1l1l_opy_:
          with open(os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭ધ")), bstack1l1l1l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬન"), bstack1l1l1l1_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨ઩"))) as f:
            bstack1lll111l1l_opy_ = json.loads(bstack1l1l1l1_opy_ (u"ࠢࡼࠤપ") + f.read().strip() + bstack1l1l1l1_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪફ") + bstack1l1l1l1_opy_ (u"ࠤࢀࠦબ"))
            bstack11ll1l1l_opy_ = bstack1lll111l1l_opy_[str(threading.get_ident())]
      except:
        pass
      if bstack1ll111111_opy_:
        for driver in bstack1ll111111_opy_:
          if bstack11ll1l1l_opy_ == driver.session_id:
            bstack1ll11l1ll_opy_ = driver
    bstack1l1lllll1l_opy_ = bstack1l11lll1l_opy_.bstack1lllllll1l_opy_(test.tags)
    if bstack1ll11l1ll_opy_:
      threading.current_thread().isA11yTest = bstack1l11lll1l_opy_.bstack1ll11ll11l_opy_(bstack1ll11l1ll_opy_, bstack1l1lllll1l_opy_)
    else:
      threading.current_thread().isA11yTest = bstack1l1lllll1l_opy_
  except:
    pass
  bstack111l11l1_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1111ll1l1_opy_
  bstack1111ll1l1_opy_ = self._test
def bstack1lll1l1lll_opy_():
  global bstack111llll1_opy_
  try:
    if os.path.exists(bstack111llll1_opy_):
      os.remove(bstack111llll1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭ભ") + str(e))
def bstack1l1lll1ll_opy_():
  global bstack111llll1_opy_
  bstack1ll11llll_opy_ = {}
  try:
    if not os.path.isfile(bstack111llll1_opy_):
      with open(bstack111llll1_opy_, bstack1l1l1l1_opy_ (u"ࠫࡼ࠭મ")):
        pass
      with open(bstack111llll1_opy_, bstack1l1l1l1_opy_ (u"ࠧࡽࠫࠣય")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack111llll1_opy_):
      bstack1ll11llll_opy_ = json.load(open(bstack111llll1_opy_, bstack1l1l1l1_opy_ (u"࠭ࡲࡣࠩર")))
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡵࡩࡦࡪࡩ࡯ࡩࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠢࡩ࡭ࡱ࡫࠺ࠡࠩ઱") + str(e))
  finally:
    return bstack1ll11llll_opy_
def bstack1l11l1ll1l_opy_(platform_index, item_index):
  global bstack111llll1_opy_
  try:
    bstack1ll11llll_opy_ = bstack1l1lll1ll_opy_()
    bstack1ll11llll_opy_[item_index] = platform_index
    with open(bstack111llll1_opy_, bstack1l1l1l1_opy_ (u"ࠣࡹ࠮ࠦલ")) as outfile:
      json.dump(bstack1ll11llll_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧળ") + str(e))
def bstack11l11l1ll_opy_(bstack1l111lllll_opy_):
  global CONFIG
  bstack1ll1ll1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࠫ઴")
  if not bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧવ") in CONFIG:
    logger.info(bstack1l1l1l1_opy_ (u"ࠬࡔ࡯ࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠤࡵࡧࡳࡴࡧࡧࠤࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢࡵࡩࡵࡵࡲࡵࠢࡩࡳࡷࠦࡒࡰࡤࡲࡸࠥࡸࡵ࡯ࠩશ"))
  try:
    platform = CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩષ")][bstack1l111lllll_opy_]
    if bstack1l1l1l1_opy_ (u"ࠧࡰࡵࠪસ") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"ࠨࡱࡶࠫહ")]) + bstack1l1l1l1_opy_ (u"ࠩ࠯ࠤࠬ઺")
    if bstack1l1l1l1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭઻") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴ઼ࠧ")]) + bstack1l1l1l1_opy_ (u"ࠬ࠲ࠠࠨઽ")
    if bstack1l1l1l1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪા") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫિ")]) + bstack1l1l1l1_opy_ (u"ࠨ࠮ࠣࠫી")
    if bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫુ") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬૂ")]) + bstack1l1l1l1_opy_ (u"ࠫ࠱ࠦࠧૃ")
    if bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪૄ") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫૅ")]) + bstack1l1l1l1_opy_ (u"ࠧ࠭ࠢࠪ૆")
    if bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩે") in platform:
      bstack1ll1ll1l1_opy_ += str(platform[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪૈ")]) + bstack1l1l1l1_opy_ (u"ࠪ࠰ࠥ࠭ૉ")
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡘࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡹࡸࡩ࡯ࡩࠣࡪࡴࡸࠠࡳࡧࡳࡳࡷࡺࠠࡨࡧࡱࡩࡷࡧࡴࡪࡱࡱࠫ૊") + str(e))
  finally:
    if bstack1ll1ll1l1_opy_[len(bstack1ll1ll1l1_opy_) - 2:] == bstack1l1l1l1_opy_ (u"ࠬ࠲ࠠࠨો"):
      bstack1ll1ll1l1_opy_ = bstack1ll1ll1l1_opy_[:-2]
    return bstack1ll1ll1l1_opy_
def bstack1111l1l11_opy_(path, bstack1ll1ll1l1_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1ll1ll11ll_opy_ = ET.parse(path)
    bstack1lll1l1l1_opy_ = bstack1ll1ll11ll_opy_.getroot()
    bstack1llll111ll_opy_ = None
    for suite in bstack1lll1l1l1_opy_.iter(bstack1l1l1l1_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬૌ")):
      if bstack1l1l1l1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫્ࠧ") in suite.attrib:
        suite.attrib[bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭૎")] += bstack1l1l1l1_opy_ (u"ࠩࠣࠫ૏") + bstack1ll1ll1l1_opy_
        bstack1llll111ll_opy_ = suite
    bstack1lll11l11l_opy_ = None
    for robot in bstack1lll1l1l1_opy_.iter(bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩૐ")):
      bstack1lll11l11l_opy_ = robot
    bstack1111llll1_opy_ = len(bstack1lll11l11l_opy_.findall(bstack1l1l1l1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ૑")))
    if bstack1111llll1_opy_ == 1:
      bstack1lll11l11l_opy_.remove(bstack1lll11l11l_opy_.findall(bstack1l1l1l1_opy_ (u"ࠬࡹࡵࡪࡶࡨࠫ૒"))[0])
      bstack1llll1l111_opy_ = ET.Element(bstack1l1l1l1_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬ૓"), attrib={bstack1l1l1l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ૔"): bstack1l1l1l1_opy_ (u"ࠨࡕࡸ࡭ࡹ࡫ࡳࠨ૕"), bstack1l1l1l1_opy_ (u"ࠩ࡬ࡨࠬ૖"): bstack1l1l1l1_opy_ (u"ࠪࡷ࠵࠭૗")})
      bstack1lll11l11l_opy_.insert(1, bstack1llll1l111_opy_)
      bstack1l1ll1llll_opy_ = None
      for suite in bstack1lll11l11l_opy_.iter(bstack1l1l1l1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ૘")):
        bstack1l1ll1llll_opy_ = suite
      bstack1l1ll1llll_opy_.append(bstack1llll111ll_opy_)
      bstack11111l1l_opy_ = None
      for status in bstack1llll111ll_opy_.iter(bstack1l1l1l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ૙")):
        bstack11111l1l_opy_ = status
      bstack1l1ll1llll_opy_.append(bstack11111l1l_opy_)
    bstack1ll1ll11ll_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠫ૚") + str(e))
def bstack11llll1l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1lll111l1_opy_
  global CONFIG
  if bstack1l1l1l1_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࡰࡢࡶ࡫ࠦ૛") in options:
    del options[bstack1l1l1l1_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࡱࡣࡷ࡬ࠧ૜")]
  bstack11l1llll1_opy_ = bstack1l1lll1ll_opy_()
  for bstack1l1ll11l11_opy_ in bstack11l1llll1_opy_.keys():
    path = os.path.join(os.getcwd(), bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡧࡵࡴࡠࡴࡨࡷࡺࡲࡴࡴࠩ૝"), str(bstack1l1ll11l11_opy_), bstack1l1l1l1_opy_ (u"ࠪࡳࡺࡺࡰࡶࡶ࠱ࡼࡲࡲࠧ૞"))
    bstack1111l1l11_opy_(path, bstack11l11l1ll_opy_(bstack11l1llll1_opy_[bstack1l1ll11l11_opy_]))
  bstack1lll1l1lll_opy_()
  return bstack1lll111l1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l11lll1ll_opy_(self, ff_profile_dir):
  global bstack1llllllll_opy_
  if not ff_profile_dir:
    return None
  return bstack1llllllll_opy_(self, ff_profile_dir)
def bstack11l111l1l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1ll1lll111_opy_
  bstack1llll1ll_opy_ = []
  if bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ૟") in CONFIG:
    bstack1llll1ll_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨૠ")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1l1l1l1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࠢૡ")],
      pabot_args[bstack1l1l1l1_opy_ (u"ࠢࡷࡧࡵࡦࡴࡹࡥࠣૢ")],
      argfile,
      pabot_args.get(bstack1l1l1l1_opy_ (u"ࠣࡪ࡬ࡺࡪࠨૣ")),
      pabot_args[bstack1l1l1l1_opy_ (u"ࠤࡳࡶࡴࡩࡥࡴࡵࡨࡷࠧ૤")],
      platform[0],
      bstack1ll1lll111_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1l1l1l1_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࡫࡯࡬ࡦࡵࠥ૥")] or [(bstack1l1l1l1_opy_ (u"ࠦࠧ૦"), None)]
    for platform in enumerate(bstack1llll1ll_opy_)
  ]
def bstack1lll1l1l_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1111l11ll_opy_=bstack1l1l1l1_opy_ (u"ࠬ࠭૧")):
  global bstack1ll111l1_opy_
  self.platform_index = platform_index
  self.bstack111l111l_opy_ = bstack1111l11ll_opy_
  bstack1ll111l1_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1ll1ll11l_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack11111ll1_opy_
  global bstack11111lll_opy_
  bstack111ll1l1l_opy_ = copy.deepcopy(item)
  if not bstack1l1l1l1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ૨") in item.options:
    bstack111ll1l1l_opy_.options[bstack1l1l1l1_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩ૩")] = []
  bstack1lll1111_opy_ = bstack111ll1l1l_opy_.options[bstack1l1l1l1_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ૪")].copy()
  for v in bstack111ll1l1l_opy_.options[bstack1l1l1l1_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ૫")]:
    if bstack1l1l1l1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡓࡐࡆ࡚ࡆࡐࡔࡐࡍࡓࡊࡅ࡙ࠩ૬") in v:
      bstack1lll1111_opy_.remove(v)
    if bstack1l1l1l1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡇࡑࡏࡁࡓࡉࡖࠫ૭") in v:
      bstack1lll1111_opy_.remove(v)
    if bstack1l1l1l1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡉࡋࡆࡍࡑࡆࡅࡑࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ૮") in v:
      bstack1lll1111_opy_.remove(v)
  bstack1lll1111_opy_.insert(0, bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜࠿ࢁࡽࠨ૯").format(bstack111ll1l1l_opy_.platform_index))
  bstack1lll1111_opy_.insert(0, bstack1l1l1l1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࠾ࢀࢃࠧ૰").format(bstack111ll1l1l_opy_.bstack111l111l_opy_))
  bstack111ll1l1l_opy_.options[bstack1l1l1l1_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ૱")] = bstack1lll1111_opy_
  if bstack11111lll_opy_:
    bstack111ll1l1l_opy_.options[bstack1l1l1l1_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ૲")].insert(0, bstack1l1l1l1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕ࠽ࡿࢂ࠭૳").format(bstack11111lll_opy_))
  return bstack11111ll1_opy_(caller_id, datasources, is_last, bstack111ll1l1l_opy_, outs_dir)
def bstack1l11l1l1l1_opy_(command, item_index):
  if bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ૴")):
    os.environ[bstack1l1l1l1_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭૵")] = json.dumps(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ૶")][item_index % bstack1lllll111_opy_])
  global bstack11111lll_opy_
  if bstack11111lll_opy_:
    command[0] = command[0].replace(bstack1l1l1l1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭૷"), bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡴࡦ࡮ࠤࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠥ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠤࠬ૸") + str(
      item_index) + bstack1l1l1l1_opy_ (u"ࠩࠣࠫૹ") + bstack11111lll_opy_, 1)
  else:
    command[0] = command[0].replace(bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩૺ"),
                                    bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡷࡩࡱࠠࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠡ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨૻ") + str(item_index), 1)
def bstack1llllllll1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1l111ll1ll_opy_
  bstack1l11l1l1l1_opy_(command, item_index)
  return bstack1l111ll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1111111l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1l111ll1ll_opy_
  bstack1l11l1l1l1_opy_(command, item_index)
  return bstack1l111ll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1l11l11lll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1l111ll1ll_opy_
  bstack1l11l1l1l1_opy_(command, item_index)
  return bstack1l111ll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack1ll11l1l1l_opy_(self, runner, quiet=False, capture=True):
  global bstack1l1l111l_opy_
  bstack11ll1lll1_opy_ = bstack1l1l111l_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack1l1l1l1_opy_ (u"ࠬ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࡠࡣࡵࡶࠬૼ")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1l1l1l1_opy_ (u"࠭ࡥࡹࡥࡢࡸࡷࡧࡣࡦࡤࡤࡧࡰࡥࡡࡳࡴࠪ૽")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack11ll1lll1_opy_
def bstack1111ll11_opy_(self, name, context, *args):
  os.environ[bstack1l1l1l1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ૾")] = json.dumps(CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૿")][int(threading.current_thread()._name) % bstack1lllll111_opy_])
  global bstack11l1llll_opy_
  if name == bstack1l1l1l1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠪ଀"):
    bstack11l1llll_opy_(self, name, context, *args)
    try:
      if not bstack1lllll11ll_opy_:
        bstack1ll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack111111l11_opy_(bstack1l1l1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩଁ")) else context.browser
        bstack1ll1l1l11l_opy_ = str(self.feature.name)
        bstack1ll111ll1l_opy_(context, bstack1ll1l1l11l_opy_)
        bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩଂ") + json.dumps(bstack1ll1l1l11l_opy_) + bstack1l1l1l1_opy_ (u"ࠬࢃࡽࠨଃ"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡨࡨࡥࡹࡻࡲࡦ࠼ࠣࡿࢂ࠭଄").format(str(e)))
  elif name == bstack1l1l1l1_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩଅ"):
    bstack11l1llll_opy_(self, name, context, *args)
    try:
      if not hasattr(self, bstack1l1l1l1_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࡠࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪଆ")):
        self.driver_before_scenario = True
      if (not bstack1lllll11ll_opy_):
        scenario_name = args[0].name
        feature_name = bstack1ll1l1l11l_opy_ = str(self.feature.name)
        bstack1ll1l1l11l_opy_ = feature_name + bstack1l1l1l1_opy_ (u"ࠩࠣ࠱ࠥ࠭ଇ") + scenario_name
        bstack1ll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack111111l11_opy_(bstack1l1l1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩଈ")) else context.browser
        if self.driver_before_scenario:
          bstack1ll111ll1l_opy_(context, bstack1ll1l1l11l_opy_)
          bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩଉ") + json.dumps(bstack1ll1l1l11l_opy_) + bstack1l1l1l1_opy_ (u"ࠬࢃࡽࠨଊ"))
    except Exception as e:
      logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱ࠽ࠤࢀࢃࠧଋ").format(str(e)))
  elif name == bstack1l1l1l1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨଌ"):
    try:
      bstack1l1l1l11_opy_ = args[0].status.name
      bstack1ll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧ଍") in threading.current_thread().__dict__.keys() else context.browser
      if str(bstack1l1l1l11_opy_).lower() == bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ଎"):
        bstack1111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࠫଏ")
        bstack1lll1llll1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࠬଐ")
        bstack1l1l11lll_opy_ = bstack1l1l1l1_opy_ (u"ࠬ࠭଑")
        try:
          import traceback
          bstack1111l1l1_opy_ = self.exception.__class__.__name__
          bstack1lll1l1111_opy_ = traceback.format_tb(self.exc_traceback)
          bstack1lll1llll1_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠠࠨ଒").join(bstack1lll1l1111_opy_)
          bstack1l1l11lll_opy_ = bstack1lll1l1111_opy_[-1]
        except Exception as e:
          logger.debug(bstack1ll1l111ll_opy_.format(str(e)))
        bstack1111l1l1_opy_ += bstack1l1l11lll_opy_
        bstack1111l1111_opy_(context, json.dumps(str(args[0].name) + bstack1l1l1l1_opy_ (u"ࠢࠡ࠯ࠣࡊࡦ࡯࡬ࡦࡦࠤࡠࡳࠨଓ") + str(bstack1lll1llll1_opy_)),
                            bstack1l1l1l1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢଔ"))
        if self.driver_before_scenario:
          bstack11llll11l_opy_(getattr(context, bstack1l1l1l1_opy_ (u"ࠩࡳࡥ࡬࡫ࠧକ"), None), bstack1l1l1l1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥଖ"), bstack1111l1l1_opy_)
          bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩଗ") + json.dumps(str(args[0].name) + bstack1l1l1l1_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦଘ") + str(bstack1lll1llll1_opy_)) + bstack1l1l1l1_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭ଙ"))
        if self.driver_before_scenario:
          bstack1l1l1lll11_opy_(bstack1ll11l1ll_opy_, bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧଚ"), bstack1l1l1l1_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧଛ") + str(bstack1111l1l1_opy_))
      else:
        bstack1111l1111_opy_(context, bstack1l1l1l1_opy_ (u"ࠤࡓࡥࡸࡹࡥࡥࠣࠥଜ"), bstack1l1l1l1_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣଝ"))
        if self.driver_before_scenario:
          bstack11llll11l_opy_(getattr(context, bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡧࡦࠩଞ"), None), bstack1l1l1l1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧଟ"))
        bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫଠ") + json.dumps(str(args[0].name) + bstack1l1l1l1_opy_ (u"ࠢࠡ࠯ࠣࡔࡦࡹࡳࡦࡦࠤࠦଡ")) + bstack1l1l1l1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧଢ"))
        if self.driver_before_scenario:
          bstack1l1l1lll11_opy_(bstack1ll11l1ll_opy_, bstack1l1l1l1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤଣ"))
    except Exception as e:
      logger.debug(bstack1l1l1l1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬତ").format(str(e)))
  elif name == bstack1l1l1l1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫଥ"):
    try:
      bstack1ll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack111111l11_opy_(bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫଦ")) else context.browser
      if context.failed is True:
        bstack1111111ll_opy_ = []
        bstack11ll11l1l_opy_ = []
        bstack1l1l1l1111_opy_ = []
        bstack1l1111111_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠧଧ")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack1111111ll_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1lll1l1111_opy_ = traceback.format_tb(exc_tb)
            bstack11lll11l_opy_ = bstack1l1l1l1_opy_ (u"ࠧࠡࠩନ").join(bstack1lll1l1111_opy_)
            bstack11ll11l1l_opy_.append(bstack11lll11l_opy_)
            bstack1l1l1l1111_opy_.append(bstack1lll1l1111_opy_[-1])
        except Exception as e:
          logger.debug(bstack1ll1l111ll_opy_.format(str(e)))
        bstack1111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࠩ଩")
        for i in range(len(bstack1111111ll_opy_)):
          bstack1111l1l1_opy_ += bstack1111111ll_opy_[i] + bstack1l1l1l1111_opy_[i] + bstack1l1l1l1_opy_ (u"ࠩ࡟ࡲࠬପ")
        bstack1l1111111_opy_ = bstack1l1l1l1_opy_ (u"ࠪࠤࠬଫ").join(bstack11ll11l1l_opy_)
        if not self.driver_before_scenario:
          bstack1111l1111_opy_(context, bstack1l1111111_opy_, bstack1l1l1l1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥବ"))
          bstack11llll11l_opy_(getattr(context, bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡨࡧࠪଭ"), None), bstack1l1l1l1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨମ"), bstack1111l1l1_opy_)
          bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬଯ") + json.dumps(bstack1l1111111_opy_) + bstack1l1l1l1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡥࡳࡴࡲࡶࠧࢃࡽࠨର"))
          bstack1l1l1lll11_opy_(bstack1ll11l1ll_opy_, bstack1l1l1l1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ଱"), bstack1l1l1l1_opy_ (u"ࠥࡗࡴࡳࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱࡶࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥࡢ࡮ࠣଲ") + str(bstack1111l1l1_opy_))
          bstack1lll1ll11_opy_ = bstack1ll1l1ll1l_opy_(bstack1l1111111_opy_, self.feature.name, logger)
          if (bstack1lll1ll11_opy_ != None):
            bstack1l11l11l_opy_.append(bstack1lll1ll11_opy_)
      else:
        if not self.driver_before_scenario:
          bstack1111l1111_opy_(context, bstack1l1l1l1_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢଳ") + str(self.feature.name) + bstack1l1l1l1_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢ଴"), bstack1l1l1l1_opy_ (u"ࠨࡩ࡯ࡨࡲࠦଵ"))
          bstack11llll11l_opy_(getattr(context, bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡪࡩࠬଶ"), None), bstack1l1l1l1_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣଷ"))
          bstack1ll11l1ll_opy_.execute_script(bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧସ") + json.dumps(bstack1l1l1l1_opy_ (u"ࠥࡊࡪࡧࡴࡶࡴࡨ࠾ࠥࠨହ") + str(self.feature.name) + bstack1l1l1l1_opy_ (u"ࠦࠥࡶࡡࡴࡵࡨࡨࠦࠨ଺")) + bstack1l1l1l1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ଻"))
          bstack1l1l1lll11_opy_(bstack1ll11l1ll_opy_, bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ଼࠭"))
          bstack1lll1ll11_opy_ = bstack1ll1l1ll1l_opy_(bstack1l1111111_opy_, self.feature.name, logger)
          if (bstack1lll1ll11_opy_ != None):
            bstack1l11l11l_opy_.append(bstack1lll1ll11_opy_)
    except Exception as e:
      logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡱࡦࡸ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡫࡫ࡡࡵࡷࡵࡩ࠿ࠦࡻࡾࠩଽ").format(str(e)))
  else:
    bstack11l1llll_opy_(self, name, context, *args)
  if name in [bstack1l1l1l1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨା"), bstack1l1l1l1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪି")]:
    bstack11l1llll_opy_(self, name, context, *args)
    if (name == bstack1l1l1l1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫୀ") and self.driver_before_scenario) or (
            name == bstack1l1l1l1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫୁ") and not self.driver_before_scenario):
      try:
        bstack1ll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack111111l11_opy_(bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫୂ")) else context.browser
        bstack1ll11l1ll_opy_.quit()
      except Exception:
        pass
def bstack11lll1ll1_opy_(config, startdir):
  return bstack1l1l1l1_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࠲ࢀࠦୃ").format(bstack1l1l1l1_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠨୄ"))
notset = Notset()
def bstack1l111lll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1l1llll1l_opy_
  if str(name).lower() == bstack1l1l1l1_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨ୅"):
    return bstack1l1l1l1_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣ୆")
  else:
    return bstack1l1llll1l_opy_(self, name, default, skip)
def bstack1l11ll1111_opy_(item, when):
  global bstack11l1lll1l_opy_
  try:
    bstack11l1lll1l_opy_(item, when)
  except Exception as e:
    pass
def bstack1111l1ll_opy_():
  return
def bstack1lll1ll11l_opy_(type, name, status, reason, bstack11ll1l1l1_opy_, bstack11111ll11_opy_):
  bstack1l1ll111ll_opy_ = {
    bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪେ"): type,
    bstack1l1l1l1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧୈ"): {}
  }
  if type == bstack1l1l1l1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ୉"):
    bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ୊")][bstack1l1l1l1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ୋ")] = bstack11ll1l1l1_opy_
    bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫୌ")][bstack1l1l1l1_opy_ (u"ࠩࡧࡥࡹࡧ୍ࠧ")] = json.dumps(str(bstack11111ll11_opy_))
  if type == bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ୎"):
    bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ୏")][bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ୐")] = name
  if type == bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ୑"):
    bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ୒")][bstack1l1l1l1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ୓")] = status
    if status == bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ୔"):
      bstack1l1ll111ll_opy_[bstack1l1l1l1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭୕")][bstack1l1l1l1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫୖ")] = json.dumps(str(reason))
  bstack1l111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪୗ").format(json.dumps(bstack1l1ll111ll_opy_))
  return bstack1l111l1l1_opy_
def bstack1l1111ll1_opy_(driver_command, response):
    if driver_command == bstack1l1l1l1_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪ୘"):
        bstack11l1l11l1_opy_.bstack1ll1lllll1_opy_({
            bstack1l1l1l1_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭୙"): response[bstack1l1l1l1_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧ୚")],
            bstack1l1l1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ୛"): bstack11l1l11l1_opy_.current_test_uuid()
        })
def bstack1l1l1lll_opy_(item, call, rep):
  global bstack1ll1l1ll11_opy_
  global bstack1ll111111_opy_
  global bstack1lllll11ll_opy_
  name = bstack1l1l1l1_opy_ (u"ࠪࠫଡ଼")
  try:
    if rep.when == bstack1l1l1l1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩଢ଼"):
      bstack11ll1l1l_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1lllll11ll_opy_:
          name = str(rep.nodeid)
          bstack1l11l1ll11_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭୞"), name, bstack1l1l1l1_opy_ (u"࠭ࠧୟ"), bstack1l1l1l1_opy_ (u"ࠧࠨୠ"), bstack1l1l1l1_opy_ (u"ࠨࠩୡ"), bstack1l1l1l1_opy_ (u"ࠩࠪୢ"))
          threading.current_thread().bstack11llllll1_opy_ = name
          for driver in bstack1ll111111_opy_:
            if bstack11ll1l1l_opy_ == driver.session_id:
              driver.execute_script(bstack1l11l1ll11_opy_)
      except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪୣ").format(str(e)))
      try:
        bstack1ll1l1lll_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack1l1l1l1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ୤"):
          status = bstack1l1l1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ୥") if rep.outcome.lower() == bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭୦") else bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ୧")
          reason = bstack1l1l1l1_opy_ (u"ࠨࠩ୨")
          if status == bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ୩"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨ୪") if status == bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ୫") else bstack1l1l1l1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ୬")
          data = name + bstack1l1l1l1_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨ୭") if status == bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ୮") else name + bstack1l1l1l1_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫ୯") + reason
          bstack11l1111l1_opy_ = bstack1lll1ll11l_opy_(bstack1l1l1l1_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫ୰"), bstack1l1l1l1_opy_ (u"ࠪࠫୱ"), bstack1l1l1l1_opy_ (u"ࠫࠬ୲"), bstack1l1l1l1_opy_ (u"ࠬ࠭୳"), level, data)
          for driver in bstack1ll111111_opy_:
            if bstack11ll1l1l_opy_ == driver.session_id:
              driver.execute_script(bstack11l1111l1_opy_)
      except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ୴").format(str(e)))
  except Exception as e:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫ୵").format(str(e)))
  bstack1ll1l1ll11_opy_(item, call, rep)
def bstack11ll1ll11_opy_(driver, bstack1l11lll111_opy_, test=None):
  global bstack111lll1l_opy_
  if test != None:
    bstack1lll1ll111_opy_ = test.get(bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭୶"), bstack1l1l1l1_opy_ (u"ࠩࠪ୷"))
    bstack111l111l1_opy_ = test.get(bstack1l1l1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ୸"), bstack1l1l1l1_opy_ (u"ࠫࠬ୹"))
    PercySDK.screenshot(driver, bstack1l11lll111_opy_, bstack1lll1ll111_opy_=bstack1lll1ll111_opy_, bstack111l111l1_opy_=bstack111l111l1_opy_, bstack11l1lll11_opy_=bstack111lll1l_opy_)
  else:
    PercySDK.screenshot(driver, bstack1l11lll111_opy_)
def bstack1l1l11l1ll_opy_(driver):
  if bstack1l11l11l11_opy_.bstack11l1ll11_opy_() is True or bstack1l11l11l11_opy_.capturing() is True:
    return
  bstack1l11l11l11_opy_.bstack111l1llll_opy_()
  while not bstack1l11l11l11_opy_.bstack11l1ll11_opy_():
    bstack1l1ll11l_opy_ = bstack1l11l11l11_opy_.bstack1l1llll11_opy_()
    bstack11ll1ll11_opy_(driver, bstack1l1ll11l_opy_)
  bstack1l11l11l11_opy_.bstack111lllll_opy_()
def bstack1l1lll1l11_opy_(sequence, driver_command, response = None, bstack1ll1llll1_opy_ = None, args = None):
    try:
      if sequence != bstack1l1l1l1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬ୺"):
        return
      if not CONFIG.get(bstack1l1l1l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ୻"), False):
        return
      bstack1l1ll11l_opy_ = bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୼"), None)
      for command in bstack1ll1ll1l1l_opy_:
        if command == driver_command:
          for driver in bstack1ll111111_opy_:
            bstack1l1l11l1ll_opy_(driver)
      bstack1lll1ll1l_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫ୽"), bstack1l1l1l1_opy_ (u"ࠤࡤࡹࡹࡵࠢ୾"))
      if driver_command in bstack1l1l1l1l11_opy_[bstack1lll1ll1l_opy_]:
        bstack1l11l11l11_opy_.bstack1ll1111ll1_opy_(bstack1l1ll11l_opy_, driver_command)
    except Exception as e:
      pass
def bstack11l11lll1_opy_(framework_name):
  global bstack111lll1ll_opy_
  global bstack1ll1ll111l_opy_
  global bstack11lllll1_opy_
  bstack111lll1ll_opy_ = framework_name
  logger.info(bstack1ll11l11ll_opy_.format(bstack111lll1ll_opy_.split(bstack1l1l1l1_opy_ (u"ࠪ࠱ࠬ୿"))[0]))
  bstack1l111111_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1l1l11l1l1_opy_:
      Service.start = bstack11llllll_opy_
      Service.stop = bstack1lllll11l_opy_
      webdriver.Remote.get = bstack1l11l11l1l_opy_
      WebDriver.close = bstack1ll11l1ll1_opy_
      WebDriver.quit = bstack1111ll1ll_opy_
      webdriver.Remote.__init__ = bstack1l11ll1l_opy_
      WebDriver.getAccessibilityResults = getAccessibilityResults
      WebDriver.get_accessibility_results = getAccessibilityResults
      WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
      WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
      WebDriver.performScan = perform_scan
      WebDriver.perform_scan = perform_scan
    if not bstack1l1l11l1l1_opy_:
        webdriver.Remote.__init__ = bstack11ll1ll1_opy_
    WebDriver.execute = bstack1ll1111l11_opy_
    bstack1ll1ll111l_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1l1l11l1l1_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack1lllll1ll_opy_
  except Exception as e:
    pass
  bstack1ll1lllll_opy_()
  if not bstack1ll1ll111l_opy_:
    bstack1lll11ll_opy_(bstack1l1l1l1_opy_ (u"ࠦࡕࡧࡣ࡬ࡣࡪࡩࡸࠦ࡮ࡰࡶࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠨ஀"), bstack1l11ll111l_opy_)
  if bstack1l1l1l1ll1_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack1ll11111ll_opy_
    except Exception as e:
      logger.error(bstack1ll1lll1l1_opy_.format(str(e)))
  if bstack11l1ll1ll_opy_():
    bstack1lllll1l1l_opy_(CONFIG, logger)
  if (bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ஁") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if CONFIG.get(bstack1l1l1l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬஂ"), False):
          bstack111l1l111_opy_(bstack1l1lll1l11_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l11lll1ll_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack1l11ll1l11_opy_
      except Exception as e:
        logger.warn(bstack1llll11ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1l11l11111_opy_
      except Exception as e:
        logger.debug(bstack1ll1ll11_opy_ + str(e))
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1llll11ll_opy_)
    Output.start_test = bstack1ll11111l1_opy_
    Output.end_test = bstack1lll11111l_opy_
    TestStatus.__init__ = bstack1l1ll1111_opy_
    QueueItem.__init__ = bstack1lll1l1l_opy_
    pabot._create_items = bstack11l111l1l_opy_
    try:
      from pabot import __version__ as bstack1ll1l11l1_opy_
      if version.parse(bstack1ll1l11l1_opy_) >= version.parse(bstack1l1l1l1_opy_ (u"ࠧ࠳࠰࠴࠹࠳࠶ࠧஃ")):
        pabot._run = bstack1l11l11lll_opy_
      elif version.parse(bstack1ll1l11l1_opy_) >= version.parse(bstack1l1l1l1_opy_ (u"ࠨ࠴࠱࠵࠸࠴࠰ࠨ஄")):
        pabot._run = bstack1111111l1_opy_
      else:
        pabot._run = bstack1llllllll1_opy_
    except Exception as e:
      pabot._run = bstack1llllllll1_opy_
    pabot._create_command_for_execution = bstack1ll1ll11l_opy_
    pabot._report_results = bstack11llll1l_opy_
  if bstack1l1l1l1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩஅ") in str(framework_name).lower():
    if not bstack1l1l11l1l1_opy_:
      return
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1ll1l11ll1_opy_)
    Runner.run_hook = bstack1111ll11_opy_
    Step.run = bstack1ll11l1l1l_opy_
  if bstack1l1l1l1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪஆ") in str(framework_name).lower():
    if not bstack1l1l11l1l1_opy_:
      return
    try:
      if CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪஇ"), False):
          bstack111l1l111_opy_(bstack1l1lll1l11_opy_)
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
def bstack111111l1_opy_():
  global CONFIG
  if bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬஈ") in CONFIG and int(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭உ")]) > 1:
    logger.warn(bstack1ll1lll1_opy_)
def bstack1ll1ll111_opy_(arg, bstack1l1ll11l1_opy_, bstack1ll11lllll_opy_=None):
  global CONFIG
  global bstack1ll11l11l1_opy_
  global bstack1l1l1ll111_opy_
  global bstack1l1l11l1l1_opy_
  global bstack1l111l111_opy_
  bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧஊ")
  if bstack1l1ll11l1_opy_ and isinstance(bstack1l1ll11l1_opy_, str):
    bstack1l1ll11l1_opy_ = eval(bstack1l1ll11l1_opy_)
  CONFIG = bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨ஋")]
  bstack1ll11l11l1_opy_ = bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪ஌")]
  bstack1l1l1ll111_opy_ = bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ஍")]
  bstack1l1l11l1l1_opy_ = bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧஎ")]
  bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ஏ"), bstack1l1l11l1l1_opy_)
  os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨஐ")] = bstack11lll11l1_opy_
  os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌ࠭஑")] = json.dumps(CONFIG)
  os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡉࡗࡅࡣ࡚ࡘࡌࠨஒ")] = bstack1ll11l11l1_opy_
  os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪஓ")] = str(bstack1l1l1ll111_opy_)
  os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡐ࡚ࡍࡉࡏࠩஔ")] = str(True)
  if bstack1l1ll1l1_opy_(arg, [bstack1l1l1l1_opy_ (u"ࠫ࠲ࡴࠧக"), bstack1l1l1l1_opy_ (u"ࠬ࠳࠭࡯ࡷࡰࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭஖")]) != -1:
    os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖ࡙ࡕࡇࡖࡘࡤࡖࡁࡓࡃࡏࡐࡊࡒࠧ஗")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1llll1l1l_opy_)
    return
  bstack1l1ll1l11_opy_()
  global bstack1llll11111_opy_
  global bstack111lll1l_opy_
  global bstack1ll1lll111_opy_
  global bstack11111lll_opy_
  global bstack1l1l11ll1l_opy_
  global bstack11lllll1_opy_
  global bstack11ll11lll_opy_
  arg.append(bstack1l1l1l1_opy_ (u"ࠢ࠮࡙ࠥ஘"))
  arg.append(bstack1l1l1l1_opy_ (u"ࠣ࡫ࡪࡲࡴࡸࡥ࠻ࡏࡲࡨࡺࡲࡥࠡࡣ࡯ࡶࡪࡧࡤࡺࠢ࡬ࡱࡵࡵࡲࡵࡧࡧ࠾ࡵࡿࡴࡦࡵࡷ࠲ࡕࡿࡴࡦࡵࡷ࡛ࡦࡸ࡮ࡪࡰࡪࠦங"))
  arg.append(bstack1l1l1l1_opy_ (u"ࠤ࠰࡛ࠧச"))
  arg.append(bstack1l1l1l1_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳࡧ࠽ࡘ࡭࡫ࠠࡩࡱࡲ࡯࡮ࡳࡰ࡭ࠤ஛"))
  global bstack11l11l1l_opy_
  global bstack1l11ll11_opy_
  global bstack1l1l1ll1l1_opy_
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
    bstack1l1l1ll1l1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack1lll11l1_opy_(CONFIG) and bstack1lll11llll_opy_():
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
    logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡳࠥࡸࡵ࡯ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡦࡵࡷࡷࠬஜ"))
  bstack1ll1lll111_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ஝"), {}).get(bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨஞ"))
  bstack11ll11lll_opy_ = True
  bstack11l11lll1_opy_(bstack1l111l1l_opy_)
  os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨட")] = CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ஠")]
  os.environ[bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬ஡")] = CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭஢")]
  os.environ[bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧண")] = bstack1l1l11l1l1_opy_.__str__()
  from _pytest.config import main as bstack111ll111_opy_
  bstack1ll1llll_opy_ = []
  try:
    bstack1ll11l11_opy_ = bstack111ll111_opy_(arg)
    if bstack1l1l1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵࠩத") in multiprocessing.current_process().__dict__.keys():
      for bstack1l1lllll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1ll1llll_opy_.append(bstack1l1lllll_opy_)
    try:
      bstack1lll11l1ll_opy_ = (bstack1ll1llll_opy_, int(bstack1ll11l11_opy_))
      bstack1ll11lllll_opy_.append(bstack1lll11l1ll_opy_)
    except:
      bstack1ll11lllll_opy_.append((bstack1ll1llll_opy_, bstack1ll11l11_opy_))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack1ll1llll_opy_.append({bstack1l1l1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ஥"): bstack1l1l1l1_opy_ (u"ࠧࡑࡴࡲࡧࡪࡹࡳࠡࠩ஦") + os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨ஧")), bstack1l1l1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨந"): traceback.format_exc(), bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩன"): int(os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫப")))})
    bstack1ll11lllll_opy_.append((bstack1ll1llll_opy_, 1))
def bstack1ll1111l_opy_(arg):
  global bstack1ll1l1lll1_opy_
  bstack11l11lll1_opy_(bstack1111lll1_opy_)
  os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭஫")] = str(bstack1l1l1ll111_opy_)
  from behave.__main__ import main as bstack1l1l1ll11l_opy_
  status_code = bstack1l1l1ll11l_opy_(arg)
  if status_code != 0:
    bstack1ll1l1lll1_opy_ = status_code
def bstack1llll11lll_opy_():
  logger.info(bstack111llll11_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1l1l1l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ஬"), help=bstack1l1l1l1_opy_ (u"ࠧࡈࡧࡱࡩࡷࡧࡴࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡥࡲࡲ࡫࡯ࡧࠨ஭"))
  parser.add_argument(bstack1l1l1l1_opy_ (u"ࠨ࠯ࡸࠫம"), bstack1l1l1l1_opy_ (u"ࠩ࠰࠱ࡺࡹࡥࡳࡰࡤࡱࡪ࠭ய"), help=bstack1l1l1l1_opy_ (u"ࠪ࡝ࡴࡻࡲࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡶࡵࡨࡶࡳࡧ࡭ࡦࠩர"))
  parser.add_argument(bstack1l1l1l1_opy_ (u"ࠫ࠲ࡱࠧற"), bstack1l1l1l1_opy_ (u"ࠬ࠳࠭࡬ࡧࡼࠫல"), help=bstack1l1l1l1_opy_ (u"࡙࠭ࡰࡷࡵࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡥࡨࡩࡥࡴࡵࠣ࡯ࡪࡿࠧள"))
  parser.add_argument(bstack1l1l1l1_opy_ (u"ࠧ࠮ࡨࠪழ"), bstack1l1l1l1_opy_ (u"ࠨ࠯࠰ࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭வ"), help=bstack1l1l1l1_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨஶ"))
  bstack1l1l1l111_opy_ = parser.parse_args()
  try:
    bstack11l111ll1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡪࡩࡳ࡫ࡲࡪࡥ࠱ࡽࡲࡲ࠮ࡴࡣࡰࡴࡱ࡫ࠧஷ")
    if bstack1l1l1l111_opy_.framework and bstack1l1l1l111_opy_.framework not in (bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫஸ"), bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭ஹ")):
      bstack11l111ll1_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠯ࡻࡰࡰ࠳ࡹࡡ࡮ࡲ࡯ࡩࠬ஺")
    bstack1ll1l111_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l111ll1_opy_)
    bstack111111111_opy_ = open(bstack1ll1l111_opy_, bstack1l1l1l1_opy_ (u"ࠧࡳࠩ஻"))
    bstack1l1l1llll_opy_ = bstack111111111_opy_.read()
    bstack111111111_opy_.close()
    if bstack1l1l1l111_opy_.username:
      bstack1l1l1llll_opy_ = bstack1l1l1llll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨ஼"), bstack1l1l1l111_opy_.username)
    if bstack1l1l1l111_opy_.key:
      bstack1l1l1llll_opy_ = bstack1l1l1llll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ஽"), bstack1l1l1l111_opy_.key)
    if bstack1l1l1l111_opy_.framework:
      bstack1l1l1llll_opy_ = bstack1l1l1llll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫா"), bstack1l1l1l111_opy_.framework)
    file_name = bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠧி")
    file_path = os.path.abspath(file_name)
    bstack1ll11lll_opy_ = open(file_path, bstack1l1l1l1_opy_ (u"ࠬࡽࠧீ"))
    bstack1ll11lll_opy_.write(bstack1l1l1llll_opy_)
    bstack1ll11lll_opy_.close()
    logger.info(bstack1l1l11llll_opy_)
    try:
      os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨு")] = bstack1l1l1l111_opy_.framework if bstack1l1l1l111_opy_.framework != None else bstack1l1l1l1_opy_ (u"ࠢࠣூ")
      config = yaml.safe_load(bstack1l1l1llll_opy_)
      config[bstack1l1l1l1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ௃")] = bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠯ࡶࡩࡹࡻࡰࠨ௄")
      bstack1l1llll1ll_opy_(bstack1111l1lll_opy_, config)
    except Exception as e:
      logger.debug(bstack1l1l1ll1_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l11ll111_opy_.format(str(e)))
def bstack1l1llll1ll_opy_(bstack1ll111l1l1_opy_, config, bstack1ll1l11l1l_opy_={}):
  global bstack1l1l11l1l1_opy_
  global bstack111lllll1_opy_
  global bstack1l111l111_opy_
  if not config:
    return
  bstack1l1ll1l1l_opy_ = bstack1l111111l_opy_ if not bstack1l1l11l1l1_opy_ else (
    bstack11ll1ll1l_opy_ if bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶࠧ௅") in config else bstack1ll111l111_opy_)
  bstack1111l1ll1_opy_ = False
  bstack1l111ll11_opy_ = False
  if bstack1l1l11l1l1_opy_ is True:
      if bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࠨெ") in config:
          bstack1111l1ll1_opy_ = True
      else:
          bstack1l111ll11_opy_ = True
  bstack11lllll11_opy_ = bstack1111ll11l_opy_.bstack1l1l1l11ll_opy_(config, bstack111lllll1_opy_)
  data = {
    bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧே"): config[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨை")],
    bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ௉"): config[bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫொ")],
    bstack1l1l1l1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ோ"): bstack1ll111l1l1_opy_,
    bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡺࡥࡤࡶࡨࡨࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧௌ"): os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ்࠭"), bstack111lllll1_opy_),
    bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ௎"): bstack11lll1l11_opy_,
    bstack1l1l1l1_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬ࠨ௏"): bstack11111111_opy_(),
    bstack1l1l1l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪௐ"): {
      bstack1l1l1l1_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭௑"): str(config[bstack1l1l1l1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ௒")]) if bstack1l1l1l1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ௓") in config else bstack1l1l1l1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧ௔"),
      bstack1l1l1l1_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࡖࡦࡴࡶ࡭ࡴࡴࠧ௕"): sys.version,
      bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡨࡨࡶࡷ࡫ࡲࠨ௖"): bstack1lllllll11_opy_(os.getenv(bstack1l1l1l1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤௗ"), bstack1l1l1l1_opy_ (u"ࠣࠤ௘"))),
      bstack1l1l1l1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫ௙"): bstack1l1l1l1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ௚"),
      bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬ௛"): bstack1l1ll1l1l_opy_,
      bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪ௜"): bstack11lllll11_opy_,
      bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨ࡟ࡶࡷ࡬ࡨࠬ௝"): os.environ[bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ௞")],
      bstack1l1l1l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࡚ࡪࡸࡳࡪࡱࡱࠫ௟"): bstack1lll111lll_opy_(os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫ௠"), bstack111lllll1_opy_)),
      bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௡"): config[bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ௢")] if config[bstack1l1l1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௣")] else bstack1l1l1l1_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢ௤"),
      bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ௥"): str(config[bstack1l1l1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ௦")]) if bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ௧") in config else bstack1l1l1l1_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱࠦ௨"),
      bstack1l1l1l1_opy_ (u"ࠫࡴࡹࠧ௩"): sys.platform,
      bstack1l1l1l1_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧ௪"): socket.gethostname(),
      bstack1l1l1l1_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨ௫"): bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩ௬"))
    }
  }
  if not bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡕ࡬࡫ࡳࡧ࡬ࠨ௭")) is None:
    data[bstack1l1l1l1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ௮")][bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡒ࡫ࡴࡢࡦࡤࡸࡦ࠭௯")] = {
      bstack1l1l1l1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ௰"): bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪ௱"),
      bstack1l1l1l1_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭௲"): bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠧࡴࡦ࡮ࡏ࡮ࡲ࡬ࡔ࡫ࡪࡲࡦࡲࠧ௳")),
      bstack1l1l1l1_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࡏࡷࡰࡦࡪࡸࠧ௴"): bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬ௵"))
    }
  if bstack1ll111l1l1_opy_ == bstack1llll1l11l_opy_:
    data[bstack1l1l1l1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭௶")][bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡆࡳࡳ࡬ࡩࡨࠩ௷")] = bstack11111l1ll_opy_(config)
  update(data[bstack1l1l1l1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ௸")], bstack1ll1l11l1l_opy_)
  try:
    response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"࠭ࡐࡐࡕࡗࠫ௹"), bstack1l1ll1l11l_opy_(bstack1l1ll11111_opy_), data, {
      bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷ࡬ࠬ௺"): (config[bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ௻")], config[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ௼")])
    })
    if response:
      logger.debug(bstack11l1lll1_opy_.format(bstack1ll111l1l1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1llll1l11_opy_.format(str(e)))
def bstack1lllllll11_opy_(framework):
  return bstack1l1l1l1_opy_ (u"ࠥࡿࢂ࠳ࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢ௽").format(str(framework), __version__) if framework else bstack1l1l1l1_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࡾࢁࠧ௾").format(
    __version__)
def bstack1l1ll1l11_opy_():
  global CONFIG
  global bstack11111l11_opy_
  if bool(CONFIG):
    return
  try:
    bstack1l1l11111l_opy_()
    logger.debug(bstack1ll11l1l1_opy_.format(str(CONFIG)))
    bstack11111l11_opy_ = bstack1lll1111ll_opy_.bstack11l1l1l1l_opy_(CONFIG, bstack11111l11_opy_)
    bstack1l111111_opy_()
  except Exception as e:
    logger.error(bstack1l1l1l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࡺࡶࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࠤ௿") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1l1lll1l_opy_
  atexit.register(bstack1llll1ll1_opy_)
  signal.signal(signal.SIGINT, bstack111l1111l_opy_)
  signal.signal(signal.SIGTERM, bstack111l1111l_opy_)
def bstack1l1lll1l_opy_(exctype, value, traceback):
  global bstack1ll111111_opy_
  try:
    for driver in bstack1ll111111_opy_:
      bstack1l1l1lll11_opy_(driver, bstack1l1l1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ఀ"), bstack1l1l1l1_opy_ (u"ࠢࡔࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥఁ") + str(value))
  except Exception:
    pass
  bstack1l1ll1l1l1_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1l1ll1l1l1_opy_(message=bstack1l1l1l1_opy_ (u"ࠨࠩం"), bstack111lll111_opy_ = False):
  global CONFIG
  bstack1lll1l11ll_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡇࡻࡧࡪࡶࡴࡪࡱࡱࠫః") if bstack111lll111_opy_ else bstack1l1l1l1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩఄ")
  try:
    if message:
      bstack1ll1l11l1l_opy_ = {
        bstack1lll1l11ll_opy_ : str(message)
      }
      bstack1l1llll1ll_opy_(bstack1llll1l11l_opy_, CONFIG, bstack1ll1l11l1l_opy_)
    else:
      bstack1l1llll1ll_opy_(bstack1llll1l11l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1ll1111ll_opy_.format(str(e)))
def bstack111llll1l_opy_(bstack111l1l1ll_opy_, size):
  bstack1ll111l1l_opy_ = []
  while len(bstack111l1l1ll_opy_) > size:
    bstack11l111ll_opy_ = bstack111l1l1ll_opy_[:size]
    bstack1ll111l1l_opy_.append(bstack11l111ll_opy_)
    bstack111l1l1ll_opy_ = bstack111l1l1ll_opy_[size:]
  bstack1ll111l1l_opy_.append(bstack111l1l1ll_opy_)
  return bstack1ll111l1l_opy_
def bstack1ll11lll1l_opy_(args):
  if bstack1l1l1l1_opy_ (u"ࠫ࠲ࡳࠧఅ") in args and bstack1l1l1l1_opy_ (u"ࠬࡶࡤࡣࠩఆ") in args:
    return True
  return False
def run_on_browserstack(bstack111ll111l_opy_=None, bstack1ll11lllll_opy_=None, bstack1111ll1l_opy_=False):
  global CONFIG
  global bstack1ll11l11l1_opy_
  global bstack1l1l1ll111_opy_
  global bstack111lllll1_opy_
  global bstack1l111l111_opy_
  bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠧఇ")
  bstack1ll1l1l1l1_opy_(bstack1l11111ll_opy_, logger)
  if bstack111ll111l_opy_ and isinstance(bstack111ll111l_opy_, str):
    bstack111ll111l_opy_ = eval(bstack111ll111l_opy_)
  if bstack111ll111l_opy_:
    CONFIG = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡄࡑࡑࡊࡎࡍࠧఈ")]
    bstack1ll11l11l1_opy_ = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡊࡘࡆࡤ࡛ࡒࡍࠩఉ")]
    bstack1l1l1ll111_opy_ = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫఊ")]
    bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬఋ"), bstack1l1l1ll111_opy_)
    bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫఌ")
  bstack1l111l111_opy_.bstack1ll11l111_opy_(bstack1l1l1l1_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ఍"), uuid4().__str__())
  logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤ࠾ࠩఎ") + bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩఏ")))
  if not bstack1111ll1l_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1llll1l1l_opy_)
      return
    if sys.argv[1] == bstack1l1l1l1_opy_ (u"ࠨ࠯࠰ࡺࡪࡸࡳࡪࡱࡱࠫఐ") or sys.argv[1] == bstack1l1l1l1_opy_ (u"ࠩ࠰ࡺࠬ఑"):
      logger.info(bstack1l1l1l1_opy_ (u"ࠪࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡓࡽࡹ࡮࡯࡯ࠢࡖࡈࡐࠦࡶࡼࡿࠪఒ").format(__version__))
      return
    if sys.argv[1] == bstack1l1l1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪఓ"):
      bstack1llll11lll_opy_()
      return
  args = sys.argv
  bstack1l1ll1l11_opy_()
  global bstack1llll11111_opy_
  global bstack1lllll111_opy_
  global bstack11ll11lll_opy_
  global bstack1ll1l11l11_opy_
  global bstack111lll1l_opy_
  global bstack1ll1lll111_opy_
  global bstack11111lll_opy_
  global bstack1l1l1llll1_opy_
  global bstack1l1l11ll1l_opy_
  global bstack11lllll1_opy_
  global bstack1111l111_opy_
  bstack1lllll111_opy_ = len(CONFIG.get(bstack1l1l1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨఔ"), []))
  if not bstack11lll11l1_opy_:
    if args[1] == bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭క") or args[1] == bstack1l1l1l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠳ࠨఖ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨగ")
      args = args[2:]
    elif args[1] == bstack1l1l1l1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨఘ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩఙ")
      args = args[2:]
    elif args[1] == bstack1l1l1l1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪచ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫఛ")
      args = args[2:]
    elif args[1] == bstack1l1l1l1_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧజ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨఝ")
      args = args[2:]
    elif args[1] == bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨఞ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩట")
      args = args[2:]
    elif args[1] == bstack1l1l1l1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪఠ"):
      bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫడ")
      args = args[2:]
    else:
      if not bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨఢ") in CONFIG or str(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩణ")]).lower() in [bstack1l1l1l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧత"), bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠴ࠩథ")]:
        bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩద")
        args = args[1:]
      elif str(CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ధ")]).lower() == bstack1l1l1l1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪన"):
        bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ఩")
        args = args[1:]
      elif str(CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩప")]).lower() == bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ఫ"):
        bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧబ")
        args = args[1:]
      elif str(CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬభ")]).lower() == bstack1l1l1l1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪమ"):
        bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫయ")
        args = args[1:]
      elif str(CONFIG[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨర")]).lower() == bstack1l1l1l1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ఱ"):
        bstack11lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧల")
        args = args[1:]
      else:
        os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪళ")] = bstack11lll11l1_opy_
        bstack1ll1lll1ll_opy_(bstack1lll1111l1_opy_)
  os.environ[bstack1l1l1l1_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪఴ")] = bstack11lll11l1_opy_
  bstack111lllll1_opy_ = bstack11lll11l1_opy_
  global bstack11111lll1_opy_
  global bstack1ll1111111_opy_
  if bstack111ll111l_opy_:
    try:
      os.environ[bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬవ")] = bstack11lll11l1_opy_
      bstack1l1llll1ll_opy_(bstack1l1ll11l1l_opy_, CONFIG)
    except Exception as e:
      logger.debug(bstack1l1l11l1_opy_.format(str(e)))
  global bstack11l11l1l_opy_
  global bstack1l11ll11_opy_
  global bstack1l1l1l1l1_opy_
  global bstack1l1l1l111l_opy_
  global bstack1l11lll11l_opy_
  global bstack11lllllll_opy_
  global bstack111l11l1_opy_
  global bstack1llllllll_opy_
  global bstack1l111ll1ll_opy_
  global bstack1ll111l1_opy_
  global bstack11111ll1_opy_
  global bstack11l1l1l11_opy_
  global bstack11l1llll_opy_
  global bstack1l1l111l_opy_
  global bstack1llll11l1_opy_
  global bstack1l1ll1ll1l_opy_
  global bstack1l1llll1l_opy_
  global bstack11l1lll1l_opy_
  global bstack1lll111l1_opy_
  global bstack1ll1l1ll11_opy_
  global bstack1l1l1ll1l1_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack11l11l1l_opy_ = webdriver.Remote.__init__
    bstack1l11ll11_opy_ = WebDriver.quit
    bstack11l1l1l11_opy_ = WebDriver.close
    bstack1llll11l1_opy_ = WebDriver.get
    bstack1l1l1ll1l1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack11111lll1_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack11lll111_opy_
    bstack1ll1111111_opy_ = bstack11lll111_opy_()
  except Exception as e:
    pass
  try:
    global bstack111ll11l1_opy_
    from QWeb.keywords import browser
    bstack111ll11l1_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack1lll11l1_opy_(CONFIG) and bstack1lll11llll_opy_():
    if bstack1l1l1111_opy_() < version.parse(bstack1l11ll11ll_opy_):
      logger.error(bstack1l11ll1ll1_opy_.format(bstack1l1l1111_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack1l1ll1ll1l_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack1ll1lll1l1_opy_.format(str(e)))
  if not CONFIG.get(bstack1l1l1l1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡻࡴࡰࡅࡤࡴࡹࡻࡲࡦࡎࡲ࡫ࡸ࠭శ"), False) and not bstack111ll111l_opy_:
    logger.info(bstack1111l11l1_opy_)
  if bstack11lll11l1_opy_ != bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬష") or (bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭స") and not bstack111ll111l_opy_):
    bstack1l11llll1l_opy_()
  if (bstack11lll11l1_opy_ in [bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭హ"), bstack1l1l1l1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ఺"), bstack1l1l1l1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ఻")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1l11lll1ll_opy_
        bstack11lllllll_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack1llll11ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1l11lll11l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1ll1ll11_opy_ + str(e))
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1llll11ll_opy_)
    if bstack11lll11l1_opy_ != bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯఼ࠫ"):
      bstack1lll1l1lll_opy_()
    bstack1l1l1l1l1_opy_ = Output.start_test
    bstack1l1l1l111l_opy_ = Output.end_test
    bstack111l11l1_opy_ = TestStatus.__init__
    bstack1l111ll1ll_opy_ = pabot._run
    bstack1ll111l1_opy_ = QueueItem.__init__
    bstack11111ll1_opy_ = pabot._create_command_for_execution
    bstack1lll111l1_opy_ = pabot._report_results
  if bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫఽ"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1ll1l11ll1_opy_)
    bstack11l1llll_opy_ = Runner.run_hook
    bstack1l1l111l_opy_ = Step.run
  if bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬా"):
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
      logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹࡵࠠࡳࡷࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࡹࠧి"))
  try:
    framework_name = bstack1l1l1l1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ీ") if bstack11lll11l1_opy_ in [bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧు"), bstack1l1l1l1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨూ"), bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫృ")] else bstack1l1l1ll11_opy_(bstack11lll11l1_opy_)
    bstack11lll1ll_opy_ = {
      bstack1l1l1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࠬౄ"): bstack1l1l1l1_opy_ (u"ࠬࢁ࠰ࡾ࠯ࡦࡹࡨࡻ࡭ࡣࡧࡵࠫ౅").format(framework_name) if bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ె") and bstack1llll1111_opy_() else framework_name,
      bstack1l1l1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫే"): bstack1lll111lll_opy_(framework_name),
      bstack1l1l1l1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ై"): __version__,
      bstack1l1l1l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡻࡳࡦࡦࠪ౉"): bstack11lll11l1_opy_
    }
    if bstack11lll11l1_opy_ in bstack1l1llll111_opy_:
      if bstack1l1l11l1l1_opy_ and bstack1l1l1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪొ") in CONFIG and CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫో")] == True:
        if bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬౌ") in CONFIG:
          os.environ[bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒ్ࠧ")] = os.getenv(bstack1l1l1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ౎"), json.dumps(CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ౏")]))
          CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ౐")].pop(bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨ౑"), None)
          CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ౒")].pop(bstack1l1l1l1_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ౓"), None)
        bstack11lll1ll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭౔")] = {
          bstack1l1l1l1_opy_ (u"ࠧ࡯ࡣࡰࡩౕࠬ"): bstack1l1l1l1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ౖࠪ"),
          bstack1l1l1l1_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪ౗"): str(bstack1l1l1111_opy_())
        }
    if bstack11lll11l1_opy_ not in [bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫౘ")]:
      bstack11l111l11_opy_ = bstack11l1l11l1_opy_.launch(CONFIG, bstack11lll1ll_opy_)
  except Exception as e:
    logger.debug(bstack1111111l_opy_.format(bstack1l1l1l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡊࡸࡦࠬౙ"), str(e)))
  if bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬౚ"):
    bstack11ll11lll_opy_ = True
    if bstack111ll111l_opy_ and bstack1111ll1l_opy_:
      bstack1ll1lll111_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ౛"), {}).get(bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ౜"))
      bstack11l11lll1_opy_(bstack1llllll1l_opy_)
    elif bstack111ll111l_opy_:
      bstack1ll1lll111_opy_ = CONFIG.get(bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬౝ"), {}).get(bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ౞"))
      global bstack1ll111111_opy_
      try:
        if bstack1ll11lll1l_opy_(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭౟")]) and multiprocessing.current_process().name == bstack1l1l1l1_opy_ (u"ࠫ࠵࠭ౠ"):
          bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨౡ")].remove(bstack1l1l1l1_opy_ (u"࠭࠭࡮ࠩౢ"))
          bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪౣ")].remove(bstack1l1l1l1_opy_ (u"ࠨࡲࡧࡦࠬ౤"))
          bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ౥")] = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭౦")][0]
          with open(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ౧")], bstack1l1l1l1_opy_ (u"ࠬࡸࠧ౨")) as f:
            bstack1llllll11l_opy_ = f.read()
          bstack1l1lll11l1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࠢࠣࡨࡵࡳࡲࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡹࡤ࡬ࠢ࡬ࡱࡵࡵࡲࡵࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩࡀࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦࠪࡾࢁ࠮ࡁࠠࡧࡴࡲࡱࠥࡶࡤࡣࠢ࡬ࡱࡵࡵࡲࡵࠢࡓࡨࡧࡁࠠࡰࡩࡢࡨࡧࠦ࠽ࠡࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱ࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡫ࡦࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠬࡸ࡫࡬ࡧ࠮ࠣࡥࡷ࡭ࠬࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤࡂࠦ࠰ࠪ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡶࡵࡽ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡡࡳࡩࠣࡁࠥࡹࡴࡳࠪ࡬ࡲࡹ࠮ࡡࡳࡩࠬ࠯࠶࠶ࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡥࡹࡥࡨࡴࡹࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡤࡷࠥ࡫࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡲࡤࡷࡸࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡴ࡭࡟ࡥࡤࠫࡷࡪࡲࡦ࠭ࡣࡵ࡫࠱ࡺࡥ࡮ࡲࡲࡶࡦࡸࡹࠪࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡖࡤࡣ࠰ࡧࡳࡤࡨࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡒࡧࡦ࠭࠯࠮ࡴࡧࡷࡣࡹࡸࡡࡤࡧࠫ࠭ࡡࡴࠢࠣࠤ౩").format(str(bstack111ll111l_opy_))
          bstack1l1lll11_opy_ = bstack1l1lll11l1_opy_ + bstack1llllll11l_opy_
          bstack1l11l11ll_opy_ = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ౪")] + bstack1l1l1l1_opy_ (u"ࠨࡡࡥࡷࡹࡧࡣ࡬ࡡࡷࡩࡲࡶ࠮ࡱࡻࠪ౫")
          with open(bstack1l11l11ll_opy_, bstack1l1l1l1_opy_ (u"ࠩࡺࠫ౬")):
            pass
          with open(bstack1l11l11ll_opy_, bstack1l1l1l1_opy_ (u"ࠥࡻ࠰ࠨ౭")) as f:
            f.write(bstack1l1lll11_opy_)
          import subprocess
          bstack1l1l11lll1_opy_ = subprocess.run([bstack1l1l1l1_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࠦ౮"), bstack1l11l11ll_opy_])
          if os.path.exists(bstack1l11l11ll_opy_):
            os.unlink(bstack1l11l11ll_opy_)
          os._exit(bstack1l1l11lll1_opy_.returncode)
        else:
          if bstack1ll11lll1l_opy_(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ౯")]):
            bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ౰")].remove(bstack1l1l1l1_opy_ (u"ࠧ࠮࡯ࠪ౱"))
            bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ౲")].remove(bstack1l1l1l1_opy_ (u"ࠩࡳࡨࡧ࠭౳"))
            bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭౴")] = bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ౵")][0]
          bstack11l11lll1_opy_(bstack1llllll1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ౶")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1l1l1l1_opy_ (u"࠭࡟ࡠࡰࡤࡱࡪࡥ࡟ࠨ౷")] = bstack1l1l1l1_opy_ (u"ࠧࡠࡡࡰࡥ࡮ࡴ࡟ࡠࠩ౸")
          mod_globals[bstack1l1l1l1_opy_ (u"ࠨࡡࡢࡪ࡮ࡲࡥࡠࡡࠪ౹")] = os.path.abspath(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ౺")])
          exec(open(bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭౻")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1l1l1l1_opy_ (u"ࠫࡈࡧࡵࡨࡪࡷࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠫ౼").format(str(e)))
          for driver in bstack1ll111111_opy_:
            bstack1ll11lllll_opy_.append({
              bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ౽"): bstack111ll111l_opy_[bstack1l1l1l1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ౾")],
              bstack1l1l1l1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭౿"): str(e),
              bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧಀ"): multiprocessing.current_process().name
            })
            bstack1l1l1lll11_opy_(driver, bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩಁ"), bstack1l1l1l1_opy_ (u"ࠥࡗࡪࡹࡳࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡼ࡯ࡴࡩ࠼ࠣࡠࡳࠨಂ") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1ll111111_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1l1l1ll111_opy_, CONFIG, logger)
      bstack11l11l11l_opy_()
      bstack111111l1_opy_()
      bstack1l1ll11l1_opy_ = {
        bstack1l1l1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧಃ"): args[0],
        bstack1l1l1l1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬ಄"): CONFIG,
        bstack1l1l1l1_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧಅ"): bstack1ll11l11l1_opy_,
        bstack1l1l1l1_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩಆ"): bstack1l1l1ll111_opy_
      }
      percy.bstack1lll1l1ll1_opy_()
      if bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫಇ") in CONFIG:
        bstack1lllllllll_opy_ = []
        manager = multiprocessing.Manager()
        bstack1l1l111l1l_opy_ = manager.list()
        if bstack1ll11lll1l_opy_(args):
          for index, platform in enumerate(CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬಈ")]):
            if index == 0:
              bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ಉ")] = args
            bstack1lllllllll_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1ll11l1_opy_, bstack1l1l111l1l_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧಊ")]):
            bstack1lllllllll_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1ll11l1_opy_, bstack1l1l111l1l_opy_)))
        for t in bstack1lllllllll_opy_:
          t.start()
        for t in bstack1lllllllll_opy_:
          t.join()
        bstack1l1l1llll1_opy_ = list(bstack1l1l111l1l_opy_)
      else:
        if bstack1ll11lll1l_opy_(args):
          bstack1l1ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨಋ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1l1ll11l1_opy_,))
          test.start()
          test.join()
        else:
          bstack11l11lll1_opy_(bstack1llllll1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1l1l1l1_opy_ (u"࠭࡟ࡠࡰࡤࡱࡪࡥ࡟ࠨಌ")] = bstack1l1l1l1_opy_ (u"ࠧࡠࡡࡰࡥ࡮ࡴ࡟ࡠࠩ಍")
          mod_globals[bstack1l1l1l1_opy_ (u"ࠨࡡࡢࡪ࡮ࡲࡥࡠࡡࠪಎ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨಏ") or bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩಐ"):
    percy.init(bstack1l1l1ll111_opy_, CONFIG, logger)
    percy.bstack1lll1l1ll1_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1llll11ll_opy_)
    bstack11l11l11l_opy_()
    bstack11l11lll1_opy_(bstack111l1l11_opy_)
    if bstack1l1l11l1l1_opy_:
      bstack11lll1lll_opy_(bstack111l1l11_opy_, args)
      if bstack1l1l1l1_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩ಑") in args:
        i = args.index(bstack1l1l1l1_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪಒ"))
        args.pop(i)
        args.pop(i)
      if bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩಓ") not in CONFIG:
        CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪಔ")] = [{}]
        bstack1lllll111_opy_ = 1
      if bstack1llll11111_opy_ == 0:
        bstack1llll11111_opy_ = 1
      args.insert(0, str(bstack1llll11111_opy_))
      args.insert(0, str(bstack1l1l1l1_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ಕ")))
    if bstack11l1l11l1_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack1lll1l11l_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack1lll11l111_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack1l1l1l1_opy_ (u"ࠤࡕࡓࡇࡕࡔࡠࡑࡓࡘࡎࡕࡎࡔࠤಖ"),
        ).parse_args(bstack1lll1l11l_opy_)
        bstack1111l11l_opy_ = args.index(bstack1lll1l11l_opy_[0]) if len(bstack1lll1l11l_opy_) > 0 else len(args)
        args.insert(bstack1111l11l_opy_, str(bstack1l1l1l1_opy_ (u"ࠪ࠱࠲ࡲࡩࡴࡶࡨࡲࡪࡸࠧಗ")))
        args.insert(bstack1111l11l_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡷࡵࡢࡰࡶࡢࡰ࡮ࡹࡴࡦࡰࡨࡶ࠳ࡶࡹࠨಘ"))))
        if bstack1l1111ll_opy_(os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࠪಙ"))) and str(os.environ.get(bstack1l1l1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࡣ࡙ࡋࡓࡕࡕࠪಚ"), bstack1l1l1l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬಛ"))) != bstack1l1l1l1_opy_ (u"ࠨࡰࡸࡰࡱ࠭ಜ"):
          for bstack1l11ll1lll_opy_ in bstack1lll11l111_opy_:
            args.remove(bstack1l11ll1lll_opy_)
          bstack1lll1l11l1_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔ࡟ࡕࡇࡖࡘࡘ࠭ಝ")).split(bstack1l1l1l1_opy_ (u"ࠪ࠰ࠬಞ"))
          for bstack1lll11ll1_opy_ in bstack1lll1l11l1_opy_:
            args.append(bstack1lll11ll1_opy_)
      except Exception as e:
        logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡤࡸࡹࡧࡣࡩ࡫ࡱ࡫ࠥࡲࡩࡴࡶࡨࡲࡪࡸࠠࡧࡱࡵࠤࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼ࠲ࠥࡋࡲࡳࡱࡵࠤ࠲ࠦࠢಟ").format(e))
    pabot.main(args)
  elif bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ಠ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1llll11ll_opy_)
    for a in args:
      if bstack1l1l1l1_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜ࠬಡ") in a:
        bstack111lll1l_opy_ = int(a.split(bstack1l1l1l1_opy_ (u"ࠧ࠻ࠩಢ"))[1])
      if bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡅࡇࡉࡐࡔࡉࡁࡍࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬಣ") in a:
        bstack1ll1lll111_opy_ = str(a.split(bstack1l1l1l1_opy_ (u"ࠩ࠽ࠫತ"))[1])
      if bstack1l1l1l1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕࠪಥ") in a:
        bstack11111lll_opy_ = str(a.split(bstack1l1l1l1_opy_ (u"ࠫ࠿࠭ದ"))[1])
    bstack1lllllll1_opy_ = None
    if bstack1l1l1l1_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫಧ") in args:
      i = args.index(bstack1l1l1l1_opy_ (u"࠭࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠬನ"))
      args.pop(i)
      bstack1lllllll1_opy_ = args.pop(i)
    if bstack1lllllll1_opy_ is not None:
      global bstack1lll1ll1ll_opy_
      bstack1lll1ll1ll_opy_ = bstack1lllllll1_opy_
    bstack11l11lll1_opy_(bstack111l1l11_opy_)
    run_cli(args)
    if bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷࠫ಩") in multiprocessing.current_process().__dict__.keys():
      for bstack1l1lllll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1ll11lllll_opy_.append(bstack1l1lllll_opy_)
  elif bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨಪ"):
    percy.init(bstack1l1l1ll111_opy_, CONFIG, logger)
    percy.bstack1lll1l1ll1_opy_()
    bstack11l1l111_opy_ = bstack111ll1l1_opy_(args, logger, CONFIG, bstack1l1l11l1l1_opy_)
    bstack11l1l111_opy_.bstack1lll1111l_opy_()
    bstack11l11l11l_opy_()
    bstack1ll1l11l11_opy_ = True
    bstack11lllll1_opy_ = bstack11l1l111_opy_.bstack11l11l1l1_opy_()
    bstack11l1l111_opy_.bstack1l1ll11l1_opy_(bstack1lllll11ll_opy_)
    bstack1ll1l11l_opy_ = bstack11l1l111_opy_.bstack11111l111_opy_(bstack1ll1ll111_opy_, {
      bstack1l1l1l1_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪಫ"): bstack1ll11l11l1_opy_,
      bstack1l1l1l1_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬಬ"): bstack1l1l1ll111_opy_,
      bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧಭ"): bstack1l1l11l1l1_opy_
    })
    try:
      bstack1ll1llll_opy_, bstack11ll1l11_opy_ = map(list, zip(*bstack1ll1l11l_opy_))
      bstack1l1l11ll1l_opy_ = bstack1ll1llll_opy_[0]
      for status_code in bstack11ll1l11_opy_:
        if status_code != 0:
          bstack1111l111_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack1l1l1l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡤࡺࡪࠦࡥࡳࡴࡲࡶࡸࠦࡡ࡯ࡦࠣࡷࡹࡧࡴࡶࡵࠣࡧࡴࡪࡥ࠯ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡀࠠࡼࡿࠥಮ").format(str(e)))
  elif bstack11lll11l1_opy_ == bstack1l1l1l1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ಯ"):
    try:
      from behave.__main__ import main as bstack1l1l1ll11l_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1lll11ll_opy_(e, bstack1ll1l11ll1_opy_)
    bstack11l11l11l_opy_()
    bstack1ll1l11l11_opy_ = True
    bstack1llllll11_opy_ = 1
    if bstack1l1l1l1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧರ") in CONFIG:
      bstack1llllll11_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨಱ")]
    if bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬಲ") in CONFIG:
      bstack11ll1lll_opy_ = int(bstack1llllll11_opy_) * int(len(CONFIG[bstack1l1l1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ಳ")]))
    else:
      bstack11ll1lll_opy_ = int(bstack1llllll11_opy_)
    config = Configuration(args)
    bstack1l1ll111l1_opy_ = config.paths
    if len(bstack1l1ll111l1_opy_) == 0:
      import glob
      pattern = bstack1l1l1l1_opy_ (u"ࠫ࠯࠰࠯ࠫ࠰ࡩࡩࡦࡺࡵࡳࡧࠪ಴")
      bstack1ll1l1l111_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1ll1l1l111_opy_)
      config = Configuration(args)
      bstack1l1ll111l1_opy_ = config.paths
    bstack1llllll1ll_opy_ = [os.path.normpath(item) for item in bstack1l1ll111l1_opy_]
    bstack1ll1l1l1_opy_ = [os.path.normpath(item) for item in args]
    bstack11ll11l1_opy_ = [item for item in bstack1ll1l1l1_opy_ if item not in bstack1llllll1ll_opy_]
    import platform as pf
    if pf.system().lower() == bstack1l1l1l1_opy_ (u"ࠬࡽࡩ࡯ࡦࡲࡻࡸ࠭ವ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1llllll1ll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11l1ll11l_opy_)))
                    for bstack11l1ll11l_opy_ in bstack1llllll1ll_opy_]
    bstack11l11l111_opy_ = []
    for spec in bstack1llllll1ll_opy_:
      bstack1l1l1lllll_opy_ = []
      bstack1l1l1lllll_opy_ += bstack11ll11l1_opy_
      bstack1l1l1lllll_opy_.append(spec)
      bstack11l11l111_opy_.append(bstack1l1l1lllll_opy_)
    execution_items = []
    for bstack1l1l1lllll_opy_ in bstack11l11l111_opy_:
      if bstack1l1l1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩಶ") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪಷ")]):
          item = {}
          item[bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࠬಸ")] = bstack1l1l1l1_opy_ (u"ࠩࠣࠫಹ").join(bstack1l1l1lllll_opy_)
          item[bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ಺")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack1l1l1l1_opy_ (u"ࠫࡦࡸࡧࠨ಻")] = bstack1l1l1l1_opy_ (u"಼ࠬࠦࠧ").join(bstack1l1l1lllll_opy_)
        item[bstack1l1l1l1_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬಽ")] = 0
        execution_items.append(item)
    bstack111ll11ll_opy_ = bstack111llll1l_opy_(execution_items, bstack11ll1lll_opy_)
    for execution_item in bstack111ll11ll_opy_:
      bstack1lllllllll_opy_ = []
      for item in execution_item:
        bstack1lllllllll_opy_.append(bstack1ll1ll1lll_opy_(name=str(item[bstack1l1l1l1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ಾ")]),
                                             target=bstack1ll1111l_opy_,
                                             args=(item[bstack1l1l1l1_opy_ (u"ࠨࡣࡵ࡫ࠬಿ")],)))
      for t in bstack1lllllllll_opy_:
        t.start()
      for t in bstack1lllllllll_opy_:
        t.join()
  else:
    bstack1ll1lll1ll_opy_(bstack1lll1111l1_opy_)
  if not bstack111ll111l_opy_:
    bstack1lll111l11_opy_()
  bstack1lll1111ll_opy_.bstack11l1l11ll_opy_()
def browserstack_initialize(bstack1ll11l11l_opy_=None):
  run_on_browserstack(bstack1ll11l11l_opy_, None, True)
def bstack1lll111l11_opy_():
  global CONFIG
  global bstack111lllll1_opy_
  global bstack1111l111_opy_
  global bstack1ll1l1lll1_opy_
  global bstack1l111l111_opy_
  bstack11l1l11l1_opy_.stop()
  bstack1ll11l1lll_opy_.bstack11l111l1_opy_()
  [bstack1lll1lll11_opy_, bstack11l1l1lll_opy_] = get_build_link()
  if bstack1lll1lll11_opy_ is not None and bstack1lll111l_opy_() != -1:
    sessions = bstack1lllll1lll_opy_(bstack1lll1lll11_opy_)
    bstack1l111l11l_opy_(sessions, bstack11l1l1lll_opy_)
  if bstack111lllll1_opy_ == bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩೀ") and bstack1111l111_opy_ != 0:
    sys.exit(bstack1111l111_opy_)
  if bstack111lllll1_opy_ == bstack1l1l1l1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪು") and bstack1ll1l1lll1_opy_ != 0:
    sys.exit(bstack1ll1l1lll1_opy_)
def bstack1l1l1ll11_opy_(bstack11lll111l_opy_):
  if bstack11lll111l_opy_:
    return bstack11lll111l_opy_.capitalize()
  else:
    return bstack1l1l1l1_opy_ (u"ࠫࠬೂ")
def bstack1l11ll1ll_opy_(bstack1l1lll1l1_opy_):
  if bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪೃ") in bstack1l1lll1l1_opy_ and bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫೄ")] != bstack1l1l1l1_opy_ (u"ࠧࠨ೅"):
    return bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ೆ")]
  else:
    bstack1l1l1111l1_opy_ = bstack1l1l1l1_opy_ (u"ࠤࠥೇ")
    if bstack1l1l1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪೈ") in bstack1l1lll1l1_opy_ and bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ೉")] != None:
      bstack1l1l1111l1_opy_ += bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬೊ")] + bstack1l1l1l1_opy_ (u"ࠨࠬࠡࠤೋ")
      if bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡰࡵࠪೌ")] == bstack1l1l1l1_opy_ (u"ࠣ࡫ࡲࡷ್ࠧ"):
        bstack1l1l1111l1_opy_ += bstack1l1l1l1_opy_ (u"ࠤ࡬ࡓࡘࠦࠢ೎")
      bstack1l1l1111l1_opy_ += (bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ೏")] or bstack1l1l1l1_opy_ (u"ࠫࠬ೐"))
      return bstack1l1l1111l1_opy_
    else:
      bstack1l1l1111l1_opy_ += bstack1l1l1ll11_opy_(bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭೑")]) + bstack1l1l1l1_opy_ (u"ࠨࠠࠣ೒") + (
              bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ೓")] or bstack1l1l1l1_opy_ (u"ࠨࠩ೔")) + bstack1l1l1l1_opy_ (u"ࠤ࠯ࠤࠧೕ")
      if bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"ࠪࡳࡸ࠭ೖ")] == bstack1l1l1l1_opy_ (u"ࠦ࡜࡯࡮ࡥࡱࡺࡷࠧ೗"):
        bstack1l1l1111l1_opy_ += bstack1l1l1l1_opy_ (u"ࠧ࡝ࡩ࡯ࠢࠥ೘")
      bstack1l1l1111l1_opy_ += bstack1l1lll1l1_opy_[bstack1l1l1l1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ೙")] or bstack1l1l1l1_opy_ (u"ࠧࠨ೚")
      return bstack1l1l1111l1_opy_
def bstack1ll1111lll_opy_(bstack11l1l1ll_opy_):
  if bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠣࡦࡲࡲࡪࠨ೛"):
    return bstack1l1l1l1_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾࡬ࡸࡥࡦࡰ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦ࡬ࡸࡥࡦࡰࠥࡂࡈࡵ࡭ࡱ࡮ࡨࡸࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ೜")
  elif bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥೝ"):
    return bstack1l1l1l1_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡲࡦࡦ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡷ࡫ࡤࠣࡀࡉࡥ࡮ࡲࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧೞ")
  elif bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ೟"):
    return bstack1l1l1l1_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡩࡵࡩࡪࡴ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡩࡵࡩࡪࡴࠢ࠿ࡒࡤࡷࡸ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ೠ")
  elif bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨೡ"):
    return bstack1l1l1l1_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡶࡪࡪ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡴࡨࡨࠧࡄࡅࡳࡴࡲࡶࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪೢ")
  elif bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥೣ"):
    return bstack1l1l1l1_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࠩࡥࡦࡣ࠶࠶࠻ࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࠤࡧࡨࡥ࠸࠸࠶ࠣࡀࡗ࡭ࡲ࡫࡯ࡶࡶ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ೤")
  elif bstack11l1l1ll_opy_ == bstack1l1l1l1_opy_ (u"ࠦࡷࡻ࡮࡯࡫ࡱ࡫ࠧ೥"):
    return bstack1l1l1l1_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡣ࡮ࡤࡧࡰࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡣ࡮ࡤࡧࡰࠨ࠾ࡓࡷࡱࡲ࡮ࡴࡧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭೦")
  else:
    return bstack1l1l1l1_opy_ (u"࠭࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡥࡰࡦࡩ࡫࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡥࡰࡦࡩ࡫ࠣࡀࠪ೧") + bstack1l1l1ll11_opy_(
      bstack11l1l1ll_opy_) + bstack1l1l1l1_opy_ (u"ࠧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭೨")
def bstack11l1ll1l_opy_(session):
  return bstack1l1l1l1_opy_ (u"ࠨ࠾ࡷࡶࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡸ࡯ࡸࠤࡁࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠥࡹࡥࡴࡵ࡬ࡳࡳ࠳࡮ࡢ࡯ࡨࠦࡃࡂࡡࠡࡪࡵࡩ࡫ࡃࠢࡼࡿࠥࠤࡹࡧࡲࡨࡧࡷࡁࠧࡥࡢ࡭ࡣࡱ࡯ࠧࡄࡻࡾ࠾࠲ࡥࡃࡂ࠯ࡵࡦࡁࡿࢂࢁࡽ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿࠳ࡹࡸ࠾ࠨ೩").format(
    session[bstack1l1l1l1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤࡡࡸࡶࡱ࠭೪")], bstack1l11ll1ll_opy_(session), bstack1ll1111lll_opy_(session[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠩ೫")]),
    bstack1ll1111lll_opy_(session[bstack1l1l1l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ೬")]),
    bstack1l1l1ll11_opy_(session[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭೭")] or session[bstack1l1l1l1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭೮")] or bstack1l1l1l1_opy_ (u"ࠧࠨ೯")) + bstack1l1l1l1_opy_ (u"ࠣࠢࠥ೰") + (session[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫೱ")] or bstack1l1l1l1_opy_ (u"ࠪࠫೲ")),
    session[bstack1l1l1l1_opy_ (u"ࠫࡴࡹࠧೳ")] + bstack1l1l1l1_opy_ (u"ࠧࠦࠢ೴") + session[bstack1l1l1l1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ೵")], session[bstack1l1l1l1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ೶")] or bstack1l1l1l1_opy_ (u"ࠨࠩ೷"),
    session[bstack1l1l1l1_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭೸")] if session[bstack1l1l1l1_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧ೹")] else bstack1l1l1l1_opy_ (u"ࠫࠬ೺"))
def bstack1l111l11l_opy_(sessions, bstack11l1l1lll_opy_):
  try:
    bstack1ll11ll1ll_opy_ = bstack1l1l1l1_opy_ (u"ࠧࠨ೻")
    if not os.path.exists(bstack1lllll1l11_opy_):
      os.mkdir(bstack1lllll1l11_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l1l1_opy_ (u"࠭ࡡࡴࡵࡨࡸࡸ࠵ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫ೼")), bstack1l1l1l1_opy_ (u"ࠧࡳࠩ೽")) as f:
      bstack1ll11ll1ll_opy_ = f.read()
    bstack1ll11ll1ll_opy_ = bstack1ll11ll1ll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠨࡽࠨࡖࡊ࡙ࡕࡍࡖࡖࡣࡈࡕࡕࡏࡖࠨࢁࠬ೾"), str(len(sessions)))
    bstack1ll11ll1ll_opy_ = bstack1ll11ll1ll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠥࡾࠩ೿"), bstack11l1l1lll_opy_)
    bstack1ll11ll1ll_opy_ = bstack1ll11ll1ll_opy_.replace(bstack1l1l1l1_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣࡓࡇࡍࡆࠧࢀࠫഀ"),
                                              sessions[0].get(bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡦࡳࡥࠨഁ")) if sessions[0] else bstack1l1l1l1_opy_ (u"ࠬ࠭ം"))
    with open(os.path.join(bstack1lllll1l11_opy_, bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪഃ")), bstack1l1l1l1_opy_ (u"ࠧࡸࠩഄ")) as stream:
      stream.write(bstack1ll11ll1ll_opy_.split(bstack1l1l1l1_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬഅ"))[0])
      for session in sessions:
        stream.write(bstack11l1ll1l_opy_(session))
      stream.write(bstack1ll11ll1ll_opy_.split(bstack1l1l1l1_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭ആ"))[1])
    logger.info(bstack1l1l1l1_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࡩࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡨࡵࡪ࡮ࡧࠤࡦࡸࡴࡪࡨࡤࡧࡹࡹࠠࡢࡶࠣࡿࢂ࠭ഇ").format(bstack1lllll1l11_opy_));
  except Exception as e:
    logger.debug(bstack11111llll_opy_.format(str(e)))
def bstack1lllll1lll_opy_(bstack1lll1lll11_opy_):
  global CONFIG
  try:
    host = bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡩ࠮ࡥ࡯ࡳࡺࡪࠧഈ") if bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱࠩഉ") in CONFIG else bstack1l1l1l1_opy_ (u"࠭ࡡࡱ࡫ࠪഊ")
    user = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩഋ")]
    key = CONFIG[bstack1l1l1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫഌ")]
    bstack1l11lll1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨ഍") if bstack1l1l1l1_opy_ (u"ࠪࡥࡵࡶࠧഎ") in CONFIG else bstack1l1l1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ഏ")
    url = bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࢁࡽ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠳ࡰࡳࡰࡰࠪഐ").format(user, key, host, bstack1l11lll1_opy_,
                                                                                bstack1lll1lll11_opy_)
    headers = {
      bstack1l1l1l1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬ഑"): bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪഒ"),
    }
    proxies = bstack11l111lll_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      return list(map(lambda session: session[bstack1l1l1l1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ഓ")], response.json()))
  except Exception as e:
    logger.debug(bstack11ll1111l_opy_.format(str(e)))
def get_build_link():
  global CONFIG
  global bstack11lll1l11_opy_
  try:
    if bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬഔ") in CONFIG:
      host = bstack1l1l1l1_opy_ (u"ࠪࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩ࠭ക") if bstack1l1l1l1_opy_ (u"ࠫࡦࡶࡰࠨഖ") in CONFIG else bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡪࠩഗ")
      user = CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨഘ")]
      key = CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪങ")]
      bstack1l11lll1_opy_ = bstack1l1l1l1_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧച") if bstack1l1l1l1_opy_ (u"ࠩࡤࡴࡵ࠭ഛ") in CONFIG else bstack1l1l1l1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬജ")
      url = bstack1l1l1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࢀࢃ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠴ࡪࡴࡱࡱࠫഝ").format(user, key, host, bstack1l11lll1_opy_)
      headers = {
        bstack1l1l1l1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫഞ"): bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩട"),
      }
      if bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩഠ") in CONFIG:
        params = {bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ഡ"): CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬഢ")], bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ണ"): CONFIG[bstack1l1l1l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ത")]}
      else:
        params = {bstack1l1l1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪഥ"): CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩദ")]}
      proxies = bstack11l111lll_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack1ll111ll11_opy_ = response.json()[0][bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡧࡻࡩ࡭ࡦࠪധ")]
        if bstack1ll111ll11_opy_:
          bstack11l1l1lll_opy_ = bstack1ll111ll11_opy_[bstack1l1l1l1_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬന")].split(bstack1l1l1l1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤ࠯ࡥࡹ࡮ࡲࡤࠨഩ"))[0] + bstack1l1l1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡵ࠲ࠫപ") + bstack1ll111ll11_opy_[
            bstack1l1l1l1_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧഫ")]
          logger.info(bstack11l1l1111_opy_.format(bstack11l1l1lll_opy_))
          bstack11lll1l11_opy_ = bstack1ll111ll11_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨബ")]
          bstack1l11l1lll_opy_ = CONFIG[bstack1l1l1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩഭ")]
          if bstack1l1l1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩമ") in CONFIG:
            bstack1l11l1lll_opy_ += bstack1l1l1l1_opy_ (u"ࠨࠢࠪയ") + CONFIG[bstack1l1l1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫര")]
          if bstack1l11l1lll_opy_ != bstack1ll111ll11_opy_[bstack1l1l1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨറ")]:
            logger.debug(bstack1ll11ll111_opy_.format(bstack1ll111ll11_opy_[bstack1l1l1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩല")], bstack1l11l1lll_opy_))
          return [bstack1ll111ll11_opy_[bstack1l1l1l1_opy_ (u"ࠬ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨള")], bstack11l1l1lll_opy_]
    else:
      logger.warn(bstack11ll1llll_opy_)
  except Exception as e:
    logger.debug(bstack1ll1l11111_opy_.format(str(e)))
  return [None, None]
def bstack1l1l11l11_opy_(url, bstack1l1lllll11_opy_=False):
  global CONFIG
  global bstack1ll111l11_opy_
  if not bstack1ll111l11_opy_:
    hostname = bstack1l111lll11_opy_(url)
    is_private = bstack1ll1ll1l_opy_(hostname)
    if (bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪഴ") in CONFIG and not bstack1l1111ll_opy_(CONFIG[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫവ")])) and (is_private or bstack1l1lllll11_opy_):
      bstack1ll111l11_opy_ = hostname
def bstack1l111lll11_opy_(url):
  return urlparse(url).hostname
def bstack1ll1ll1l_opy_(hostname):
  for bstack1l11l1l1ll_opy_ in bstack1l11l1l11l_opy_:
    regex = re.compile(bstack1l11l1l1ll_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack111111l11_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False
def getAccessibilityResults(driver):
  global CONFIG
  global bstack111lll1l_opy_
  bstack1lll1lll_opy_ = not (bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬശ"), None) and bstack1l111l1ll1_opy_(
          threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨഷ"), None))
  bstack111111l1l_opy_ = getattr(driver, bstack1l1l1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪസ"), None) != True
  if not bstack1l11lll1l_opy_.bstack1ll1llllll_opy_(CONFIG, bstack111lll1l_opy_) or (bstack111111l1l_opy_ and bstack1lll1lll_opy_):
    logger.warning(bstack1l1l1l1_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸ࠴ࠢഹ"))
    return {}
  try:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩഺ"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack1ll1ll1l11_opy_.bstack1l1l11ll_opy_)
    return results
  except Exception:
    logger.error(bstack1l1l1l1_opy_ (u"ࠨࡎࡰࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡻࡪࡸࡥࠡࡨࡲࡹࡳࡪ࠮഻ࠣ"))
    return {}
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack111lll1l_opy_
  bstack1lll1lll_opy_ = not (bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷ഼ࠫ"), None) and bstack1l111l1ll1_opy_(
          threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧഽ"), None))
  bstack111111l1l_opy_ = getattr(driver, bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩാ"), None) != True
  if not bstack1l11lll1l_opy_.bstack1ll1llllll_opy_(CONFIG, bstack111lll1l_opy_) or (bstack111111l1l_opy_ and bstack1lll1lll_opy_):
    logger.warning(bstack1l1l1l1_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡩࡹࡸࡩࡦࡸࡨࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡹࡵ࡮࡯ࡤࡶࡾ࠴ࠢി"))
    return {}
  try:
    logger.debug(bstack1l1l1l1_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺࠩീ"))
    logger.debug(perform_scan(driver))
    bstack1l111l11_opy_ = driver.execute_async_script(bstack1ll1ll1l11_opy_.bstack11ll1l11l_opy_)
    return bstack1l111l11_opy_
  except Exception:
    logger.error(bstack1l1l1l1_opy_ (u"ࠧࡔ࡯ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡸࡱࡲࡧࡲࡺࠢࡺࡥࡸࠦࡦࡰࡷࡱࡨ࠳ࠨു"))
    return {}
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack111lll1l_opy_
  bstack1lll1lll_opy_ = not (bstack1l111l1ll1_opy_(threading.current_thread(), bstack1l1l1l1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪൂ"), None) and bstack1l111l1ll1_opy_(
          threading.current_thread(), bstack1l1l1l1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ൃ"), None))
  bstack111111l1l_opy_ = getattr(driver, bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨൄ"), None) != True
  if not bstack1l11lll1l_opy_.bstack1ll1llllll_opy_(CONFIG, bstack111lll1l_opy_) or (bstack111111l1l_opy_ and bstack1lll1lll_opy_):
    logger.warning(bstack1l1l1l1_opy_ (u"ࠤࡑࡳࡹࠦࡡ࡯ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡸࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡹࡣࡢࡰ࠱ࠦ൅"))
    return {}
  try:
    bstack1l111l1ll_opy_ = driver.execute_async_script(bstack1ll1ll1l11_opy_.perform_scan, {bstack1l1l1l1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࠪെ"): kwargs.get(bstack1l1l1l1_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࡣࡨࡵ࡭࡮ࡣࡱࡨࠬേ"), None) or bstack1l1l1l1_opy_ (u"ࠬ࠭ൈ")})
    return bstack1l111l1ll_opy_
  except Exception:
    logger.error(bstack1l1l1l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡵࡹࡳࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡳࡤࡣࡱ࠲ࠧ൉"))
    return {}