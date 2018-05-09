# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import scrapy

class BokeyuanPipeline(object):
    def __init__(self):
        try:
            self.conn = pymysql.connect('127.0.0.1','root','123456','myspiderproject',charset='utf8')
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
    def process_item(self,item,spider):
        sql,data = item.get_sql()
        try:
            self.cursor.execute(sql,data)
            self.conn.commit()
        except Exception as e:
            print('执行添加操作失败')
            self.conn.rollback()
        return item
    def close_spider(self,spider):
        self.cursor.close()
        self.conn.close()

from scrapy.pipelines.images import ImagesPipeline
class CnblogImagePipeline(ImagesPipeline):
    def item_completed(self,result,item,info):
        print(result)
        return item