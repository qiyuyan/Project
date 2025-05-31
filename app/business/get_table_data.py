from app.database import *


def return_table_data(api):
    response = {
        "code": 200,
        "message": "Success",
        "data": [],
    }
    _random = ["PI", "Commercial Invoice","Test Report","PL","Contract"]
    if api == "order-related-doc":
        try:
            # 执行查询
            results = db.session.query(
                Document.document_id,
                Document.document_type,
                Document.create_date,
                Customer.customer_name,
                Document.order_id
            ).join(
                Customer, Document.customer == Customer.customer_code
            ).outerjoin(
                Order, Document.order_id == Order.order_number
            ).all()

            # 格式化数据为前端需要的数组格式
            for row in results:
                response["data"].append([
                    row.document_id,
                    row.document_type,
                    row.create_date.strftime('%Y-%m-%d') if row.create_date else '',
                    row.customer_name,
                    row.order_id
                ])

        except Exception as e:
            response = {
                "code": 500,
                "message": str(e),
                "data": []
            }
        print(response["data"])
    else:
        response["code"] = 400
        response["message"] = "Invalid API"
    return response