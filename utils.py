# coding=utf-8
import configparser
import os


def get_db_config():
    cfgpath = "config.ini"
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3
    items = conf.items('db')
    return dict(items)


def set_db_config(args):
    """
    将db信息写入配置文件
    :param args: 字典
    :return:
    """

    cfgpath = "config.ini"
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3
    items = conf.items('db')
    for item in args:
        conf.set('db', item, args[item])
    with open(cfgpath, "w+", encoding="utf-8") as cfgpath_fd:
        conf.write(cfgpath_fd)
    return dict(items)


def set_cookie_config(args):
    """
    将db信息写入配置文件
    :param args: 字典
    :return:
    """

    cfgpath = "config.ini"
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3
    if conf.has_section('cookies'):
        conf.remove_section('cookies')
    if not conf.has_section('cookies'):
        conf.add_section('cookies')
    # items = conf.items('cookies')
    for item in args:
        if args[item]:
            conf.set('cookies', item, args[item])
    with open(cfgpath, "w+", encoding="utf-8") as cfgpath_fd:
        conf.write(cfgpath_fd)
    # return dict(items)


def set_config(section, args):
    """
    设置配置信息
    :param section: [section] 的名字
    :param args: 字典
    :return:
    """

    cfgpath = "config.ini"
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3
    if conf.has_section(section):
        conf.remove_section(section)
    if not conf.has_section(section):
        conf.add_section(section)
    for item in args:
        if args[item]:
            conf.set(section, item, args[item])
    with open(cfgpath, "w+", encoding="utf-8") as cfgpath_fd:
        conf.write(cfgpath_fd)


def get_config(section):

    cfgpath = "config.ini"
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")  # python3
    items = conf.items(section)
    return dict(items)


def get_phantomjs_path():
    phantomjs = "third-party/phantomjs-2.1.1-windows/bin/phantomjs.exe"
    return phantomjs



