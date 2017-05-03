#------------------------------------------------------------
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
# Client for api.tvalacarta.info
#------------------------------------------------------------

import os
import sys
import urlparse
import plugintools
import jsontools
import config
import time

import urllib
from item import Item
from exceptions import UserException
from exceptions import InvalidAuthException

MAIN_URL = "https://api.tvalacarta.info/v2"
API_KEY = "26h4yt45Cuzr8HX"
DEFAULT_HEADERS = [ ["User-Agent",config.PLUGIN_NAME+" "+config.PLATFORM_NAME] ]

# ---------------------------------------------------------------------------------------------------------
#  Common function for API calls
# ---------------------------------------------------------------------------------------------------------

# Make a remote call using post, ensuring api key is here
def remote_call(url,parameters={},require_session=True):
    plugintools.log("tvalacarta.core.api.remote_call url="+url+", parameters="+repr(parameters))

    if not url.startswith("http"):
        url = MAIN_URL + "/" + url

    if not "api_key" in parameters:
        parameters["api_key"] = API_KEY

    # Add session token if not here
    if not "s" in parameters and require_session:
        parameters["s"] = get_session_token()

    headers = DEFAULT_HEADERS
    post = urllib.urlencode(parameters)

    response_body,response_headers = plugintools.read_body_and_headers(url,post,headers)

    return jsontools.load_json(response_body)

# Make a remote call for loading next items
def get_items(item):
    plugintools.log("tvalacarta.core.api.get_items item="+item.tostring())

    # Break the GET URL for building a POST request
    plugintools.log("item.url="+item.url)
    parameters = {}
    if "?" in item.url:
        plugintools.log("item.url.split="+repr(item.url.split("?")))
        url = item.url.split("?")[0]
        parameter_list = urlparse.parse_qsl( item.url.split("?")[1] )
        for parameter in parameter_list:
            parameters[parameter[0]] = parameter[1]

        plugintools.log("parameters="+repr(parameters))
    else:
        url = item.url

    # Make the call
    json_response = remote_call( url , parameters )

    # Treat invalid data error
    if json_response["error"] and json_response["error_code"]=="400":
        raise UserException(json_response["error_message"])

    # Treat invalid authorization error
    if json_response["error"] and json_response["error_code"]=="403":
        raise InvalidAuthException(json_response["error_message"])

    return parse_itemlist_from_response(json_response)

def remote_call_and_get_items(url,parameters={}):
    plugintools.log("tvalacarta.core.api.remote_call_and_get_items url="+url+", parameters="+repr(parameters))
    
    json_response = remote_call(url,parameters)

    # Treat invalid data error
    if json_response["error"] and json_response["error_code"]=="400":
        raise UserException(json_response["error_message"])

    # Treat invalid authorization error
    if json_response["error"] and json_response["error_code"]=="403":
        raise InvalidAuthException(json_response["error_message"])

    return parse_itemlist_from_response(json_response)

# Parse the response JSON as a list if items
def parse_itemlist_from_response(json_response):
    plugintools.log("tvalacarta.core.api.parse_itemlist_from_response")

    itemlist = []
    for entry in json_response['body']:

        plugintools.log("tvalacarta.core.api.parse_itemlist_from_response entry="+repr(entry))
        
        item = Item()

        if "item_type" in entry:
            item.item_type = entry['item_type']

        if "title" in entry:
            item.title = entry['title']

        if "url" in entry:
            item.url = entry['url']

        if "id" in entry:
            item.id = entry['id']

        if "thumbnail" in entry:
            item.thumbnail = entry['thumbnail']

        if "plot" in entry:
            item.plot = entry['plot']

        if "category" in entry:
            item.category = entry['category']

        if "fanart" in entry:
            item.fanart = entry['fanart']

        if "action" in entry:
            item.action = entry['action']

        if "view" in entry:
            item.view = entry['view']            

        if "folder" in entry:
            item.folder = entry['folder']

        if "id" in entry:
            item.id = entry['id']

        if "channel_id" in entry:
            item.channel_id = entry['channel_id']

        if "show_id" in entry:
            item.show_id = entry['show_id']

        if "episode_id" in entry:
            item.episode_id = entry['episode_id']

        if "channel_title" in entry:
            item.channel_title = entry['channel_title']

        if "show_title" in entry:
            item.show_title = entry['show_title']

        if "last_updated" in entry:
            item.last_updated = entry['last_updated']

        if "updated_date" in entry:
            item.updated_date = entry['updated_date']

        if "number_of_programs" in entry:
            item.number_of_programs = entry['number_of_programs']

        if "found_date" in entry:
            item.found_date = entry['found_date']

        if "aired_date" in entry:
            item.aired_date = entry['aired_date']

        if "episode_date" in entry:
            item.episode_date = entry['episode_date']

        if "is_favorite" in entry and entry['is_favorite']==True:
            item.is_favorite = "true"
        else:
            item.is_favorite = "false"

        if "is_hidden" in entry and entry['is_hidden']==True:
            item.is_hidden = "true"
        else:
            item.is_hidden = "false"

        if "is_favorite_show" in entry and entry['is_favorite_show']==True:
            item.is_favorite_show = "true"
        else:
            item.is_favorite_show = "false"

        if "watched" in entry and entry['watched']==True:
            item.watched = "true"
        else:
            item.watched = "false"

        if "folder" in entry:
            item.folder = entry['folder']

        if item.is_favorite == "true":
            item.title = "[COLOR yellow]" + item.title + "[/COLOR]"

        item.channel = "api_programas"

        plugintools.log("tvalacarta.core.api.parse_itemlist_from_response item="+item.tostring())

        itemlist.append( item )

    return itemlist

