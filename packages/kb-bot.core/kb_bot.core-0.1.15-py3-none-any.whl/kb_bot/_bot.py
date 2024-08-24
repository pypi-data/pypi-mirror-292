import time

from scraper import WebScraper
from db import TiDBProvider
from chunkers import SemanticChunker
from embedding import OpenAIEmbedClient

import dotenv
dotenv.load_dotenv()

tidb = TiDBProvider()

tidb.connect()

embed_client = OpenAIEmbedClient(
    api_key="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"
)

scraper = WebScraper(
    urls=["https://www.pingcap.com/blog/"],
    follow_links=True,
    restrict_navigation_css=".tmpl-archive.tmpl-archive-blog",
    restrict_css=".tmpl-single-post__content",
    ignore_css=".tmpl-archive-sidebar",
    chunker=SemanticChunker(),
    db_provider=tidb,
    group="new-user-id",
    embedding_client=embed_client
)

scraper.crawl()

time.sleep(60)