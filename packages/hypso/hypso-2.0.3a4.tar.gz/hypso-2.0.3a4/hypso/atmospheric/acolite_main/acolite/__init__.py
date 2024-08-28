from hypso.atmospheric.acolite_main.acolite import landsat
from hypso.atmospheric.acolite_main.acolite import sentinel2
from hypso.atmospheric.acolite_main.acolite import sentinel3
from hypso.atmospheric.acolite_main.acolite import planet
from hypso.atmospheric.acolite_main.acolite import pleiades
from hypso.atmospheric.acolite_main.acolite import worldview
from hypso.atmospheric.acolite_main.acolite import venus
from hypso.atmospheric.acolite_main.acolite import ikonos
from hypso.atmospheric.acolite_main.acolite import viirs
from pathlib import Path
from hypso.atmospheric.acolite_main.acolite import chris
from hypso.atmospheric.acolite_main.acolite import prisma
from hypso.atmospheric.acolite_main.acolite import hico
from hypso.atmospheric.acolite_main.acolite import hyperion
from hypso.atmospheric.acolite_main.acolite import desis
from hypso.atmospheric.acolite_main.acolite import enmap
from hypso.atmospheric.acolite_main.acolite import emit
from hypso.atmospheric.acolite_main.acolite import hypso

from hypso.atmospheric.acolite_main.acolite import gf
from hypso.atmospheric.acolite_main.acolite import amazonia
from hypso.atmospheric.acolite_main.acolite import formosat
from hypso.atmospheric.acolite_main.acolite import ecostress
from hypso.atmospheric.acolite_main.acolite import sdgsat
from hypso.atmospheric.acolite_main.acolite import dimap
from hypso.atmospheric.acolite_main.acolite import s2resampling

from hypso.atmospheric.acolite_main.acolite import ac
from hypso.atmospheric.acolite_main.acolite import aerlut
from hypso.atmospheric.acolite_main.acolite import output
from hypso.atmospheric.acolite_main.acolite import shared
from hypso.atmospheric.acolite_main.acolite import dem
from hypso.atmospheric.acolite_main.acolite import ged

from hypso.atmospheric.acolite_main.acolite import tact
from hypso.atmospheric.acolite_main.acolite import acolite
from hypso.atmospheric.acolite_main.acolite import adjacency

from hypso.atmospheric.acolite_main.acolite import gem
from hypso.atmospheric.acolite_main.acolite import parameters

from hypso.atmospheric.acolite_main.acolite import cdse
from hypso.atmospheric.acolite_main.acolite import earthexplorer
from importlib.resources import files
## ignore numpy errors
import numpy as np
olderr = np.seterr(all='ignore')

import os, sys, datetime, platform
## get platform identifiers
uname = platform.uname()
python = {'platform':sys.platform, 'version':sys.version}
system = {'sysname': uname.system, 'release': uname.release, 'machine': uname.machine, 'version': uname.version}

code_path = os.path.dirname(str(Path(files("hypso.atmospheric"),"acolite_main","acolite","__init__.py")))
path = os.path.dirname(code_path)

## find config file
if not os.path.exists('{}{}config'.format(path, os.path.sep)):
    range_level = 0
    ## check if binary distribution
    if os.path.join('dist','acolite','_internal') in path:
        range_level = 3 ## three levels for this file
    elif os.path.join('dist','acolite') in path:
        range_level = 2 ## two levels for this file
    for i in range(range_level): path = os.path.split(path)[0]

cfile = str(Path(files("hypso.atmospheric"),"acolite_main","config","config.txt"))
config = shared.import_config(cfile)
config['code_path'] = code_path
config['path'] = path

## update version info
if 'version' in config:
    version = 'Generic Version {}'.format(config['version'])
else:
    version = 'Generic GitHub Clone'

    gitdir = '{}/.git'.format(path)
    gd = {}
    if os.path.isdir(gitdir):
        gitfiles = os.listdir(gitdir)

        for f in ['ORIG_HEAD', 'FETCH_HEAD', 'HEAD']:
            gfile = '{}/{}'.format(gitdir, f)
            if not os.path.exists(gfile): continue
            st = os.stat(gfile)
            dt = datetime.datetime.fromtimestamp(st.st_mtime)
            gd[f] = dt.isoformat()[0:19]

        version_long = ''
        if 'HEAD' in gd:
            version_long+='clone {}'.format(gd['HEAD'])
            version = 'Generic GitHub Clone c{}'.format(gd['HEAD'])
        if 'FETCH_HEAD' in gd:
            version_long+=' pull {}'.format(gd['FETCH_HEAD'])
            version = 'Generic GitHub Clone p{}'.format(gd['FETCH_HEAD'])

## run through config data
for t in config:
    ## set EARTHDATA credentials
    if t in ['EARTHDATA_u', 'EARTHDATA_p']:
        if (t not in os.environ) & (len(config[t]) > 0): os.environ[t] = config[t]
        continue
    ## split lists (currently only sensors)
    if ',' in config[t]:
        config[t] = config[t].split(',')
        continue

    ## test paths
    ## replace $ACDIR in config by ac.path
    if '$ACDIR' == config[t][0:6]:
        # os.path.join did not give the intended result on Windows
        config[t] = path + '/' + config[t].replace('$ACDIR', '')
        config[t] = config[t].replace('/', os.sep)

        ## make acolite dirs if they do not exist
        if not (os.path.exists(config[t])):
            os.makedirs(config[t])

    if (os.path.exists(config[t])):
        config[t] = os.path.abspath(config[t])

if 'verbosity' not in config: config['verbosity'] = 5

## read parameter scaling and settings
param = {'scaling':acolite.parameter_scaling(), 'discretisation': acolite.parameter_discretisation()}
import json
with open(config['parameter_cf_attributes'], 'r', encoding='utf-8') as f:
    param['attributes'] = json.load(f)

settings = {}
## read default processing settings
settings['defaults'] =  acolite.settings.parse(None, settings=acolite.settings.load(None), merge=False)
## copy defaults to run, run will be updated with user settings and sensor defaults
settings['run'] = {k:settings['defaults'][k] for k in settings['defaults']}
