# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
#------------------------------------------------------------
# json_tools
# Parsea un string en JSON probando varios módulos
#------------------------------------------------------------

import traceback
import config
import logger

def load_json(data):
    logger.info("core.jsontools.load_json Probando simplejson en directorio lib")

    # callback to transform json string values to utf8
    def to_utf8(dct):
        rdct = {}
        for k, v in dct.items() :
            if isinstance(v, (str, unicode)) :
                rdct[k] = v.encode('utf8', 'ignore')
            else :
                rdct[k] = v
        return rdct

    try:
        logger.info("core.jsontools.load_json Probando simplejson en directorio lib")
        from lib import simplejson
        json_data = simplejson.loads(data, object_hook=to_utf8)
        #logger.info("core.jsontools.load_json -> "+repr(json_data))
        return json_data
    except:
        logger.info(traceback.format_exc())

        try:
            logger.info("core.jsontools.load_json Probando simplejson incluido en el interprete")
            import simplejson
            json_data = simplejson.loads(data, object_hook=to_utf8)
            #logger.info("core.jsontools.load_json -> "+repr(json_data))
            return json_data
        except:
            logger.info(traceback.format_exc())
            
            try:
                logger.info("core.jsontools.load_json Probando json incluido en el interprete")
                import json
                json_data = json.loads(data, object_hook=to_utf8)
                #logger.info("core.jsontools.load_json -> "+repr(json_data))
                return json_data
            except:
                logger.info(traceback.format_exc())

                try:
                    logger.info("core.jsontools.load_json Probando JSON de Plex")
                    json_data = JSON.ObjectFromString(data, encoding="utf-8")
                    #logger.info("core.jsontools.load_json -> "+repr(json_data))
                    return json_data
                except:
                    logger.info(traceback.format_exc())

    logger.info("core.jsontools.load_json No se ha encontrado un parser de JSON valido")
    logger.info("core.jsontools.load_json -> (nada)")
    return ""

