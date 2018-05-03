# -*- coding: utf-8 -*-

import os
import sys
import urlparse,urllib,urllib2
import threading
import time
import random

import xbmc
import xbmcgui
import xbmcaddon

import windowtools
from windowtools import *
from item import Item

import plugintools
import custom_player

class PlayerWindowBackground(xbmcgui.WindowXML):

    def __init__(self, xml_name, fallback_path):
        plugintools.log("PlayerWindowBackground.__init__ xml_name="+xml_name+" fallback_path="+fallback_path)

        self.itemlist = None
        self.first_time = True
        self.current_position = 0

    def setCurrentPosition(self,position):
        self.current_position = position

    def setItemlist(self,itemlist):
        plugintools.log("PlayerWindowBackground.setItemlist")

        self.itemlist = []

        for item in itemlist:
            plugintools.log("PlayerWindowBackground.setItemlist item="+item.tostring())
            self.itemlist.append(item)

    def onInit( self ):
        plugintools.log("PlayerWindowBackground.onInit")

        if self.itemlist is None:
            self.itemlist = []

        if self.first_time:
            self.first_time = False

            import window_player
            window = window_player.PlayerWindow("player.xml",plugintools.get_runtime_path())
            window.setItemlist(self.itemlist)
            window.setCurrentPosition(self.current_position)
            window.doModal()
            del window

            self.close()

    def onAction(self, action):
        plugintools.log("PlayerLiveWindow.onAction action="+windowtools.action_to_string(action))

        if action == ACTION_PARENT_DIR or action==ACTION_PREVIOUS_MENU or action==ACTION_PREVIOUS_MENU2 or action==ACTION_STOP:
            self.close()

    def onFocus( self, control_id ):
        plugintools.log("PlayerWindowBackground.onFocus "+repr(control_id))
        pass

    def onClick( self, control_id ):
        plugintools.log("PlayerWindowBackground.onClick "+repr(control_id))
        pass

    def onControl(self, control):
        plugintools.log("PlayerWindowBackground.onClick "+repr(control))
        pass
