class Colors:
    BLACK = '\033[0m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    GREY = '\033[93m'
    RED = '\033[91m'
    YELLOW = '\033[33m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

import time

def paint(content: str, color) -> str:
    return (color + content + Colors.ENDC)

def time_tag() -> str:
    return '[{}]'.format(time.strftime("%H:%M:%S", time.localtime()))

def log(tag: str, content: str, tag_color: str, content_color: str) -> None:
    print('{}[{}] : {}'.format(time_tag(), paint(tag, tag_color), paint(content, content_color)))

def info(content: str) -> None:
    log(tag='INFO', content=content, tag_color=Colors.BLUE, content_color=Colors.BLACK)

def success(content: str) -> None:
    log(tag='SUCCESS', content=content, tag_color=Colors.GREEN, content_color=Colors.GREEN)

def warning(content: str) -> None:
    log(tag='WARNING', content=content, tag_color=Colors.RED, content_color=Colors.YELLOW)

def error(content: str) -> None:
    log(tag='ERROR', content=content, tag_color=Colors.RED, content_color=Colors.RED)

def fail(content: str) -> None:
    log(tag='FAIL', content=content, tag_color=Colors.GREY, content_color=Colors.GREY)

def debug(content: str) -> None:
    log(tag='DEBUG', content=content, tag_color=Colors.PURPLE, content_color=Colors.BLACK)

def runtime(content: str) -> None:
    log(tag='RUNTIME', content=content, tag_color=Colors.PURPLE, content_color=Colors.PURPLE)

def chat(content: str) -> None:
    log(tag='CHAT', content=content, tag_color=Colors.BLUE, content_color=Colors.BLUE)