import os

import xlrd
from flask import Flask, session, flash, url_for, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from .config import Config
from flask_bootstrap import Bootstrap
from functools import wraps

db=SQLAlchemy()
class Books(db.Model):
    __tablename__ = "books"
    id = db.Column("book_id",db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    author = db.Column(db.String(50))
    price = db.Column(db.String(10))

class User(db.Model):
    __tablename__="users"
    id = db.Column("user_id",db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    age = db.Column(db.String(3))




#create app
def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    #这是一个装饰器
    def auth(func):
        @wraps(func)
        def inner(*args,**kwargs):
            if 'username' in session:
                logsuccessmsg = f"登录成功{session['username']}"
                return func(*args,**kwargs)
            # flash和它的名字一样，是闪现，意思就是我们的消息只会显示一次，当我们再次刷新也面的时候，它就不存在了，而正是这点，它经常被用来显示一些提示消息，比如登陆之后，显示欢迎信息等
            else:
                flash("登录失败！")
                return redirect(url_for("login"))
        return  inner

    #注册
    @app.route("/register" ,methods=["GET","POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")
        account = request.form.get("account")
        user = User.query.filter_by(name=account).first()
        if user:
            flash("该用户名已经被使用了，请换一个！")
            return render_template("register.html")
        password = request.form.get("password")
        age = request.form.get("age")

        user = User(name=account, password=password,age=age)
        db.session.add(user)
        db.session.commit()
        print('注册成功！')
        return render_template("login.html")


    #登录
    @app.route('/login',methods=["GET","POST"])
    def login():
        if request.method =="GET":
            return render_template("login.html")
        account = request.form.get("account")
        password = request.form.get("password")

        user = User.query.filter_by(name=account).first()
        if not user:
            flash('用户名不存在，请先注册！')
            return render_template("login.html")
        #这个地方应该要从数据库中匹配用户名和密码
        if password==user.password:
            session["username"] = account
            return redirect("/index")
        flash('用户名或密码错误，请重新登录！')
        return render_template("login.html")

    #登出
    @app.route("/logout")
    @auth
    def logout():
        # 删除单个Session的值，可以使用Session.pop(‘key’)方法，如果要清除多个值，可以使用Session.clear()方法。
        session.pop('username',None)
        return redirect(url_for("index") )

    @app.route('/')
    @app.route('/index')
    @auth
    def index():
        return render_template("index.html", account_name=session["username"],books=Books.query.all())

    #添加新书
    @app.route('/new_book', methods=['GET','POST'])
    @auth
    def new_book():
        if request.method=="POST":
            if not request.form['name'] or not request.form['author'] or not request.form['price']:
                flash('表格请填写完整', 'error')
            else:
                book = Books(name=request.form['name'],author=request.form['author'],price=request.form['price'])
                db.session.add(book)
                db.session.commit()
                print("添加成功！")
                return redirect(url_for("index"))
        return render_template("new_book.html")

    #删除
    @app.route('/delete/<int:id>')
    @auth
    def delete(id):
        book=Books.query.filter_by(id=id).first_or_404()
        db.session.delete(book)
        db.session.commit()
        return redirect('/index')

    #修改
    @app.route('/modify',methods=['GET','POST'])
    @auth
    def mofdify():
        id = request.args['id']
        book=Books.query.filter_by(id=int(id)).first_or_404()
        if request.method=="POST":
            book.author=request.form['author']
            book.price=request.form['price']
            db.session.commit()
            return redirect(url_for('index'))
        name =book.name
        author = book.author
        price = book.price
        return render_template("modify.html", name=name, author=author,price=price)

    @app.route('/search',methods=['GET','POST'])
    @auth
    def search():
        name = request.form['name']
        books = Books.query.filter(Books.name.contains(name)).all()
        return render_template("search.html",search=name,books=books)
    #上传
    @app.route('/upload_excel',methods=['GET','POST'])
    @auth
    def upload_excel():
        if request.method=="POST":
            f=request.files['file']
            print(request.files)
            f_path=os.path.join(app.config['UPLOAD_FOLDER'],f.filename)
            f.save(f_path)
            #通过xlrd模块读取文件
            wb=xlrd.open_workbook(f_path)
            ws=wb.sheets()[0]

            for row_n in range(ws.nrows):
                row_v = ws.row_values(row_n)
                book=Books(name =row_v[0],author=row_v[1],price =str(row_v[2]))
                db.session.add(book)
            db.session.commit()
            flash("导入Excel成功！")
            os.remove(f_path)
            return redirect(url_for("/index"))
        return render_template("upload_excel.html")

    return app


