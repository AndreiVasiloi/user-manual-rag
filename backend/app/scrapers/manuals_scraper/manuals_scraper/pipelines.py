import scrapy
from scrapy.pipelines.files import FilesPipeline


class ManualPdfPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get("file_urls", []):
            yield scrapy.Request(url, meta={"item": item})

    def file_path(self, request, response=None, info=None, *, item=None):
        if item is None:
            item = request.meta["item"]

        model = item.get("model", "unknown_model").replace("/", "_")
        return f"{model}.pdf"
