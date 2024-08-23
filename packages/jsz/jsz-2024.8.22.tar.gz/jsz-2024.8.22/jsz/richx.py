from rich import print_json, inspect, print
from .settings import ANSI_COLOR_NAMES

__all__ = [
    "columns",
    "inspect",
    "markdown",
    "panel",
    "padding",
    "pprint",
    "print",
    "printx",
    "print_json",
    "print_exception",
    "rule",
    "status",
    "track",
]


def printx(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file=None,
    flush=True,
    style: str | None = None,
    justify: str | None = None,
    overflow: str | None = None,
    no_wrap: bool | None = None,
    emoji: bool | None = None,
    markup: bool | None = None,
    highlight: bool | None = None,
    width: int | None = None,
    height: int | None = None,
    crop: bool = True,
    soft_wrap: bool | None = None,
    new_line_start: bool = False,
):
    """
    增加随机颜色的print, 支持富文本


    sep: 分隔符
    end: 结尾
    file: 文件
    flush: 是否刷新, 默认是,不支持修改
    style: 样式
    justify: 对齐方式, 支持 "left", "center", "right", 默认是 None
    overflow: 溢出方式, 支持 "fold", "crop", "ellipsis", 默认是 None
    no_wrap: 是否不换行
    emoji: 是否支持 emoji
    markup: 是否支持 markup
    highlight: 是否支持 highlight
    width: 宽度
    height: 高度
    crop: 是否裁剪
    soft_wrap: 是否软换行
    new_line_start: 是否换行开始
    """
    import random
    from rich.console import Console

    console = Console(file=file) if file else Console()
    console.print(
        *[
            (f"[{random.choice(ANSI_COLOR_NAMES)}]{i}[/]" if isinstance(i, str) else i)
            for i in objects
        ],
        sep=sep,
        end=end,
        style=style,
        justify=justify,
        overflow=overflow,
        no_wrap=no_wrap,
        emoji=emoji,
        markup=markup,
        highlight=highlight,
        width=width,
        height=height,
        crop=crop,
        soft_wrap=soft_wrap,
        new_line_start=new_line_start,
    )


def print_exception(
    *,
    width: int = 100,
    extra_lines: int = 3,
    theme: str = None,
    word_wrap: bool = False,
    show_locals: bool = False,
    suppress=(),
    max_frames: int = 100,
) -> None:
    """
    打印更好看的异常信息

    width: 宽度
    extra_lines: 额外行数
    theme: 主题
    word_wrap: 是否换行
    show_locals: 是否显示局部变量
    suppress: 不显示的模块
    max_frames: 最大帧数
    """
    from rich.traceback import Traceback
    from rich import print

    traceback = Traceback(
        width=width,
        extra_lines=extra_lines,
        theme=theme,
        word_wrap=word_wrap,
        show_locals=show_locals,
        suppress=suppress,
        max_frames=max_frames,
    )
    print(traceback)


def panel(
    renderable,
    title=None,
    title_align="center",
    subtitle=None,
    subtitle_align="center",
    safe_box=None,
    expand=False,
    style="none",
    border_style="none",
    width=None,
    height=None,
    padding=(0, 1),
    highlight=False,
):
    """
    rich panel 封装

    renderable: 渲染对象
    title: 标题
    title_align: 标题对齐方式
    subtitle: 副标题
    safe_box: 安全盒子
    expand: 是否展开, 默认不展开
    style: 样式
    border_style: 边框样式
    width: 宽度
    height: 高度
    padding: 内边距
    highlight: 是否高亮
    """
    from rich.panel import Panel

    return Panel(
        renderable=renderable,
        title=title,
        title_align=title_align,
        subtitle=subtitle,
        subtitle_align=subtitle_align,
        safe_box=safe_box,
        expand=expand,
        style=style,
        border_style=border_style,
        width=width,
        height=height,
        padding=padding,
        highlight=highlight,
    )


def rule(
    title="",
    *,
    characters: str = "─",
    style: str = "rule.line",
    end: str = "\n",
    align: str = "center",
) -> None:
    """
    绘制一条线，可选择带有居中文本的标题。

    title (str, 可选): 在线条上方渲染的文本。默认为 ""。
    characters (str, 可选): 用于组成线条的字符。默认为 "─"。
    style (str, 可选): 线条样式。默认为 "rule.line"。
    align (str, 可选): 标题的对齐方式，可为 "left"、"center" 或 "right"。默认为 "center"。
    """
    from rich.rule import Rule
    from rich import print

    print(
        Rule(
            title=title,
            characters=characters,
            style=style,
            end=end,
            align=align,
        )
    )


