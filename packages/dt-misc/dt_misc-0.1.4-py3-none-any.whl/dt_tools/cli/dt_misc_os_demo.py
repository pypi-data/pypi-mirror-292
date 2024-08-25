from loguru import logger as LOGGER

import dt_tools.logger.logging_helper as lh
from dt_tools.os.os_helper import OSHelper

def demo():
    LOGGER.info('')
    LOGGER.info('dt_misc_os_demo')
    LOGGER.info('-'*80)
    LOGGER.info('')
    LOGGER.info('Determine OS:')
    LOGGER.info('-'*40)
    if OSHelper.is_raspberrypi():
        LOGGER.info('- Running on Raspberry Pi')
    if OSHelper.is_linux():
        LOGGER.success('- Running on Linux')
    if OSHelper.is_windows():
        LOGGER.success('- Running on Windows')

    LOGGER.info('')
    LOGGER.info('Check if Executable is available:')
    LOGGER.info('-'*40)
    for pgm in ['gitx', 'git']:
        exe = OSHelper.is_executable_available(pgm)
        LOGGER.log("ERROR" if exe is None else "SUCCESS", f'  {pgm:8} : {exe}')

    if OSHelper.is_windows():
        LOGGER.info('')
        input('Press ENTER to Continue for Admin Check')
        LOGGER.info('')
        LOGGER.info('Admin Check:')
        LOGGER.info('-'*40)
        if OSHelper.is_windows_admin():
            LOGGER.info('')
            LOGGER.info('  ****************************************')
            LOGGER.info('  ** Windows admin privileges in effect **')
            LOGGER.info('  ****************************************')
            LOGGER.info('')
            input('Press Enter to continue...')        
        else:
            LOGGER.warning('  Not Admin, Elevate privileges')
            if OSHelper.elevate_to_admin():
                LOGGER.info('  - New prompt Shelled as admin')
            else:
                LOGGER.error('  - Unable to elevate. (User cancelled or error)')

        LOGGER.info('')
        LOGGER.info('Demo commplete.')            

if __name__ == "__main__":
    lh.configure_logger(log_format=lh.DEFAULT_CONSOLE_LOGFMT, log_level="INFO")
    demo()
