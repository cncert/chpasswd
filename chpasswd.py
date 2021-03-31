from random import choice 
import string
import paramiko
import logging
from logging.handlers import RotatingFileHandler
import time
import sys

DEFAULT_USER = "root"
DEFAULT_PASSWORD = "111111"

def getLogger():
    # 同时输出到屏幕和日志文件
    logger = logging.getLogger()
    rf_handler = logging.StreamHandler(sys.stderr)
    rotating_log_handler = RotatingFileHandler(filename="new_passwd_"+str(int(time.time())))
    formatter = logging.Formatter("%(message)s")
    rotating_log_handler.setFormatter(formatter)
    logger.addHandler(rf_handler)
    logger.addHandler(rotating_log_handler)
    logger.setLevel(logging.WARN)
    return logger

def makePasswd():
    # 生成随机密码，密码包含数字, 字母，特殊字符 
    SpecialChar = '?%!^()_?%!^()_' 
    length = 14 
    chars = string.ascii_letters+string.digits+SpecialChar 
    passwd = ''.join([choice(chars) for i in range(length)]) 
    return passwd

pass_logger = getLogger()

def makeConnect(host_ip, user, password, port, new_password):
    try:
        port = int(port)
    except Exception as e:
        pass_logger.error("{} has error: an integer port is required (got type str)".format(host_ip))
        return
    try:
        s = paramiko.Transport((host_ip, port))
        s.connect(username=user, password=password)
        chan = s.open_session()
        chan.get_pty()
        chan.invoke_shell()
        chan.send('passwd root\n')
        time.sleep(1)
        chan.send('{}\n'.format(new_password))
        time.sleep(1)
        chan.send('{}\n'.format(new_password))
        time.sleep(1)
        pass_logger.warning(",".join([host_ip, str(port), user, new_password]))
    except Exception as err:
        pass_logger.error("{} has error: {}".format(host_ip, err))
    return

def chpasswd():
    user = DEFAULT_USER
    password = DEFAULT_PASSWORD
    with open("hosts", "r", encoding="utf8") as f:
        for line in f:
            if not line:
                continue
            if line.startswith("#"):
                continue
            host_info = line.split()
            host_ip = host_info[0]
            new_password = makePasswd()
            if len(host_info)<2:
                pass_logger.error("host {} don't specify port".format(host_ip))
                continue
            if len(host_info)<3:
                port = host_info[1]
                makeConnect(host_ip, user, password, port, new_password)
                continue
            if len(host_info)<4:
                pass_logger.error("host {} don't specify user or password".format(host_ip))
                continue
            if len(host_info)<5:
                port = host_info[1]
                user = host_info[2]
                password = host_info[3]
                makeConnect(host_ip, user, password, port, new_password)
                continue
            else:
                pass_logger.error("host {} have too many args, cann't do task".format(host_ip))

if __name__ == "__main__": 
    chpasswd()