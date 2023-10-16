# from pathlib import Path
from datetime import timedelta, date
import time
import random
# import re
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
# from scrapy_splash import SplashRequest

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    page_max = 5
    start_date = date(2023, 11, 2)
    end_date = date(2023, 11, 4)
    days = []
    start_urls = ['https://ecm.coopculture.it/index.php']
    base_url = "https://ecm.coopculture.it/index.php?option=com_snapp&task=event.getperformancelist&format=raw&id=3793660E-5E3F-9172-2F89-016CB3FAD609&type=1&dispoonly=0&lang=it&_=1685906258655"
    result = []
    octofence_jslc = 'de315ef8e2fdf9f6cc6225f74ec98680115bade577ab62eb12d89457f5fab616'
    # allowed_domains = ['ecm.coopculture.it', 'imgur.com']

    def request(self, callback, day, page):
        url = self.base_url + '&date_req=' + str(day) + '&page=' + str(page)
        request = scrapy.Request(url=url, callback=callback, errback=self.errback_httpbin, meta={'day': day, 'page': page}, dont_filter=True)
        # request.meta={"dont_merge_cookies": True}

        # request.cookies['__cl_preferences'] = ('VGh1LCAyNiBTZXAgMjAyNCAxNjo1NjozNSBHTVQ=')
        request.cookies['octofence_jslc_fp'] = ('3392781997')
        request.cookies['39097b3b2e04683e28975acd811e725c'] = ('9deis3a3frnon405sq54ao17u2')
        request.cookies['octofence_jslc'] = self.octofence_jslc

        request.headers['User-Agent'] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        # request.headers[':authority'] = ('ecm.coopculture.it')
        # request.headers[':method'] = "GET",
        # request.headers[':path'] = "/index.php?option=com_snapp&task=event.getperformancelist&format=raw&id=3793660E-5E3F-9172-2F89-016CB3FAD609&type=1&date_req=2023-10-03&dispoonly=0&page=2&lang=it&_=1685906258655",
        # request.headers[':scheme'] = "https",
        request.headers['Accept'] = ('text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7')
        request.headers['Accept-Encoding'] = ('gzip, deflate, br')
        request.headers['Accept-Language'] = ('en-US,en;q=0.9')
        request.headers['Cache-Control'] = ('max-age=0')
        # request.headers['Cookie'] ='__cl_preferences=VGh1LCAyNiBTZXAgMjAyNCAxNjo1NjozNSBHTVQ=; octofence_jslc=5fc84ab2b4c8632205d48f21a04035a5e0a0476008f49e7ae897817821618105; octofence_jslc_fp=3392781997; 39097b3b2e04683e28975acd811e725c=fhpd1oneu0apb7prlk04dl8ooi'
        request.headers['Sec-Ch-Ua'] = ('"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"')
        request.headers['Sec-Ch-Ua-Mobile'] = ('?0')
        request.headers['Sec-Ch-Ua-Platform'] = ('"Windows"')
        request.headers['Sec-Fetch-Dest'] = 'document'
        request.headers['Sec-Fetch-Mode'] = 'navigate'
        request.headers['Sec-Fetch-Site'] = 'same-origin'
        request.headers['Sec-Fetch-User'] = ('?1')
        request.headers['Upgrade-Insecure-Requests'] = '1'
        return request
    
    def get_dates_between(self):
        return [(self.start_date + timedelta(days=i)).strftime('%F')
            for i in range((self.end_date - self.start_date).days)]
    
    def parse(self, response):
        self.days = self.get_dates_between()
        for i, day in enumerate(self.days):
            for page in range(self.page_max):
                # time.sleep(random.randint(1, 3))
                yield self.request(self.parse_item, day, page+1)

    def parse_item(self, response):
        day = str(response.meta['day'])
        page = response.meta['page']

        divList = response.css('div.perf_row')
        item = []
        for div in divList:
            item = div.xpath('//div[1]//div[1]/text()').extract()
            yield item
        while(" " in item):
            item.remove(" ")
        bFound = False
        i=0
        for r in self.result:
            if r['day'] == day:
                self.result[i]['hours'] = self.result[i]['hours'] + item
                bFound = True
            i = i+1
        if (bFound==False):
            self.result.append({'day':day, 'hours':item})

        cl = response.headers.getlist('Set-Cookie')
        if cl and len(cl)>0:
            cookie = cl[0].split(';')[0]
            print('++++++++++++++++++++++++ Set Cookie: ++++++++++++++++++++++++')
            print(cookie)
            print('++++++++++++++++++++++++ End of ++++++++++++++++++++++++')
            if cookie !='':
                self.octofence_jslc = cookie.spilt('=')[1]
        
        if len(self.result) == len(self.days) and page == self.page_max:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('++++++++++++++++++++++++ Result: ++++++++++++++++++++++++')
            print(self.result)
            print('++++++++++++++++++++++++ End of ++++++++++++++++++++++++')
        # url = response.xpath('//a[@rel="nofollow next"]/@href').extract_first()
        # if url:
        #     yield self.request(url, self.parse_item)
        # you may consider scrapy.pipelines.images.ImagesPipeline :D

    def errback_httpbin(self, failure):
        # log all failures
        print('---------- Error Current octofence_jslc: ------------')
        print(self.octofence_jslc)
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error("DNSLookupError on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError on %s", request.url)
        print('--------- Error -------------')