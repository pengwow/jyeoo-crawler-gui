# -*- coding: utf-8 -*-

from sqlalchemy import INT, Column, String, create_engine, Boolean, DateTime, Text  # , ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid
import datetime

# 创建对象的基类:
Base = declarative_base()


# Create your views here.
def get_uuid():
    s_uuid = str(uuid.uuid1())

    l_uuid = s_uuid.split('-')

    s_uuid = ''.join(l_uuid)

    return s_uuid


#  以上代码完成SQLAlchemy的初始化和具体每个表的class定义
# 绑定元信息
# metadata = MetaData(engine)

class CookieInfo(Base):
    from sqlalchemy import Text
    # 表的名字:
    __tablename__ = 'cookie_info'
    # 唯一id
    id = Column(String(32), primary_key=True, default=get_uuid)
    # 创建时间
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    # cookie 
    cookie = Column(Text)
    # 是否有效 False 为失效
    is_valid = Column(Boolean, default=True)


class LibraryEntry(Base):
    # 表的名字:
    __tablename__ = 'library_entry'
    # 唯一id
    id = Column(String(36), primary_key=True)
    # 授课层级Code
    # 参数表 style = 4
    level_code = Column(String(10))
    # 科目Code
    # 参数表 style = 6
    subject_code = Column(String(10))
    # 教材名称
    style_name = Column(String(30))
    # 教材序号
    style_idx = Column(INT)
    # 年级编码
    # 参数表 style = 5
    grade_code = Column(String(10))


class LevelGradeRef(Base):
    # 表的名字:
    __tablename__ = 'level_grade_ref'
    # 唯一id
    id = Column(INT, autoincrement=True, primary_key=True)
    # 授课层级名称
    level_name = Column(String(20))
    # 授课层级Code
    level_code = Column(String(10))
    # 科目名称
    grade_name = Column(String(20))
    # 科目编码
    grade_code = Column(String(10))


class LevelSubjectsRef(Base):
    # 表的名字:
    __tablename__ = 'level_subjects_ref'
    # 唯一id
    id = Column(INT, autoincrement=True, primary_key=True)
    # 授课层级名称
    level_name = Column(String(20))
    # 授课层级Code
    level_code = Column(String(10))
    # 科目名称
    subject_name = Column(String(20))
    # 科目编码
    subject_code = Column(String(10))
    # 科目URL
    search_url = Column(String(100))


class ItemStyle(Base):
    # 表的名字:
    __tablename__ = 'item_style'
    # 唯一id
    id = Column(String(36), primary_key=True)
    # 年级名字
    level_name = Column(String(20))
    # 年级代码
    level_code = Column(String(10))
    # 科目名称
    subject_name = Column(String(20))
    # 科目编码
    subject_code = Column(String(10))
    # 题型名称
    style_name = Column(String(20))
    # 题型编码
    style_code = Column(String(10))


class LibraryChapter(Base):
    # 表的名字:
    __tablename__ = 'library_chapter'
    # 唯一id
    id = Column(String(36), primary_key=True)
    # 教材题库ID
    library_id = Column(String(36))
    # 章节名称
    name = Column(String(50))
    # 父节点
    parent_id = Column(String(36))
    # 直接索引
    pk = Column(String(80))
    # 是否已经查询过
    is_finish = Column(INT, default=0)


class ChaperPoint(Base):
    # 表的名字:
    __tablename__ = 'chaper_point'
    # 主键 UUID
    id = Column(INT, autoincrement=True, primary_key=True)
    # 章节ID
    chaper_id = Column(String(36))
    # 知识点说明
    title = Column(String(500))
    # 知识点编码
    code = Column(String(10))
    # 知识点内容
    content = Column(String(8000))
    # 知识点URL
    url = Column(String(255))


class ItemPoint(Base):
    # 表的名字:
    __tablename__ = 'item_point'
    # 主键 自增ID
    id = Column(INT, autoincrement=True, primary_key=True)
    # 试题ID
    item_id = Column(String(36))
    # 知识点编码
    point_code = Column(String(10))


