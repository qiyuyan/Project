import pandas as pd
from io import StringIO
from app.database import db, Order, Customer, Batch, Container, Formula, SKU, Loading
from app.tool import gen_batch_code, gen_random_nutrition


def process_order_submission(form_data):
    """
    处理订单提交
    :param form_data: 表单数据
    :return: 处理结果
    """
    # 1，处理order数据，对应数据库中的order表和customer表
    data = form_data["order"]
    if data.strip():
        df = pd.read_csv(StringIO(data), sep='\t')  # 按制表符分隔
        _process_order(df)

    # 2，处理product数据，对应数据库中formula表和sku表
    data = form_data["product"]
    if data.strip():
        df = pd.read_csv(StringIO(data), sep='\t')  # 按制表符分隔
        _process_product(df)

    # 3，处理container数据，对应数据库中container表
    data = form_data["container"]
    if data.strip():
        df = pd.read_csv(StringIO(data), sep='\t')  # 按制表符分隔
        _process_container(df)

    # 4，处理loading数据，对应数据库中loading表和batch表
    data = form_data["loading"]
    if data.strip():
        df = pd.read_csv(StringIO(data), sep='\t')  # 按制表符分隔
        _process_loading(df)


def _process_order(df: pd.DataFrame) -> None:
    """
    处理订单数据
    :param df: 订单数据
    """
    for _, row in df.iterrows():
        success = 0
        failures = []
        try:
            # 处理Order数据
            order = Order.query.filter_by(order_number=row['order_number']).first()
            order_data = {
                'date': pd.to_datetime(row['date']).date(),
                'factory': row['factory'],
                'deal_term': row['deal_term'],
                'currency': row['currency'].split('-')[0].strip(),
                'from_location': row['from'].split('-')[0].strip(),
                'to_location': row['to'].split('-')[0].strip(),
                'customer_code': row['customer_code']
            }

            if order:
                for key, value in order_data.items():
                    setattr(order, key, value)
            else:
                order = Order(
                    order_number=row['order_number'],
                    **order_data
                )
                db.session.add(order)

            # 处理Customer数据（如果customer_name存在且非空）
            if pd.notna(row.get('customer_name')) and str(row['customer_name']).strip():
                customer = Customer.query.filter_by(customer_code=row['customer_code']).first()
                customer_data = {
                    'customer_name': row['customer_name'],
                    'tax_id': row.get('tax_id', ''),
                    'customer_address': row.get('customer_address', ''),
                    'customer_email': row.get('customer_email', ''),
                    'contact': row.get('contact', ''),
                    'phone': row.get('phone', '')
                }

                if customer:
                    for key, value in customer_data.items():
                        setattr(customer, key, value)
                else:
                    customer = Customer(
                        customer_code=row['customer_code'],
                        **customer_data
                    )
                    db.session.add(customer)

            db.session.commit()
            success += 1
        except Exception as e:
            db.session.rollback()
            failures.append({
                'row': _ + 2,  # Excel行号（从1开始，+1因为跳过标题）
                'error': str(e),
                'order_number': row.get('order_number', '')
            })

    return {'total': len(df),'success': success,'failures': failures}

def _process_product(df: pd.DataFrame) -> None:
    """
    处理产品数据
    :param df: 产品数据
    """
    for _, row in df.iterrows():
        success = 0
        failures = []
        try:
            # 处理SKU数据
            sku = SKU.query.filter_by(sku_id=row['sku_id']).first()
            sku_data = {
                'size': row['size'],
                'box_qty': row['box_qty'],
                'cbm': row['cbm'],
                'gross_weight': row['gross_weight'],
                'from_location': row['from'].split('-')[0].strip(),
                'unit_price': row['unit_price']
            }
            for key in ["box_qty", "cbm", "gross_weight", "unit_price"]:
                try:
                    sku_data[key] = float(sku_data[key])
                except ValueError:
                    sku_data[key] = 0

            if sku:
                for key, value in sku_data.items():
                    setattr(sku, key, value)
            else:
                sku = SKU(
                    sku_id=row['sku_id'],
                    **sku_data
                )
                db.session.add(sku)

            # 处理Formula数据（如果name_en存在且非空）
            row["formula_code"] = row['sku_id'][:row['sku_id'].rfind('-')]
            if pd.notna(row.get('name_en')) and str(row['name_en']).strip():
                formula = Formula.query.filter_by(formula_code=row['formula_code']).first()
                formula_data = {
                    'name_en': row['name_en'],
                    'name_cn': row.get('name_cn'),
                    'pet': row.get('pet'),
                    'tech': row.get('tech'),
                    'brand': row.get('brand'),
                    'formula': row.get('phone'),
                    'protein_design': row.get('protein'),
                    'fat_design': row.get('fat'),
                    'fiber_design': row.get('fiber'),
                    'ash_design': row.get('ash'),
                    'cal_design': row.get('cal'),
                    'phos_design': row.get('phos'),
                    'moisture_design': row.get('moisture'),
                }
                try:
                    for key in ["protein_design", "fat_design", "fiber_design", "ash_design", "cal_design", "phos_design", "moisture_design"]:
                        sku_data[key] = float(sku_data[key])
                except ValueError:
                    pass

                if formula:
                    for key, value in formula_data.items():
                        setattr(formula, key, value)
                else:
                    formula = Formula(
                        formula_code=row['formula_code'],
                        **formula_data
                    )
                    db.session.add(formula)

            db.session.commit()
            success += 1
        except Exception as e:
            db.session.rollback()
            failures.append({
                'row': _ + 2,  # Excel行号（从1开始，+1因为跳过标题）
                'error': str(e),
                'order_number': row.get('order_number', '')
            })

    return {'total': len(df),'success': success,'failures': failures}

