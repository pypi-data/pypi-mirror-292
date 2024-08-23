import re 

def make_xml(body: str, tag: str) -> str:
    return f'<{tag}> {body} </{tag}>'


def get_tag_list(response: str, tag: str):
    tag_content = re.findall(f'<{tag}>(.*?)</{tag}>', response, re.DOTALL)
    return [content.lower().strip() for content in tag_content]

