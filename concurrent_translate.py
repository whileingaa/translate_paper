from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
import time
import os
from tqdm import tqdm
from llm_translate import translate_text
from chunk_md import chunk_md
from service.filename_clean import sanitize_filename

def translate_chunk_with_retry(
    chunk: str,
    chunk_index: int,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Tuple[int, Optional[str], Optional[str]]:
    """
    翻译单个文本块，支持指数退避重试。
    
    Args:
        chunk: 要翻译的文本块
        chunk_index: 文本块的索引（用于保持顺序）
        max_retries: 最大重试次数
        initial_delay: 初始重试延迟（秒）
    
    Returns:
        (chunk_index, translated_text, error_message)
        - chunk_index: 原始索引
        - translated_text: 翻译后的文本，失败则为 None
        - error_message: 错误信息，成功则为 None
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            response = translate_text(chunk)
            translated = response.choices[0].message.content
            return (chunk_index, translated, None)
        
        except Exception as e:
            error_msg = f"Chunk {chunk_index} attempt {attempt + 1}/{max_retries} failed: {str(e)}"
            
            if attempt < max_retries - 1:
                # 不是最后一次尝试，等待后重试
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                # 最后一次尝试也失败了
                return (chunk_index, None, error_msg)
    
    return (chunk_index, None, f"Chunk {chunk_index} failed after {max_retries} retries")


def translate_chunks_concurrent(
    chunks: List[str],
    max_workers: int = 3,
    max_retries: int = 3
) -> Tuple[List[str], List[str]]:
    """
    并发翻译多个文本块。
    
    Args:
        chunks: 要翻译的文本块列表
        max_workers: 最大并发线程数
        max_retries: 每个块的最大重试次数
    
    Returns:
        (translated_chunks, errors)
        - translated_chunks: 翻译后的文本块列表（按原始顺序）
        - errors: 错误信息列表
    """
    if not chunks:
        return [], []
    
    print(f"\n开始翻译 {len(chunks)} 个文本块...")
    print(f"并发数: {max_workers}, 最大重试次数: {max_retries}\n")
    
    # 用于存储结果的字典，key 是 chunk_index
    results = {}
    errors = []
    
    # 使用线程池并发执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_index = {
            executor.submit(
                translate_chunk_with_retry,
                chunk,
                i,
                max_retries
            ): i
            for i, chunk in enumerate(chunks)
        }
        
        # 使用 tqdm 显示进度
        with tqdm(total=len(chunks), desc="翻译进度", unit="块") as pbar:
            for future in as_completed(future_to_index):
                chunk_index, translated, error = future.result()
                
                if error:
                    errors.append(error)
                    tqdm.write(f"❌ {error}")
                    # 即使失败也保存一个占位符，保持索引一致
                    results[chunk_index] = f"\n<!-- 翻译失败: {error} -->\n{chunks[chunk_index]}\n"
                else:
                    results[chunk_index] = translated
                    tqdm.write(f"✓ 块 {chunk_index} 翻译完成")
                
                pbar.update(1)
    
    # 按索引顺序重建翻译后的列表
    translated_chunks = [results[i] for i in range(len(chunks))]
    
    # 打印统计信息
    success_count = len(chunks) - len(errors)
    print(f"\n翻译完成统计:")
    print(f"  成功: {success_count}/{len(chunks)}")
    print(f"  失败: {len(errors)}/{len(chunks)}")
    
    return translated_chunks, errors


def save_translated_markdown(
    translated_chunks: List[str],
    output_path: str,
    errors: Optional[List[str]] = None
) -> None:
    """
    将翻译后的文本块保存为 Markdown 文件。
    
    Args:
        translated_chunks: 翻译后的文本块列表
        output_path: 输出文件路径
        errors: 错误信息列表（可选，会附加到文件末尾）
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 合并所有翻译块
    full_text = "\n\n".join(translated_chunks)
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
        
        # 如果有错误，附加到文件末尾
        if errors:
            f.write("\n\n---\n\n")
            f.write("## 翻译错误日志\n\n")
            for error in errors:
                f.write(f"- {error}\n")
    
    print(f"\n翻译结果已保存到: {output_path}")


def translate_paper(
    input_md_path: str,
    output_md_path = None,
    max_tokens: int = 2048,
    max_workers: int = 3,
    max_retries: int = 3
) -> bool:
    """
    完整的论文翻译流程：分块 -> 并发翻译 -> 保存结果。
    
    Args:
        input_md_path: 输入的 Markdown 文件路径
        output_md_path: 输出的 Markdown 文件路径或文件夹路径
        max_tokens: 每个块的最大 token 数
        max_workers: 最大并发线程数
        max_retries: 每个块的最大重试次数
    
    Returns:
        是否成功完成（即使有部分失败，只要保存了文件就返回 True）
    """
    try:
        print(f"正在处理文件: {input_md_path}")
        if not output_md_path:
            # 自动生成输出路径（与输入文件同目录）
            base, ext = os.path.splitext(os.path.basename(input_md_path))
            # 清理文件名
            clean_base = sanitize_filename(base)
            output_filename = f"{clean_base}_translated{ext}"
            output_md_path = os.path.join(os.path.dirname(input_md_path), output_filename)
        elif os.path.isdir(output_md_path):
            # 输出路径是目录，自动生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(os.path.basename(input_md_path))
            # 清理文件名
            clean_base = sanitize_filename(base)
            output_filename = f"{clean_base}_translated_{timestamp}{ext}"
            output_md_path = os.path.join(output_md_path, output_filename)
        else:
            # 用户指定了完整的输出路径，仍需清理文件名部分
            output_dir = os.path.dirname(output_md_path)
            output_file = os.path.basename(output_md_path)
            clean_output_file = sanitize_filename(output_file)
            output_md_path = os.path.join(output_dir, clean_output_file) if output_dir else clean_output_file
        
        print(f"输出路径: {output_md_path}\n")
        
        # 步骤 1: 分块
        print("步骤 1/3: 分块处理...")
        chunks = chunk_md(input_md_path, max_tokens=max_tokens)
        
        if not chunks:
            print("错误: 未能从文件中提取任何内容块")
            return False
        
        print(f"成功分割为 {len(chunks)} 个块\n")
        
        # 步骤 2: 并发翻译
        print("步骤 2/3: 并发翻译...")
        translated_chunks, errors = translate_chunks_concurrent(
            chunks,
            max_workers=max_workers,
            max_retries=max_retries
        )
        
        # 步骤 3: 保存结果
        print("\n步骤 3/3: 保存翻译结果...")
        save_translated_markdown(translated_chunks, output_md_path, errors)
        
        if errors:
            print(f"\n⚠️ 警告: 有 {len(errors)} 个块翻译失败，详见输出文件末尾")
        else:
            print("\n✅ 所有块均成功翻译！")
        
        return True
    
    except Exception as e:
        print(f"\n❌ 翻译过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 示例用法
    input_file = "./output/2504.17550v1/2504.17550v1.md"
    
    translate_paper(
        input_md_path=input_file,
        output_md_path=None,  # None 表示自动生成输出路径
        max_tokens=2048,
        max_workers=3,  # 并发数，可根据 API 限制调整
        max_retries=3   # 重试次数
    )
