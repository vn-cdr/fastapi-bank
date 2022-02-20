from datetime import datetime
from pickle import FALSE

from db import Base, ENGINE, session
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER

import hashlib


class User(Base):
    """
    Userテーブル

    id       : 主キー
    username : ユーザネーム
    password : パスワード
    mail     : メールアドレス
    """
    __tablename__ = 'user'
    id        = Column('id', INTEGER(unsigned=True), primary_key=True, autoincrement=True,)
    username  = Column('username' , String(256))
    password  = Column('password' , String(256))
    mail      = Column('mail'     , String(256))

    def __init__(self, username, password, mail,):
        self.username = username
        # パスワードはハッシュ化して保存
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.mail = mail

    def __str__(self):
        return str(self.id) + ':' + self.username


class Account(Base):
    """
    口座テーブル

    id      : 主キー
    money   : 貯金額
    userid  : userid 外部キー
    """
    __tablename__ = 'account'
    id = Column('id', INTEGER(unsigned=True), primary_key=True, autoincrement=True,)
    money = Column('money', INTEGER)
    userid = Column('userid', ForeignKey('user.id'))

    def __init__(self, money, userid):
        self.money = money
        self.userid = userid

    def __str__(self):
        return str(self.id) + \
                ': money -> ' + str(self.money) + \
                ', userid -> ' + str(self.userid)


# 初期設定用
def main():
    Base.metadata.create_all(ENGINE)
    
    # テスト用としてAdminユーザ作成
    admin = User(username="admin", password="password", mail="",)
    session.add(admin) # insert

    account = Account(money=10, userid=admin.id)
    session.add(account) # insert

    session.commit() # commit


if __name__ == '__main__':
    main()
