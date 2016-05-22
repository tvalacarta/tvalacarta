# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta 4
# Copyright 2016 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

class Item(object):

    def __init__(self, channel="", title="", channel_title="", show_title="", url="", page="", thumbnail="", plot="", uid="", duration="", fanart="", action="", server="directo", extra="", show="", category = "" , language = "" , subtitle="" , folder=True, context = "",totalItems = 0, overlay = None, type="", password="", fulltitle="", viewmode="list", aired_date="", size="" ):
        self.channel = channel
        self.title = title
        self.channel_title = channel_title
        self.show_title = show_title
        self.url = url
        if page=="":
            self.page = url
        else:
            self.page = page
        self.thumbnail = thumbnail
        self.plot = plot
        self.uid = uid
        self.duration = duration
        self.fanart = fanart
        self.folder = folder
        self.server = server
        self.action = action
        self.extra = extra
        self.show = show
        self.category = category
        self.childcount = 0
        self.language = language
        self.type = type
        self.context = context
        self.subtitle = subtitle
        self.totalItems = totalItems
        self.overlay = overlay
        self.password = password
        self.fulltitle = fulltitle
        self.viewmode = viewmode
        self.aired_date = aired_date
        self.size = size

        self.totalItems =0
        self.channel_id = ""
        self.date = ""
        self.aired_date = ""
        self.media_width = 0
        self.media_height = 0
        self.media_url = ""
        self.geolocked = "0"
        self.is_favorite = "false"

    def __repr__(self):
        return self.tostring()

    def tostring(self):
        return "title=["+self.title+"], url=["+self.url+"], thumbnail=["+self.thumbnail+"], action=["+self.action+"], show=["+self.show+"], category=["+self.category+"], date=["+self.date+"]"
    
    def serialize(self):
        separator = "|>|<|"
        devuelve = ""
        devuelve = devuelve + self.title + separator
        devuelve = devuelve + self.url + separator
        devuelve = devuelve + self.channel + separator
        devuelve = devuelve + self.action + separator
        devuelve = devuelve + self.server + separator
        devuelve = devuelve + self.extra + separator
        devuelve = devuelve + self.category + separator
        devuelve = devuelve + self.fulltitle + separator
        devuelve = devuelve + self.viewmode + separator
        return devuelve
    
    def deserialize(self,cadena):
        trozos=cadena.split("|>|<|")
        self.title = trozos[0]
        self.url = trozos[1]
        self.channel = trozos[2]
        self.action = trozos[3]
        self.server = trozos[4]
        self.extra = trozos[5]
        self.category = trozos[6]
        self.fulltitle = trozos[7]
        self.viewmode = trozos[8]

if __name__ == "__main__":
    item = Item(title="bla b", url="http://bla")
    cadena=item.serialize()
    print cadena
    
    item2 = Item()
    item2.deserialize(cadena)
    print item2.title,item2.url
