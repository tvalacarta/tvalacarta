# Passing log and config to an external library
# All credits to: https://gist.github.com/mikew/5011984

# Contents/Libraries/Shared/bridge.py
logger = None
config = None
localized_strings = None

def init(Log,Dict,Locale):
    global config,logger,localized_strings
    config = Dict
    logger = Log
    localized_strings = Locale

def log_info(texto):
    logger(texto)

def get_setting(name):
    return config[name]

def get_localized_string(code):
    return localized_strings.LocalString(code)

'''
Using:

# Contents/Libraries/Shared/library.py
import bridge
 
def test():
    # this will log to com.plexapp.plugin.foo.log
    bridge.config['Dict']['foo'] = 'bar'
    bridge.config['Log']('Dict[foo] is %s' % config['Dict']['foo'])
'''