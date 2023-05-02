from pro_excel import config, create_app, db

app = create_app()

app.config.from_object(config.Config)
#初始化数据库
db.init_app(app)
app.app_context().push()
db.create_all() #创建所有的表

if __name__ == '__main__':
    app.run(debug=True,port=3389)
