import requests
import os
import zipfile
from service.filename_clean import sanitize_filename

mineru_api_url = "http://localhost:8000/file_parse"

def request_mineru_translate(filepath, url=mineru_api_url, output_dir="output", lang="en", extract_zip_after=True, delete_zip=False) -> str:

    if not os.path.exists(filepath):
        print(f"需要翻译的文件不存在: {filepath}")
        return ""
    #mineru api运行后，打开http://localhost:8000/docs查看文档
    data = {
        "output_dir": output_dir,
        "lang_list": lang,
        "backend": "pipeline",
        "parse_method": "auto",
        "formula_enable": "true",
        "table_enable": "true",
        "server_url": "string",
        "return_md": "true",
        "return_middle_json": "false",
        "return_model_output": "false",
        "return_content_list": "false",
        "return_images": "true",
        "response_format_zip": "true",
        "start_page_id": "0",
        "end_page_id": "99999",       
    }
    # 获取原始文件名并清理
    original_filename = os.path.basename(filepath)
    filename, file_extension = os.path.splitext(original_filename)
    
    # 清理文件名，移除不合法字符
    clean_filename = sanitize_filename(filename)
    
    files={
        'files': (original_filename, open(filepath, 'rb'), f"application/{file_extension.replace('.', '')}"),
    }
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        # 使用清理后的文件名保存
        zip_path = os.path.join(output_dir, f"{clean_filename}.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print(f"File saved to {zip_path}")

        #解压下载的zip文件，解压路径同zip文件路径，是否删除zip文件可选
        if extract_zip_after:
            extract_zip(zip_path, delete_zip=delete_zip)
            return os.path.join(output_dir, clean_filename, clean_filename + ".md")
        return zip_path


    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return ""


def extract_zip(zip_path, extract_to=None, delete_zip=False):
    if not extract_to:
        extract_to = os.path.dirname(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Extracted files to {extract_to}")

    if delete_zip:
        if not os.path.exists(zip_path):
            print(f"Zip file does not exist: {zip_path}")
            return
        os.remove(zip_path)
        print(f"Deleted zip file: {zip_path}")

# if __name__ == "__main__":
#     test_filepath = r"C:\Users\zzz\Downloads\2504.17550v1.pdf"
#     request_mineru_translate(test_filepath)

#     extract_zip(r"C:\zzz_disk\project\translate_paper\output\2504.17550v1_translated.zip", delete_zip=False)