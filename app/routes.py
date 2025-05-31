from flask import request, session, render_template, redirect, Blueprint, url_for, jsonify, abort
from app.database import *
from app.business import *

bp = Blueprint('routes', __name__)

USER = {"id": 0}

# 登录页面
@bp.route('/login')
def login_page():
    params = {}
    return render_template('login.html', **params)  # 新增登录页面路由

# 用户登录接口
@bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # 修改这里，直接比较明文密码
        session['user_id'] = user.id
        return redirect('/index')  # 登录成功重定向到 index 页面
    params = {
        "error": "Invalid credentials",
    }
    return render_template('login.html', **params)  # 登录失败返回登录页并显示错误

# 用户注销接口
@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')  # 注销后重定向到登录页

# 首页
@bp.route('/')
def default_route():
    return redirect('/index')

@bp.route('/index')
def index():
    params = _if_login(required=True)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    return render_template('index.html', **params)  # 已登录显示 index 页面

# 单据管理 > 订单数据录入
@bp.route('/order-data-input')
def order_data_input():
    params = _if_login(required=True)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    return render_template('order-data-input.html', **params)  # 已登录显示 index 页面

@bp.route('/translate')
def translate():
    params = _if_login(required=False)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    return render_template('translate.html', **params)  # 已登录显示 index 页面

@bp.route('/translate_submit', methods=['POST'])
def translate_submit():
    params = _if_login(required=False)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    direction = request.form.get('direction')
    text = request.form.get('from_sentence')
    params["translate_result"] = translater.translate(direction=direction, text=text)
    return render_template('translate.html', **params)  # 已登录显示 index 页面

@bp.route('/translate_new_word', methods=['POST'])
def translate_add_word():
    # 处理表单数据
    new_word = request.form.get('new_word')
    translate_add_new_word(new_word=new_word)
    # 重定向到指定页面
    return redirect(url_for('routes.translate'))

@bp.route('/data-submit', methods=['POST'])
def handle_order_input():
    # 处理表单数据
    form_data = request.form.to_dict()
    process_order_submission(form_data=form_data)
    # 重定向到指定页面
    return redirect(url_for('routes.order-related-doc'))

@bp.route('/order-related-doc')
def order_related_doc():
    params = _if_login(required=True)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    return render_template('order-related-doc.html', **params)  # 已登录显示 index 页面

@bp.route('/get-table-data' ,methods=['POST'])
def get_table_data():
    try:
        # Get the parameters sent by the frontend
        data = request.get_json()
        api = data.get('api')
        response = return_table_data(api=api)
        return jsonify(response)
    except Exception as e:
        redirect("/500")

@bp.route('/print_a4')
def print_a4():
    params = _if_login(required=True)
    if not params:
        params = {"nickname": "未注册 Not Registered", "username": "non-registered"}
        return render_template('403.html', **params)  # 未登录重定向到登录页
    # 获取查询参数
    doc_id = request.args.get('doc_id')
    doc_type = request.args.get('doc_type')
    # 验证必要参数是否存在
    if not doc_id or not doc_type:
        abort(400, description="缺少必要参数(doc_id或doc_type)")
    url, params = _print_correct(doc_id=doc_id, doc_type=doc_type, params=params)
    return render_template(url, **params)

@bp.route('/500')
def error_500():
    return render_template('500.html')

# Define a global 404 error handler
@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def _if_login(required:bool = True):
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if not user_id:
        if required:
            print("未登录重定向到登录页")
            return None  # 未登录重定向到登录页
        else:
            params = {
                "nickname": "未注册 Not Registered",
                "username": "non-registered"
            }
    else:
        params = {
            "nickname": user.nickname,
            "username": user.username
        }
    return params

def _print_correct(doc_id, doc_type, params):
    """
    打印正确的模板，URL为打印类型对应的模板名称，例如：
    URL = {"PI":'print_pi.html'}
    :param doc_id: 文件ID
    :param doc_type: 文件类型
    :param params: 传参
    :return: 渲染模板
    """
    # 检查doc_id和doc_type是否存在
    URL = {"PI":'print_pi.html', "Commercial Invoice":"print_ci.html","Test Report":"print_tr.html","PL":"print_pl.html","Contract": "print_ct.html",}
    params = get_doc_data(doc_id=doc_id, doc_type=doc_type, params=params)
    return URL[doc_type], params