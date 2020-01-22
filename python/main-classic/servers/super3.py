# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Super3
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re
from core import scrapertools
from core import logger
from core import jsontools

import tv3

def get_video_url(page_url, premium = False, user="", password="", video_password="", page_data=""):
    return tv3.get_video_url(page_url)
