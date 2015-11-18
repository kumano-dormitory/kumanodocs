# -*- coding:utf-8 -*-

import pymysql
import yaml
import random
import string
import hashlib
import parse
import sys
import datetime

"""
1, mysqlのデータをまともなものに直す
2, yamlに吐く
3, db.sqlite3に追加
"""

def main():
    user = sys.argv[1]
    password = sys.argv[2]
    connection = pymysql.connect(host='localhost'
                                ,user=user
                                ,password=password
                                ,db='kumano_shiryo'
                                ,charset='utf8mb4'
                                ,cursorclass=pymysql.cursors.DictCursor)

    date_id_offset = 15 # mysqlにおけるdateをdb.sqlite3に移動するとき、db.sqlite3におけるそのdateのidは(元のid+date_id_offset)となる
    issue_id_offset = 105 # 上記と同様
    
    try:
        with connection.cursor() as cursor:
            # delete
            cursor.execute("DELETE FROM proposal where del_flg = 1")
            cursor.execute("DELETE FROM proposal where title is NULL")
            cursor.execute("DELETE FROM giziroku where block = 0")
            #cursor.execute("DELETE FROM giziroku where del_flg = 1")
            # テストデータなど
            for i in [17, 20, 27,1012,1016,]:
                cursor.execute("DELETE FROM proposal where id = %s",(i,))
            connection.commit()
            
            # update
            cursor.execute("SELECT id,title from proposal")
            res = cursor.fetchall()
            for row in res:
                if "【】" in row["title"]:
                    cursor.execute("UPDATE proposal SET title = %s where id = %s",(row["title"].replace("【】",""),row["id"]))
            connection.commit()
            
            # append deleted date
            cursor.execute("SELECT DISTINCT date from proposal where date != ALL (SELECT id from date) ORDER BY date")
            res = cursor.fetchall()
            d = datetime.date(1980,1,1)
            dt = datetime.timedelta(days=1)
            for row in res:
                cursor.execute("INSERT INTO date (id, time, proposal_locked, giziroku_locked) VALUES (%s, %s, 0, 0)",(row["date"] if row["date"] != 0 else 10,d))
                d += dt
            connection.commit()

            print("data validation success")
            
            # meeting
            sql = "SELECT id,time FROM date"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            with open("./document_system/fixtures/meeting.yaml","a") as f:
                for item in result:
                    fixture = [{
                        "model":"document_system.Meeting",
                        "pk":int(item["id"])+date_id_offset,
                        "fields": {
                            "meeting_date":str(item["time"]),
                        }
                    }]
                    yaml.dump(fixture, f, encoding='utf8', allow_unicode=True)
            
            print("successfully meeting.yaml generated")

            # issue
            issue_type_dict = {
                "周知":1,
                "再周知":1,
                "資料":1,
                "報告":1,
                "議論":2,
                "検討":2,
                "特別決議案":2,
                "議論：特別決議案":2,
                "調査":2,
                "採決":3,
                "募集":4,
                "委員募集":4,
                "意見募集":4,
                "議案":2,
                "追加資料":2,
                "案":2,
                "総括":2,
            }

            sql = "SELECT id,title,main,user,date,num from proposal"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            parsers = [
                parse.compile("{title}【{}】【{}】【{}】"),
                parse.compile("{title}【{}・{}】【{}・{}】"),
                parse.compile("{title}【{}】【{}】"),
                parse.compile("{title}【{}・{}・{}】"),
                parse.compile("{title}【{}・{}】"),
                parse.compile("{title}【{}と{}】"),
                parse.compile("{title}【{}】"),
                parse.compile("{title}〈{}〉"),
                parse.compile("{title}〈{}・{}〉"),
                parse.compile("【{}・{}】{title}"),
                parse.compile("【{}】{title}"),
                parse.compile("{title}({}・{})"),
                parse.compile("{title}({})"),
                parse.compile("{title}（{}・{}）"),
                parse.compile("{title}（{}）"),
            ]
            
            for item in result:
                parsed_item = {}
                try:
                    parser_result = None
                    for parser in parsers:
                        if parser_result == None:
                            parser_result = parser.parse(item["title"])
                        else :
                            break
                    if parser_result == None:
                        raise NameError('New Pattern')
                    else:
                        parsed_item["fixed"] = parser_result.fixed
                        parsed_item["title"] = parser_result["title"]
                except:
                    if item["title"] == "今後の日程":
                        parsed_item["title"] = item["title"]
                        parsed_item["fixed"] = ("周知",)
                    elif "方針" in item["title"] or "総括" in item["title"] or "決算" in item["title"]:
                        parsed_item["title"] = item["title"].replace("【総括】","").replace("[総括]","")
                        parsed_item["fixed"] = ("議論",)
                    elif "お知らせ" in item["title"]:
                        parsed_item["title"] = item["title"]
                        parsed_item["fixed"] = ("周知",)
                    else:
                        # めんどくさいので、どのパターンにも当てはまらない議案は、タイトルはそのままで、issue_typeは【周知・議論】とする
                        parsed_item["title"] = item["title"].replace("【】","")
                        parsed_item["fixed"] = ["周知","議論"]
                        
                issue_types = list(set([issue_type_dict[issue_type] for issue_type in parsed_item["fixed"]]))
                fixture = [{
                    "model":"document_system.Issue",
                    "pk":int(item["id"]) + issue_id_offset,
                    "fields":{
                        "meeting":item["date"] + date_id_offset if item["date"] + date_id_offset != 15 else 25,
                        "title"  :parsed_item["title"],
                        "issue_types":issue_types,
                        "author" :item["user"],
                        "text"   :item["main"],
                        "hashed_password":"",
                        "issue_order":item["num"] if item["num"] else -1,
                    }
                }]
                with open("./document_system/fixtures/issue.yaml","a") as f:
                    yaml.dump(fixture, f, encoding='utf8', allow_unicode=True)
            
            print("successfully issue.yaml generated")

            # note
            sql = "SELECT DISTINCT main,block,number,date FROM giziroku"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            for item in result:
                # item["number"] が整数である場合
                if parse.parse("{:d}",item["number"]):
                    num = item["number"]
                # item["number"] が始まりに整数を含む場合(ex: "11】ほげほげ A101鈴木"など)
                elif parse.search("{:d}】",item["number"]):
                    num = parse.search("{:d}】",item["number"])[0]
                # item["number"]にissue_orderの情報を含まない場合(ex: "追加資料２"など)
                else :
                    num = None
                if num != None:
                    cursor.execute("SELECT id FROM proposal WHERE date = %s AND num = %s",(item["date"],num))
                    res = cursor.fetchone()
                    if res != None:
                        fixture = [{
                            "model":"document_system.Note",
                            "fields":{
                                "issue":int(res["id"]) + 105,
                                "block":item["block"],
                                "text":item["main"],
                                "hashed_password":"",
                            },
                        }]
                        print("issue:%s, block:%s" % (res["id"],item["block"]))
                        with open("./document_system/fixtures/note.yaml","a") as f:
                            yaml.dump(fixture,f,encoding='utf8',allow_unicode=True)

            print("successfully note.yaml generated")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
