# -*- coding: utf-8 -*-
import scrapy
import re,random
from bokeyuan.items import BokeyuanItem
from datetime import datetime
from w3lib.html import remove_tags
from urllib import request
import hashlib


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    # start_urls = ['http://cnblogs.com/']
    # 只针对当前爬虫文件生效的settings配置
    custom_settings = {
        'RETRY_TIMES': 2,
        'COOKIES_ENABLED': False,
        # 'DOWNLOAD_DELAY': random.random() * 6,
        'CONCURRENT_REQUESTS': 1,
        'DEFAULT_REQUEST_HEADERS': {
            "Host": "www.cnblogs.com",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8",
        },
        # 数据存储管道
        'ITEM_PIPELINES': {
            'bokeyuan.pipelines.BokeyuanPipeline': 2,
            'bokeyuan.pipelines.CnblogImagePipeline':1
        },
        'DOWNLOADER_MIDDLEWARES': {
            'bokeyuan.mymiddleware.ImgDownload': 300,
        }
    }
    # 构建首次请求,获取所有分类链接
    def start_requests(self):
        base_url = 'https://www.cnblogs.com/aggsite/SubCategories'
        body = '{cateIds: "108698,2,108701,108703,108704,108705,108709,108712,108724,4"}'
        yield scrapy.Request(base_url,method='POST',body=body,callback=self.parse)

    def parse(self, response):
        # 获取分类链接列表
        cate_list = response.xpath('//a/@href').extract()
        for url in cate_list:
            # 拼接完整路由
            link = request.urljoin(response.url,url)
            yield scrapy.Request(link,callback=self.parse_first,meta={'url':link})

    # 解析所有分类第一页
    def parse_first(self,response):
        # 完整分页路由
        url = response.meta['url']  + '%d'
        # 获取最大页数
        try:
            max_page = int(response.xpath('//div[@class="pager"]/a/text()').extract()[-2])
        except Exception as e:
            max_page = 1
        for i in range(1,max_page):
            fullurl = url % i
            yield scrapy.Request(fullurl,callback=self.parse_list)
    # 解析列表页
    def parse_list(self,response):
        # 定位文章列表
        article_list = response.xpath('//div[@class="post_item"]')
        for article in article_list:
            item = BokeyuanItem()
            # 文章标题
            title = article.css('h3 a::text').extract_first()
            # 文章详情连接
            article_link = article.css('h3 a::attr(href)').extract_first()
            # 对链接进行MD5加密，作为数据表唯一索引
            # url MD5加密
            m = hashlib.md5()
            m.update(article_link.encode(encoding='utf-8'))
            link_id = m.hexdigest()
            # 推荐数
            re_num = article.css('span.diggnum::text').extract_first()
            # 文章摘要
            industry = article.css('p.post_item_summary::text').extract_first()
            # 作者
            author = article.css('div.post_item_foot a::text').extract_first()
            # 发布时间
            date_pub = article.css('div.post_item_foot::text').extract()[-1]
            date_pub = date_pub.strip('\r\n ').strip('发布于 ')
            # 评论数
            comment_num = article.css('span.article_comment a::text').extract_first()
            comment_num = self.get_num(comment_num)
            # 阅读数
            read_num = article.css('span.article_view a::text').extract_first()
            read_num = self.get_num(read_num)

            item['title'] = title
            item['article_link'] = article_link
            item['link_id'] = link_id
            item['re_num'] = re_num
            item['author'] = author
            item['industry'] = industry
            item['date_pub'] = date_pub
            item['comment_num'] = comment_num
            item['read_num'] = read_num
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d')

            yield scrapy.Request(article_link,callback=self.parse_detail,meta={'data':item})
    # 解析详情页
    def parse_detail(self,response):
        item = response.meta['data']
        content = response.xpath('//div[@id="cnblogs_post_body"]').extract_first()
        # 获取图片地址
        img_pat = re.compile(r'<img src="(http.*?)" alt',re.S)   # re.S表示正则表达式能识别换行
        img_list = img_pat.findall(content)
        img_url = ''
        if img_list is not None:
            img_url = ','.join(img_list)
        # 去掉博文中的标签
        post = remove_tags(content).strip()
        # print(img_list)
        item['img_url'] = img_url
        item['images'] = img_list
        item['post'] = post
        yield item

    # 获取数字
    def get_num(self,value):
        num_pat = re.compile('\d+')
        res = num_pat.search(value)
        if res is not None:
            return int(res.group(0))
        else:
            return 0