# ---------------------------------------------------------------------------------------------------------
#  accounts
# ---------------------------------------------------------------------------------------------------------
def get_session_token():
    plugintools.log("tvalacarta.core.api.get_session_token")

    # No tiene sesión
    if plugintools.get_setting("account_session")=="":

        # Si no tiene email y password, es un login anónimo
        if plugintools.get_setting("account_email")=="" or plugintools.get_setting("account_password")=="":

            plugintools.set_setting( "account_type_registered" , "0")

            # Obtiene el ID anónimo, o calcula uno si no lo tiene
            get_anonymous_account_or_request_new()

            # Hace el login anónimo
            result = accounts_login()

            if not result["error"]:
                plugintools.set_setting( "account_session" , result["body"]["s"] )
            else:
                # Si el login anonimo no funciona, lo borra para que se pueda volver a generar
                plugintools.set_setting( "account_anonymous_id" , "" )
                plugintools.set_setting( "account_session" , "" )

        # Si tiene email y password, es un login normal
        else:
            result = accounts_login( plugintools.get_setting("account_email") , plugintools.get_setting("account_password") )

            if not result["error"]:
                plugintools.set_setting( "account_session" , result["body"]["s"] )
                # El login ha sido bueno, borra el id anónimo si lo hubiera porque ya no es necesario
                plugintools.set_setting( "account_type_registered" , "1")
                plugintools.set_setting( "account_anonymous_id" , "" )
            else:
                plugintools.set_setting( "account_session" , "" )

    return plugintools.get_setting("account_session")

def get_anonymous_account_or_request_new():

    # Obtiene el ID anónimo, o calcula uno si no lo tiene
    if plugintools.get_setting("account_anonymous_id")=="":
        result = accounts_get_new_anonymous_account()

        if not result["error"]:
            plugintools.set_setting( "account_anonymous_id" , result["body"]["anonymous_id"] )

    return plugintools.get_setting("account_anonymous_id")

def accounts_get_new_anonymous_account():
    plugintools.log("tvalacarta.core.api.accounts_get_new_anonymous_account")

    return remote_call( "accounts/get_new_anonymous_account.php" , require_session=False )

def accounts_login( account_email="" , account_password="" ):
    plugintools.log("tvalacarta.core.api.accounts_login")

    if account_email!="" and account_password!="":
        parameters = { "u":account_email , "p":account_password }
    else:
        parameters = { "a":get_anonymous_account_or_request_new() }

    return remote_call( "accounts/login.php" , parameters , require_session=False )

def accounts_logout(session):
    plugintools.log("tvalacarta.core.api.accounts_logout")

    parameters = { "s":session }
    return remote_call( "accounts/logout.php" , parameters )

def accounts_register(email,password):
    plugintools.log("tvalacarta.core.api.accounts_register")

    parameters = { "u":email , "p":password }
    return remote_call( "accounts/register.php" , parameters , require_session=False )

