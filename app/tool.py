import random
import re
from datetime import datetime


def gen_batch_code(formula_code, date):
    # 1. 移除两个-之间的单个字母（如-H-）
    _processed = re.sub(r'(?<=-)[A-Za-z](?=-)', '', formula_code)

    # 2. 处理日期为YYMMDD
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_clean = date_obj.strftime('%y%m%d')  # 250106

    # 3. 生成4为随机数字
    random_number = ''.join(random.choices('0123456789', k=4))

    return _processed + date_clean + random_number

def gen_random_nutrition(tech, designed_dict):
    return designed_dict