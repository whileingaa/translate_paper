"""
测试文件名清理功能
"""
from service.filename_clean import sanitize_filename

def test_sanitize_filename():
    """测试各种文件名情况"""
    
    test_cases = [
        # (输入, 预期输出的特点描述)
        ("normal_file.md", "应该保持不变"),
        ("file with spaces.md", "空格应该被替换为下划线"),
        ("file:with:colons.md", "冒号应该被替换"),
        ('file"with"quotes.md', "引号应该被替换"),
        ("file<with>brackets.md", "尖括号应该被替换"),
        ("file|with|pipes.md", "管道符应该被替换"),
        ("file?with?questions.md", "问号应该被替换"),
        ("file*with*stars.md", "星号应该被替换"),
        ("file\\with\\backslashes.md", "反斜杠应该被替换"),
        ("file/with/slashes.md", "斜杠应该被替换"),
        ("file   with   spaces.md", "多个空格应该被合并"),
        (".hidden_file.md", "以点开头应该处理"),
        ("  file  .md", "首尾空格应该被移除"),
        ("Generative Agents: Interactive Simulacra of Human Behavior.pdf", "真实案例：含空格和冒号"),
        ("Park 等 - 2023 - Generative Agents Interactive Simulacra of Human Behavior.pdf", "真实案例：多个空格和连字符"),
    ]
    
    print("=" * 80)
    print("文件名清理测试")
    print("=" * 80)
    
    for i, (input_name, description) in enumerate(test_cases, 1):
        output = sanitize_filename(input_name)
        print(f"\n测试 {i}: {description}")
        print(f"  输入:  '{input_name}'")
        print(f"  输出:  '{output}'")
        
        # 基本验证
        assert output, "输出不应为空"
        assert not any(c in output for c in r'<>:"/\|?*'), "输出不应包含非法字符"
        assert not output.startswith(' ') and not output.endswith(' '), "输出不应有首尾空格"
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)


if __name__ == "__main__":
    test_sanitize_filename()