def accounts_reset_password_request(email):
    plugintools.log("tvalacarta.core.api.accounts_reset_password_request")

    parameters = { "u":email }
    return remote_call( "accounts/reset_password_request.php" , parameters , require_session=False )

def accounts_reset_password_confirmation(request_id,password):
    plugintools.log("tvalacarta.core.api.accounts_reset_password_confirmation")

    parameters = { "id":request_id , "p":password }
    return remote_call( "accounts/reset_password_confirmation.php" , parameters , require_session=False )

def accounts_change_password(old_password,new_password):
    plugintools.log("tvalacarta.core.api.accounts_change_password")

    parameters = { "s":plugintools.get_setting("account_session") , "old_password":old_password , "new_password":new_password }
    return remote_call( "accounts/change_password.php" , parameters , require_session=False )

# ---------------------------------------------------------------------------------------------------------
#  navigation service calls
# ---------------------------------------------------------------------------------------------------------

def navigation_get_programs_menu(item):
    plugintools.log("tvalacarta.core.api.navigation_get_programs_menu")

    item = Item(url=MAIN_URL+"/navigation/get_programs_menu.php")

    return get_items(item)

def navigation_get_programs_menu_by_section(item,section):
    plugintools.log("tvalacarta.core.api.navigation_get_programs_menu")

    item = Item(url=MAIN_URL+"/navigation/get_programs_menu_by_section.php?section="+section)

    return get_items(item)

def other_videos_same_program(item):
    plugintools.log("tvalacarta.core.api.other_videos_same_program")

    item = Item(url=MAIN_URL+"/videos/get_other_videos_same_program.php?id="+item.id)

    return get_items(item)

def add_to_favorites(item):
    plugintools.log("tvalacarta.core.api.add_to_favorites")

    parameters = { "channel_id":item.channel_id , "show_id":item.show_id }
    return remote_call( "favorites/add.php" , parameters )

def remove_from_favorites(item):
    plugintools.log("tvalacarta.core.api.remove_from_favorites")

    parameters = { "channel_id":item.channel_id , "show_id":item.show_id }
    return remote_call( "favorites/remove.php" , parameters )

def add_to_hidden(item):
    plugintools.log("tvalacarta.core.api.add_to_hidden")

    parameters = { "channel_id":item.channel_id , "show_id":item.show_id }
    return remote_call( "programs/add_to_hidden.php" , parameters )

def remove_from_hidden(item):
    plugintools.log("tvalacarta.core.api.remove_from_hidden")

    parameters = { "channel_id":item.channel_id , "show_id":item.show_id }
    return remote_call( "programs/remove_from_hidden.php" , parameters )

def mark_as_watched(item,really_watched=True):
    plugintools.log("tvalacarta.core.api.mark_as_watched")

    if really_watched:
        really_watched_param = "1"
    else:
        really_watched_param = "0"

    parameters = { "id" : item.id , "really_watched" : really_watched_param }
    return remote_call( "videos/mark_as_watched.php" , parameters )

def mark_as_unwatched(item):
    plugintools.log("tvalacarta.core.api.mark_as_unwatched")

    parameters = { "id" : item.id }
    return remote_call( "videos/mark_as_unwatched.php" , parameters )

def get_hidden_programs(item):
    plugintools.log("tvalacarta.core.api.get_hidden_programs")

    parameters = { }
    return remote_call_and_get_items( "programs/get_hidden.php" , parameters )

def get_favorite_programs(item):
    plugintools.log("tvalacarta.core.api.get_favorite_programs")

    parameters = { "favorites" : "1" }
    return remote_call_and_get_items( "programs/get_all.php" , parameters )

def get_section_thumbnail(section):
    today = time.strftime("%Y%m%d")
    return MAIN_URL+"/programs/get_section_thumbnail.php?section="+section+"&effect=green&s="+get_session_token()+"&date="+today

def plugins_get_latest_packages():
    plugintools.log("tvalacarta.core.api.plugins.get_latest_packages")

    parameters = { "plugin" : config.PLUGIN_NAME , "platform" : config.get_platform() }
    return remote_call( "plugins/get_latest_packages.php" , parameters )

# ---------------------------------------------------------------------------------------------------------
#  video service calls
# ---------------------------------------------------------------------------------------------------------

def videos_get_media_url(item):
    plugintools.log("tvalacarta.core.api.get_media_url")

    parameters = { "id" : item.id }
    return remote_call( "videos/get_media_url.php" , parameters )
