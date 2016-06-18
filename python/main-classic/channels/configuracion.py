# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
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

	return itemlist

def settings(item):
    config.open_settings( )

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
