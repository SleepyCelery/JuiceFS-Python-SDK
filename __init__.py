import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
debug = True
if debug:
    from package_configs import juicefs_config

    os.environ['JFS_METAURL'] = juicefs_config.METAURL
    os.environ['JFS_MOUNTPOINT'] = '/Users/sleepycelery/JuiceFSMountpoint'
