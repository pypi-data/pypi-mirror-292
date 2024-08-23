"""
处理网页数据
"""

from parsel import Selector
from .settings import NON_BREAKING_ELEMENTS, BLOCK_TAGS

__all__ = [
    "bs_get_text",
    "bs_get_text2",
    "bs_html",
    "html2md",
    "Selector",
]


def bs_html(
    markup: str = "",
    features: str = "lxml",
    builder=None,
    parse_only=None,
    from_encoding=None,
    exclude_encodings=None,
    element_classes=None,
):
    """
    使用 BeautifulSoup 解析网页

    markup: 网页源码
    features: 默认使用 lxml 解析
    """
    from bs4 import BeautifulSoup

    return BeautifulSoup(
        markup=markup,
        features=features,
        builder=builder,
        parse_only=parse_only,
        from_encoding=from_encoding,
        exclude_encodings=exclude_encodings,
        element_classes=element_classes,
    )


def bs_get_text(
    soup,
    strip_tags: list = ["style", "script"],
) -> str:
    """
    ## 基于 BeautifulSoup 提取网页文本v1

    不在非块级标签 NON_BREAKING_ELEMENTS 中的才换行

    soup: BeautifulSoup 对象或html文本
    strip_tags: 需要删除的节点
    """
    import re

    if isinstance(soup, str):
        soup = bs_html(soup)
    if strip_tags:
        for node in soup(strip_tags):
            node.extract()
    for node in soup.find_all():
        if node.name not in NON_BREAKING_ELEMENTS:
            node.append("\n") if node.name == "br" else node.append("\n\n")
    return re.sub(
        "\n\n+",
        "\n\n",
        soup.get_text().strip().replace("\xa0", " ").replace("\u3000", " "),
    )


def bs_get_text2(
    soup,
    strip_tags: list = ["style", "script"],
):
    """
    ## 基于 BeautifulSoup 提取网页文本v2

    在块级标签 BLOCK_TAGS 中的才换行

    soup: BeautifulSoup 对象或html文本
    """
    from bs4 import element
    import re

    if isinstance(soup, str):
        soup = bs_html(soup)
    if strip_tags:
        for node in soup(strip_tags):
            node.extract()

    def traverse(node):
        if isinstance(node, element.NavigableString):
            if node.strip():
                yield node.strip()
        else:
            if node.name in BLOCK_TAGS:
                yield "\n"
            for child in node.children:
                yield from traverse(child)
            if node.name in BLOCK_TAGS:
                yield "\n"

    return re.sub(
        "\n\n+",
        "\n\n",
        "".join(traverse(soup)).strip().replace("\xa0", " ").replace("\u3000", " "),
    )


def html2md(
    string: str,
    base_url: str = "",
    bodywidth: int = 0,
    ignore_links: bool = True,
    ignore_images: bool = True,
    ignore_tables: bool = True,
    ignore_emphasis: bool = True,
    ignore_mailto_links: bool = True,
) -> str:
    """
    ## HTML 转 Markdown

    string: HTML
    base_url: 图片链接的基础 URL
    bodywidth: 正文宽度, 默认为 0 表示不限制宽度
    ignore_links: 是否忽略链接, 默认为 True
    ignore_images: 是否忽略图像, 默认为 True
    ignore_tables: 是否忽略表格, 默认为 True
    ignore_emphasis: 是否忽略强调, 默认为 True
    ignore_mailto_links: 是否忽略mailto链接, 默认为 True
    """
    import html2text
    import re

    converter = html2text.HTML2Text(baseurl=base_url, bodywidth=bodywidth)
    converter.ignore_links = ignore_links  # 忽略链接
    converter.ignore_images = ignore_images  # 忽略图像
    converter.ignore_tables = ignore_tables  # 忽略表格
    converter.ignore_emphasis = ignore_emphasis  # 忽略强调
    converter.ignore_mailto_links = ignore_mailto_links  # 忽略mailto链接
    if ignore_tables:
        string = re.sub("<table.*?</table>", "", string)
    content = converter.handle(string)
    return content