def status(
    status="Working",
    *,
    spinner: str = "dots",
    spinner_style="status.spinner",
    speed: float = 1.0,
    refresh_per_second: float = 12.5,
):
    """
    显示进度，动画效果，基于 rich status 封装。

    `from rich.spinner import SPINNERS` 可以查看全部样式。

    status: 标题
    spinner: 动画类型, 支持 "aesthetic", "weather", "moon", \
                           "earth", "clock", "bouncingBar", \
                           "line", "growHorizontal", "arrow2" 等.
    spinner_style: 动画样式
    speed: 动画速度
    refresh_per_second: 每秒刷新次数

    ```py
    import jsz

    with jsz.status("下载中..."):
        jsz.sleep(3)
        jsz.print("下载完成")
    ```
    """
    from rich.status import Status

    status_renderable = Status(
        status,
        spinner=spinner,
        spinner_style=spinner_style,
        speed=speed,
        refresh_per_second=refresh_per_second,
    )
    return status_renderable


def padding(
    renderable,
    pad=(0, 0, 0, 0),
    style="none",
    expand=True,
):
    """
    给renderable对象添加padding

    renderable: 渲染对象
    pad: padding 大小
    style: padding 样式
    expand: 是否展开
    """
    from rich.padding import Padding

    return Padding(
        renderable,
        pad=pad,
        style=style,
        expand=expand,
    )


def columns(
    renderables=None,
    padding=(0, 1),
    width=None,
    expand=False,
    equal=False,
    column_first=False,
    right_to_left=False,
    align=None,
    title=None,
):
    """
    rich 自定义列

    renderables: 渲染对象
    padding: padding 大小
    width: 列宽
    expand: 是否展开
    equal: 是否相等
    column_first: 列优先
    right_to_left: 从右到左
    align: 对齐方式
    title: 标题
    """
    from rich.columns import Columns

    return Columns(
        renderables=renderables,
        padding=padding,
        width=width,
        expand=expand,
        equal=equal,
        column_first=column_first,
        right_to_left=right_to_left,
        align=align,
        title=title,
    )


def markdown(
    markup,
    code_theme="monokai",
    justify=None,
    style="none",
    hyperlinks=True,
    inline_code_lexer=None,
    inline_code_theme=None,
):
    """
    显示 Markdown 文本

    markup: Markdown 文本
    code_theme: 代码块主题
    justify: 文本对齐方式
    style: 样式
    hyperlinks: 是否启用超链接
    inline_code_lexer: 内联代码词法分析器
    inline_code_theme: 内联代码主题
    """
    from rich.markdown import Markdown

    return Markdown(
        markup=markup,
        code_theme=code_theme,
        justify=justify,
        style=style,
        hyperlinks=hyperlinks,
        inline_code_lexer=inline_code_lexer,
        inline_code_theme=inline_code_theme,
    )


def pprint(
    obj,
    console=None,
    indent_guides: bool = True,
    max_length: int | None = None,
    max_string: int | None = None,
    max_depth: int | None = None,
    expand_all: bool = False,
):
    """
    rich 美化打印对象

    obj: 打印对象
    console: 控制台
    indent_guides: 是否启用缩进指南
    max_length: 最大长度
    max_string: 最大字符串
    max_depth: 最大深度
    expand_all: 是否展开所有对象
    """
    from rich.pretty import pprint as pprint_

    pprint_(
        obj,
        console=console,
        indent_guides=indent_guides,
        max_length=max_length,
        max_string=max_string,
        max_depth=max_depth,
        expand_all=expand_all,
    )


def track(
    sequence,
    description="Working...",
    total=None,
    auto_refresh=True,
    console=None,
    transient=False,
    get_time=None,
    refresh_per_second=10,
    style="bar.back",
    complete_style="bar.complete",
    finished_style="bar.finished",
    pulse_style="bar.pulse",
    update_period=0.1,
    disable=False,
    show_speed=True,
):
    """
    进度条, 封装 rich 的 track

    ```py
    import jsz

    for i in jsz.track(range(10)):
        jsz.print(i)
        jsz.sleep(0.2)
    ```
    """
    from rich.progress import track as track_

    return track_(
        sequence=sequence,
        description=description,
        total=total,
        auto_refresh=auto_refresh,
        console=console,
        transient=transient,
        get_time=get_time,
        refresh_per_second=refresh_per_second,
        style=style,
        complete_style=complete_style,
        finished_style=finished_style,
        pulse_style=pulse_style,
        update_period=update_period,
        disable=disable,
        show_speed=show_speed,
    )
