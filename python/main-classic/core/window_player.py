# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

import os
import sys
import urlparse,urllib,urllib2
import threading
import time
import random

import xbmc
import xbmcgui
import xbmcaddon

from windowtools import *
from item import Item

import plugintools
import custom_player

class PlayerWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, xml_name, fallback_path):
        plugintools.log("PlayerWindow.__init__ xml_name="+xml_name+" fallback_path="+fallback_path)

        self.custom_player = None
        self.osd_visible = True
        self.hide_osd_timer = None
        self.zap_timer = None

        self.channels = []
        self.current_position = 0

    def setCurrentPosition(self,position):
        self.current_position = position

    def setItemlist(self,itemlist):
        plugintools.log("PlayerWindow.setItemlist")

        self.channels = []

        for item in itemlist:
            plugintools.log("PlayerWindow.setItemlist item="+item.tostring())

            channel = Item( category=item.category, title=item.title, url=item.url, thumbnail=item.thumbnail, plot="", now="", next="")
            self.channels.append(channel)

    def onInit( self ):
        plugintools.log("PlayerWindow.onInit")
            
        self.show_osd()

        # Lanza el vídeo
        self.custom_player = custom_player.CustomPlayer()
        self.custom_player.set_listener(self)
        self.play_current_channel()

    def onAction(self, action):
        plugintools.log("PlayerWindow.onAction action.id="+repr(action.getId())+" action.buttonCode="+repr(action.getButtonCode()))

        # Press OK -> info
        if action == ACTION_SELECT_ITEM:
            self.toogle_osd_visible()

        elif action == ACTION_PARENT_DIR or action==ACTION_PREVIOUS_MENU or action==ACTION_PREVIOUS_MENU2:
            self.custom_player.stop()
            self.close()

        elif action == ACTION_MOVE_RIGHT:
            self.zap_to_next_channel_async()

        elif action == ACTION_MOVE_LEFT:
            self.zap_to_previous_channel_async()

    def zap_to_next_channel_async(self):
        plugintools.log("PlayerWindow.zap_to_next_channel_async")
    
        # Primero salta al nuevo canal
        self.current_position = self.current_position + 1
        if self.current_position >= len(self.channels):
            self.current_position = 0

        self.update_osd()
        self.show_osd()

        # Y finalmente hace el zapping tras un pequeño delay
        if self.zap_timer is not None and self.zap_timer.is_alive():
            self.zap_timer.cancel()

        self.zap_timer = threading.Timer(0.5,self.stop_and_play_current_channel)
        self.zap_timer.start()

    def zap_to_previous_channel_async(self):
        plugintools.log("PlayerWindow.zap_to_previous_channel_async")

        self.show_osd()

        self.custom_player.stop()
        self.current_position = self.current_position - 1
        if self.current_position < 0:
            self.current_position = len(self.channels)-1

        self.play_current_channel()

    def zap_to_next_channel_sync(self):
        plugintools.log("PlayerWindow.zap_to_next_channel_sync")
    
        self.show_osd()

        self.custom_player.stop()
        self.current_position = self.current_position + 1
        if self.current_position >= len(self.channels):
            self.current_position = 0

        self.play_current_channel()

    def zap_to_previous_channel_sync(self):
        plugintools.log("PlayerWindow.zap_to_previous_channel_sync")

        self.show_osd()

        self.custom_player.stop()
        self.current_position = self.current_position - 1
        if self.current_position < 0:
            self.current_position = len(self.channels)-1

        self.play_current_channel()

    def show_osd(self):
        plugintools.log("PlayerWindow.show_osd")

        if self.hide_osd_timer is not None and self.hide_osd_timer.is_alive():
            self.hide_osd_timer.cancel()

        self.set_osd_visible(True)
        self.hide_osd_timer = threading.Timer(5,self.hide_osd_after_delay)
        self.hide_osd_timer.start()
        
    def hide_osd_after_delay(self):
        plugintools.log("PlayerWindow.hide_osd_after_delay")

        self.set_osd_visible(False)
        self.hide_osd_timer = None

    def set_osd_visible(self, visible):
        plugintools.log("PlayerWindow.set_osd_visible visible="+str(visible))

        if self.osd_visible!=visible:
            self.getControl(101).setVisible(visible)
            self.osd_visible = visible

    def toogle_osd_visible(self):
        plugintools.log("PlayerWindow.toogle_osd_visible")

        if self.osd_visible:
            self.set_osd_visible(False)
        else:
            self.set_osd_visible(True)

    def stop_and_play_current_channel( self ):
        self.custom_player.stop()
        self.custom_player.play_stream( self.channels[self.current_position].url )
        
    def play_current_channel( self ):
        self.custom_player.play_stream( self.channels[self.current_position].url )

        self.update_osd()

    # Muestra y actualiza el OSD
    def update_osd( self ):
        self.getControl(103).setImage(self.channels[self.current_position].thumbnail)
        self.getControl(104).setText(self.channels[self.current_position].title+"\n"+self.channels[self.current_position].now+"\n"+self.channels[self.current_position].plot)
        self.getControl(105).setText("") #Luego:\n"+self.channels[self.current_position].next)

    def on_playback_stopped( self ):
        plugintools.log("PlayerWindow.on_playback_stopped currentTime="+str(self.custom_player.get_current_time())+", totalTime="+str(self.custom_player.get_total_time()))
        #self.close()

    def on_playback_ended( self ):
        plugintools.log("PlayerWindow.on_playback_ended")
        #self.close()

    def onFocus( self, control_id ):
        plugintools.log("PlayerWindow.onFocus "+repr(control_id))
        pass

    def onClick( self, control_id ):
        plugintools.log("PlayerWindow.onClick "+repr(control_id))
        pass

    def onControl(self, control):
        plugintools.log("PlayerWindow.onClick "+repr(control))
        pass
