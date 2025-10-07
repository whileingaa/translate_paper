from mineru_ocr import request_mineru_translate
from concurrent_translate import translate_paper
def main(input_file:str, output_file :str="./output", extract_zip_after=True, delete_zip=True,max_tokens=2048, max_workers=3, max_retries=3):
    # 示例用法

    input_md_path = request_mineru_translate(filepath=input_file, output_dir=output_file, extract_zip_after=extract_zip_after, delete_zip=delete_zip)
    if not input_md_path:
        print("OCR 处理失败，无法继续翻译")
        return
    elif not input_md_path.endswith(".md"):
        print(f"OCR 处理未返回 Markdown 文件，返回路径: {input_md_path}")
        return
    translate_paper(
        input_md_path=input_md_path,
        output_md_path=None,  # None 表示自动生成输出路径
        max_tokens=max_tokens,   # 每块最大 token 数
        max_workers=max_workers,     # 并发线程数
        max_retries=max_retries      # 重试次数
    )

if __name__ == "__main__":
    test_filepath = r""
    main(
        input_file=test_filepath,
        output_file="./output",
        extract_zip_after=True,
        delete_zip=True,
        max_tokens=2048,
        max_workers=5,
        max_retries=3
    )
    