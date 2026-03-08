"""
字数检查器

检查章节字数是否达标
"""

import re
from typing import Optional


class WordCountChecker:
    """章节字数检查器"""
    
    def check(self, content: str, result, target: int = 3000, strict: bool = True):
        """
        检查字数
        
        Args:
            content: 章节内容（不含元数据）
            result: GateResult 对象
            target: 目标字数
            strict: 是否严格模式（必须>=target，否则允许>=target*0.8）
        """
        # 去除元数据头
        content = self._strip_metadata(content)
        
        # 统计字数（不含标点）
        word_count = self._count_words(content)
        
        # 计算百分比
        percentage = word_count / target * 100 if target > 0 else 0
        
        if strict:
            # 严格模式：必须达到目标
            if word_count >= target:
                result.add_check(
                    "字数检查",
                    True,
                    f"{word_count}字 (目标{target}字)"
                )
            else:
                result.add_check(
                    "字数检查",
                    False,
                    f"字数不足: {word_count}/{target}字 ({percentage:.0f}%)"
                )
        else:
            # 宽松模式：80%即可通过
            min_acceptable = int(target * 0.8)
            
            if word_count >= target:
                result.add_check(
                    "字数检查",
                    True,
                    f"{word_count}字 (目标{target}字)"
                )
            elif word_count >= min_acceptable:
                result.add_check(
                    "字数检查",
                    True,
                    f"{word_count}字 (最低{min_acceptable}字)"
                )
            else:
                result.add_check(
                    "字数检查",
                    False,
                    f"字数不足: {word_count}/{target}字 ({percentage:.0f}%)"
                )
    
    def _strip_metadata(self, content: str) -> str:
        """去除元数据头"""
        pattern = r'^---.*?^---'
        return re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE).strip()
    
    def _count_words(self, text: str) -> int:
        """
        统计字数（不含标点）
        
        规则：
        - 汉字算1字
        - 英文字母算1字
        - 数字算1字
        - 标点符号不算
        """
        # 只保留汉字、英文字母、数字
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)
        
        # 统计字符数
        # 汉字全角转半角（每个汉字算1字）
        # 英文和数字也是每个字符算1字
        return len(cleaned)
    
    def count_with_punctuation(self, text: str) -> int:
        """统计字数（含标点）"""
        content = self._strip_metadata(text)
        # 只保留可见字符
        cleaned = re.sub(r'[\s\n\r\t]', '', content)
        return len(cleaned)