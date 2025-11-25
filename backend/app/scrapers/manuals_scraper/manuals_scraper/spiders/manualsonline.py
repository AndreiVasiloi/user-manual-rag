import scrapy
from manuals_scraper.items import ManualItem


class ManualsonlineSpider(scrapy.Spider):
    name = "manualsonline"
    allowed_domains = [
        "manualsonline.com",
        "kitchen.manualsonline.com",
        "fitness.manualsonline.com",
        "pdfstore-manualsonline.prod.a.ki"
    ]

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("Missing required argument: start_url")
        self.start_urls = [start_url]

    def parse(self, response):

        # The PDF icon always has the link
        pdf_link = response.css(".pdf-icon::attr(href)").get()
        pdf_link = response.urljoin(pdf_link) if pdf_link else None

        # Model and metadata are optional → not important for pipeline
        text_blocks = response.css(".pdf-page .tt::text").getall()
        model = text_blocks[0].strip() if len(text_blocks) else None
        language = text_blocks[1].strip() if len(text_blocks) > 1 else None

        item = ManualItem()
        item["url"] = response.url
        item["model"] = model
        item["language"] = language
        item["title"] = response.css("title::text").get(default="").strip()
        item["file_urls"] = [pdf_link] if pdf_link else []

        yield item