class ItemBank(Base):
    # 表的名字:
    __tablename__ = 'item_bank'
    # 主键 UUID
    id = Column(String(36), primary_key=True, default=get_uuid)
    # 教材ID
    library_id = Column(String(36))
    # 章节ID
    chaper_id = Column(String(36))
    # 题型
    item_style_code = Column(String(10))
    # 难度编码
    difficult_code = Column(String(10))
    # 题类编码
    field_code = Column(String(10))
    # 来源编码
    from_code = Column(String(10))
    # 年份编码
    year_code = Column(String(10))
    # 组卷次数
    used_times = Column(String(10))  # Column(INT)
    # 真题次数
    exam_times = Column(String(10))  # Column(INT)
    # 试题内容
    context = Column(Text)
    # 试题解析
    anwser = Column(Text)
    # 年份与地区
    year_area = Column(String(100))
    # 收录时间
    record_time = Column(String(10))
    # url地址
    url = Column(String(255))
    # 爬取时间
    create_date = Column(DateTime, default=datetime.datetime.now().strftime('%Y-%m-%d'), comment='爬取时间')


class ItemBankInit(Base):
    # 表的名字:
    __tablename__ = 'item_bank_init'
    # 主键 自增ID
    id = Column(INT, autoincrement=True, primary_key=True)
    # 课题的id
    fieldset_id = Column(String(36))
    # 详情页url
    detail_page_url = Column(String(255))
    # 搜索页url
    ques_url = Column(String(255))
    # 学科
    from_code = Column(String(36))
    # 题型
    item_style_code = Column(String(10))
    # 教材ID
    library_id = Column(String(36))
    # 章节ID
    chaper_id = Column(String(36))
    # 是否已经查询过
    is_finish = Column(INT, default=0)


class DBSession(object):

    def __init__(self, account, password, ip, port, dbname):
        # from jyeoo.settings import MYSQL_ENGINE
        # 初始化数据库连接: password 为自己数据库密码
        # '数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名'
        MYSQL_ENGINE = 'mysql+pymysql://{account}:{password}@{ip}:{port}/{dbname}'
        self.engine = create_engine(MYSQL_ENGINE.format(account=account,
                                                        password=password,
                                                        ip=ip,
                                                        port=port,
                                                        dbname=dbname))
        # 创建DBSession类型:
        db_session = sessionmaker(bind=self.engine)
        self._session = db_session()

    @property
    def session(self):
        return self._session

    def add(self, param):
        """
        添加值
        :param param:
        :return:
        """
        self._session.add(param)
        self._session.commit()

    # def update(self, table, field, value=list()):
    #     """
    #     修改值
    #     :param table: 表名
    #     :param field: 修改字段名称
    #     :param value: 修改的值 {'key':'','value':''}
    #     :return:
    #     """
    #     eval_command = "{table}.{field}".format(table=table, field=field)
    #     query = self._session.query(table).filter(eval(eval_command)).first()
    #     for item in value:
    #         eval('query.{key}={value}'.format(key=item['key'], value=item['value']))
    #     self._session.commit()

    def __del__(self):
        self.session.close()

    def rebuild_table(self):
        # 删除表结构
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

# 创建数据表，如果数据表存在则忽视！！！
# Base.metadata.create_all(engine)  # 创建表结构
# Base.metadata.drop_all(engine)  # 创建表结构

# 由于有了ORM，我们向数据库表中添加一行记录，可以视为添加一个User对象
#  DBSession对象可视为当前数据库连接
#  创建session对象:
# session = DBSession()
# aaa = session.session.query(LibraryEntry).all()
# for item in aaa:
#     print(item.style_name)
# # 重建表
# session.rebuild_table()
# # # 创建新User对象:
# new_user = InvoiceText(text='111111111')
# # 添加到session:
# session.add(new_user)
# #  提交即保存到数据库:
# session.commit()
# #  关闭session:
# session.close()
# aaaaaa = 'f3c07ef0c47f11e8b5e338378beebca7'
# aaa = session.session.query(InvoiceText).filter(InvoiceText.info_id==aaaaaa)
# # aaa = session.session.query(TextInfoR,InvoiceText).filter(TextInfoR.info_id=='3c33c562c47711e8a6c438378beebca7').
# filter(InvoiceText.id==TextInfoR.text_id)
# #
# for u in aaa:
#     print(u.text)

# 插入图片数据

# with open('D:\\workspace\\Own project\\AutoInvoice\\test_image\\43.jpg', 'rb') as fp:
#     result = fp.read()
#     print(result)
# image_data = ImageInfoR(id='12344', image=result, info_id='333232')
# session.add(image_data)
# session.close()
