from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from .routes import bp
from .database import db


def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)

    # 阿里数据库链接
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "mysql+pymysql://"
        f'{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
        f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/'
        f'{os.getenv("DB_NAME")}?charset=utf8mb4'
    )
    # 关闭追踪对象的修改并发送信号，这会消耗额外内存，生产环境建议关闭
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图（如果使用蓝图）或直接使用路由
    app.register_blueprint(blueprint=bp)

    # 确保表结构存在
    with app.app_context():
        db.create_all()

    return app