# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BokeyuanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    article_link = scrapy.Field()
    link_id = scrapy.Field()
    re_num = scrapy.Field()
    industry = scrapy.Field()
    author = scrapy.Field()
    date_pub = scrapy.Field()
    comment_num = scrapy.Field()
    read_num = scrapy.Field()
    images = scrapy.Field()
    img_url = scrapy.Field()
    post = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_sql(self):
        sql = 'insert into cnblogs(title,article_link,link_id,re_num,industry,author,date_pub,comment_num,read_num,img_url,post,crawl_time) ' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update link_id=values(link_id)'
        data = (self['title'],self["article_link"],self["link_id"],self["re_num"],self["industry"],self["author"],self["date_pub"],self["comment_num"],self["read_num"],self["img_url"],self["post"],self["crawl_time"])

        return sql,data



