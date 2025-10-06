"""
测试并发翻译功能的脚本
"""
from concurrent_translate import translate_paper
import os

def main():
    # 配置文件路径
    input_file = "./output/2504.17550v1/2504.17550v1.md"
    output_file = "./output/2504.17550v1/2504.17550v1_translated.md"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在: {input_file}")
        print("请确保文件路径正确")
        return
    
    print("=" * 60)
    print("论文并发翻译工具")
    print("=" * 60)
    
    # 执行翻译
    success = translate_paper(
        input_md_path=input_file,
        output_md_path=output_file,
        max_tokens=2048,      # 每个块的最大 token 数
        max_workers=3,        # 并发线程数（可根据 API 限制调整）
        max_retries=3         # 最大重试次数
    )
    
    print("\n" + "=" * 60)
    if success:
        print("翻译流程执行完成！")
        print(f"请查看输出文件: {output_file}")
    else:
        print("翻译流程执行失败！")
    print("=" * 60)


if __name__ == "__main__":
    main()
