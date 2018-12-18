# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# tester
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

# Añade pelisalacarta al PYTHONPATH
#import os,sys
#ruta = os.path.abspath( os.path.join( os.path.dirname(__file__) , ".." , "tvalacarta" ) )
#sys.path.append(ruta)

# Fuerza la plataforma a "developer"
#from core import platform_name
#platform_name.PLATFORM_NAME = "developer"

from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

def test_one_channel(channelid):

    try:
        print channelid
        exec "from channels import "+channelid+" as channelmodule"
        resultado = channelmodule.test()
    except:
        import traceback
        from pprint import pprint
        exc_type, exc_value, exc_tb = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        for line in lines:
            line_splits = line.split("\n")
            for line_split in line_splits:
                print line_split

        resultado = False

    return resultado

def test_channels():
    
    para_probar = []

    #    # List all the items in source folder
    #    channel_scrapers_available = os.listdir( "scraper" )
    #
    #    for file in channel_scrapers_available
    #        if not file.startswith("__init__"):
    #            para_probar.append( file[0:-3] )
    #
    #    channel_scrapers_available = os.listdir( "channel" )
    #
    #    for file in channel_scrapers_available
    #        if not file.startswith("__init__"):
    #            para_probar.append( file[0:-3] )
    #
    para_probar.append( "sieterm" )
    para_probar.append( "vuittv" )
    para_probar.append( "adnstream" )
    para_probar.append( "acbtv" )
    para_probar.append( "aragontv" )
    para_probar.append( "a3media" )
    para_probar.append( "azteca7" )
    para_probar.append( "azteca13" )
    para_probar.append( "canal22" )

    funcionan = []
    no_funcionan = []
    
    no_probados = []
    #no_probados.append("justintv")

    # Verifica los canales
    for canal in para_probar:

        try:
            resultado,motivo = test_one_channel(canal)
        except:
            resultado=False
            import traceback
            motivo = traceback.format_exc()

        if resultado:
            funcionan.append(canal)
        else:
            no_funcionan.append([canal,motivo])
    
    print "------------------------------------"
    print " funcionan: %d" % len(funcionan)
    for canal in funcionan:
        print "   %s" % canal
    print " no funcionan: %d" % len(no_funcionan)
    for canal,motivo in no_funcionan:
        print "   %s (%s)" % (canal,motivo)
    print " no probados: %d" % len(no_probados)
    for canal in no_probados:
        print "   %s" % canal

if __name__ == "__main__":

    test_channels()
