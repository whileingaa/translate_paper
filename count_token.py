import tiktoken
from functools import lru_cache

@lru_cache(maxsize=8)
def _get_encoding(model="gpt-3.5-turbo"):
    """
    获取并缓存编码器（优化性能）
    """
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text, model="gpt-3.5-turbo"):
    """
    计算文本的 token 数量（已优化性能）
    
    参数:
        text (str): 需要计算 token 的文本（支持中文和英文）
        model (str): 使用的模型名称，默认为 "gpt-3.5-turbo"
                    可选: "gpt-4", "gpt-3.5-turbo", "text-davinci-003" 等
    
    返回:
        int: token 数量
        
    性能说明:
        - 短文本（<1000字符）: ~0.1-1ms
        - 中等文本（1000-10000字符）: ~1-10ms
        - 长文本（>10000字符）: ~10-100ms
        - 编码器会被缓存，重复调用更快
    """
    # 使用缓存的编码器
    encoding = _get_encoding(model)
    
    # 编码文本并返回 token 数量
    tokens = encoding.encode(text)
    return len(tokens)


def count_tokens_batch(texts, model="gpt-3.5-turbo"):
    """
    批量计算多个文本的 token 数量（更高效）
    
    参数:
        texts (list): 文本列表
        model (str): 使用的模型名称
    
    返回:
        list: 每个文本的 token 数量列表
    """
    encoding = _get_encoding(model)
    return [len(encoding.encode(text)) for text in texts]


# # 测试示例
# if __name__ == "__main__":
#     # 测试英文
#     english_text = "Hello, how are you? This is a test sentence."
#     english_tokens = count_tokens(english_text)
#     print(f"英文文本: {english_text}")
#     print(f"Token 数量: {english_tokens}\n")
    
#     # 测试中文
#     chinese_text = "你好，这是一个测试句子。今天天气很好。"
#     chinese_tokens = count_tokens(chinese_text)
#     print(f"中文文本: {chinese_text}")
#     print(f"Token 数量: {chinese_tokens}\n")
    
#     # 测试混合文本
#     mixed_text = "Hello 你好，This is a mixed text 这是混合文本。"
#     mixed_tokens = count_tokens(mixed_text)
#     print(f"混合文本: {mixed_text}")
#     print(f"Token 数量: {mixed_tokens}\n")
    
#     # 测试不同模型
#     text = "OpenAI GPT models are powerful."
#     print(f"文本: {text}")
#     print(f"GPT-3.5-turbo tokens: {count_tokens(text, 'gpt-3.5-turbo')}")
#     print(f"GPT-4 tokens: {count_tokens(text, 'gpt-4')}")