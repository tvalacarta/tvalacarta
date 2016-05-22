#------------------------------------------------------------
# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Client for api.tvalacarta.info
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

import os
import sys
import urlparse
import plugintools
import jsontools
import config

import urllib
from item import Item

MAIN_URL = "https://api.tvalacarta.info"
API_KEY = "nzp4SYUe9McbS4V"

DEFAULT_HEADERS = [ ["User-Agent",config.PLUGIN_NAME+" "+config.PLATFORM_NAME] ]

# ---------------------------------------------------------------------------------------------------------
#  responses
# ---------------------------------------------------------------------------------------------------------

def parse_itemlist_from_response(json_response, viewmode="", channel="", context="", title_field="title", folder=True):
    plugintools.log("tvalacarta.api.parse_itemlist_from_response context="+context)

    itemlist = []
    if not json_response['error']:
        for entry in json_response['body']:

            plugintools.log("entry="+repr(entry))
            
            item = Item(title = entry[title_field])

            # TODO: Adaptarlo a clase item
            if 'plot' in entry:
                item.plot = entry['plot']

            if 'thumbnail' in entry and entry['thumbnail'] is not None and entry['thumbnail']<>"":
                item.thumbnail = entry['thumbnail']

            if 'fanart' in entry and entry['fanart'] is not None and entry['fanart']<>"":
                item.fanart = entry['fanart']
            else:
                item.fanart = item.thumbnail

            if 'action' in entry:
                item.action = entry['action']
            else:
                item.action = "play"

            if 'url' in entry:
                item.url = entry['url']
            elif 'id' in entry:
                item.url = entry['id']
            else:
                item.url = entry['title']

            item.folder = folder
            item.viewmode = viewmode
            item.channel = channel

            if 'channel_name' in entry:
                item.category = entry['channel_name']

            if 'channel_title' in entry:
                item.channel_title = entry['channel_title']

            if 'show_title' in entry:
                item.show_title = entry['show_title']

            if 'channel_id' in entry:
                item.extra = entry['channel_id']
            else:
                item.extra = "sinchannel"

            if 'updated_date' in entry:
                item.date = entry['updated_date']
            elif 'episode_date' in entry:
                item.date = entry['episode_date']
            else:
                item.date = "2016"

            item.context = context

            if 'id' in entry:
                item.id = str(entry['id'])
                item.uid = str(entry['id'])
            else:
                item.id = ""
                item.uid = ""

            item.is_favorite = "false"
            if 'is_favorite' in entry and entry['is_favorite']=="1":
                item.is_favorite = "true"

            if item.is_favorite == "true":
                item.title = "[COLOR yellow]" + item.title + "[/COLOR]"

            plugintools.log("item="+repr(item))

            itemlist.append( item )

    return itemlist

def get_itemlist(service_url,parameters,channel="",viewmode="",folder=True):
    plugintools.log("tvalacarta.api.get_itemlist service_url="+service_url+", parameters="+repr(parameters))

    json_response = get_response(service_url,parameters)

    itemlist = parse_itemlist_from_response(json_response,viewmode=viewmode,channel=channel,folder=folder)

    return itemlist

def get_response(service_url,parameters):
    plugintools.log("tvalacarta.api.get_response service_url="+service_url+", parameters="+repr(parameters))

    # Service call
    service_parameters = urllib.urlencode(parameters)
    plugintools.log("tvalacarta.api.get_response parameters="+service_parameters)

    try:
        body, response_headers = read( service_url , service_parameters )
    except:
        import traceback
        plugintools.log("tvalacarta.api.get_response "+traceback.format_exc())

    json_response = plugintools.load_json(body)

    if json_response["error"] and json_response["error_code"]=="403":
        config.set_setting("account_session","")

    return json_response

def read( url="" , post="" ):
    plugintools.log("tvalacarta.api.read url="+url+", post="+repr(post))

    headers = DEFAULT_HEADERS

    return plugintools.read_body_and_headers(url,post,headers)

# ---------------------------------------------------------------------------------------------------------
#  common service calls
# ---------------------------------------------------------------------------------------------------------

def get_itemlist_from_item(item, viewmode="", channel="", context="", title_field="title", folder=True):
    plugintools.log("tvalacarta.api.get_itemlist_from_item item="+repr(item)+", context="+context)

    body , response_headers = read( item.url )
    json_response = plugintools.load_json(body)

    if json_response["error"] and json_response["error_code"]=="403":
        config.set_setting("account_session","")

    return parse_itemlist_from_response(json_response,folder=folder,viewmode=viewmode,channel=channel,context=context,title_field=title_field)

