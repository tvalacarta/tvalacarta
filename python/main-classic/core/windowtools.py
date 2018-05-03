# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
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

# -*- coding: utf-8 -*-

ACTION_MOVE_LEFT       =  1 #Dpad Left
ACTION_MOVE_RIGHT      =  2 #Dpad Right
ACTION_MOVE_UP         =  3 #Dpad Up
ACTION_MOVE_DOWN       =  4 #Dpad Down
ACTION_PAGE_UP         =  5 #Left trigger
ACTION_PAGE_DOWN       =  6 #Right trigger
ACTION_SELECT_ITEM     =  7 #'A'
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9 #'B'
ACTION_PREVIOUS_MENU   = 10 #'Back'
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13 #'Start'
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_XBUTTON         = 18 #'X'
ACTION_YBUTTON         = 34 #'Y'
ACTION_MOUSEMOVE       = 90 # Mouse has moved
ACTION_MOUSEMOVE2      = 107 # Mouse has moved
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_PREVIOUS_MENU2  = 92 #'Back'
ACTION_CONTEXT_MENU    = 117 # pops up the context menu
ACTION_CONTEXT_MENU2   = 229 # pops up the context menu (remote control "title" button)
ACTION_TOUCH_TAP = 401
ACTION_NOOP = 999

def action_to_string(action):
    try:
        value = "[id="+repr(action.getId())
    except:
        value = "[id="+repr(action)

    if action==ACTION_MOVE_LEFT:
        value = value + ", name=ACTION_MOVE_LEFT"
    if action==ACTION_MOVE_RIGHT:
        value = value + ", name=ACTION_MOVE_RIGHT"
    if action==ACTION_MOVE_UP:
        value = value + ", name=ACTION_MOVE_UP"
    if action==ACTION_MOVE_DOWN:
        value = value + ", name=ACTION_MOVE_DOWN"
    if action==ACTION_PAGE_UP:
        value = value + ", name=ACTION_PAGE_UP"
    if action==ACTION_PAGE_DOWN:
        value = value + ", name=ACTION_PAGE_DOWN"
    if action==ACTION_SELECT_ITEM:
        value = value + ", name=ACTION_SELECT_ITEM"
    if action==ACTION_HIGHLIGHT_ITEM:
        value = value + ", name=ACTION_HIGHLIGHT_ITEM"
    if action==ACTION_PARENT_DIR:
        value = value + ", name=ACTION_PARENT_DIR"
    if action==ACTION_PREVIOUS_MENU:
        value = value + ", name=ACTION_PREVIOUS_MENU"
    if action==ACTION_SHOW_INFO:
        value = value + ", name=ACTION_SHOW_INFO"
    if action==ACTION_PAUSE:
        value = value + ", name=ACTION_PAUSE"
    if action==ACTION_STOP:
        value = value + ", name=ACTION_STOP"
    if action==ACTION_NEXT_ITEM:
        value = value + ", name=ACTION_NEXT_ITEM"
    if action==ACTION_PREV_ITEM:
        value = value + ", name=ACTION_PREV_ITEM"
    if action==ACTION_XBUTTON:
        value = value + ", name=ACTION_XBUTTON"
    if action==ACTION_YBUTTON:
        value = value + ", name=ACTION_YBUTTON"
    if action==ACTION_MOUSEMOVE:
        value = value + ", name=ACTION_MOUSEMOVE"
    if action==ACTION_MOUSEMOVE2:
        value = value + ", name=ACTION_MOUSEMOVE2"
    if action==ACTION_MOUSE_LEFT_CLICK:
        value = value + ", name=ACTION_MOUSE_LEFT_CLICK"
    if action==ACTION_PREVIOUS_MENU2:
        value = value + ", name=ACTION_PREVIOUS_MENU2"
    if action==ACTION_CONTEXT_MENU:
        value = value + ", name=ACTION_CONTEXT_MENU"
    if action==ACTION_CONTEXT_MENU2:
        value = value + ", name=ACTION_CONTEXT_MENU2"
    if action==ACTION_TOUCH_TAP:
        value = value + ", name=ACTION_TOUCH_TAP"
    if action==ACTION_NOOP:
        value = value + ", name=ACTION_NOOP"

    try:
        value = value +", buttonCode="+repr(action.getButtonCode())
    except:
        pass

    value = value +"]"

    return value