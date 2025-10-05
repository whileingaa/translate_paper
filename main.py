from mineru_ocr import request_mineru_translate
from concurrent_translate import translate_paper
def main():
    # 示例用法
    test_filepath = r"C:\Users\zzz\Zotero\storage\QS95IVS6\Park 等 - 2023 - Generative Agents Interactive Simulacra of Human Behavior.pdf"
    input_md_path = request_mineru_translate(test_filepath, output_dir="./output", extract_zip_after=True, delete_zip=True)
    if not input_md_path:
        print("OCR 处理失败，无法继续翻译")
        return
    elif not input_md_path.endswith(".md"):
        print(f"OCR 处理未返回 Markdown 文件，返回路径: {input_md_path}")
        return
    translate_paper(
        input_md_path=input_md_path,
        output_md_path=None,  # None 表示自动生成输出路径
        max_tokens=2048,   # 每块最大 token 数
        max_workers=5,     # 并发线程数
        max_retries=3      # 重试次数
    )

if __name__ == "__main__":
    main()
    