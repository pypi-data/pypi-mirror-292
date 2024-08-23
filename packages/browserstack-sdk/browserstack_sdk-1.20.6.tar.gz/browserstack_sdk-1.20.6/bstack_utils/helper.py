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
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
import urllib
from urllib.parse import urlparse
import copy
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack11l111l1ll_opy_, bstack1l11l1l11l_opy_, bstack1l11l1llll_opy_, bstack111l1l1l_opy_,
                                    bstack11l111llll_opy_, bstack11l1111ll1_opy_, bstack11l11l111l_opy_, bstack11l111ll1l_opy_)
from bstack_utils.messages import bstack11ll11ll1_opy_, bstack1ll1lll1l1_opy_
from bstack_utils.proxy import bstack11l111lll_opy_, bstack111l1ll1_opy_
bstack1l111l111_opy_ = Config.bstack1llll1111l_opy_()
logger = logging.getLogger(__name__)
def bstack11l1ll111l_opy_(config):
    return config[bstack1l1l1l1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪᇿ")]
def bstack11l1ll11ll_opy_(config):
    return config[bstack1l1l1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬሀ")]
def bstack1l11ll1l1l_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll1l1l_opy_(obj):
    values = []
    bstack111l1llll1_opy_ = re.compile(bstack1l1l1l1_opy_ (u"ࡵࠦࡣࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࡟ࡨ࠰ࠪࠢሁ"), re.I)
    for key in obj.keys():
        if bstack111l1llll1_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111ll1l1l1_opy_(config):
    tags = []
    tags.extend(bstack111lll1l1l_opy_(os.environ))
    tags.extend(bstack111lll1l1l_opy_(config))
    return tags
def bstack111ll1ll11_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111lll1111_opy_(bstack111lllll11_opy_):
    if not bstack111lllll11_opy_:
        return bstack1l1l1l1_opy_ (u"ࠫࠬሂ")
    return bstack1l1l1l1_opy_ (u"ࠧࢁࡽࠡࠪࡾࢁ࠮ࠨሃ").format(bstack111lllll11_opy_.name, bstack111lllll11_opy_.email)
def bstack11l1lll1l1_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111l1l1ll1_opy_ = repo.common_dir
        info = {
            bstack1l1l1l1_opy_ (u"ࠨࡳࡩࡣࠥሄ"): repo.head.commit.hexsha,
            bstack1l1l1l1_opy_ (u"ࠢࡴࡪࡲࡶࡹࡥࡳࡩࡣࠥህ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1l1l1l1_opy_ (u"ࠣࡤࡵࡥࡳࡩࡨࠣሆ"): repo.active_branch.name,
            bstack1l1l1l1_opy_ (u"ࠤࡷࡥ࡬ࠨሇ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1l1l1l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡷࡩࡷࠨለ"): bstack111lll1111_opy_(repo.head.commit.committer),
            bstack1l1l1l1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡸࡪࡸ࡟ࡥࡣࡷࡩࠧሉ"): repo.head.commit.committed_datetime.isoformat(),
            bstack1l1l1l1_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࠧሊ"): bstack111lll1111_opy_(repo.head.commit.author),
            bstack1l1l1l1_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡥࡤࡢࡶࡨࠦላ"): repo.head.commit.authored_datetime.isoformat(),
            bstack1l1l1l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠣሌ"): repo.head.commit.message,
            bstack1l1l1l1_opy_ (u"ࠣࡴࡲࡳࡹࠨል"): repo.git.rev_parse(bstack1l1l1l1_opy_ (u"ࠤ࠰࠱ࡸ࡮࡯ࡸ࠯ࡷࡳࡵࡲࡥࡷࡧ࡯ࠦሎ")),
            bstack1l1l1l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡰࡰࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦሏ"): bstack111l1l1ll1_opy_,
            bstack1l1l1l1_opy_ (u"ࠦࡼࡵࡲ࡬ࡶࡵࡩࡪࡥࡧࡪࡶࡢࡨ࡮ࡸࠢሐ"): subprocess.check_output([bstack1l1l1l1_opy_ (u"ࠧ࡭ࡩࡵࠤሑ"), bstack1l1l1l1_opy_ (u"ࠨࡲࡦࡸ࠰ࡴࡦࡸࡳࡦࠤሒ"), bstack1l1l1l1_opy_ (u"ࠢ࠮࠯ࡪ࡭ࡹ࠳ࡣࡰ࡯ࡰࡳࡳ࠳ࡤࡪࡴࠥሓ")]).strip().decode(
                bstack1l1l1l1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧሔ")),
            bstack1l1l1l1_opy_ (u"ࠤ࡯ࡥࡸࡺ࡟ࡵࡣࡪࠦሕ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1l1l1l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡶࡣࡸ࡯࡮ࡤࡧࡢࡰࡦࡹࡴࡠࡶࡤ࡫ࠧሖ"): repo.git.rev_list(
                bstack1l1l1l1_opy_ (u"ࠦࢀࢃ࠮࠯ࡽࢀࠦሗ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111l1l111l_opy_ = []
        for remote in remotes:
            bstack111l11llll_opy_ = {
                bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥመ"): remote.name,
                bstack1l1l1l1_opy_ (u"ࠨࡵࡳ࡮ࠥሙ"): remote.url,
            }
            bstack111l1l111l_opy_.append(bstack111l11llll_opy_)
        bstack1111lll11l_opy_ = {
            bstack1l1l1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧሚ"): bstack1l1l1l1_opy_ (u"ࠣࡩ࡬ࡸࠧማ"),
            **info,
            bstack1l1l1l1_opy_ (u"ࠤࡵࡩࡲࡵࡴࡦࡵࠥሜ"): bstack111l1l111l_opy_
        }
        bstack1111lll11l_opy_ = bstack111lll1ll1_opy_(bstack1111lll11l_opy_)
        return bstack1111lll11l_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1l1l1l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡳࡵࡻ࡬ࡢࡶ࡬ࡲ࡬ࠦࡇࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨም").format(err))
        return {}
def bstack111lll1ll1_opy_(bstack1111lll11l_opy_):
    bstack1111ll1lll_opy_ = bstack111ll11l11_opy_(bstack1111lll11l_opy_)
    if bstack1111ll1lll_opy_ and bstack1111ll1lll_opy_ > bstack11l111llll_opy_:
        bstack111llll1l1_opy_ = bstack1111ll1lll_opy_ - bstack11l111llll_opy_
        bstack1111llll1l_opy_ = bstack111l1ll1l1_opy_(bstack1111lll11l_opy_[bstack1l1l1l1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧሞ")], bstack111llll1l1_opy_)
        bstack1111lll11l_opy_[bstack1l1l1l1_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡤࡳࡥࡴࡵࡤ࡫ࡪࠨሟ")] = bstack1111llll1l_opy_
        logger.info(bstack1l1l1l1_opy_ (u"ࠨࡔࡩࡧࠣࡧࡴࡳ࡭ࡪࡶࠣ࡬ࡦࡹࠠࡣࡧࡨࡲࠥࡺࡲࡶࡰࡦࡥࡹ࡫ࡤ࠯ࠢࡖ࡭ࡿ࡫ࠠࡰࡨࠣࡧࡴࡳ࡭ࡪࡶࠣࡥ࡫ࡺࡥࡳࠢࡷࡶࡺࡴࡣࡢࡶ࡬ࡳࡳࠦࡩࡴࠢࡾࢁࠥࡑࡂࠣሠ")
                    .format(bstack111ll11l11_opy_(bstack1111lll11l_opy_) / 1024))
    return bstack1111lll11l_opy_
def bstack111ll11l11_opy_(bstack11l1llll1_opy_):
    try:
        if bstack11l1llll1_opy_:
            bstack111ll11ll1_opy_ = json.dumps(bstack11l1llll1_opy_)
            bstack11l11111ll_opy_ = sys.getsizeof(bstack111ll11ll1_opy_)
            return bstack11l11111ll_opy_
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠢࡔࡱࡰࡩࡹ࡮ࡩ࡯ࡩࠣࡻࡪࡴࡴࠡࡹࡵࡳࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡣࡢ࡮ࡦࡹࡱࡧࡴࡪࡰࡪࠤࡸ࡯ࡺࡦࠢࡲࡪࠥࡐࡓࡐࡐࠣࡳࡧࡰࡥࡤࡶ࠽ࠤࢀࢃࠢሡ").format(e))
    return -1
def bstack111l1ll1l1_opy_(field, bstack111l11111l_opy_):
    try:
        bstack111llllll1_opy_ = len(bytes(bstack11l1111ll1_opy_, bstack1l1l1l1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧሢ")))
        bstack111ll11l1l_opy_ = bytes(field, bstack1l1l1l1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨሣ"))
        bstack111l1lll1l_opy_ = len(bstack111ll11l1l_opy_)
        bstack111lll111l_opy_ = ceil(bstack111l1lll1l_opy_ - bstack111l11111l_opy_ - bstack111llllll1_opy_)
        if bstack111lll111l_opy_ > 0:
            bstack111ll1ll1l_opy_ = bstack111ll11l1l_opy_[:bstack111lll111l_opy_].decode(bstack1l1l1l1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩሤ"), errors=bstack1l1l1l1_opy_ (u"ࠫ࡮࡭࡮ࡰࡴࡨࠫሥ")) + bstack11l1111ll1_opy_
            return bstack111ll1ll1l_opy_
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡸࡷࡻ࡮ࡤࡣࡷ࡭ࡳ࡭ࠠࡧ࡫ࡨࡰࡩ࠲ࠠ࡯ࡱࡷ࡬࡮ࡴࡧࠡࡹࡤࡷࠥࡺࡲࡶࡰࡦࡥࡹ࡫ࡤࠡࡪࡨࡶࡪࡀࠠࡼࡿࠥሦ").format(e))
    return field
def bstack111111lll_opy_():
    env = os.environ
    if (bstack1l1l1l1_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡖࡔࡏࠦሧ") in env and len(env[bstack1l1l1l1_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡗࡕࡐࠧረ")]) > 0) or (
            bstack1l1l1l1_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡋࡓࡒࡋࠢሩ") in env and len(env[bstack1l1l1l1_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢࡌࡔࡓࡅࠣሪ")]) > 0):
        return {
            bstack1l1l1l1_opy_ (u"ࠥࡲࡦࡳࡥࠣራ"): bstack1l1l1l1_opy_ (u"ࠦࡏ࡫࡮࡬࡫ࡱࡷࠧሬ"),
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣር"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤሮ")),
            bstack1l1l1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤሯ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡌࡒࡆࡤࡔࡁࡎࡇࠥሰ")),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣሱ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤሲ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠦࡈࡏࠢሳ")) == bstack1l1l1l1_opy_ (u"ࠧࡺࡲࡶࡧࠥሴ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡉࡉࠣስ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧሶ"): bstack1l1l1l1_opy_ (u"ࠣࡅ࡬ࡶࡨࡲࡥࡄࡋࠥሷ"),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧሸ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨሹ")),
            bstack1l1l1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨሺ"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡐࡏࡃࠤሻ")),
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧሼ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࠥሽ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠣࡅࡌࠦሾ")) == bstack1l1l1l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢሿ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࠥቀ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤቁ"): bstack1l1l1l1_opy_ (u"࡚ࠧࡲࡢࡸ࡬ࡷࠥࡉࡉࠣቂ"),
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤቃ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙࡟ࡃࡗࡌࡐࡉࡥࡗࡆࡄࡢ࡙ࡗࡒࠢቄ")),
            bstack1l1l1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥቅ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦቆ")),
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤቇ"): env.get(bstack1l1l1l1_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥቈ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡉࠣ቉")) == bstack1l1l1l1_opy_ (u"ࠨࡴࡳࡷࡨࠦቊ") and env.get(bstack1l1l1l1_opy_ (u"ࠢࡄࡋࡢࡒࡆࡓࡅࠣቋ")) == bstack1l1l1l1_opy_ (u"ࠣࡥࡲࡨࡪࡹࡨࡪࡲࠥቌ"):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢቍ"): bstack1l1l1l1_opy_ (u"ࠥࡇࡴࡪࡥࡴࡪ࡬ࡴࠧ቎"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ቏"): None,
            bstack1l1l1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢቐ"): None,
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧቑ"): None
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡆࡗࡇࡎࡄࡊࠥቒ")) and env.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡈࡕࡍࡎࡋࡗࠦቓ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢቔ"): bstack1l1l1l1_opy_ (u"ࠥࡆ࡮ࡺࡢࡶࡥ࡮ࡩࡹࠨቕ"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢቖ"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡉࡌࡘࡤࡎࡔࡕࡒࡢࡓࡗࡏࡇࡊࡐࠥ቗")),
            bstack1l1l1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣቘ"): None,
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ቙"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥቚ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡍࠧቛ")) == bstack1l1l1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣቜ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠦࡉࡘࡏࡏࡇࠥቝ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ቞"): bstack1l1l1l1_opy_ (u"ࠨࡄࡳࡱࡱࡩࠧ቟"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥበ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡌࡊࡐࡎࠦቡ")),
            bstack1l1l1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦቢ"): None,
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤባ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡉࡘࡏࡏࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤቤ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡉࠣብ")) == bstack1l1l1l1_opy_ (u"ࠨࡴࡳࡷࡨࠦቦ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࠥቧ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠣࡰࡤࡱࡪࠨቨ"): bstack1l1l1l1_opy_ (u"ࠤࡖࡩࡲࡧࡰࡩࡱࡵࡩࠧቩ"),
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨቪ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋ࡟ࡐࡔࡊࡅࡓࡏ࡚ࡂࡖࡌࡓࡓࡥࡕࡓࡎࠥቫ")),
            bstack1l1l1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢቬ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦቭ")),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨቮ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡏࡕࡂࡠࡋࡇࠦቯ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡍࠧተ")) == bstack1l1l1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣቱ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠦࡌࡏࡔࡍࡃࡅࡣࡈࡏࠢቲ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥታ"): bstack1l1l1l1_opy_ (u"ࠨࡇࡪࡶࡏࡥࡧࠨቴ"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥት"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡗࡕࡐࠧቶ")),
            bstack1l1l1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦቷ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣቸ")),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥቹ"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤࡏࡄࠣቺ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠨࡃࡊࠤቻ")) == bstack1l1l1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧቼ") and bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࠦች"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢቾ"): bstack1l1l1l1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥ࡭࡬ࡸࡪࠨቿ"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢኀ"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦኁ")),
            bstack1l1l1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣኂ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡐࡆࡈࡅࡍࠤኃ")) or env.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡎࡂࡏࡈࠦኄ")),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣኅ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧኆ"))
        }
    if bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"࡙ࠦࡌ࡟ࡃࡗࡌࡐࡉࠨኇ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥኈ"): bstack1l1l1l1_opy_ (u"ࠨࡖࡪࡵࡸࡥࡱࠦࡓࡵࡷࡧ࡭ࡴࠦࡔࡦࡣࡰࠤࡘ࡫ࡲࡷ࡫ࡦࡩࡸࠨ኉"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥኊ"): bstack1l1l1l1_opy_ (u"ࠣࡽࢀࡿࢂࠨኋ").format(env.get(bstack1l1l1l1_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡆࡐࡗࡑࡈࡆ࡚ࡉࡐࡐࡖࡉࡗ࡜ࡅࡓࡗࡕࡍࠬኌ")), env.get(bstack1l1l1l1_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡑࡔࡒࡎࡊࡉࡔࡊࡆࠪኍ"))),
            bstack1l1l1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ኎"): env.get(bstack1l1l1l1_opy_ (u"࡙࡙ࠧࡔࡖࡈࡑࡤࡊࡅࡇࡋࡑࡍ࡙ࡏࡏࡏࡋࡇࠦ኏")),
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧነ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢኑ"))
        }
    if bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࠥኒ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢና"): bstack1l1l1l1_opy_ (u"ࠥࡅࡵࡶࡶࡦࡻࡲࡶࠧኔ"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢን"): bstack1l1l1l1_opy_ (u"ࠧࢁࡽ࠰ࡲࡵࡳ࡯࡫ࡣࡵ࠱ࡾࢁ࠴ࢁࡽ࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀࠦኖ").format(env.get(bstack1l1l1l1_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡗࡕࡐࠬኗ")), env.get(bstack1l1l1l1_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡄࡇࡈࡕࡕࡏࡖࡢࡒࡆࡓࡅࠨኘ")), env.get(bstack1l1l1l1_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡔࡗࡕࡊࡆࡅࡗࡣࡘࡒࡕࡈࠩኙ")), env.get(bstack1l1l1l1_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭ኚ"))),
            bstack1l1l1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧኛ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣኜ")),
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦኝ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢኞ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠢࡂ࡜ࡘࡖࡊࡥࡈࡕࡖࡓࡣ࡚࡙ࡅࡓࡡࡄࡋࡊࡔࡔࠣኟ")) and env.get(bstack1l1l1l1_opy_ (u"ࠣࡖࡉࡣࡇ࡛ࡉࡍࡆࠥአ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢኡ"): bstack1l1l1l1_opy_ (u"ࠥࡅࡿࡻࡲࡦࠢࡆࡍࠧኢ"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢኣ"): bstack1l1l1l1_opy_ (u"ࠧࢁࡽࡼࡿ࠲ࡣࡧࡻࡩ࡭ࡦ࠲ࡶࡪࡹࡵ࡭ࡶࡶࡃࡧࡻࡩ࡭ࡦࡌࡨࡂࢁࡽࠣኤ").format(env.get(bstack1l1l1l1_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩእ")), env.get(bstack1l1l1l1_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࠬኦ")), env.get(bstack1l1l1l1_opy_ (u"ࠨࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠨኧ"))),
            bstack1l1l1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦከ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠥኩ")),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥኪ"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧካ"))
        }
    if any([env.get(bstack1l1l1l1_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦኬ")), env.get(bstack1l1l1l1_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡖࡊ࡙ࡏࡍࡘࡈࡈࡤ࡙ࡏࡖࡔࡆࡉࡤ࡜ࡅࡓࡕࡌࡓࡓࠨክ")), env.get(bstack1l1l1l1_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡘࡕࡕࡓࡅࡈࡣ࡛ࡋࡒࡔࡋࡒࡒࠧኮ"))]):
        return {
            bstack1l1l1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢኯ"): bstack1l1l1l1_opy_ (u"ࠥࡅ࡜࡙ࠠࡄࡱࡧࡩࡇࡻࡩ࡭ࡦࠥኰ"),
            bstack1l1l1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ኱"): env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡒࡘࡆࡑࡏࡃࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦኲ")),
            bstack1l1l1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣኳ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧኴ")),
            bstack1l1l1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢኵ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢ኶"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡦࡺ࡯࡬ࡥࡐࡸࡱࡧ࡫ࡲࠣ኷")):
        return {
            bstack1l1l1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤኸ"): bstack1l1l1l1_opy_ (u"ࠧࡈࡡ࡮ࡤࡲࡳࠧኹ"),
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤኺ"): env.get(bstack1l1l1l1_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡘࡥࡴࡷ࡯ࡸࡸ࡛ࡲ࡭ࠤኻ")),
            bstack1l1l1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥኼ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡶ࡬ࡴࡸࡴࡋࡱࡥࡒࡦࡳࡥࠣኽ")),
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤኾ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡑࡹࡲࡨࡥࡳࠤ኿"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࠨዀ")) or env.get(bstack1l1l1l1_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡎࡃࡌࡒࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡔࡖࡄࡖ࡙ࡋࡄࠣ዁")):
        return {
            bstack1l1l1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧዂ"): bstack1l1l1l1_opy_ (u"࡙ࠣࡨࡶࡨࡱࡥࡳࠤዃ"),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧዄ"): env.get(bstack1l1l1l1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢዅ")),
            bstack1l1l1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ዆"): bstack1l1l1l1_opy_ (u"ࠧࡓࡡࡪࡰࠣࡔ࡮ࡶࡥ࡭࡫ࡱࡩࠧ዇") if env.get(bstack1l1l1l1_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡎࡃࡌࡒࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡔࡖࡄࡖ࡙ࡋࡄࠣወ")) else None,
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨዉ"): env.get(bstack1l1l1l1_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡊࡍ࡙ࡥࡃࡐࡏࡐࡍ࡙ࠨዊ"))
        }
    if any([env.get(bstack1l1l1l1_opy_ (u"ࠤࡊࡇࡕࡥࡐࡓࡑࡍࡉࡈ࡚ࠢዋ")), env.get(bstack1l1l1l1_opy_ (u"ࠥࡋࡈࡒࡏࡖࡆࡢࡔࡗࡕࡊࡆࡅࡗࠦዌ")), env.get(bstack1l1l1l1_opy_ (u"ࠦࡌࡕࡏࡈࡎࡈࡣࡈࡒࡏࡖࡆࡢࡔࡗࡕࡊࡆࡅࡗࠦው"))]):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥዎ"): bstack1l1l1l1_opy_ (u"ࠨࡇࡰࡱࡪࡰࡪࠦࡃ࡭ࡱࡸࡨࠧዏ"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥዐ"): None,
            bstack1l1l1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥዑ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡓࡖࡔࡐࡅࡄࡖࡢࡍࡉࠨዒ")),
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤዓ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨዔ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࠣዕ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦዖ"): bstack1l1l1l1_opy_ (u"ࠢࡔࡪ࡬ࡴࡵࡧࡢ࡭ࡧࠥ዗"),
            bstack1l1l1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦዘ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣዙ")),
            bstack1l1l1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧዚ"): bstack1l1l1l1_opy_ (u"ࠦࡏࡵࡢࠡࠥࡾࢁࠧዛ").format(env.get(bstack1l1l1l1_opy_ (u"࡙ࠬࡈࡊࡒࡓࡅࡇࡒࡅࡠࡌࡒࡆࡤࡏࡄࠨዜ"))) if env.get(bstack1l1l1l1_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡍࡓࡇࡥࡉࡅࠤዝ")) else None,
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨዞ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥዟ"))
        }
    if bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠤࡑࡉ࡙ࡒࡉࡇ࡛ࠥዠ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠥࡲࡦࡳࡥࠣዡ"): bstack1l1l1l1_opy_ (u"ࠦࡓ࡫ࡴ࡭࡫ࡩࡽࠧዢ"),
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣዣ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡄࡆࡒࡏࡓ࡞ࡥࡕࡓࡎࠥዤ")),
            bstack1l1l1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤዥ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡕࡌࡘࡊࡥࡎࡂࡏࡈࠦዦ")),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣዧ"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡌࡈࠧየ"))
        }
    if bstack1l1111ll_opy_(env.get(bstack1l1l1l1_opy_ (u"ࠦࡌࡏࡔࡉࡗࡅࡣࡆࡉࡔࡊࡑࡑࡗࠧዩ"))):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥዪ"): bstack1l1l1l1_opy_ (u"ࠨࡇࡪࡶࡋࡹࡧࠦࡁࡤࡶ࡬ࡳࡳࡹࠢያ"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥዬ"): bstack1l1l1l1_opy_ (u"ࠣࡽࢀ࠳ࢀࢃ࠯ࡢࡥࡷ࡭ࡴࡴࡳ࠰ࡴࡸࡲࡸ࠵ࡻࡾࠤይ").format(env.get(bstack1l1l1l1_opy_ (u"ࠩࡊࡍ࡙ࡎࡕࡃࡡࡖࡉࡗ࡜ࡅࡓࡡࡘࡖࡑ࠭ዮ")), env.get(bstack1l1l1l1_opy_ (u"ࠪࡋࡎ࡚ࡈࡖࡄࡢࡖࡊࡖࡏࡔࡋࡗࡓࡗ࡟ࠧዯ")), env.get(bstack1l1l1l1_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡗ࡛ࡎࡠࡋࡇࠫደ"))),
            bstack1l1l1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢዱ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡗࡐࡔࡎࡊࡑࡕࡗࠣዲ")),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨዳ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠࡔࡘࡒࡤࡏࡄࠣዴ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡍࠧድ")) == bstack1l1l1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣዶ") and env.get(bstack1l1l1l1_opy_ (u"࡛ࠦࡋࡒࡄࡇࡏࠦዷ")) == bstack1l1l1l1_opy_ (u"ࠧ࠷ࠢዸ"):
        return {
            bstack1l1l1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦዹ"): bstack1l1l1l1_opy_ (u"ࠢࡗࡧࡵࡧࡪࡲࠢዺ"),
            bstack1l1l1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦዻ"): bstack1l1l1l1_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࡾࢁࠧዼ").format(env.get(bstack1l1l1l1_opy_ (u"࡚ࠪࡊࡘࡃࡆࡎࡢ࡙ࡗࡒࠧዽ"))),
            bstack1l1l1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨዾ"): None,
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦዿ"): None,
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠨࡔࡆࡃࡐࡇࡎ࡚࡙ࡠࡘࡈࡖࡘࡏࡏࡏࠤጀ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧጁ"): bstack1l1l1l1_opy_ (u"ࠣࡖࡨࡥࡲࡩࡩࡵࡻࠥጂ"),
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧጃ"): None,
            bstack1l1l1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧጄ"): env.get(bstack1l1l1l1_opy_ (u"࡙ࠦࡋࡁࡎࡅࡌࡘ࡞ࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡏࡃࡐࡉࠧጅ")),
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦጆ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧጇ"))
        }
    if any([env.get(bstack1l1l1l1_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࠥገ")), env.get(bstack1l1l1l1_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࡣ࡚ࡘࡌࠣጉ")), env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠢጊ")), env.get(bstack1l1l1l1_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡔࡆࡃࡐࠦጋ"))]):
        return {
            bstack1l1l1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤጌ"): bstack1l1l1l1_opy_ (u"ࠧࡉ࡯࡯ࡥࡲࡹࡷࡹࡥࠣግ"),
            bstack1l1l1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤጎ"): None,
            bstack1l1l1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤጏ"): env.get(bstack1l1l1l1_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤጐ")) or None,
            bstack1l1l1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ጑"): env.get(bstack1l1l1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡌࡈࠧጒ"), 0)
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠦࡌࡕ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤጓ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥጔ"): bstack1l1l1l1_opy_ (u"ࠨࡇࡰࡅࡇࠦጕ"),
            bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ጖"): None,
            bstack1l1l1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ጗"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡊࡓࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢጘ")),
            bstack1l1l1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤጙ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡌࡕ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡆࡓ࡚ࡔࡔࡆࡔࠥጚ"))
        }
    if env.get(bstack1l1l1l1_opy_ (u"ࠧࡉࡆࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥጛ")):
        return {
            bstack1l1l1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦጜ"): bstack1l1l1l1_opy_ (u"ࠢࡄࡱࡧࡩࡋࡸࡥࡴࡪࠥጝ"),
            bstack1l1l1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦጞ"): env.get(bstack1l1l1l1_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣጟ")),
            bstack1l1l1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧጠ"): env.get(bstack1l1l1l1_opy_ (u"ࠦࡈࡌ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡑࡅࡒࡋࠢጡ")),
            bstack1l1l1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦጢ"): env.get(bstack1l1l1l1_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦጣ"))
        }
    return {bstack1l1l1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨጤ"): None}
def get_host_info():
    return {
        bstack1l1l1l1_opy_ (u"ࠣࡪࡲࡷࡹࡴࡡ࡮ࡧࠥጥ"): platform.node(),
        bstack1l1l1l1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࠦጦ"): platform.system(),
        bstack1l1l1l1_opy_ (u"ࠥࡸࡾࡶࡥࠣጧ"): platform.machine(),
        bstack1l1l1l1_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧጨ"): platform.version(),
        bstack1l1l1l1_opy_ (u"ࠧࡧࡲࡤࡪࠥጩ"): platform.architecture()[0]
    }
def bstack1lll11llll_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111llll111_opy_():
    if bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧጪ")):
        return bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ጫ")
    return bstack1l1l1l1_opy_ (u"ࠨࡷࡱ࡯ࡳࡵࡷ࡯ࡡࡪࡶ࡮ࡪࠧጬ")
def bstack111l1lllll_opy_(driver):
    info = {
        bstack1l1l1l1_opy_ (u"ࠩࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨጭ"): driver.capabilities,
        bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠧጮ"): driver.session_id,
        bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬጯ"): driver.capabilities.get(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪጰ"), None),
        bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨጱ"): driver.capabilities.get(bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨጲ"), None),
        bstack1l1l1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪጳ"): driver.capabilities.get(bstack1l1l1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨጴ"), None),
    }
    if bstack111llll111_opy_() == bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩጵ"):
        info[bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬጶ")] = bstack1l1l1l1_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫጷ") if bstack111ll1ll_opy_() else bstack1l1l1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨጸ")
    return info
