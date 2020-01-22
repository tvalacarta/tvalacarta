# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
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
# ------------------------------------------------------------

import os
import time

import config
import logger
import scrapertools
import versiontools


# Método antiguo, muestra un popup con la versión
def checkforupdates():
    logger.info()

    # Valores por defecto
    numero_version_publicada = 0
    tag_version_publicada = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()
    for latest_package in latest_packages["body"]:
        if latest_package["package"]=="plugin":
            numero_version_publicada = latest_package["version"]
            tag_version_publicada = latest_package["tag"]
            break

    logger.info("version remota="+str(numero_version_publicada))

    # Lee la versión local
    numero_version_local = versiontools.get_current_plugin_version()
    logger.info("version local="+str(numero_version_local))

    hayqueactualizar = numero_version_publicada > numero_version_local
    logger.info("-> hayqueactualizar="+repr(hayqueactualizar))

    # Si hay actualización disponible, devuelve la Nueva versión para que cada plataforma se encargue de mostrar los avisos
    if hayqueactualizar:
        return tag_version_publicada
    else:
        return None

# Método nuevo, devuelve el nº de actualizaciones disponibles además de indicar si hay nueva versión del plugin
def get_available_updates():
    logger.info()

    # Cuantas actualizaciones hay?
    number_of_updates = 0
    new_published_version_tag = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()

    for latest_package in latest_packages["body"]:

        if latest_package["package"]=="plugin":
            if latest_package["version"] > versiontools.get_current_plugin_version():
                number_of_updates = number_of_updates + 1
                new_published_version_tag = latest_package["tag"]

        elif latest_package["package"]=="channels":
            if latest_package["version"] > versiontools.get_current_channels_version():
                number_of_updates = number_of_updates + 1

        elif latest_package["package"]=="servers":
            if latest_package["version"] > versiontools.get_current_servers_version():
                number_of_updates = number_of_updates + 1

    return new_published_version_tag,number_of_updates

def update(item):
    logger.info()

    # Valores por defecto
    published_version_url = ""
    published_version_filename = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()
    for latest_package in latest_packages["body"]:
        if latest_package["package"]=="plugin":
            published_version_url = latest_package["url"]
            published_version_filename = latest_package["filename"]
            published_version_number = latest_package["version"]
            break

    # La URL viene del API, y lo descarga en "userdata"
    remotefilename = published_version_url
    localfilename = os.path.join(config.get_data_path(),published_version_filename)

    download_and_install(remotefilename,localfilename)

def download_and_install(remote_file_name,local_file_name):
    logger.info("from "+remote_file_name+" to "+local_file_name)

    if os.path.exists(local_file_name):
        os.remove(local_file_name)

    # Descarga el fichero
    inicio = time.clock()
    from core import downloadtools
    downloadtools.downloadfile(remote_file_name, local_file_name, continuar=False)
    fin = time.clock()
    logger.info("Descargado en %d segundos " % (fin-inicio+1))
    
    logger.info("descomprime fichero...")
    import ziptools
    unzipper = ziptools.ziptools()

    # Lo descomprime en "addons" (un nivel por encima del plugin)
    installation_target = os.path.join(config.get_runtime_path(),"..")
    logger.info("installation_target=%s" % installation_target)

    unzipper.extract(local_file_name,installation_target)
    
    # Borra el zip descargado
    logger.info("borra fichero...")
    os.remove(local_file_name)
    logger.info("...fichero borrado")
