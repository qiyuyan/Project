import os
import pymysql
import time
import re


def translate_add_new_word(new_word:str = None):
    print(new_word)
    if not new_word or not new_word.strip():
        return  # 如果 new_word 为空或 None，直接返回
        # 构建文件路径
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_dir, 'static', 'new_words.txt')

    try:
        # 以追加模式打开文件，另起一行写入 new_word
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(new_word + '\n')
    except Exception as e:
        print(f"写入文件时出错: {e}")


class Translator(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.lang = {"en_to_cn": [], "cn_to_en": []}
        self.update_time = 12  # 12小时
        self._connect_db()
        self.update_list()
        self.last_update_day = -1  # 记录上次更新的日期（避免同一天重复更新）

    def _connect_db(self):
        DB_CONFIG = {
            'host': "rm-bp153zvpu95372h5f1o.mysql.rds.aliyuncs.com",  # 数据库地址
            "port": 3306,
            'user': "ian_001",  # 用户名
            'password': "C7#Ado0b9c9s",  # 密码
            'database': "customs",  # 数据库名
            'charset': 'utf8mb4'
        }
        self.conn = pymysql.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()

    def update_list(self):
        self.cur.execute("SELECT cn, en, direction FROM translation")
        tran_list = self.cur.fetchall()
        tran_list = sorted(tran_list, key=lambda x: len(x[0]), reverse=True)
        self.lang["en_to_cn"] = [[trans[1], trans[0], trans[2]] for trans in tran_list if trans[2] != "cn_to_en"]
        self.lang["en_to_cn"] = sorted(self.lang["en_to_cn"], key=lambda x: len(x[0]), reverse=True)
        self.lang["cn_to_en"] = [trans for trans in tran_list if trans[2] != "en_to_cn"]

    def translate(self, text: str, direction: str):
        now = time.localtime()
        if now.tm_mday != self.last_update_day:
            self.update_list()
            self.last_update_day = now.tm_mday  # 标记当天已更新

        REPLACEMENTS = [
            (r" {2,}", " "),  # 多个空格替换为单个空格
            (r"\s*,\s*", ", "),  # 逗号左右空格只保留右侧1个
            (r"\s*\(\s*", " ("),  # 空格 + 左括号替换为左括号
            (r"\s*\)\s*", ") "),  # 右括号 + 空格替换为右括号
            (r"\s*\)\s*,", "),"),  # 右括号 + 空格替换为右括号
            (r"\s*≥\s*", "≥"),  # 空格 + ≥ 替换为 ≥
            (r"\s*≤\s*", "≤"),  # 空格 + ≤ 替换为 ≤
            (r"%,\s*\n", "%\n"),  # %, + 换行替换为 %\n
            (r"\s*、\s*", "、"),  # 顿号 + 空格替换为顿号
            (r"\s*\n\s*", "\n"),  # 换行 + 空格替换为换行
            (r'([a-zA-Z])(\d+(\.\d+)?%)', r'\1 \2'),
            (r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2'),  # 删除中文之间空格
            (r" %", "%"),
            (r"[-]{3,}", ""),
            (r"个", ""),
        ]
        if text and self.lang[direction]:
            for _pairs in self.lang[direction]:
                text = re.sub(re.escape(_pairs[0]), " " + _pairs[1] + "", text, flags=re.IGNORECASE)
            for i in range(20):
                for pattern, replacement in REPLACEMENTS:
                    text = re.sub(pattern, replacement, text)
                    text = text.strip()
        return text

translater = Translator()
