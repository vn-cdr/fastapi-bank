from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.responses import RedirectResponse
from models import User, Account
from datetime import datetime, timedelta
from auth import auth
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, Form
from databases import Database

import pathlib
import hashlib
import re, cgi, random
import db
from db import session

pattern = re.compile(r'\w{4,20}')  # 任意の4~20の英数字を示す正規表現
pattern_pw = re.compile(r'\w{6,20}')  # 任意の6~20の英数字を示す正規表現
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$') 


app = FastAPI(
    title='FastAPIでつくるtoDoアプリケーション',
    description='FastAPIチュートリアル：FastAPI(とstarlette)でシンプルなtoDoアプリを作りましょう．',
    version='0.9 beta'
)

# staticディレクトリの絶対パスを取得
PATH_STATIC = str(
    pathlib.Path(__file__).resolve() \
        .parent / "static"
)

# URL`/static"以下にstaticファイルをマウントする
app.mount(
    '/static',
    StaticFiles(directory=PATH_STATIC, html=False),
    name='static',
)

# templatesディレクトリの絶対パスを取得
# new テンプレート関連の設定 (jinja2)
PATH_TEMPLATES = str(
    pathlib.Path(__file__).resolve() \
        .parent / "templates"
)
templates = Jinja2Templates(directory=PATH_TEMPLATES)

# Jinja2.Environment : filterやglobalの設定用
jinja_env = templates.env  
security = HTTPBasic()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse('index.html',
                                      {'request': request})

@app.get("/main")
async def main(request: Request,
                credentials: HTTPBasicCredentials = Depends(security)):

    # Basic認証で受け取った情報
    username = credentials.username
    password = hashlib.md5(credentials.password.encode()).hexdigest()

    # データベースからユーザ名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    db.session.close()

    # 該当ユーザがいない場合
    if user is None or user.password != password:
        error = 'ユーザ名かパスワードが間違っています．'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
        )

    return templates.TemplateResponse('main.html',
                                      {'request': request,
                                       'user': user,})


@app.get("/reference")
async def reference(request: Request, 
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # ログインユーザの口座情報を取得(allにすべきかな)
    account = db.session.query(Account).filter(Account.userid == user.id).first()

    # 口座残高を定義
    money = account.money

    return templates.TemplateResponse('reference.html',
                                     {'request': request,
                                      'money': money,})


@app.get("/draw")
async def draw(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    auth(credentials)

    return templates.TemplateResponse('draw.html',
                                     {'request': request,})


@app.get("/deposit")
async def deposit(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    auth(credentials)

    return templates.TemplateResponse('deposit.html',
                                     {'request': request,})


@app.post("/draw_confirm")
async def draw_confirm(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # ログインユーザの口座情報を取得(allにすべきかな)
    account = db.session.query(Account).filter(Account.userid == user.id).first()

    # POSTデータ
    data = await request.form()
    draw = data.get('draw')

    if tmp_user is not None:
            error.append('同じユーザ名のユーザが存在します。')

    # 口座残高を計算
    money = account.money - int(draw)

    return templates.TemplateResponse('draw_confirm.html',
                                     {'request': request,
                                      'draw': draw,
                                      'money': money,})


@app.post("/deposit_confirm")
async def deposit_confirm(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # ログインユーザの口座情報を取得(allにすべきかな)
    account = db.session.query(Account).filter(Account.userid == user.id).first()

    # POSTデータ
    data = await request.form()
    deposit = data.get('deposit')

    # 口座残高を計算
    money = account.money + int(deposit)

    return templates.TemplateResponse('deposit_confirm.html',
                                     {'request': request,
                                      'deposit': deposit,
                                      'money': money,})


@app.post("/draw_comp")
async def draw_comp(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()
    

    # POSTデータ
    data = await request.form()
    draw = data.get('draw')

    # 口座残高を計算
    account = db.session.query(Account).filter(Account.userid == user.id).first()
    money = account.money - int(draw)

    # DB更新
    account.money = money
    db.session.commit()

    return templates.TemplateResponse('draw_comp.html',
                                     {'request': request,
                                      'money': money,})


@app.post("/deposit_comp")
async def deposit_comp(request: Request,
                    credentials: HTTPBasicCredentials = Depends(security)):

    # 認証OK？
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # POSTデータ
    data = await request.form()
    deposit = data.get('deposit')

    # 口座残高を計算
    account = db.session.query(Account).filter(Account.userid == user.id).first()
    money = account.money + int(deposit)

    # DB更新
    account.money = money
    db.session.commit()

    # DB更新確認
    account = db.session.query(Account).filter(Account.userid == user.id).first()
    money = account.money

    return templates.TemplateResponse('deposit_comp.html',
                                     {'request': request,
                                      'money': money,})


# 口座開設
@app.get("/register")
@app.post("/register")
async def register(request: Request):
    if request.method == 'GET':
        return templates.TemplateResponse('register.html',
                                          {'request': request,
                                           'username': '',
                                           'error': []})

    if request.method == 'POST':
        # POSTデータ
        data = await request.form()
        username = data.get('username')
        password = data.get('password')
        password_tmp = data.get('password_tmp')
        mail = data.get('mail')

        error = []

        tmp_user = db.session.query(User).filter(User.username == username).first()

        # 怒涛のエラー処理
        if tmp_user is not None:
            error.append('同じユーザ名のユーザが存在します。')
        if password != password_tmp:
            error.append('入力したパスワードが一致しません。')
        if pattern.match(username) is None:
            error.append('ユーザ名は4~20文字の半角英数字にしてください。')
        if pattern_pw.match(password) is None:
            error.append('パスワードは6~20文字の半角英数字にしてください。')
        if pattern_mail.match(mail) is None:
            error.append('正しくメールアドレスを入力してください。')

        # エラーがあれば登録ページへ戻す
        if error:
            return templates.TemplateResponse('register.html',
                                              {'request': request,
                                               'username': username,
                                               'error': error})

        # 問題がなければユーザ登録
        user = User(username, password, mail)
        db.session.add(user)

        # 初期残高は0円固定
        money = 0
        account = Account(money, user.id)
        db.session.add(account)

        db.session.commit()
        db.session.close()

        return templates.TemplateResponse('complete.html',
                                          {'request': request,
                                           'username': username})
