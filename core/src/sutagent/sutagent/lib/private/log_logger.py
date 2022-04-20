import os
import logging
import logging.config
import sys

# Log level seeting function. Log levels we have are DEBUG, INFO, ERROR, WARNING, CRICTICAL in  which if we set the log level as the first command line argument while running the test case like
# for e.g --log_level=INFO then the logfile will have the info,error,warning and critical messages excludind DEBUG messages.
# for e.g --log_level=ERROR then the logfile will have the error,warning and critical messages excluding DEBUG and INFO messages.
# If we dont set the log level while running the test case by default the log level will be DEBUG.
# from sutagent.lib.hostutility import testcaselogger


def get_argv(name, default=''):
    argv = default
    try:
        arg = sys.argv[1]
        argItems = arg.split('--')
        for item in argItems:
            if item.startswith('{0}='.format(name)):
                argv = item.replace('{0}='.format(name), '').strip()
                break

    except Exception as ex:
        logging.info('exception: {}'.format(ex))
    finally:
        return argv


log_level = get_argv('log_level')

# log configuration file
# LOG_CONF = os.path.abspath("../globals/logging.conf")  #get logging.conf path
#parPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# LOG_CONF = os.path.join(parPath,r'globals\logging.conf') #get logging.conf path

LOG_CONF = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'globals', 'logging.conf'))

if 'DEBUG' in log_level:
    log_level = logging.DEBUG
elif 'INFO' in log_level:
    log_level = logging.INFO
elif 'WARNING' in log_level:
    log_level = logging.WARNING
elif 'ERROR' in log_level:
    log_level = logging.ERROR
elif 'CRITICAL' in log_level:
    log_level = logging.CRITICAL
else:
    log_level = logging.DEBUG

# log_level = logging.DEBUG  # User can modify this item to control which level of log will be output for spark.
logging.config.fileConfig(LOG_CONF)  # load configuration file.

# create sparklogger and define it's log level
sparklogger = logging.getLogger('Spark')  # used for API log system.
sparklogger.setLevel(log_level)

# create sparklogger and define it's log level
caselogger = logging.getLogger('TestCase')  # used for API log system.
caselogger.setLevel(log_level)

# example code:  as design, only two level log for APIs: DEBUG and ERROR.
# sparklogger.debug('spark debug message')
# sparklogger.error('spark error message')
