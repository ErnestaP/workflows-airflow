import xml.etree.ElementTree as ET

from common.parsing.parser import IParser
from common.parsing.xml_extractors import CustomExtractor
from structlog import get_logger


class IOPParser(IParser):
    article_type_mapping = {
        "research-article": "article",
        "corrected-article": "article",
        "original-article": "article",
        "correction": "corrigendum",
        "addendum": "addendum",
        "editorial": "editorial",
    }

    def __init__(self) -> None:
        self.dois = None
        self.logger = get_logger().bind(class_name=type(self).__name__)
        extractors = [
            CustomExtractor(
                destination="dois",
                extraction_function=self._get_dois,
                required=True,
            ),
            CustomExtractor(
                destination="journal_doctype",
                extraction_function=self._get_journal_doctype,
            ),
        ]
        super().__init__(extractors)

    def _get_dois(self, article: ET.Element):
        node = article.find("front/article-meta/article-id/[@pub-id-type='doi']")
        if node is None:
            return None
        dois = node.text
        if dois:
            self.logger.msg("Parsing dois for article", dois=dois)
            self.dois = dois
            return [dois]
        return

    def _get_journal_doctype(self, article: ET.Element):
        node = article.find(".")
        value = node.get("article-type")
        if not value:
            self.logger.error("Article-type is not found in XML", doi=self.dois)
            return None
        try:
            return self.article_type_mapping[value]
        except KeyError:
            self.logger.error(
                "Unmapped article type", doi=self.dois, article_type=value
            )
        except Exception:
            self.logger.error("Unknown error", doi=self.dois)
