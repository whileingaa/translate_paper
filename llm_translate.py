from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
def translate_text(text):
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_URL"),
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": """
                指令： 请将以下提供的英文学术论文内容准确、专业、流畅地翻译成中文，要求以markdown的格式进行输出。 
                具体要求：
                1. 核心原则：
                - 准确性优先： 确保原文信息（包括事实、数据、论点、逻辑关系）完整无误地传递。
                - 专业性： 严格遵循相关学科的专业术语和共识译法。对于不确定的专业术语，请尽力查找或提供合理的直译并加注（如`[原文：Term]`）。
                - 学术风格： 译文需符合中文科技/学术论文的正式、严谨、客观的语体风格。避免口语化、随意化表达。
                - 流畅性与可读性： 在忠实原文的基础上，译文应符合中文表达习惯，句子通顺自然，避免过度欧化句式或生硬直译。
                1. 格式与结构处理：
                - 保留结构： 严格对应原文的章节标题、小标题、段落划分、列表项（有序/无序）。翻译标题时需简洁准确。
                - 章节标题：一级章节标题(如1)采用markdown的2号标题格式，二级章节标题（如1.1）采用3号标题格式，以此类推。章节内的小标题采用加粗格式。
                - 数学公式/方程式： 原文保留，不翻译。确保其编号与上下文引用一致，需用$作为公式的起始和结束符号
                - 代码/变量名： 原文保留，不翻译。
                - 专有名词： 人名、地名、机构名等，采用通用、权威的译名（如新华社译名室标准）。若无通用译名，可保留原文或音译。首次出现时可在括号内注明原文。
                - 参考文献 (References)： 不翻译条目本身（作者、标题、期刊名、出版社等保持原文）。
                - 脚注/尾注： 内容需要翻译，并保留相应编号。
                2. 输出要求：
                - 应保证内容的完整性，直接输出完整的中文译文，不需要其他任何解释。
                - 译文应清晰易读，避免因过度追求字面准确而导致晦涩难懂。
                """
            },
            {
                "role": "user",
                "content": f"""
                待翻译的英文论文内容：
                {text}
                """
            },
        ],
        stream=False,
    )
    return response
# if __name__ =="__main__":
#     test_text = """
#     # 1 Introduction
#     This is a sample English text for translation.
#     """
#     translated = translate_text(test_text)
#     print(translated.choices[0].message.content)