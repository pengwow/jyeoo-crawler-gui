# coding=utf-8
import configparser
import uuid
import platform
from multiprocessing import Lock
import os
import zipfile
import hashlib
import base64
from Crypto.Cipher import AES

the_salt = "jyeoo_crawler"
the_key = "jyeoo_crawler"

# 锁
mutex = Lock()


# import os

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
    将cookie信息写入配置文件
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
    current_system = platform.system()
    phantomjs = "third-party/phantomjs"
    if "Windows" == current_system:
        phantomjs = "third-party/phantomjs.exe"
    if not os.path.exists(phantomjs) and os.path.exists(phantomjs + '.zip'):
        zipf = zipfile.ZipFile(phantomjs + '.zip')
        zipf.extractall('third-party')
    return phantomjs


def kill_process(process_name):
    try:
        current_system = platform.system()
        if "Windows" == current_system:
            os.system('taskkill /f /im %s' % process_name)
        else:
            cmd = 'ps aux | grep {process_name} '.format(process_name=process_name)
            cmd += "| awk {print '$2'} | xargs kill"
            os.system(cmd)
    except Exception as e:
        print(str(e))


def recursive_get_li(parent_id, library_id, xpath_list):
    """
    递归获取li
    :param parent_id:父节点ID
    :param library_id:
    :param xpath_list:
    :return:
    """
    re_list = list()
    if xpath_list:
        li = xpath_list.xpath('./ul/li')
        for item in li:
            temp_dict = dict()
            pk = item.attrib.get('pk')
            nm = item.attrib.get('nm')
            temp_dict['id'] = str(uuid.uuid1())
            temp_dict['parent_id'] = parent_id
            temp_dict['library_id'] = library_id
            temp_dict['pk'] = pk
            temp_dict['name'] = nm
            child = recursive_get_li(temp_dict['id'], library_id, item)
            temp_dict['child'] = child
            re_list.append(temp_dict)
    return re_list


def split_list(src_list):
    """
    拆分列表,层级关系拆成一层
    :param src_list:
    :return:
    """
    new_list = list()
    for item in src_list:
        child = item.pop('child')
        new_list.append(item)
        if child:
            child = split_list(child)
            new_list.extend(child)
    return new_list


# 取字符串中两个符号之间的东东
def txt_wrap_by(start_str, end, html):
    if not html:
        return ''
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()


class HashManager(object):

    # ######MD5加密#######
    @staticmethod
    def get_md5(the_string):
        the_string_with_salt = the_string + the_salt
        the_md5 = hashlib.md5()
        the_md5.update(the_string_with_salt.encode('utf-8'))
        the_string_md5 = the_md5.hexdigest()
        return the_string_md5

    # ######SHA1加密#######
    @staticmethod
    def get_sha1(the_string):
        the_string_with_salt = the_string + the_salt
        the_sha1 = hashlib.sha1()
        the_sha1.update(the_string_with_salt.encode('utf-8'))
        the_string_sha1 = the_sha1.hexdigest()
        return the_string_sha1

    # ######SHA256加密#######
    @staticmethod
    def get_sha256(the_string):
        the_string_with_salt = the_string + the_salt
        the_sha256 = hashlib.sha256()
        the_sha256.update(the_string_with_salt.encode('utf-8'))
        the_string_sha1 = the_sha256.hexdigest()
        return the_string_sha1

    # ######SHA512加密#######
    @staticmethod
    def get_sha512(the_string):
        the_string_with_salt = the_string + the_salt
        the_sha512 = hashlib.sha512()
        the_sha512.update(the_string_with_salt.encode('utf-8'))
        the_string_sha1 = the_sha512.hexdigest()
        return the_string_sha1

    # ######AES加密，ECB模式#######
    def get_aes_ecb(self, the_string):
        aes = AES.new(self.pkcs7padding_tobytes(the_key), AES.MODE_ECB)  # 初始化加密器
        encrypt_aes = aes.encrypt(self.pkcs7padding_tobytes(the_string))  # 进行aes加密
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 用base64转成字符串形式
        return encrypted_text

    # ######AES解密，ECB模式#######
    def back_aes_ecb(self, the_string):
        try:
            aes = AES.new(self.pkcs7padding_tobytes(the_key), AES.MODE_ECB)  # 初始化加密器
            decrypted_base64 = base64.decodebytes(the_string.encode(encoding='utf-8'))  # 逆向解密base64成bytes
            decrypted_text = str(aes.decrypt(decrypted_base64), encoding='utf-8')  # 执行解密密并转码返回str
            decrypted_text_last = self.pkcs7unpadding(decrypted_text)  # 去除填充处理
            return decrypted_text_last
        except Exception as e:
            return ''

    # ######AES加密，CFB模式#######
    def get_aes_cfb(self, the_string):
        key_bytes = self.pkcs7padding_tobytes(the_key)
        iv = key_bytes
        aes = AES.new(key_bytes, AES.MODE_CFB, iv)  # 初始化加密器，key,iv使用同一个
        encrypt_aes = iv + aes.encrypt(the_string.encode())  # 进行aes加密
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 用base64转成字符串形式
        return encrypted_text

    # ######AES解密，CFB模式#######
    def back_aes_cfb(self, the_string):
        key_bytes = self.pkcs7padding_tobytes(the_key)
        iv = key_bytes
        aes = AES.new(key_bytes, AES.MODE_CFB, iv)  # 初始化加密器，key,iv使用同一个
        decrypted_base64 = base64.decodebytes(the_string.encode(encoding='utf-8'))  # 逆向解密base64成bytes
        decrypted_text = str(aes.decrypt(decrypted_base64[16:]), encoding='utf-8')  # 执行解密密并转码返回str
        return decrypted_text

    # ######AES加密，CBC模式#######
    def get_aes_cbc(self, the_string):
        key_bytes = self.pkcs7padding_tobytes(the_key)
        iv = key_bytes
        aes = AES.new(key_bytes, AES.MODE_CBC, iv)  # 初始化加密器，key,iv使用同一个
        encrypt_bytes = aes.encrypt(self.pkcs7padding_tobytes(the_string))  # 进行aes加密
        encrypted_text = str(base64.b64encode(encrypt_bytes), encoding='utf-8')  # 用base64转成字符串形式
        return encrypted_text

    # ######AES解密，CBC模式#######
    def back_aes_cbc(self, the_string):
        key_bytes = self.pkcs7padding_tobytes(the_key)
        iv = key_bytes
        aes = AES.new(key_bytes, AES.MODE_CBC, iv)  # 初始化加密器，key,iv使用同一个
        decrypted_base64 = base64.b64decode(the_string)  # 逆向解密base64成bytes
        decrypted_text = str(aes.decrypt(decrypted_base64), encoding='utf-8')  # 执行解密密并转码返回str
        decrypted_text_last = self.pkcs7unpadding(decrypted_text)  # 去除填充处理
        return decrypted_text_last

    # ######填充相关函数#######
    def pkcs7padding_tobytes(self, text):
        return bytes(self.pkcs7padding(text), encoding='utf-8')

    @staticmethod
    def pkcs7padding(text):
        bs = AES.block_size
        # ###tips：utf-8编码时，英文占1个byte，而中文占3个byte####
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        padding_size = length if (bytes_length == length) else bytes_length
        ####################################################
        padding = bs - padding_size % bs
        padding_text = chr(padding) * padding  # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        return text + padding_text

    @staticmethod
    def pkcs7unpadding(text):
        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]

