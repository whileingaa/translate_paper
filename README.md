translate_paper 论文翻译工具

### 项目简介

- 将英文论文 PDF 通过 MinerU OCR 转为 Markdown，并使用大语言模型并发翻译为中文，最终输出为 Markdown 文件。
- 完整流程：PDF → OCR(zip) → 解压得到 Markdown → 标题分块与贪心合并 → 并发调用 LLM 翻译 → 保存译文与错误日志。

### 主要特性

- 端到端流程：从 PDF 到中文 Markdown。
- 智能分块：基于 Markdown 标题与章节合并，控制每块 token 数。
- 并发翻译：线程池并发 + 指数退避重试，提高吞吐与稳定性。

### 环境要求

- Python 3.10+（推荐 3.11/3.12）。
- 需要可在本地跑[mineru ocr模型](https://opendatalab.github.io/MinerU/zh/)
- 需可访问使用的 LLM 服务（暂时只提供DeepSeek进行翻译）。

### 安装

- 

### 配置

- 将`.env.example`修改拓展名，复制为`.env`，填入自己的api key
- [docker部署MinerU OCR 服务](https://opendatalab.github.io/MinerU/zh/quick_start/docker_deployment/)，启动 Web API 服务
- 输出目录：
  - 默认使用 `./output`，脚本会自动创建；也可通过 `main(output_file=...)` 或指定完整 `output_md_path` 覆盖。

#### 快速开始

- 修改main.py中需要翻译的文件路径，直接运行入口脚本 `main.py`：
  - `python main.py`

#### 参数说明（核心）

- `main(input_file, output_file="./output", extract_zip_after=True, delete_zip=True, max_tokens=2048, max_workers=3, max_retries=3)`
  - `input_file`: 输入 PDF 路径。
  - `output_file`: OCR 结果与译文输出的根目录。
  - `extract_zip_after`: MinerU 返回 zip 后是否解压。
  - `delete_zip`: 解压后是否删除 zip 包。
  - `max_tokens`: 单块最大 token 数（用于单次传递翻译token数量控制）。
  - `max_workers`: 并发线程数。
  - `max_retries`: LLM 调用每块的最大重试次数。

#### 目录结构

函数功能与调用关系如[PROJECT](PROJECT.md)所示

