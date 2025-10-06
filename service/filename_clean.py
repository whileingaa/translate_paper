import re
import os
def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除或替换不合法的字符。
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    # 保留文件名（不含路径）
    name_only = os.path.basename(filename)
    
    # Windows 不允许的字符: < > : " / \ | ? *
    # 替换为下划线或移除
    name_only = re.sub(r'[<>:"/\\|?*]', '_', name_only)
    
    # 替换多个连续空格为单个下划线
    name_only = re.sub(r'\s+', '_', name_only)
    
    # 移除首尾的空格、点号、下划线
    name_only = name_only.strip(' ._')
    
    # 如果文件名为空或只有扩展名，使用默认名称
    if not name_only or name_only.startswith('.'):
        name_only = 'translated_document' + name_only
    
    # 限制文件名长度（Windows 路径限制）
    name, ext = os.path.splitext(name_only)
    if len(name) > 200:  # 保留足够空间给扩展名和路径
        name = name[:200]
    
    return name + ext