# ---------------------------------------------------------------------------------------------------------
#  accounts service calls
# ---------------------------------------------------------------------------------------------------------
def get_session_token():
    plugintools.log("tvalacarta.api.get_session_token")

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
    plugintools.log("tvalacarta.api.accounts_get_new_anonymous_account")

    url = MAIN_URL+"/accounts/get_new_anonymous_account.php"
    parameters = { "api_key":API_KEY }
    post = urllib.urlencode(parameters)
    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_login( account_email="" , account_password="" ):
    plugintools.log("tvalacarta.api.accounts_login")

    url = MAIN_URL+"/accounts/login.php"

    if account_email!="" and account_password!="":
        parameters = { "u":account_email , "p":account_password ,"api_key":API_KEY}
    else:
        parameters = { "a":get_anonymous_account_or_request_new() ,"api_key":API_KEY}

    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_logout(session):
    plugintools.log("tvalacarta.api.accounts_logout")

    url = MAIN_URL+"/accounts/logout.php"
    parameters = { "s":session ,"api_key":API_KEY}
    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_register(email,password):
    plugintools.log("tvalacarta.api.accounts_register")

    url = MAIN_URL+"/accounts/register.php"
    parameters = { "u":email , "p":password ,"api_key":API_KEY}
    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_reset_password_request(email):
    plugintools.log("tvalacarta.api.accounts_reset_password_request")

    url = MAIN_URL+"/accounts/reset_password_request.php"
    parameters = { "u":email ,"api_key":API_KEY}
    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_reset_password_confirmation(request_id,password):
    plugintools.log("tvalacarta.api.accounts_reset_password_confirmation")

    url = MAIN_URL+"/accounts/reset_password_confirmation.php"
    parameters = { "id":request_id , "p":password ,"api_key":API_KEY}
    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

def accounts_change_password(old_password,new_password):
    plugintools.log("tvalacarta.api.accounts_change_password")

    url = MAIN_URL+"/accounts/change_password.php"
    parameters = { "s":plugintools.get_setting("account_session") , "old_password":old_password , "new_password":new_password ,"api_key":API_KEY}
    post = urllib.urlencode(parameters)

    body, response_headers = read( url , post )

    json_object = plugintools.load_json(body)

    return json_object

# ---------------------------------------------------------------------------------------------------------
#  navigation service calls
# ---------------------------------------------------------------------------------------------------------

def navigation_get_updated_menu(item,viewmode="",channel=""):
    plugintools.log("tvalacarta.api.navigation_get_updated_menu")

    service_url = MAIN_URL+"/navigation/get_updated_menu.php"
    service_parameters = {"s":get_session_token(),"api_key":API_KEY}

    return get_itemlist(service_url,service_parameters,viewmode=viewmode,channel=channel)

def navigation_get_programs_menu(item,viewmode="",channel=""):
    plugintools.log("tvalacarta.api.navigation_get_programs_menu")

    service_url = MAIN_URL+"/navigation/get_programs_menu.php"
    service_parameters = {"s":get_session_token(),"api_key":API_KEY}

    return get_itemlist(service_url,service_parameters,viewmode=viewmode,channel=channel)

def get_favorite_programs(item,viewmode="", channel="", context=""):
    plugintools.log("tvalacarta.api.get_favorite_programs")

    service_url = MAIN_URL+"/programs/get_all.php"
    service_parameters = {"favorites":"1","s":get_session_token(),"api_key":API_KEY}

    return get_itemlist(service_url,service_parameters,viewmode=viewmode,channel=channel)


def add_to_favorites(id):
    plugintools.log("tvalacarta.api.add_to_favorites")

    service_url = MAIN_URL+"/favorites/add.php"
    service_parameters = {"id_program":id,"s":get_session_token(),"api_key":API_KEY}

    get_itemlist(service_url,service_parameters)

def remove_from_favorites(id):
    plugintools.log("tvalacarta.api.remove_from_favorites")

    service_url = MAIN_URL+"/favorites/remove.php"
    service_parameters = {"id_program":id,"s":get_session_token(),"api_key":API_KEY}

    get_itemlist(service_url,service_parameters)

def add_to_hidden(id):
    plugintools.log("tvalacarta.api.add_to_hidden")

    service_url = MAIN_URL+"/programs/add_to_hidden.php"
    service_parameters = {"id":id,"s":get_session_token(),"api_key":API_KEY}

    get_itemlist(service_url,service_parameters)

def remove_from_hidden(id):
    plugintools.log("tvalacarta.api.remove_from_hidden")

    service_url = MAIN_URL+"/programs/remove_from_hidden.php"
    service_parameters = {"id":id,"s":get_session_token(),"api_key":API_KEY}

    get_itemlist(service_url,service_parameters)

# ---------------------------------------------------------------------------------------------------------
#  video service calls
# ---------------------------------------------------------------------------------------------------------

def videos_get_media_url(id):
    plugintools.log("tvalacarta.api.get_media_url")

    service_url = MAIN_URL+"/videos/get_media_url.php"
    service_parameters = {"id":id,"s":get_session_token(),"api_key":API_KEY}

    return get_response(service_url,service_parameters)
