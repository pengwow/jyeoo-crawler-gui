from pyupdater.client import Client
from client_config import ClientConfig

client = Client(ClientConfig())
client.refresh()
def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)
client.add_progress_hook(print_status_info)

APP_NAME = 'jyeoo-crawler'
APP_VERSION = '0.0.0'
app_update = client.update_check(APP_NAME, APP_VERSION)
if app_update is not None:
    print("111111")
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
