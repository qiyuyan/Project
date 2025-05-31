def get_doc_data(doc_id, doc_type, params):
    """
    根据doc_id和doc_type查询对应的数据库表
    :param doc_id: 单据ID
    :param doc_type: 单据类型
    :param params: 参数
    :return: params = {
        "nickname": user.nickname,
        "username": user.username,
        "data":{"once":{}, "repeat":[{key:value}, {key:value}]},
    }
    """
    pass
    # doc_id = int(doc_id)
    # if doc_type == "pi":
    #     # 查询不重复数据
    #     pi = Order.query.filter_by(id=doc_id).first()
    #     if not pi:
    #         abort(404, description="文件不存在")
    #     # 查询重复数据
    #     customer = Customer.query.filter_by(id=pi.id).all()
    #     if not customer:
    #         pass
    return params
