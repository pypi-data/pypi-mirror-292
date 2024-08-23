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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack1l1ll1l11l_opy_, bstack1l1111lll_opy_
class bstack1l11llll11_opy_:
  working_dir = os.getcwd()
  bstack111ll1ll_opy_ = False
  config = {}
  binary_path = bstack1l1l1l1_opy_ (u"ࠩࠪᑡ")
  bstack1lllll11ll1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࠫᑢ")
  bstack1l11l11l11_opy_ = False
  bstack1llllllll11_opy_ = None
  bstack1llll1lll11_opy_ = {}
  bstack1lllllllll1_opy_ = 300
  bstack1lllll1111l_opy_ = False
  logger = None
  bstack1llll1ll11l_opy_ = False
  bstack111111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠫࠬᑣ")
  bstack1lllll11l1l_opy_ = {
    bstack1l1l1l1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬᑤ") : 1,
    bstack1l1l1l1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧᑥ") : 2,
    bstack1l1l1l1_opy_ (u"ࠧࡦࡦࡪࡩࠬᑦ") : 3,
    bstack1l1l1l1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࠨᑧ") : 4
  }
  def __init__(self) -> None: pass
  def bstack1lllll1l11l_opy_(self):
    bstack1llll1llll1_opy_ = bstack1l1l1l1_opy_ (u"ࠩࠪᑨ")
    bstack111111l111_opy_ = sys.platform
    bstack1lllll1llll_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩᑩ")
    if re.match(bstack1l1l1l1_opy_ (u"ࠦࡩࡧࡲࡸ࡫ࡱࢀࡲࡧࡣࠡࡱࡶࠦᑪ"), bstack111111l111_opy_) != None:
      bstack1llll1llll1_opy_ = bstack11l1111l11_opy_ + bstack1l1l1l1_opy_ (u"ࠧ࠵ࡰࡦࡴࡦࡽ࠲ࡵࡳࡹ࠰ࡽ࡭ࡵࠨᑫ")
      self.bstack111111l1l1_opy_ = bstack1l1l1l1_opy_ (u"࠭࡭ࡢࡥࠪᑬ")
    elif re.match(bstack1l1l1l1_opy_ (u"ࠢ࡮ࡵࡺ࡭ࡳࢂ࡭ࡴࡻࡶࢀࡲ࡯࡮ࡨࡹࡿࡧࡾ࡭ࡷࡪࡰࡿࡦࡨࡩࡷࡪࡰࡿࡻ࡮ࡴࡣࡦࡾࡨࡱࡨࢂࡷࡪࡰ࠶࠶ࠧᑭ"), bstack111111l111_opy_) != None:
      bstack1llll1llll1_opy_ = bstack11l1111l11_opy_ + bstack1l1l1l1_opy_ (u"ࠣ࠱ࡳࡩࡷࡩࡹ࠮ࡹ࡬ࡲ࠳ࢀࡩࡱࠤᑮ")
      bstack1lllll1llll_opy_ = bstack1l1l1l1_opy_ (u"ࠤࡳࡩࡷࡩࡹ࠯ࡧࡻࡩࠧᑯ")
      self.bstack111111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠪࡻ࡮ࡴࠧᑰ")
    else:
      bstack1llll1llll1_opy_ = bstack11l1111l11_opy_ + bstack1l1l1l1_opy_ (u"ࠦ࠴ࡶࡥࡳࡥࡼ࠱ࡱ࡯࡮ࡶࡺ࠱ࡾ࡮ࡶࠢᑱ")
      self.bstack111111l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬࡲࡩ࡯ࡷࡻࠫᑲ")
    return bstack1llll1llll1_opy_, bstack1lllll1llll_opy_
  def bstack1llll1lllll_opy_(self):
    try:
      bstack1llllll111l_opy_ = [os.path.join(expanduser(bstack1l1l1l1_opy_ (u"ࠨࡾࠣᑳ")), bstack1l1l1l1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᑴ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack1llllll111l_opy_:
        if(self.bstack1111111111_opy_(path)):
          return path
      raise bstack1l1l1l1_opy_ (u"ࠣࡗࡱࡥࡱࡨࡥࠡࡶࡲࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠧᑵ")
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪࠦࡰࡢࡶ࡫ࠤ࡫ࡵࡲࠡࡲࡨࡶࡨࡿࠠࡥࡱࡺࡲࡱࡵࡡࡥ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦ࠭ࠡࡽࢀࠦᑶ").format(e))
  def bstack1111111111_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack1111111lll_opy_(self, bstack1llll1llll1_opy_, bstack1lllll1llll_opy_):
    try:
      bstack1llllll1l11_opy_ = self.bstack1llll1lllll_opy_()
      bstack1lllll1lll1_opy_ = os.path.join(bstack1llllll1l11_opy_, bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺ࠰ࡽ࡭ࡵ࠭ᑷ"))
      bstack1llllll1lll_opy_ = os.path.join(bstack1llllll1l11_opy_, bstack1lllll1llll_opy_)
      if os.path.exists(bstack1llllll1lll_opy_):
        self.logger.info(bstack1l1l1l1_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࢁࡽ࠭ࠢࡶ࡯࡮ࡶࡰࡪࡰࡪࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠨᑸ").format(bstack1llllll1lll_opy_))
        return bstack1llllll1lll_opy_
      if os.path.exists(bstack1lllll1lll1_opy_):
        self.logger.info(bstack1l1l1l1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡿ࡯ࡰࠡࡨࡲࡹࡳࡪࠠࡪࡰࠣࡿࢂ࠲ࠠࡶࡰࡽ࡭ࡵࡶࡩ࡯ࡩࠥᑹ").format(bstack1lllll1lll1_opy_))
        return self.bstack1lllll1l111_opy_(bstack1lllll1lll1_opy_, bstack1lllll1llll_opy_)
      self.logger.info(bstack1l1l1l1_opy_ (u"ࠨࡄࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡪࡷࡵ࡭ࠡࡽࢀࠦᑺ").format(bstack1llll1llll1_opy_))
      response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠧࡈࡇࡗࠫᑻ"), bstack1llll1llll1_opy_, {}, {})
      if response.status_code == 200:
        with open(bstack1lllll1lll1_opy_, bstack1l1l1l1_opy_ (u"ࠨࡹࡥࠫᑼ")) as file:
          file.write(response.content)
        self.logger.info(bstack1l1l1l1_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥࡧ࡮ࡥࠢࡶࡥࡻ࡫ࡤࠡࡣࡷࠤࢀࢃࠢᑽ").format(bstack1lllll1lll1_opy_))
        return self.bstack1lllll1l111_opy_(bstack1lllll1lll1_opy_, bstack1lllll1llll_opy_)
      else:
        raise(bstack1l1l1l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡶ࡫ࡩࠥ࡬ࡩ࡭ࡧ࠱ࠤࡘࡺࡡࡵࡷࡶࠤࡨࡵࡤࡦ࠼ࠣࡿࢂࠨᑾ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡱࡺࡲࡱࡵࡡࡥࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹ࠻ࠢࡾࢁࠧᑿ").format(e))
  def bstack11111111ll_opy_(self, bstack1llll1llll1_opy_, bstack1lllll1llll_opy_):
    try:
      retry = 2
      bstack1llllll1lll_opy_ = None
      bstack1lllll11lll_opy_ = False
      while retry > 0:
        bstack1llllll1lll_opy_ = self.bstack1111111lll_opy_(bstack1llll1llll1_opy_, bstack1lllll1llll_opy_)
        bstack1lllll11lll_opy_ = self.bstack111111l1ll_opy_(bstack1llll1llll1_opy_, bstack1lllll1llll_opy_, bstack1llllll1lll_opy_)
        if bstack1lllll11lll_opy_:
          break
        retry -= 1
      return bstack1llllll1lll_opy_, bstack1lllll11lll_opy_
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡩࡨࡸࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡵࡧࡴࡩࠤᒀ").format(e))
    return bstack1llllll1lll_opy_, False
  def bstack111111l1ll_opy_(self, bstack1llll1llll1_opy_, bstack1lllll1llll_opy_, bstack1llllll1lll_opy_, bstack1llllll11l1_opy_ = 0):
    if bstack1llllll11l1_opy_ > 1:
      return False
    if bstack1llllll1lll_opy_ == None or os.path.exists(bstack1llllll1lll_opy_) == False:
      self.logger.warn(bstack1l1l1l1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡶࡡࡵࡪࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩ࠲ࠠࡳࡧࡷࡶࡾ࡯࡮ࡨࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠦᒁ"))
      return False
    bstack1lllll1ll1l_opy_ = bstack1l1l1l1_opy_ (u"ࠢ࡟࠰࠭ࡄࡵ࡫ࡲࡤࡻ࡟࠳ࡨࡲࡩࠡ࡞ࡧ࠲ࡡࡪࠫ࠯࡞ࡧ࠯ࠧᒂ")
    command = bstack1l1l1l1_opy_ (u"ࠨࡽࢀࠤ࠲࠳ࡶࡦࡴࡶ࡭ࡴࡴࠧᒃ").format(bstack1llllll1lll_opy_)
    bstack1lllllll1ll_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack1lllll1ll1l_opy_, bstack1lllllll1ll_opy_) != None:
      return True
    else:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡦ࡬ࡪࡩ࡫ࠡࡨࡤ࡭ࡱ࡫ࡤࠣᒄ"))
      return False
  def bstack1lllll1l111_opy_(self, bstack1lllll1lll1_opy_, bstack1lllll1llll_opy_):
    try:
      working_dir = os.path.dirname(bstack1lllll1lll1_opy_)
      shutil.unpack_archive(bstack1lllll1lll1_opy_, working_dir)
      bstack1llllll1lll_opy_ = os.path.join(working_dir, bstack1lllll1llll_opy_)
      os.chmod(bstack1llllll1lll_opy_, 0o755)
      return bstack1llllll1lll_opy_
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡵ࡯ࡼ࡬ࡴࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠦᒅ"))
  def bstack1111111l1l_opy_(self):
    try:
      percy = str(self.config.get(bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᒆ"), bstack1l1l1l1_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦᒇ"))).lower()
      if percy != bstack1l1l1l1_opy_ (u"ࠨࡴࡳࡷࡨࠦᒈ"):
        return False
      self.bstack1l11l11l11_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡨࡪࡺࡥࡤࡶࠣࡴࡪࡸࡣࡺ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᒉ").format(e))
  def bstack1lllllll111_opy_(self):
    try:
      bstack1lllllll111_opy_ = str(self.config.get(bstack1l1l1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫᒊ"), bstack1l1l1l1_opy_ (u"ࠤࡤࡹࡹࡵࠢᒋ"))).lower()
      return bstack1lllllll111_opy_
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡦࡶࡨࡧࡹࠦࡰࡦࡴࡦࡽࠥࡩࡡࡱࡶࡸࡶࡪࠦ࡭ࡰࡦࡨ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦᒌ").format(e))
  def init(self, bstack111ll1ll_opy_, config, logger):
    self.bstack111ll1ll_opy_ = bstack111ll1ll_opy_
    self.config = config
    self.logger = logger
    if not self.bstack1111111l1l_opy_():
      return
    self.bstack1llll1lll11_opy_ = config.get(bstack1l1l1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᒍ"), {})
    self.bstack1lllll1l1ll_opy_ = config.get(bstack1l1l1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨᒎ"), bstack1l1l1l1_opy_ (u"ࠨࡡࡶࡶࡲࠦᒏ"))
    try:
      bstack1llll1llll1_opy_, bstack1lllll1llll_opy_ = self.bstack1lllll1l11l_opy_()
      bstack1llllll1lll_opy_, bstack1lllll11lll_opy_ = self.bstack11111111ll_opy_(bstack1llll1llll1_opy_, bstack1lllll1llll_opy_)
      if bstack1lllll11lll_opy_:
        self.binary_path = bstack1llllll1lll_opy_
        thread = Thread(target=self.bstack1lllll111ll_opy_)
        thread.start()
      else:
        self.bstack1llll1ll11l_opy_ = True
        self.logger.error(bstack1l1l1l1_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡲࡨࡶࡨࡿࠠࡱࡣࡷ࡬ࠥ࡬࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾ࠮࡙ࠣࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡖࡥࡳࡥࡼࠦᒐ").format(bstack1llllll1lll_opy_))
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᒑ").format(e))
  def bstack1llll1ll1ll_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack1l1l1l1_opy_ (u"ࠩ࡯ࡳ࡬࠭ᒒ"), bstack1l1l1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺ࠰࡯ࡳ࡬࠭ᒓ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack1l1l1l1_opy_ (u"ࠦࡕࡻࡳࡩ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡱࡵࡧࡴࠢࡤࡸࠥࢁࡽࠣᒔ").format(logfile))
      self.bstack1lllll11ll1_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡨࡸࠥࡶࡥࡳࡥࡼࠤࡱࡵࡧࠡࡲࡤࡸ࡭࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨᒕ").format(e))
  def bstack1lllll111ll_opy_(self):
    bstack1llll1ll1l1_opy_ = self.bstack1llllll1ll1_opy_()
    if bstack1llll1ll1l1_opy_ == None:
      self.bstack1llll1ll11l_opy_ = True
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡺ࡯࡬ࡧࡱࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠬࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺࠤᒖ"))
      return False
    command_args = [bstack1l1l1l1_opy_ (u"ࠢࡢࡲࡳ࠾ࡪࡾࡥࡤ࠼ࡶࡸࡦࡸࡴࠣᒗ") if self.bstack111ll1ll_opy_ else bstack1l1l1l1_opy_ (u"ࠨࡧࡻࡩࡨࡀࡳࡵࡣࡵࡸࠬᒘ")]
    bstack111111ll11_opy_ = self.bstack1llllllll1l_opy_()
    if bstack111111ll11_opy_ != None:
      command_args.append(bstack1l1l1l1_opy_ (u"ࠤ࠰ࡧࠥࢁࡽࠣᒙ").format(bstack111111ll11_opy_))
    env = os.environ.copy()
    env[bstack1l1l1l1_opy_ (u"ࠥࡔࡊࡘࡃ࡚ࡡࡗࡓࡐࡋࡎࠣᒚ")] = bstack1llll1ll1l1_opy_
    env[bstack1l1l1l1_opy_ (u"࡙ࠦࡎ࡟ࡃࡗࡌࡐࡉࡥࡕࡖࡋࡇࠦᒛ")] = os.environ.get(bstack1l1l1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᒜ"), bstack1l1l1l1_opy_ (u"࠭ࠧᒝ"))
    bstack1llllll11ll_opy_ = [self.binary_path]
    self.bstack1llll1ll1ll_opy_()
    self.bstack1llllllll11_opy_ = self.bstack11111111l1_opy_(bstack1llllll11ll_opy_ + command_args, env)
    self.logger.debug(bstack1l1l1l1_opy_ (u"ࠢࡔࡶࡤࡶࡹ࡯࡮ࡨࠢࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠣᒞ"))
    bstack1llllll11l1_opy_ = 0
    while self.bstack1llllllll11_opy_.poll() == None:
      bstack111111111l_opy_ = self.bstack1111111ll1_opy_()
      if bstack111111111l_opy_:
        self.logger.debug(bstack1l1l1l1_opy_ (u"ࠣࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠦᒟ"))
        self.bstack1lllll1111l_opy_ = True
        return True
      bstack1llllll11l1_opy_ += 1
      self.logger.debug(bstack1l1l1l1_opy_ (u"ࠤࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠡࡔࡨࡸࡷࡿࠠ࠮ࠢࡾࢁࠧᒠ").format(bstack1llllll11l1_opy_))
      time.sleep(2)
    self.logger.error(bstack1l1l1l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡎࡥࡢ࡮ࡷ࡬ࠥࡉࡨࡦࡥ࡮ࠤࡋࡧࡩ࡭ࡧࡧࠤࡦ࡬ࡴࡦࡴࠣࡿࢂࠦࡡࡵࡶࡨࡱࡵࡺࡳࠣᒡ").format(bstack1llllll11l1_opy_))
    self.bstack1llll1ll11l_opy_ = True
    return False
  def bstack1111111ll1_opy_(self, bstack1llllll11l1_opy_ = 0):
    try:
      if bstack1llllll11l1_opy_ > 10:
        return False
      bstack1lllll11l11_opy_ = os.environ.get(bstack1l1l1l1_opy_ (u"ࠫࡕࡋࡒࡄ࡛ࡢࡗࡊࡘࡖࡆࡔࡢࡅࡉࡊࡒࡆࡕࡖࠫᒢ"), bstack1l1l1l1_opy_ (u"ࠬ࡮ࡴࡵࡲ࠽࠳࠴ࡲ࡯ࡤࡣ࡯࡬ࡴࡹࡴ࠻࠷࠶࠷࠽࠭ᒣ"))
      bstack1lllll11111_opy_ = bstack1lllll11l11_opy_ + bstack11l111l111_opy_
      response = requests.get(bstack1lllll11111_opy_)
      return True if response.json() else False
    except:
      return False
  def bstack1llllll1ll1_opy_(self):
    bstack1llll1lll1l_opy_ = bstack1l1l1l1_opy_ (u"࠭ࡡࡱࡲࠪᒤ") if self.bstack111ll1ll_opy_ else bstack1l1l1l1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩᒥ")
    bstack1111ll1l11_opy_ = bstack1l1l1l1_opy_ (u"ࠣࡣࡳ࡭࠴ࡧࡰࡱࡡࡳࡩࡷࡩࡹ࠰ࡩࡨࡸࡤࡶࡲࡰ࡬ࡨࡧࡹࡥࡴࡰ࡭ࡨࡲࡄࡴࡡ࡮ࡧࡀࡿࢂࠬࡴࡺࡲࡨࡁࢀࢃࠢᒦ").format(self.config[bstack1l1l1l1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᒧ")], bstack1llll1lll1l_opy_)
    uri = bstack1l1ll1l11l_opy_(bstack1111ll1l11_opy_)
    try:
      response = bstack1l1111lll_opy_(bstack1l1l1l1_opy_ (u"ࠪࡋࡊ࡚ࠧᒨ"), uri, {}, {bstack1l1l1l1_opy_ (u"ࠫࡦࡻࡴࡩࠩᒩ"): (self.config[bstack1l1l1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᒪ")], self.config[bstack1l1l1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᒫ")])})
      if response.status_code == 200:
        bstack1llllll1111_opy_ = response.json()
        if bstack1l1l1l1_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨᒬ") in bstack1llllll1111_opy_:
          return bstack1llllll1111_opy_[bstack1l1l1l1_opy_ (u"ࠣࡶࡲ࡯ࡪࡴࠢᒭ")]
        else:
          raise bstack1l1l1l1_opy_ (u"ࠩࡗࡳࡰ࡫࡮ࠡࡐࡲࡸࠥࡌ࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾࠩᒮ").format(bstack1llllll1111_opy_)
      else:
        raise bstack1l1l1l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡶࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡳࡵࡣࡷࡹࡸࠦ࠭ࠡࡽࢀ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡃࡱࡧࡽࠥ࠳ࠠࡼࡿࠥᒯ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡵࡸ࡯࡫ࡧࡦࡸࠧᒰ").format(e))
  def bstack1llllllll1l_opy_(self):
    bstack1lllll111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1l1l1_opy_ (u"ࠧࡶࡥࡳࡥࡼࡇࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠣᒱ"))
    try:
      if bstack1l1l1l1_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᒲ") not in self.bstack1llll1lll11_opy_:
        self.bstack1llll1lll11_opy_[bstack1l1l1l1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᒳ")] = 2
      with open(bstack1lllll111l1_opy_, bstack1l1l1l1_opy_ (u"ࠨࡹࠪᒴ")) as fp:
        json.dump(self.bstack1llll1lll11_opy_, fp)
      return bstack1lllll111l1_opy_
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡩࡲࡦࡣࡷࡩࠥࡶࡥࡳࡥࡼࠤࡨࡵ࡮ࡧ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᒵ").format(e))
  def bstack11111111l1_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack111111l1l1_opy_ == bstack1l1l1l1_opy_ (u"ࠪࡻ࡮ࡴࠧᒶ"):
        bstack1lllllll1l1_opy_ = [bstack1l1l1l1_opy_ (u"ࠫࡨࡳࡤ࠯ࡧࡻࡩࠬᒷ"), bstack1l1l1l1_opy_ (u"ࠬ࠵ࡣࠨᒸ")]
        cmd = bstack1lllllll1l1_opy_ + cmd
      cmd = bstack1l1l1l1_opy_ (u"࠭ࠠࠨᒹ").join(cmd)
      self.logger.debug(bstack1l1l1l1_opy_ (u"ࠢࡓࡷࡱࡲ࡮ࡴࡧࠡࡽࢀࠦᒺ").format(cmd))
      with open(self.bstack1lllll11ll1_opy_, bstack1l1l1l1_opy_ (u"ࠣࡣࠥᒻ")) as bstack111111l11l_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack111111l11l_opy_, text=True, stderr=bstack111111l11l_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack1llll1ll11l_opy_ = True
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠣࡻ࡮ࡺࡨࠡࡥࡰࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦᒼ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack1lllll1111l_opy_:
        self.logger.info(bstack1l1l1l1_opy_ (u"ࠥࡗࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡖࡥࡳࡥࡼࠦᒽ"))
        cmd = [self.binary_path, bstack1l1l1l1_opy_ (u"ࠦࡪࡾࡥࡤ࠼ࡶࡸࡴࡶࠢᒾ")]
        self.bstack11111111l1_opy_(cmd)
        self.bstack1lllll1111l_opy_ = False
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡳࡵࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥࡩ࡯࡮࡯ࡤࡲࡩࠦ࠭ࠡࡽࢀ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧᒿ").format(cmd, e))
  def bstack1lll1l1ll1_opy_(self):
    if not self.bstack1l11l11l11_opy_:
      return
    try:
      bstack1lllll1ll11_opy_ = 0
      while not self.bstack1lllll1111l_opy_ and bstack1lllll1ll11_opy_ < self.bstack1lllllllll1_opy_:
        if self.bstack1llll1ll11l_opy_:
          self.logger.info(bstack1l1l1l1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡹࡥࡵࡷࡳࠤ࡫ࡧࡩ࡭ࡧࡧࠦᓀ"))
          return
        time.sleep(1)
        bstack1lllll1ll11_opy_ += 1
      os.environ[bstack1l1l1l1_opy_ (u"ࠧࡑࡇࡕࡇ࡞ࡥࡂࡆࡕࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒ࠭ᓁ")] = str(self.bstack1111111l11_opy_())
      self.logger.info(bstack1l1l1l1_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡴࡧࡷࡹࡵࠦࡣࡰ࡯ࡳࡰࡪࡺࡥࡥࠤᓂ"))
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡥࡵࡷࡳࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥᓃ").format(e))
  def bstack1111111l11_opy_(self):
    if self.bstack111ll1ll_opy_:
      return
    try:
      bstack1lllllll11l_opy_ = [platform[bstack1l1l1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨᓄ")].lower() for platform in self.config.get(bstack1l1l1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᓅ"), [])]
      bstack1llllll1l1l_opy_ = sys.maxsize
      bstack1lllll1l1l1_opy_ = bstack1l1l1l1_opy_ (u"ࠬ࠭ᓆ")
      for browser in bstack1lllllll11l_opy_:
        if browser in self.bstack1lllll11l1l_opy_:
          bstack1llllllllll_opy_ = self.bstack1lllll11l1l_opy_[browser]
        if bstack1llllllllll_opy_ < bstack1llllll1l1l_opy_:
          bstack1llllll1l1l_opy_ = bstack1llllllllll_opy_
          bstack1lllll1l1l1_opy_ = browser
      return bstack1lllll1l1l1_opy_
    except Exception as e:
      self.logger.error(bstack1l1l1l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡣࡧࡶࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢᓇ").format(e))