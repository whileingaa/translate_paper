from typing import List, Tuple
import re
from service.count_token import count_tokens, count_tokens_batch
def _detect_atx_headings(line:str)->bool:
    return bool(re.match(r'^#{1,6}\s', line))

def split_by_headings(file_path) -> List[List[str]]:
    # 读取文件内容
    with open(file_path,'r', encoding = 'utf-8') as f:
        raw_lines = f.readlines()
    lines = [line for line in raw_lines if line.strip()]
    if not lines:
        print("文件是空的或仅包含空行。")
        return []

    # 按照markdown中的#进行分块
    chunks = []
    current_chunk = []
    for line in lines:
        if _detect_atx_headings(line):
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
        current_chunk.append(line)
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def merge_chunks_by_major_headings(chunks: list[str]) -> list[str]:
    """
    根据论文的主要章节标题合并文本块。

    一个新的合并块由一个 '# ' 后跟数字的标题开始（例如 '# 1', '# 2'）。

    Args:
        chunks: 一个包含所有文本块的字符串列表。

    Returns:
        一个合并后的字符串列表，每个字符串代表一个完整的逻辑章节。
    """
    if not chunks:
        return []

    merged_blocks = []
    # current_block_chunks 用于临时存储属于同一个大章节的所有小块
    current_block_chunks = []

    # 定义一个正则表达式来识别主要章节标题，例如 "# 1", "# 2", etc.
    # ^ 表示字符串开头, #\s 匹配 "# "， \d+ 匹配一个或多个数字
    major_heading_pattern = re.compile(r'^#\s\d+')

    for chunk in chunks:
        trimmed_chunk = chunk.strip()     

        # 当遇到以reference开头的块时，停止处理（支持普通文本和markdown标题格式）
        if re.match(r'^#*\s*reference', trimmed_chunk, re.IGNORECASE):
            break
        
        if major_heading_pattern.match(trimmed_chunk):
            # 如果是，并且 current_block_chunks 中已有内容，
            # 说明上一个章节已经完整，需要先保存它。
            if current_block_chunks:
                # 使用分隔符将小块连接成一个大块
                merged_blocks.append("".join(current_block_chunks))
            current_block_chunks = [chunk]
        else:
            current_block_chunks.append(chunk)

    # 循环结束后，不要忘记保存最后一个正在构建的块
    if current_block_chunks:
        merged_blocks.append("".join(current_block_chunks))

    return merged_blocks


def greedy_merge_chunks(chunks: list[str], max_tokens: int = 2048) -> list[str]:
    """
    贪心合并文本块，确保每个块的 token 数不超过 max_tokens。
    
    使用贪心策略：尽可能地将连续的块合并在一起，直到添加下一个块会超过限制。
    
    Args:
        chunks: 待合并的文本块列表
        max_tokens: 每个块允许的最大 token 数，默认为 2048
    
    Returns:
        合并后的文本块列表，每个块的 token 数不超过 max_tokens
    """
    if not chunks:
        return []
    
    result = []
    current_merged = ""
    current_tokens = 0
    
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)
        
        # 如果单个块就超过限制，只能单独作为一个块
        if chunk_tokens > max_tokens:
            # 先保存当前已合并的内容
            if current_merged:
                result.append(current_merged)
                current_merged = ""
                current_tokens = 0
            # 将超大块单独添加（可能需要后续处理）
            result.append(chunk)
            print(f"警告: 发现单个块的 token 数 ({chunk_tokens}) 超过限制 ({max_tokens})")
            continue
        
        # 尝试合并当前块
        potential_tokens = count_tokens(current_merged + chunk)
        
        if potential_tokens <= max_tokens:
            # 可以合并
            current_merged += chunk
            current_tokens = potential_tokens
        else:
            # 无法合并，保存当前已合并的内容，开始新的合并块
            if current_merged:
                result.append(current_merged)
            current_merged = chunk
            current_tokens = chunk_tokens
    
    # 保存最后一个合并块
    if current_merged:
        result.append(current_merged)
    
    return result


def chunk_md(file_path: str, max_tokens: int = 2048) -> List[str]:
    """
    读取 Markdown 文件，
    1.按章节标题分块，
    2.进行贪心合并，确保每个块的 token 数不超过 max_tokens。
    
    Args:
        file_path: Markdown 文件路径
        max_tokens: 每个块允许的最大 token 数，默认为 2048
    
    Returns:
        合并后的文本块列表，每个块的 token 数不超过 max_tokens
    """
    # 按章节标题分块
    split_chunks = split_by_headings(file_path)
    if not split_chunks:
        return []
    
    # 将分块内容从 List[List[str]] 转换为 List[str]
    split_chunks_str = [''.join(chunk) for chunk in split_chunks]
    
    # 先按主要章节合并
    merged = merge_chunks_by_major_headings(split_chunks_str)
    
    # 再进行贪心合并，确保每个块不超过 max_tokens
    greedy_merged = greedy_merge_chunks(merged, max_tokens=max_tokens)
    
    return greedy_merged


# if __name__ == "__main__":
#     split = split_by_headings("./output/2504.17550v1/2504.17550v1.md")
    
#     merged = merge_chunks_by_major_headings([''.join(chunk) for chunk in split])

#     print("=== 主要章节合并后的结果 ===")
#     for i,chunk in enumerate(merged):
#         token_count = count_tokens(chunk)
#         print(f"Chunk {i+1} token count: {token_count}")
    
#     print(f"\n总共 {len(merged)} 个主要章节块")
    
#     # 进行贪心合并，确保每个块不超过 2048 tokens
#     print("\n=== 贪心合并（max_tokens=2048）===")
#     greedy_merged = greedy_merge_chunks(merged, max_tokens=2048)
    
#     print(f"贪心合并后总共 {len(greedy_merged)} 个块")
#     for i, chunk in enumerate(greedy_merged):
#         token_count = count_tokens(chunk)
#         print(f"Greedy Chunk {i+1} token count: {token_count}")
    
#     # 可选：将结果写入文件
#     with open("temp.txt", "w", encoding="utf-8") as f:
#         for i, chunk in enumerate(greedy_merged):
#             token_count = count_tokens(chunk)
#             f.write(f"--- Greedy Merged Chunk {i+1} (tokens: {token_count}) ---\n")
#             f.write(chunk)
#             f.write("\n\n")


