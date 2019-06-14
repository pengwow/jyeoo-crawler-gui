import configparser
import os
from interface.mysql_model import *
from interface.utils import *

ddd = 'sssss2'
# print(db_dict)
print(ddd[:-1])

#
# db_connect = DBSession(account=db_dict['db_account'], password=db_dict['db_password'],
#                        ip=db_dict['db_ip'], port=db_dict['db_port'], dbname=db_dict['db_dbname'])
#
# aaa = db_connect.session.query(ItemStyle.level_name,ItemStyle.level_code).group_by(ItemStyle.level_name)
# for item in aaa:
#     print(item)
# aaa = get_config('cookies')
# print(aaa)
# import time
#
# print(int(time.time()) +100000)
#
#
# timeStamp = int(time.time()) +10000000
# timeArray = time.localtime(timeStamp)
# otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
# print(otherStyleTime)   # 2013--10--10 23:40:00
