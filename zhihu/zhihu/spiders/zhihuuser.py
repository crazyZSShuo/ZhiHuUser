# -*- coding: utf-8 -*-
import scrapy
from zhihu.items import ZhihuItem
import json

class ZhihuuserSpider(scrapy.Spider):
    name = 'zhihuuser'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    
    # 开始用户
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    start_user = 'Germey'
    user_include = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    
    # 他关注的人
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followees_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    
    
    # 他的粉丝们
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'


    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user,include=self.user_include),callback=self.parse_user)
        yield scrapy.Request(self.followees_url.format(user=self.start_user,include=self.followees_include,offset=20,limit=20),callback=self.followees_parse)
        yield  scrapy.Request(self.followers_url.format(user=self.start_user,include=self.followers_include,offset=20,limit=20),callback=self.followers_parse)
    
    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        
        yield scrapy.Request(self.followees_url.format(user=result.get('url_token'),include=self.followees_include,offset=20,limit=20),callback=self.followees_parse)
        yield scrapy.Request(self.followers_url.format(user=result.get('url_token'),include=self.followers_include,offset=20,limit=20),callback=self.followers_parse)
        
     
     # 他关注的人
    def followees_parse(self,response):
        result = json.loads(response.text)
        
        if 'data'in result.keys():
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_include),callback=self.parse_user)
        
        if 'paging'in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,callback=self.followees_parse)

    # 粉丝
    def followers_parse(self,response):
        result = json.loads(response.text)
        
        if 'data' in result.keys():
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_include),callback=self.parse_user)
                
        if 'paging' in result.keys() and result.get('paging').get('is_end')==False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,callback=self.followers_parse)