def bstack111ll1ll_opy_():
    if bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ጹ")):
        return True
    if bstack1l1111ll_opy_(os.environ.get(bstack1l1l1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩጺ"), None)):
        return True
    return False
def bstack1l1111lll_opy_(bstack111lll11l1_opy_, url, data, config):
    headers = config.get(bstack1l1l1l1_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪጻ"), None)
    proxies = bstack11l111lll_opy_(config, url)
    auth = config.get(bstack1l1l1l1_opy_ (u"ࠪࡥࡺࡺࡨࠨጼ"), None)
    response = requests.request(
            bstack111lll11l1_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack111llll1l_opy_(bstack111l1l1ll_opy_, size):
    bstack1ll111l1l_opy_ = []
    while len(bstack111l1l1ll_opy_) > size:
        bstack11l111ll_opy_ = bstack111l1l1ll_opy_[:size]
        bstack1ll111l1l_opy_.append(bstack11l111ll_opy_)
        bstack111l1l1ll_opy_ = bstack111l1l1ll_opy_[size:]
    bstack1ll111l1l_opy_.append(bstack111l1l1ll_opy_)
    return bstack1ll111l1l_opy_
def bstack1111ll1111_opy_(message, bstack111l1l11ll_opy_=False):
    os.write(1, bytes(message, bstack1l1l1l1_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪጽ")))
    os.write(1, bytes(bstack1l1l1l1_opy_ (u"ࠬࡢ࡮ࠨጾ"), bstack1l1l1l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬጿ")))
    if bstack111l1l11ll_opy_:
        with open(bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠭ࡰ࠳࠴ࡽ࠲࠭ፀ") + os.environ[bstack1l1l1l1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧፁ")] + bstack1l1l1l1_opy_ (u"ࠩ࠱ࡰࡴ࡭ࠧፂ"), bstack1l1l1l1_opy_ (u"ࠪࡥࠬፃ")) as f:
            f.write(message + bstack1l1l1l1_opy_ (u"ࠫࡡࡴࠧፄ"))
def bstack111lll1l11_opy_():
    return os.environ[bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨፅ")].lower() == bstack1l1l1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫፆ")
def bstack1l1ll1l11l_opy_(bstack1111ll1l11_opy_):
    return bstack1l1l1l1_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭ፇ").format(bstack11l111l1ll_opy_, bstack1111ll1l11_opy_)
def bstack1ll1l11lll_opy_():
    return bstack11llll11l1_opy_().replace(tzinfo=None).isoformat() + bstack1l1l1l1_opy_ (u"ࠨ࡜ࠪፈ")
def bstack111ll1llll_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1l1l1l1_opy_ (u"ࠩ࡝ࠫፉ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1l1l1l1_opy_ (u"ࠪ࡞ࠬፊ")))).total_seconds() * 1000
def bstack111l1l1111_opy_(timestamp):
    return bstack111l111l11_opy_(timestamp).isoformat() + bstack1l1l1l1_opy_ (u"ࠫ࡟࠭ፋ")
def bstack111ll111l1_opy_(bstack111l11l1ll_opy_):
    date_format = bstack1l1l1l1_opy_ (u"࡙ࠬࠫࠦ࡯ࠨࡨࠥࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨࠪፌ")
    bstack111l11l11l_opy_ = datetime.datetime.strptime(bstack111l11l1ll_opy_, date_format)
    return bstack111l11l11l_opy_.isoformat() + bstack1l1l1l1_opy_ (u"࡚࠭ࠨፍ")
def bstack111l11ll1l_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧፎ")
    else:
        return bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨፏ")
def bstack1l1111ll_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1l1l1l1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧፐ")
def bstack111ll11lll_opy_(val):
    return val.__str__().lower() == bstack1l1l1l1_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩፑ")
def bstack11ll1l11ll_opy_(bstack1111lll1l1_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack1111lll1l1_opy_ as e:
                print(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥࢁࡽࠡ࠯ࡁࠤࢀࢃ࠺ࠡࡽࢀࠦፒ").format(func.__name__, bstack1111lll1l1_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111l1111ll_opy_(bstack111l1ll111_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111l1ll111_opy_(cls, *args, **kwargs)
            except bstack1111lll1l1_opy_ as e:
                print(bstack1l1l1l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡻࡾࠢ࠰ࡂࠥࢁࡽ࠻ࠢࡾࢁࠧፓ").format(bstack111l1ll111_opy_.__name__, bstack1111lll1l1_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111l1111ll_opy_
    else:
        return decorator
def bstack111ll1ll1_opy_(bstack11ll111lll_opy_):
    if bstack1l1l1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪፔ") in bstack11ll111lll_opy_ and bstack111ll11lll_opy_(bstack11ll111lll_opy_[bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫፕ")]):
        return False
    if bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪፖ") in bstack11ll111lll_opy_ and bstack111ll11lll_opy_(bstack11ll111lll_opy_[bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫፗ")]):
        return False
    return True
def bstack1llll1111_opy_():
    try:
        from pytest_bdd import reporting
        return True
    except Exception as e:
        return False
def bstack11lll1l1_opy_(hub_url):
    if bstack1l1l1111_opy_() <= version.parse(bstack1l1l1l1_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪፘ")):
        if hub_url != bstack1l1l1l1_opy_ (u"ࠫࠬፙ"):
            return bstack1l1l1l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨፚ") + hub_url + bstack1l1l1l1_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥ፛")
        return bstack1l11l1llll_opy_
    if hub_url != bstack1l1l1l1_opy_ (u"ࠧࠨ፜"):
        return bstack1l1l1l1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ፝") + hub_url + bstack1l1l1l1_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ፞")
    return bstack111l1l1l_opy_
def bstack1111ll1l1l_opy_():
    return isinstance(os.getenv(bstack1l1l1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡐ࡚ࡍࡉࡏࠩ፟")), str)
def bstack1l111lll11_opy_(url):
    return urlparse(url).hostname
def bstack1ll1ll1l_opy_(hostname):
    for bstack1l11l1l1ll_opy_ in bstack1l11l1l11l_opy_:
        regex = re.compile(bstack1l11l1l1ll_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack1111lll111_opy_(bstack111l1l11l1_opy_, file_name, logger):
    bstack1l11lllll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠫࢃ࠭፠")), bstack111l1l11l1_opy_)
    try:
        if not os.path.exists(bstack1l11lllll1_opy_):
            os.makedirs(bstack1l11lllll1_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1l1l1l1_opy_ (u"ࠬࢄࠧ፡")), bstack111l1l11l1_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1l1l1l1_opy_ (u"࠭ࡷࠨ።")):
                pass
            with open(file_path, bstack1l1l1l1_opy_ (u"ࠢࡸ࠭ࠥ፣")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack11ll11ll1_opy_.format(str(e)))
def bstack111lll1lll_opy_(file_name, key, value, logger):
    file_path = bstack1111lll111_opy_(bstack1l1l1l1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨ፤"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1ll11llll_opy_ = json.load(open(file_path, bstack1l1l1l1_opy_ (u"ࠩࡵࡦࠬ፥")))
        else:
            bstack1ll11llll_opy_ = {}
        bstack1ll11llll_opy_[key] = value
        with open(file_path, bstack1l1l1l1_opy_ (u"ࠥࡻ࠰ࠨ፦")) as outfile:
            json.dump(bstack1ll11llll_opy_, outfile)
def bstack1lll1l111_opy_(file_name, logger):
    file_path = bstack1111lll111_opy_(bstack1l1l1l1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ፧"), file_name, logger)
    bstack1ll11llll_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1l1l1l1_opy_ (u"ࠬࡸࠧ፨")) as bstack1l11ll11l_opy_:
            bstack1ll11llll_opy_ = json.load(bstack1l11ll11l_opy_)
    return bstack1ll11llll_opy_
def bstack1ll1l1l1l1_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡦࡨࡰࡪࡺࡩ࡯ࡩࠣࡪ࡮ࡲࡥ࠻ࠢࠪ፩") + file_path + bstack1l1l1l1_opy_ (u"ࠧࠡࠩ፪") + str(e))
def bstack1l1l1111_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1l1l1l1_opy_ (u"ࠣ࠾ࡑࡓ࡙࡙ࡅࡕࡀࠥ፫")
def bstack1l11lll11_opy_(config):
    if bstack1l1l1l1_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨ፬") in config:
        del (config[bstack1l1l1l1_opy_ (u"ࠪ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩ፭")])
        return False
    if bstack1l1l1111_opy_() < version.parse(bstack1l1l1l1_opy_ (u"ࠫ࠸࠴࠴࠯࠲ࠪ፮")):
        return False
    if bstack1l1l1111_opy_() >= version.parse(bstack1l1l1l1_opy_ (u"ࠬ࠺࠮࠲࠰࠸ࠫ፯")):
        return True
    if bstack1l1l1l1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭፰") in config and config[bstack1l1l1l1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ፱")] is False:
        return False
    else:
        return True
def bstack1l1ll1l1_opy_(args_list, bstack1111ll111l_opy_):
    index = -1
    for value in bstack1111ll111l_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack1l1111ll11_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack1l1111ll11_opy_ = bstack1l1111ll11_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1l1l1l1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ፲"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1l1l1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ፳"), exception=exception)
    def bstack11ll1111l1_opy_(self):
        if self.result != bstack1l1l1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ፴"):
            return None
        if bstack1l1l1l1_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢ፵") in self.exception_type:
            return bstack1l1l1l1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨ፶")
        return bstack1l1l1l1_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢ፷")
    def bstack11l1111111_opy_(self):
        if self.result != bstack1l1l1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ፸"):
            return None
        if self.bstack1l1111ll11_opy_:
            return self.bstack1l1111ll11_opy_
        return bstack111lll11ll_opy_(self.exception)
def bstack111lll11ll_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack111l1l1l11_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l111l1ll1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1lllll1l1l_opy_(config, logger):
    try:
        import playwright
        bstack1111ll1ll1_opy_ = playwright.__file__
        bstack111ll111ll_opy_ = os.path.split(bstack1111ll1ll1_opy_)
        bstack111l11l1l1_opy_ = bstack111ll111ll_opy_[0] + bstack1l1l1l1_opy_ (u"ࠨ࠱ࡧࡶ࡮ࡼࡥࡳ࠱ࡳࡥࡨࡱࡡࡨࡧ࠲ࡰ࡮ࡨ࠯ࡤ࡮࡬࠳ࡨࡲࡩ࠯࡬ࡶࠫ፹")
        os.environ[bstack1l1l1l1_opy_ (u"ࠩࡊࡐࡔࡈࡁࡍࡡࡄࡋࡊࡔࡔࡠࡊࡗࡘࡕࡥࡐࡓࡑ࡛࡝ࠬ፺")] = bstack111l1ll1_opy_(config)
        with open(bstack111l11l1l1_opy_, bstack1l1l1l1_opy_ (u"ࠪࡶࠬ፻")) as f:
            bstack1llllll11l_opy_ = f.read()
            bstack1111l1llll_opy_ = bstack1l1l1l1_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯࠱ࡦ࡭ࡥ࡯ࡶࠪ፼")
            bstack111l1ll1ll_opy_ = bstack1llllll11l_opy_.find(bstack1111l1llll_opy_)
            if bstack111l1ll1ll_opy_ == -1:
              process = subprocess.Popen(bstack1l1l1l1_opy_ (u"ࠧࡴࡰ࡮ࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠤ፽"), shell=True, cwd=bstack111ll111ll_opy_[0])
              process.wait()
              bstack111ll1l11l_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠢࡶࡵࡨࠤࡸࡺࡲࡪࡥࡷࠦࡀ࠭፾")
              bstack111l1l1lll_opy_ = bstack1l1l1l1_opy_ (u"ࠢࠣࠤࠣࡠࠧࡻࡳࡦࠢࡶࡸࡷ࡯ࡣࡵ࡞ࠥ࠿ࠥࡩ࡯࡯ࡵࡷࠤࢀࠦࡢࡰࡱࡷࡷࡹࡸࡡࡱࠢࢀࠤࡂࠦࡲࡦࡳࡸ࡭ࡷ࡫ࠨࠨࡩ࡯ࡳࡧࡧ࡬࠮ࡣࡪࡩࡳࡺࠧࠪ࠽ࠣ࡭࡫ࠦࠨࡱࡴࡲࡧࡪࡹࡳ࠯ࡧࡱࡺ࠳ࡍࡌࡐࡄࡄࡐࡤࡇࡇࡆࡐࡗࡣࡍ࡚ࡔࡑࡡࡓࡖࡔ࡞࡙ࠪࠢࡥࡳࡴࡺࡳࡵࡴࡤࡴ࠭࠯࠻ࠡࠤࠥࠦ፿")
              bstack111l11ll11_opy_ = bstack1llllll11l_opy_.replace(bstack111ll1l11l_opy_, bstack111l1l1lll_opy_)
              with open(bstack111l11l1l1_opy_, bstack1l1l1l1_opy_ (u"ࠨࡹࠪᎀ")) as f:
                f.write(bstack111l11ll11_opy_)
    except Exception as e:
        logger.error(bstack1ll1lll1l1_opy_.format(str(e)))
def bstack11111111_opy_():
  try:
    bstack111ll1lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩᎁ"))
    bstack1111llll11_opy_ = []
    if os.path.exists(bstack111ll1lll1_opy_):
      with open(bstack111ll1lll1_opy_) as f:
        bstack1111llll11_opy_ = json.load(f)
      os.remove(bstack111ll1lll1_opy_)
    return bstack1111llll11_opy_
  except:
    pass
  return []
def bstack111l1111_opy_(bstack1llll1lll_opy_):
  try:
    bstack1111llll11_opy_ = []
    bstack111ll1lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠪࡳࡵࡺࡩ࡮ࡣ࡯ࡣ࡭ࡻࡢࡠࡷࡵࡰ࠳ࡰࡳࡰࡰࠪᎂ"))
    if os.path.exists(bstack111ll1lll1_opy_):
      with open(bstack111ll1lll1_opy_) as f:
        bstack1111llll11_opy_ = json.load(f)
    bstack1111llll11_opy_.append(bstack1llll1lll_opy_)
    with open(bstack111ll1lll1_opy_, bstack1l1l1l1_opy_ (u"ࠫࡼ࠭ᎃ")) as f:
        json.dump(bstack1111llll11_opy_, f)
  except:
    pass
def bstack11ll1l1ll_opy_(logger, bstack111l111lll_opy_ = False):
  try:
    test_name = os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨᎄ"), bstack1l1l1l1_opy_ (u"࠭ࠧᎅ"))
    if test_name == bstack1l1l1l1_opy_ (u"ࠧࠨᎆ"):
        test_name = threading.current_thread().__dict__.get(bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡃࡦࡧࡣࡹ࡫ࡳࡵࡡࡱࡥࡲ࡫ࠧᎇ"), bstack1l1l1l1_opy_ (u"ࠩࠪᎈ"))
    bstack111ll1l111_opy_ = bstack1l1l1l1_opy_ (u"ࠪ࠰ࠥ࠭ᎉ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111l111lll_opy_:
        bstack1l1l1l11l_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᎊ"), bstack1l1l1l1_opy_ (u"ࠬ࠶ࠧᎋ"))
        bstack1lll1ll11_opy_ = {bstack1l1l1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᎌ"): test_name, bstack1l1l1l1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᎍ"): bstack111ll1l111_opy_, bstack1l1l1l1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᎎ"): bstack1l1l1l11l_opy_}
        bstack111l1ll11l_opy_ = []
        bstack111ll1l1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡳࡴࡵࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶ࠱࡮ࡸࡵ࡮ࠨᎏ"))
        if os.path.exists(bstack111ll1l1ll_opy_):
            with open(bstack111ll1l1ll_opy_) as f:
                bstack111l1ll11l_opy_ = json.load(f)
        bstack111l1ll11l_opy_.append(bstack1lll1ll11_opy_)
        with open(bstack111ll1l1ll_opy_, bstack1l1l1l1_opy_ (u"ࠪࡻࠬ᎐")) as f:
            json.dump(bstack111l1ll11l_opy_, f)
    else:
        bstack1lll1ll11_opy_ = {bstack1l1l1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ᎑"): test_name, bstack1l1l1l1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ᎒"): bstack111ll1l111_opy_, bstack1l1l1l1_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬ᎓"): str(multiprocessing.current_process().name)}
        if bstack1l1l1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷࠫ᎔") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1lll1ll11_opy_)
  except Exception as e:
      logger.warn(bstack1l1l1l1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡴࡾࡺࡥࡴࡶࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡ࠻ࠢࡾࢁࠧ᎕").format(e))
def bstack1111l1l1l_opy_(error_message, test_name, index, logger):
  try:
    bstack111lllll1l_opy_ = []
    bstack1lll1ll11_opy_ = {bstack1l1l1l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ᎖"): test_name, bstack1l1l1l1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ᎗"): error_message, bstack1l1l1l1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ᎘"): index}
    bstack111l11l111_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭᎙"))
    if os.path.exists(bstack111l11l111_opy_):
        with open(bstack111l11l111_opy_) as f:
            bstack111lllll1l_opy_ = json.load(f)
    bstack111lllll1l_opy_.append(bstack1lll1ll11_opy_)
    with open(bstack111l11l111_opy_, bstack1l1l1l1_opy_ (u"࠭ࡷࠨ᎚")) as f:
        json.dump(bstack111lllll1l_opy_, f)
  except Exception as e:
    logger.warn(bstack1l1l1l1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡵࡳࡧࡵࡴࠡࡨࡸࡲࡳ࡫࡬ࠡࡦࡤࡸࡦࡀࠠࡼࡿࠥ᎛").format(e))
def bstack1ll1l1ll1l_opy_(bstack1l1111111_opy_, name, logger):
  try:
    bstack1lll1ll11_opy_ = {bstack1l1l1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭᎜"): name, bstack1l1l1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ᎝"): bstack1l1111111_opy_, bstack1l1l1l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ᎞"): str(threading.current_thread()._name)}
    return bstack1lll1ll11_opy_
  except Exception as e:
    logger.warn(bstack1l1l1l1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡢࡦࡪࡤࡺࡪࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠣ᎟").format(e))
  return
def bstack1111lllll1_opy_():
    return platform.system() == bstack1l1l1l1_opy_ (u"ࠬ࡝ࡩ࡯ࡦࡲࡻࡸ࠭Ꭰ")
def bstack11ll111l_opy_(bstack11l111111l_opy_, config, logger):
    bstack1111llllll_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11l111111l_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1l1l1l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡱࡺࡥࡳࠢࡦࡳࡳ࡬ࡩࡨࠢ࡮ࡩࡾࡹࠠࡣࡻࠣࡶࡪ࡭ࡥࡹࠢࡰࡥࡹࡩࡨ࠻ࠢࡾࢁࠧᎡ").format(e))
    return bstack1111llllll_opy_
def bstack111l1lll11_opy_(bstack111llll11l_opy_, bstack111l111111_opy_):
    bstack111lllllll_opy_ = version.parse(bstack111llll11l_opy_)
    bstack111l1l1l1l_opy_ = version.parse(bstack111l111111_opy_)
    if bstack111lllllll_opy_ > bstack111l1l1l1l_opy_:
        return 1
    elif bstack111lllllll_opy_ < bstack111l1l1l1l_opy_:
        return -1
    else:
        return 0
def bstack11llll11l1_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack111l111l11_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack1111ll11ll_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1llll1l1ll_opy_(options, framework):
    if options is None:
        return
    if getattr(options, bstack1l1l1l1_opy_ (u"ࠧࡨࡧࡷࠫᎢ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1l1l1ll1ll_opy_ = caps.get(bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᎣ"))
    bstack111l111ll1_opy_ = True
    if bstack111ll11lll_opy_(caps.get(bstack1l1l1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩ࡜࠹ࡃࠨᎤ"))) or bstack111ll11lll_opy_(caps.get(bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡥࡷ࠴ࡥࠪᎥ"))):
        bstack111l111ll1_opy_ = False
    if bstack1l11lll11_opy_({bstack1l1l1l1_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦᎦ"): bstack111l111ll1_opy_}):
        bstack1l1l1ll1ll_opy_ = bstack1l1l1ll1ll_opy_ or {}
        bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᎧ")] = bstack1111ll11ll_opy_(framework)
        bstack1l1l1ll1ll_opy_[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᎨ")] = bstack111lll1l11_opy_()
        if getattr(options, bstack1l1l1l1_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨᎩ"), None):
            options.set_capability(bstack1l1l1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᎪ"), bstack1l1l1ll1ll_opy_)
        else:
            options[bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᎫ")] = bstack1l1l1ll1ll_opy_
    else:
        if getattr(options, bstack1l1l1l1_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫᎬ"), None):
            options.set_capability(bstack1l1l1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬᎭ"), bstack1111ll11ll_opy_(framework))
            options.set_capability(bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭Ꭾ"), bstack111lll1l11_opy_())
        else:
            options[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᎯ")] = bstack1111ll11ll_opy_(framework)
            options[bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᎰ")] = bstack111lll1l11_opy_()
    return options
def bstack1111lll1ll_opy_(bstack111l1111l1_opy_, framework):
    if bstack111l1111l1_opy_ and len(bstack111l1111l1_opy_.split(bstack1l1l1l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᎱ"))) > 1:
        ws_url = bstack111l1111l1_opy_.split(bstack1l1l1l1_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᎲ"))[0]
        if bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭Ꮃ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111ll11111_opy_ = json.loads(urllib.parse.unquote(bstack111l1111l1_opy_.split(bstack1l1l1l1_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᎴ"))[1]))
            bstack111ll11111_opy_ = bstack111ll11111_opy_ or {}
            bstack111ll11111_opy_[bstack1l1l1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭Ꮅ")] = str(framework) + str(__version__)
            bstack111ll11111_opy_[bstack1l1l1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᎶ")] = bstack111lll1l11_opy_()
            bstack111l1111l1_opy_ = bstack111l1111l1_opy_.split(bstack1l1l1l1_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭Ꮇ"))[0] + bstack1l1l1l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᎸ") + urllib.parse.quote(json.dumps(bstack111ll11111_opy_))
    return bstack111l1111l1_opy_
def bstack11lll111_opy_():
    global bstack1ll1111111_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1ll1111111_opy_ = BrowserType.connect
    return bstack1ll1111111_opy_
def bstack11l1ll111_opy_(framework_name):
    global bstack111lll1ll_opy_
    bstack111lll1ll_opy_ = framework_name
    return framework_name
def bstack1l11l1111l_opy_(self, *args, **kwargs):
    global bstack1ll1111111_opy_
    try:
        global bstack111lll1ll_opy_
        if bstack1l1l1l1_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭Ꮉ") in kwargs:
            kwargs[bstack1l1l1l1_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᎺ")] = bstack1111lll1ll_opy_(
                kwargs.get(bstack1l1l1l1_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᎻ"), None),
                bstack111lll1ll_opy_
            )
    except Exception as e:
        logger.error(bstack1l1l1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡥ࡯ࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡓࡅࡍࠣࡧࡦࡶࡳ࠻ࠢࡾࢁࠧᎼ").format(str(e)))
    return bstack1ll1111111_opy_(self, *args, **kwargs)
def bstack111ll1111l_opy_(bstack111l11lll1_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack11l111lll_opy_(bstack111l11lll1_opy_, bstack1l1l1l1_opy_ (u"ࠨࠢᎽ"))
        if proxies and proxies.get(bstack1l1l1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᎾ")):
            parsed_url = urlparse(proxies.get(bstack1l1l1l1_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᎿ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡉࡱࡶࡸࠬᏀ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1l1l1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡲࡶࡹ࠭Ꮑ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1l1l1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡘࡷࡪࡸࠧᏂ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1l1l1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡦࡹࡳࠨᏃ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11111l1ll_opy_(bstack111l11lll1_opy_):
    bstack1111ll11l1_opy_ = {
        bstack11l111ll1l_opy_[bstack111l111l1l_opy_]: bstack111l11lll1_opy_[bstack111l111l1l_opy_]
        for bstack111l111l1l_opy_ in bstack111l11lll1_opy_
        if bstack111l111l1l_opy_ in bstack11l111ll1l_opy_
    }
    bstack1111ll11l1_opy_[bstack1l1l1l1_opy_ (u"ࠨࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࠨᏄ")] = bstack111ll1111l_opy_(bstack111l11lll1_opy_, bstack1l111l111_opy_.get_property(bstack1l1l1l1_opy_ (u"ࠢࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠢᏅ")))
    bstack111llll1ll_opy_ = [element.lower() for element in bstack11l11l111l_opy_]
    bstack11l11111l1_opy_(bstack1111ll11l1_opy_, bstack111llll1ll_opy_)
    return bstack1111ll11l1_opy_
def bstack11l11111l1_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1l1l1l1_opy_ (u"ࠣࠬ࠭࠮࠯ࠨᏆ")
    for value in d.values():
        if isinstance(value, dict):
            bstack11l11111l1_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack11l11111l1_opy_(item, keys)