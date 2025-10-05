import requests
import os
import zipfile

mineru_api_url = "http://localhost:8000/file_parse"

def request_mineru_translate(filepath, url=mineru_api_url, output_dir="output", extract_zip_after=True, delete_zip=False) -> str:
    data = {
        "return_middle_json": "false",
        "return_model_output": "false",
        "return_md": "true",
        "return_images": "true",
        "end_page_id": "99999",
        "parse_method": "auto",
        "start_page_id": "0",
        "lang_list": "ch",
        "output_dir": output_dir,
        "server_url": "string",
        "return_content_list": "false",
        "backend": "pipeline",
        "table_enable": "true",
        "response_format_zip": "true",
        "formula_enable": "true",
    }
    filename, file_extension = os.path.splitext(os.path.basename(filepath))
    files={
        'files': (filename + file_extension,open(filepath, 'rb'), f"application/{file_extension.replace('.', '')}"),
    }
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{filename}.zip"), "wb") as f:
            f.write(response.content)
        print(f"File saved to {os.path.join(output_dir, f'{filename}.zip')}")

        #解压下载的zip文件，解压路径同zip文件路径，是否删除zip文件可选
        if extract_zip_after:
            extract_zip(os.path.join(output_dir, f"{filename}.zip"), delete_zip=delete_zip)
            return os.path.join(output_dir, filename, filename + ".md")
        return os.path.join(output_dir, f"{filename}.zip")


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