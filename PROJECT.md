#### 项目说明（架构与调用关系）

底层功能函数(service)：

- `count_tokens.py` 用于翻译块token的计数，使得在合并时，每个大块的token数不多于max_token
- `filename_clean.py` 用于清理写入的文件名
- `llm_translate.py` 调用llm api进行翻译



`main.py`

- `mineru_ocr.py`
  - request_mineru_translate ：用于调用mineru的api
    - extract_zip：用于解压压缩包
- `concurrent_translate.py`
  - translate_paper ：
    - `chunk_md.py` ：步骤 1/3: 分块处理...
      - split_by_headings：按md标题格式“#”分成小块
      - merge_chunks_by_major_headings：将小块进行第一次合并，将语义相似的合并到一起；删除了参考文献及之后的内容
      - greedy_merge_chunks ：按每块的token数进行第二次合并，保证每次调用api的token数不多也不少
    - translate_chunks_concurrent：步骤 2/3: 并发翻译...
    - save_translated_markdown：步骤 3/3: 保存翻译结果...
