__author__ = 'yxu42x'

import os
import shutil
from datetime import datetime
from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.configuration.configuration import host_platform, is_linux_host, is_windows_host
import stat


class LogHandler(object):
    if is_windows_host():
        log_path = r'c:\Logs'
    elif is_linux_host():
        log_path = r'/Logs'
    else:
        raise Exception('os not define {0}'.format(host_platform()))
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    src_path = os.getenv('LC_RESULT_PATH') if os.getenv('LC_RESULT_PATH') else os.getenv('CAF_CASE_LOG_PATH')

    @classmethod
    def log_processor(cls):
        if cls.src_path:
            log_dir = os.path.join(cls.log_path, datetime.now().strftime('%Y-%m-%d'), os.path.basename(cls.src_path))
            sparklogger.info('src path {}'.format(cls.src_path))
            sparklogger.info('logs dir => {}'.format(log_dir))
            ret = os.system(r'robocopy /mt /e /is {} {}'.format(cls.src_path, log_dir))
            if ret <= 3:
                sparklogger.info('copy directory {} to {} successfully'.format(cls.src_path, log_dir))
        delete_dirs = cls._dir_filter_by_date()
        if len(delete_dirs) > 0:
            for dir, date in delete_dirs:
                os.chmod(dir, stat.S_IWRITE)
                if os.path.isfile(dir):
                    os.unlink(dir)
                else:
                    shutil.rmtree(dir)
                sparklogger.info('delete logs dir {} with create date {}'.format(dir, date))

    @classmethod
    def _dir_filter_by_date(cls):
        log_dir = os.listdir(cls.log_path)
        file_exceed_ten_days = []
        cur_date = datetime.now().date()
        for dir in log_dir:
            dir_path = os.path.join(cls.log_path, dir)
            file_create_timestamp = os.path.getctime(dir_path)
            file_create_date = datetime.fromtimestamp(file_create_timestamp).date()
            date_delta = (cur_date - file_create_date).days
            if date_delta > 10:
                file_exceed_ten_days.append((dir_path, file_create_date))
        return file_exceed_ten_days
