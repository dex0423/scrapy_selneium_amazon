# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi



class AmazonTestPipeline:
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            port=settings["MYSQL_PORT"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
            cp_reconnect=True,
        )
        # 注意调用的是adb.ConnectionPool()、而不是adb.Connection()
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)


    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步插入
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        #  执行具体的插入

        # insert_sql, params = item.get_insert_sql()
        # cursor.execute(insert_sql, params)

        insert_sql = """
            insert into scrapy_selenium(good_name, good_url, price, star_level, answers)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item["good_name"], item["good_url"], item["price"], item["star_level"], item["answers"]))
        print(f"[INSERT SQL] : {insert_sql}")