def _process_container(df: pd.DataFrame) -> None:
    """
    处理货柜数据
    :param df: 货柜数据
    """
    for _, row in df.iterrows():
        success = 0
        failures = []
        try:
            # 处理container数据
            container = Container.query.filter_by(container_id=row['container_id']).first()
            container_data = {
                'type': row['type'],
                'bl_number': row['bl_number'],
                'cbm': row['cbm'],
                'container_code': row['container_code'],
                'seal': row['seal'],
                'sub_bl_number': row['sub_bl_number'],
                'comment': row['comment'],
            }

            if container:
                for key, value in container_data.items():
                    setattr(container, key, value)
            else:
                container = Container(
                    container_id=row['container_id'],
                    **container_data
                )
                db.session.add(container)

            db.session.commit()
            success += 1
        except Exception as e:
            db.session.rollback()
            failures.append({
                'row': _ + 2,  # Excel行号（从1开始，+1因为跳过标题）
                'error': str(e),
                'order_number': row.get('order_number', '')
            })

    return {'total': len(df),'success': success,'failures': failures}

def _process_loading(df: pd.DataFrame) -> None:
    container_count = {}
    """
    处理货柜数据
    :param df: 货柜数据
    """
    for _, row in df.iterrows():
        success = 0
        failures = []
        try:
            # 处理loading数据
            loading_data = {
                'container_id': row['container_id'],
                'sku_id': row['sku_id'],
                'loading_boxes': row['loading_boxes'],
            }


            for key in ["loading_boxes"]:
                try:
                    loading_data[key] = float(loading_data[key])
                except ValueError:
                    loading_data[key] = 0

            if row['container_id'] not in container_count.keys():
                container_count[row['container_id']] = 0
                Loading.query.filter_by(container_id=row['container_id']).delete()
                db.session.commit()

            loading = Loading(
                **loading_data
            )
            db.session.add(loading)

            # 处理batch数据
            row["formula_code"] = row['sku_id'][:row['sku_id'].rfind('-')]
            row["batch_id"] = gen_batch_code(row['formula_code'], row['production_date'])
            formula = Formula.query.filter_by(formula_code=row['formula_code']).first()
            designed_dict = {
                "protein": formula.protein_design,
                "fat": formula.fat_design,
                "fiber": formula.fiber_design,
                "ash": formula.ash_design,
                "cal": formula.cal_design,
                "phos": formula.phos_design,
                "moisture": formula.moisture_design,
            }

            batch_data = gen_random_nutrition(tech=formula.tech, designed_dict=designed_dict)
            batch_data["production_date"] = row['production_date']
            batch_data["formula_code"] = row['formula_code']

            for key in ["protein", "fat", "fiber", "ash", "cal", "phos", "moisture"]:
                try:
                    batch_data[key] = float(batch_data[key])
                except ValueError:
                    batch_data[key] = 0

            batch = Batch.query.filter_by(batch_id=row['batch_id']).first()
            if not batch:
                batch = Batch(
                    batch_id=row['batch_id'],
                    **batch_data
                )
                db.session.add(batch)

            db.session.commit()
            success += 1
        except Exception as e:
            db.session.rollback()
            failures.append({
                'row': _ + 2,  # Excel行号（从1开始，+1因为跳过标题）
                'error': str(e),
                'order_number': row.get('order_number', '')
            })

    return {'total': len(df),'success': success,'failures': failures}
