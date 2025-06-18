from docx import Document
from collections import OrderedDict, defaultdict
import re

excluded_titles = [
    '\[.*'
]

def parse_word_document(doc_path):
    """解析Word文档并按标题分类内容"""
    doc = Document(doc_path)
    title_content_map = OrderedDict()
    current_title = None
    current_content = []

    dup_title = defaultdict(int)

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # 改进的标题判断逻辑 ======================================
        is_heading = False

        # 检查标题是否包含 excluded_titles 中的任何字符串
        if any(re.match(excluded_title, text) for excluded_title in excluded_titles):
            continue

        # 1. 首先检查段落样式
        if hasattr(para.style, 'name'):
            style_name = para.style.name.lower()
            is_heading = any(h in style_name for h in ['heading', 'title', 'header'])

        # 2. 如果样式不明确，再使用文本特征判断
        if not is_heading:
            is_heading = is_title(text, para)
        # ======================================================

        if is_heading:
            if current_title:
                title_content_map[current_title] = '\n'.join(current_content).strip()
            current_title = text
            current_content = []
            if current_title in dup_title:
                dup_title[current_title] += 1
                current_title = f"{current_title} ({dup_title[current_title]})"
            else:
                dup_title[current_title] = 1
        else:
            if current_title:
                current_content.append(text)

    if current_title:
        title_content_map[current_title] = '\n'.join(current_content).strip()
    return title_content_map

def is_title(text, paragraph=None):
    """改进的标题判断函数，结合样式和文本特征"""
    if not text:
        return False

    # 如果传入了段落对象，先检查样式
    if paragraph and hasattr(paragraph.style, 'name'):
        style_name = paragraph.style.name.lower()
        if any(h in style_name for h in ['heading', 'title', 'header']):
            return True

    return False
    # # 原始文本特征判断（保留原有逻辑）
    # title_patterns = [
    #     r'^[A-Z][^.]*$',
    #     r'^.*? - .*?$',
    #     r'^.*?: .*?$',
    #     r'^[A-Z]{2,}.*$',
    #     r'^[0-9]+\. .*$',
    #     r'^Main Script.*$',
    #     r'^Grabbers$'
    # ]
    # return any(re.match(pattern, text) for pattern in title_patterns)


def print_title_content_map(title_content_map):
    """打印标题和内容映射"""
    for title, content in title_content_map.items():
        print(f"标题: {title}")
        print(f"内容: \n{content}\n")
        print("-" * 80)


# 主函数
if __name__ == "__main__":
    # 替换为实际的文档路径
    doc_path = r"C:\Users\proaim.LAPTOP-HTKQPIIT\Downloads\Aeons Shoot 30-05_ All Scripts + Direction.docx"

    try:
        title_content_map = parse_word_document(doc_path)
        # 打印结果或保存为文件
        print_title_content_map(title_content_map)

        # 如果需要保存为JSON
        import json

        with open("title_content_map.json", "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in title_content_map.items()}, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"解析文档时出错: {e}")