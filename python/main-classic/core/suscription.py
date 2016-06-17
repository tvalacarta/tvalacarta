# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Suscription management
#------------------------------------------------------------
import urllib
import os
import sys
import config
import logger
import scrapertools
from item import Item

SUSCRIPTIONS_FILE = os.path.join( config.get_data_path() , "suscriptions.xml" )

# ------------------------------------------------------------------------------------------
# Public functions
# ------------------------------------------------------------------------------------------

# Read all the suscriptions
def get_current_suscriptions():
    logger.info("suscription.get_current_suscriptions")

    return _read_suscription_file()

# Append a new suscription to file
def append_suscription(item):
    logger.info("suscription.append_suscription item="+item.tostring())

    # Read suscriptions from file
    current_suscriptions = _read_suscription_file()

    # If not suscribed yet, appends the new suscription to file
    if not already_suscribed(item):
        current_suscriptions.append(item)
        _write_suscription_file(current_suscriptions)

# Remove suscription from file
def remove_suscription(item):
    logger.info("suscription.remove_suscription item="+item.tostring())

    current_suscriptions = _read_suscription_file()
    new_suscriptions = []

    for suscription in current_suscriptions:

        if item.url!=suscription.url:
            new_suscriptions.append(suscription)

    _write_suscription_file(new_suscriptions)

# Checks if a suscription is already on file
def already_suscribed(item):
    logger.info("suscription.already_suscribed item="+item.tostring())

    current_suscriptions = _read_suscription_file()

    # Check if suscription already on file
    existe = False
    for suscription_item in current_suscriptions:
        logger.info("suscription.already_suscribed suscription_item="+suscription_item.tostring())

        if suscription_item.url == item.url:
            existe = True
            break

    logger.info("suscription.already_suscribed -> "+repr(existe))

    return existe

# ------------------------------------------------------------------------------------------
# Private functions
# ------------------------------------------------------------------------------------------

# Read suscriptions from file
def _read_suscription_file():
    logger.info("suscription._read_suscription_file")

    # Read file
    if os.path.exists(SUSCRIPTIONS_FILE):
        f = open(SUSCRIPTIONS_FILE,"r")
        data = f.read()
        f.close()
    else:
        data = ""

    # Parse suscriptions
    suscriptions = []

    matches = scrapertools.find_multiple_matches(data,"<suscription>(.*?)</suscription>")
    for match in matches:
        channel = scrapertools.find_single_match(match,"<channel>([^<]+)</channel>")
        url = scrapertools.find_single_match(match,"<url>([^<]+)</url>")
        extra = scrapertools.find_single_match(match,"<extra>([^<]+)</extra>")
        action = scrapertools.find_single_match(match,"<action>([^<]+)</action>")
        show_name = scrapertools.find_single_match(match,"<show_name>([^<]+)</show_name>")
        thumbnail = scrapertools.find_single_match(match,"<thumbnail>([^<]+)</thumbnail>")

        suscriptions.append( Item( channel=channel, url=url, action=action, title=show_name, show=show_name, thumbnail=thumbnail ) )

    return suscriptions

# Write suscriptions to file
def _write_suscription_file(itemlist):
    logger.info("suscription._write_suscription_file")

    f = open(SUSCRIPTIONS_FILE,"w")
    f.write("<?xml version='1.0' encoding='utf-8'?>\n")
    f.write("<suscriptions>\n")

    for item in itemlist:
        logger.info("suscription._write_suscription_file item="+item.tostring())
        f.write("<suscription>\n")
        f.write("  <channel>"+item.channel+"</channel>\n")
        f.write("  <action>"+item.action+"</action>\n")
        f.write("  <url>"+item.url+"</url>\n")
        f.write("  <extra>"+item.extra+"</extra>\n")

        # API saves program name in "item.show_title"
        if item.show_title<>"":
            f.write("  <show_name>"+item.show_title+"</show_name>\n")
        # Channels save program name in "item.show"
        elif item.show<>"":
            f.write("  <show_name>"+item.show+"</show_name>\n")
        # Rest of cases
        else:
            f.write("  <show_name>"+item.title+"</show_name>\n")

        f.write("  <thumbnail>"+item.thumbnail+"</thumbnail>\n")
        f.write("</suscription>\n")

    f.write("</suscriptions>\n")
