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
import sys
import logging
import tarfile
import io
import os
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l11l1111_opy_, bstack11l11l111l_opy_
import tempfile
import json
bstack11111l11ll_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠬᏲ"))
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1l1l1l1_opy_ (u"ࠫࡡࡴࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩᏳ"),
      datefmt=bstack1l1l1l1_opy_ (u"ࠬࠫࡈ࠻ࠧࡐ࠾࡙ࠪࠧᏴ"),
      stream=sys.stdout
    )
  return logger
def bstack11111l11l1_opy_():
  global bstack11111l11ll_opy_
  if os.path.exists(bstack11111l11ll_opy_):
    os.remove(bstack11111l11ll_opy_)
def bstack11l1l11ll_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def bstack11l1l1l1l_opy_(config, log_level):
  bstack11111ll11l_opy_ = log_level
  if bstack1l1l1l1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᏵ") in config and config[bstack1l1l1l1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩ᏶")] in bstack11l11l1111_opy_:
    bstack11111ll11l_opy_ = bstack11l11l1111_opy_[config[bstack1l1l1l1_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪ᏷")]]
  if config.get(bstack1l1l1l1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫᏸ"), False):
    logging.getLogger().setLevel(bstack11111ll11l_opy_)
    return bstack11111ll11l_opy_
  global bstack11111l11ll_opy_
  bstack11l1l11ll_opy_()
  bstack11111l1lll_opy_ = logging.Formatter(
    fmt=bstack1l1l1l1_opy_ (u"ࠪࡠࡳࠫࠨࡢࡵࡦࡸ࡮ࡳࡥࠪࡵࠣ࡟ࠪ࠮࡮ࡢ࡯ࡨ࠭ࡸࡣ࡛ࠦࠪ࡯ࡩࡻ࡫࡬࡯ࡣࡰࡩ࠮ࡹ࡝ࠡ࠯ࠣࠩ࠭ࡳࡥࡴࡵࡤ࡫ࡪ࠯ࡳࠨᏹ"),
    datefmt=bstack1l1l1l1_opy_ (u"ࠫࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭ᏺ")
  )
  bstack11111ll111_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack11111l11ll_opy_)
  file_handler.setFormatter(bstack11111l1lll_opy_)
  bstack11111ll111_opy_.setFormatter(bstack11111l1lll_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack11111ll111_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1l1l1l1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴ࠱ࡶࡪࡳ࡯ࡵࡧ࠱ࡶࡪࡳ࡯ࡵࡧࡢࡧࡴࡴ࡮ࡦࡥࡷ࡭ࡴࡴࠧᏻ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack11111ll111_opy_.setLevel(bstack11111ll11l_opy_)
  logging.getLogger().addHandler(bstack11111ll111_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack11111ll11l_opy_
def bstack11111ll1l1_opy_(config):
  try:
    bstack11111lll1l_opy_ = set(bstack11l11l111l_opy_)
    bstack11111llll1_opy_ = bstack1l1l1l1_opy_ (u"࠭ࠧᏼ")
    with open(bstack1l1l1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪᏽ")) as bstack11111ll1ll_opy_:
      bstack11111lll11_opy_ = bstack11111ll1ll_opy_.read()
      bstack11111llll1_opy_ = re.sub(bstack1l1l1l1_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠦ࠲࠯ࠪ࡜࡯ࠩ᏾"), bstack1l1l1l1_opy_ (u"ࠩࠪ᏿"), bstack11111lll11_opy_, flags=re.M)
      bstack11111llll1_opy_ = re.sub(
        bstack1l1l1l1_opy_ (u"ࡵࠫࡣ࠮࡜ࡴ࠭ࠬࡃ࠭࠭᐀") + bstack1l1l1l1_opy_ (u"ࠫࢁ࠭ᐁ").join(bstack11111lll1l_opy_) + bstack1l1l1l1_opy_ (u"ࠬ࠯࠮ࠫࠦࠪᐂ"),
        bstack1l1l1l1_opy_ (u"ࡸࠧ࡝࠴࠽ࠤࡠࡘࡅࡅࡃࡆࡘࡊࡊ࡝ࠨᐃ"),
        bstack11111llll1_opy_, flags=re.M | re.I
      )
    def bstack11111l1l11_opy_(dic):
      bstack11111l1ll1_opy_ = {}
      for key, value in dic.items():
        if key in bstack11111lll1l_opy_:
          bstack11111l1ll1_opy_[key] = bstack1l1l1l1_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫᐄ")
        else:
          if isinstance(value, dict):
            bstack11111l1ll1_opy_[key] = bstack11111l1l11_opy_(value)
          else:
            bstack11111l1ll1_opy_[key] = value
      return bstack11111l1ll1_opy_
    bstack11111l1ll1_opy_ = bstack11111l1l11_opy_(config)
    return {
      bstack1l1l1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫᐅ"): bstack11111llll1_opy_,
      bstack1l1l1l1_opy_ (u"ࠩࡩ࡭ࡳࡧ࡬ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠬᐆ"): json.dumps(bstack11111l1ll1_opy_)
    }
  except Exception as e:
    return {}
def bstack1ll1l1111l_opy_(config):
  global bstack11111l11ll_opy_
  try:
    if config.get(bstack1l1l1l1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬᐇ"), False):
      return
    uuid = os.getenv(bstack1l1l1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᐈ"))
    if not uuid or uuid == bstack1l1l1l1_opy_ (u"ࠬࡴࡵ࡭࡮ࠪᐉ"):
      return
    bstack11111lllll_opy_ = [bstack1l1l1l1_opy_ (u"࠭ࡲࡦࡳࡸ࡭ࡷ࡫࡭ࡦࡰࡷࡷ࠳ࡺࡸࡵࠩᐊ"), bstack1l1l1l1_opy_ (u"ࠧࡑ࡫ࡳࡪ࡮ࡲࡥࠨᐋ"), bstack1l1l1l1_opy_ (u"ࠨࡲࡼࡴࡷࡵࡪࡦࡥࡷ࠲ࡹࡵ࡭࡭ࠩᐌ"), bstack11111l11ll_opy_]
    bstack11l1l11ll_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯࡯ࡳ࡬ࡹ࠭ࠨᐍ") + uuid + bstack1l1l1l1_opy_ (u"ࠪ࠲ࡹࡧࡲ࠯ࡩࡽࠫᐎ"))
    with tarfile.open(output_file, bstack1l1l1l1_opy_ (u"ࠦࡼࡀࡧࡻࠤᐏ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack11111lllll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack11111ll1l1_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack11111l1l1l_opy_ = data.encode()
        tarinfo.size = len(bstack11111l1l1l_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack11111l1l1l_opy_))
    bstack1l1l11ll1_opy_ = MultipartEncoder(
      fields= {
        bstack1l1l1l1_opy_ (u"ࠬࡪࡡࡵࡣࠪᐐ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1l1l1l1_opy_ (u"࠭ࡲࡣࠩᐑ")), bstack1l1l1l1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡾ࠭ࡨࡼ࡬ࡴࠬᐒ")),
        bstack1l1l1l1_opy_ (u"ࠨࡥ࡯࡭ࡪࡴࡴࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᐓ"): uuid
      }
    )
    response = requests.post(
      bstack1l1l1l1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡹࡵࡲ࡯ࡢࡦ࠰ࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡣ࡭࡫ࡨࡲࡹ࠳࡬ࡰࡩࡶ࠳ࡺࡶ࡬ࡰࡣࡧࠦᐔ"),
      data=bstack1l1l11ll1_opy_,
      headers={bstack1l1l1l1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩᐕ"): bstack1l1l11ll1_opy_.content_type},
      auth=(config[bstack1l1l1l1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᐖ")], config[bstack1l1l1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᐗ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1l1l1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡻࡰ࡭ࡱࡤࡨࠥࡲ࡯ࡨࡵ࠽ࠤࠬᐘ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1l1l1l1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡦࡰࡧ࡭ࡳ࡭ࠠ࡭ࡱࡪࡷ࠿࠭ᐙ") + str(e))
  finally:
    try:
      bstack11111l11l1_opy_()
    except:
      pass