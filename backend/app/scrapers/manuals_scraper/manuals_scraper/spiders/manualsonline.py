import scrapy
from manuals_scraper.items import ManualItem

class ManualsonlineSpider(scrapy.Spider):
    name = "manualsonline"
    allowed_domains = ["kitchen.manualsonline.com", "pdfstore-manualsonline.prod.a.ki"]

    start_urls = [
        "https://kitchen.manualsonline.com/manuals/mfg/aeg/30006ff.html"
    ]

    def parse(self, response):
        # Extract model, lang, title text blocks
        text_blocks = response.css(".pdf-page .tt::text").getall()

        model = text_blocks[0].strip() if len(text_blocks) > 0 else None
        language = text_blocks[1].strip() if len(text_blocks) > 1 else None
        
        # Extract title (join multiple spans)
        title = "".join(
            response.css(".pdf-page .tt:nth-child(3) ::text").getall()
        ).strip()

        # Extract PDF link
        pdf_link = response.css(".pdf-icon::attr(href)").get()
        pdf_link = response.urljoin(pdf_link) if pdf_link else None
        
        item = ManualItem()
        item["url"] = response.url
        item["model"] = model
        item["language"] = language
        item["title"] = title
        item["file_urls"] = [pdf_link]

        yield item

