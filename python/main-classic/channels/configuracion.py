# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import os
import urlparse,re
import urllib
import datetime
import time
import plugintools

from core import api
from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "configuracion"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.configuracion mainlist")

    itemlist = []
    if config.get_setting("account_type_registered")=="0":
        itemlist.append( Item(channel=CHANNELNAME, title="Iniciar sesion", action="login", folder=False) )
        itemlist.append( Item(channel=CHANNELNAME, title="Crear nueva cuenta", action="register", folder=False) )
        itemlist.append( Item(channel=CHANNELNAME, title="Olvide mi contraseña", action="reset_password", folder=False) )
    else:
        itemlist.append( Item(channel=CHANNELNAME, title="Cuenta: "+config.get_setting("account_email"), action="", folder=False) )
        itemlist.append( Item(channel=CHANNELNAME, title="Cerrar sesion", action="logout", folder=False) )
        itemlist.append( Item(channel=CHANNELNAME, title="Cambiar contraseña", action="change_password", folder=False) )

    itemlist.append( Item(channel=CHANNELNAME, title="", action="", folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Preferencias", action="settings", folder=False) )
    itemlist.append( Item(channel="api_programas", title="Configurar programas ocultos", action="get_hidden_programs", folder=True) )

    title="Descargar e instalar otras versiones"
    if config.get_setting("plugin_updates_available")=="0":
        nuevas = ""
    elif config.get_setting("plugin_updates_available") == "1":
        title = "[COLOR yellow]"+title+" (1 nueva)[/COLOR]"
    else:
        title = "[COLOR yellow]"+title+" (%s nuevas)" % str(config.get_setting("plugin_updates_available"))+"[/COLOR]"

    thumb_configuracion = "menu/settings_%s.png" % config.get_setting("plugin_updates_available")

    import channelselector
    itemlist.append(Item(channel=CHANNELNAME, title=title,
                         action="get_all_versions", folder=True,
                         thumbnail=channelselector.get_thumbnail_path(thumb_configuracion)))

    return itemlist

#------------------------------------------------------------
# Abrir ajustes de kodi
#------------------------------------------------------------
def settings(item):
    config.open_settings( )

#------------------------------------------------------------
# Gestionar la cuenta de api.tvalacarta.info
#------------------------------------------------------------
def login(item):
    logger.info("tvalacarta.channels.configuracion login")

    email = plugintools.keyboard_input( config.get_setting("account_email") ,"Introduce tu email")
    if email=="":
        return

    password = plugintools.keyboard_input("","Introduce tu contraseña",hidden=True)
    if password=="":
        return

    result = api.accounts_login( email , password)

    if not result["error"]:
        # Login con éxito, actualiza los datos y quita el id anónimo
        config.set_setting("account_type_registered","1")
        config.set_setting("account_email",email)
        config.set_setting("account_session",result["body"]["s"])
        config.set_setting("account_anonymous_id","")

        plugintools.refresh_items()
        plugintools.message("Iniciar sesión","Sesion iniciada con "+email)

    else:
        # Login sin éxito, invalida la sesión y deja el login como anónimo
        config.set_setting("account_session","")
        config.set_setting("account_type_registered","0")

        plugintools.message("Iniciar sesión","Identificacion no valida",result["error_message"])

def logout(item):
    logger.info("tvalacarta.channels.configuracion logout")

    confirmation = plugintools.message_yes_no("Cerrar sesión","¿Seguro que quieres cerrar la sesion?")

    if confirmation:
        api.accounts_logout( config.get_setting("account_session") )
        config.set_setting( "account_session" , "")
        config.set_setting( "account_type_registered" , "0")
        config.set_setting( "account_anonymous_id" , "" )

        plugintools.refresh_items()

        plugintools.message("Cerrar sesión","Sesion cerrada")
    else:
        plugintools.message("Cerrar sesión","La sesion sigue abierta")

def register(item):
    logger.info("tvalacarta.channels.configuracion register")

    email = plugintools.keyboard_input( config.get_setting("account_email") ,"Introduce tu email")
    password = plugintools.keyboard_input("","Introduce tu contraseña",hidden=True)
    if len(password)<6:
        plugintools.message("Crear nueva cuenta","La contraseña debe tener al menos 6 caracteres")
        return

    password_confirmation = plugintools.keyboard_input("","Confirma tu contraseña",hidden=True)

    if password<>password_confirmation:
        plugintools.message("Crear nueva cuenta","La contraseña y la confirmacion", "deben ser iguales")
        return

    result = api.accounts_register( email , password )

    if not result["error"]:
        config.set_setting("account_type_registered","1")
        config.set_setting("account_email",email)
        config.set_setting("account_session",result["body"]["s"])

        plugintools.refresh_items()

        plugintools.message("Crear nueva cuenta","Sesion iniciada con "+email)
    else:
        plugintools.message("Crear nueva cuenta","Error al crear la nueva cuenta", result["error_message"] )

def reset_password(item):
    logger.info("tvalacarta.channels.configuracion reset_password")

    email = plugintools.keyboard_input( config.get_setting("account_email") ,"Introduce tu email")
    if len(email.strip())==0:
        plugintools.message("Olvidé mi contraseña","No has introducido ningún email")
        return

    result = api.accounts_reset_password_request( email )

    if result["error"]:
        plugintools.message("Olvidé mi contraseña","Se ha producido un error",result["error_message"])
        return

    request_id = result["body"]["request_id"]
    
    canceled = plugintools.message("Olvidé mi contraseña","Te llegará un correo con un enlace","Haz click sobre él y luego pulsa OK para introducir tu nueva contraseña")

    if not canceled:
        password = plugintools.keyboard_input("","Introduce tu nueva contraseña",hidden=True)
        password_confirmation = plugintools.keyboard_input("","Confirma tu nueva contraseña",hidden=True)

        result = api.accounts_reset_password_confirmation(request_id , password)

        if not result["error"]:
            plugintools.message("Olvidé mi contraseña","Tu contraseña ha sido modificada")
        else:
            plugintools.message("Olvidé mi contraseña","Error al cambiar la contraseña", result["error_message"] )

    else:
        plugintools.message("Olvidé mi contraseña","El proceso se ha interrumpido","Tu contraseña no ha cambiado")

    plugintools.refresh_items()

def change_password(item):
    logger.info("tvalacarta.channels.configuracion change_password")

    old_password = plugintools.keyboard_input("","Introduce tu ANTIGUA contraseña",hidden=True)
    if len(old_password)<6:
        plugintools.message("Cambiar contraseña","La contraseña debe tener al menos 6 caracteres")
        return

    password = plugintools.keyboard_input("","Introduce tu NUEVA contraseña",hidden=True)
    if len(password)<6:
        plugintools.message("Cambiar contraseña","La contraseña debe tener al menos 6 caracteres")
        return

    password_confirmation = plugintools.keyboard_input("","Confirma tu NUEVA contraseña",hidden=True)

    if password<>password_confirmation:
        plugintools.message("Cambiar contraseña","La contraseña y la confirmacion", "deben ser iguales")
        return

    result = api.accounts_change_password(old_password,password)

    if not result["error"]:
        plugintools.message("Cambiar contraseña","Tu contraseña ha sido modificada")
    else:
        plugintools.message("Cambiar contraseña","Error al cambiar la contraseña", result["error_message"] )

    plugintools.refresh_items()

#------------------------------------------------------------
# Actualizar paquetes
#------------------------------------------------------------
def get_all_versions(item):
    logger.info()

    itemlist = []

    # Lee la versión local
    from core import versiontools

    # Descarga la lista de versiones
    from core import api
    api_response = api.plugins_get_all_packages()

    if api_response["error"]:
        plugintools.message("Error", "Se ha producido un error al descargar la lista de versiones")
        return

    for entry in api_response["body"]:

        if entry["package"] == "plugin":
            title = "tvalacarta " + entry["tag"] + " (Publicada " + entry["date"] + ")"
            local_version_number = versiontools.get_current_plugin_version()
        elif entry["package"] == "channels":
            title = "Canales (Publicada " + entry["date"] + ")"
            local_version_number = versiontools.get_current_channels_version()
        elif entry["package"] == "servers":
            title = "Servidores (Publicada "+entry["date"]+")"
            local_version_number = versiontools.get_current_servers_version()
        else:
            title = entry["package"]+" (Publicada "+entry["date"]+")"
            local_version_number = None

        title_color = ""

        if local_version_number is None:
            title = title

        elif entry["version"] == local_version_number:
            title += " ACTUAL"

        elif entry["version"] > local_version_number:
            title = "[COLOR yellow]"+title+"[/COLOR]"

        else:
            title_color = "[COLOR 0xFF666666]"+title+"[/COLOR]"

        itemlist.append(Item(channel=CHANNELNAME, title=title, url=entry["url"],
                             filename=entry["filename"], package=entry["package"],
                             version=str(entry["version"]), text_color=title_color,
                             action="download_and_install_package", folder=False))

    return itemlist


def download_and_install_package(item):
    logger.info()

    from core import updater
    from core import versiontools

    if item.package == "plugin":
        if int(item.version) < versiontools.get_current_plugin_version():
            if not plugintools.message_yes_no("Instalando versión anterior",
                                              "¿Seguro que quieres instalar una versión anterior?"):
                return
        elif int(item.version) == versiontools.get_current_plugin_version():
            if not plugintools.message_yes_no("Reinstalando versión actual",
                                              "¿Seguro que quieres reinstalar la misma versión que ya tienes?"):
                return
        elif int(item.version) > versiontools.get_current_plugin_version():
            if not plugintools.message_yes_no("Instalando nueva versión",
                                              "¿Seguro que quieres instalar esta nueva versión?"):
                return
    else:
        if not plugintools.message_yes_no("Instalando paquete", "¿Seguro que quieres instalar este paquete?"):
            return

    local_file_name = os.path.join(config.get_data_path(), item.filename)
    updater.download_and_install(item.url, local_file_name)

    if config.is_xbmc() and config.get_system_platform() != "xbox":
        import xbmc
        xbmc.executebuiltin("Container.Refresh")

