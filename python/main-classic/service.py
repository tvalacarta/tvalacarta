# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import time

from core import scrapertools
from core import config
from core import logger
from core import suscription
from core.item import Item
from servers import servertools

import xbmc
import xbmcgui

def wait_if_xbmc_not_closing(espera):
    logger.info("tvalacarta.service_subscription.wait_if_xbmc_not_closing "+repr(espera))

    while not xbmc.abortRequested and espera > 0:

        #logger.info("tvalacarta.service_subscription xbmc.abortRequested="+repr(xbmc.abortRequested)+" espera="+repr(espera))
        # Cada segundo se comprueba si XBMC esta cerrándose, hasta que ha pasado el tiempo
        xbmc.sleep(1000)
        espera = espera - 1

    if espera==0:
        logger.info("tvalacarta.service_subscription Wait finished")

if config.get_setting("suscription_check")=="true":

    # Espera 60 segundos antes de empezar, para dar tiempo a XBMC a inicializarse
    wait_if_xbmc_not_closing(10)

    logger.info("tvalacarta.service_subscription First time launch")

    while not xbmc.abortRequested:

        logger.info("tvalacarta.service_subscription Checking for new items in subscriptions")

        current_suscriptions = suscription.get_current_suscriptions()

        for item in current_suscriptions:
            from core import downloadtools
            exec "from channels import "+item.channel+" as channel_module"
            downloadtools.download_all_episodes(item,channel_module,silent=True)

            if xbmc.abortRequested:
                break

        # Espera 8 horas (en segundos)    
        logger.info("tvalacarta.service_subscription Done, waiting for the expected lapse...")
        wait_if_xbmc_not_closing(8*60*60)

    logger.info("tvalacarta.service_subscription XBMC Abort requested")

else:

    logger.info("tvalacarta.service_subscription Suscription check disabled in config")
