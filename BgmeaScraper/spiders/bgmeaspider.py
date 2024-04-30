import scrapy
import re

class BgmeaScrapy(scrapy.Spider):
    name = 'bgmea'
    start_urls = ['https://www.bgmea.com.bd/page/member-list?page=1']

    def parse(self, response):
        # Extracting data from the current page
        for row in response.css('table tbody tr'):
            company = row.css('td:nth-child(1)::text').get().strip()
            name = row.css('td:nth-child(3)::text').get().strip()
            detail_page_url = row.css('td:nth-child(5) a::attr(href)').get()

            # Following the detail page URL to extract mobile number
            yield response.follow(detail_page_url, self.parse_detail, meta={'company': company,'name': name})

        # Extracting the current page number
        current_page = int(response.url.split('=')[-1])

        # Checking if there's a next page and generating its URL
        if current_page < 197:
            next_page_url = response.urljoin(f'?page={current_page + 1}')
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_detail(self, response):
        # Extracting name and company from meta
        company = response.meta['company']
        name = response.meta['name']
        # Extracting phone number
        phone_number = response.css('tbody tr td:nth-child(3)::text').get().strip()
        # If phone number is empty, set it to None
        if not phone_number:
            phone_number = None
        # Extracting email address
        email_address = response.css('tbody tr td:nth-child(4)::text').re(r'[\w\.-]+@[\w\.-]+')
        if email_address:
            email_address = email_address[0]
        else:
            email_address = None

        yield {
            'company': company,
            'name': name,
            'email_address': email_address,
            'phone_number': phone_number,
        }
