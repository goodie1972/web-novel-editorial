"""
AI去味检查器

检测AI写作痕迹
"""

import re
from typing import List, Set


class AIDetector:
    """AI写作痕迹检测器"""
    
    def __init__(self, forbidden_words: List[str] = None, forbidden_patterns: List[str] = None):
        """
        初始化
        
        Args:
            forbidden_words: 禁用词汇列表
            forbidden_patterns: 禁用模式列表（正则）
        """
        self.forbidden_words = forbidden_words or [
            "值得注意的是", "需要强调的是", "事实上", "实际上",
            "首先", "其次", "最后", "总之", "综上所述",
            "此外", "与此同时", "至关重要", "深入探讨",
            "从某种角度来说", "从整体来看", "不难发现",
            "可以看出", "由此可见", "总的来说",
            "一方面", "另一方面", "更重要的是",
        ]
        
        self.forbidden_patterns = forbidden_patterns or [
            r"不仅.*而且.*",
            r"从\d+到\d+",
            r"这不仅仅是.*而是.*",
            r"\d+个?方面",
            r"第一[、，,].*第二[、，,].*第三",
            r"一方面.*另一方面.*",
            r"首先[，,].*然后[，,].*最后",
        ]
    
    def check(self, content: str, result):
        """
        检查AI痕迹
        
        Args:
            content: 章节内容（不含元数据）
            result: GateResult 对象
        """
        # 去除元数据头
        content = self._strip_metadata(content)
        
        # 检测禁用词汇
        found_words = self._check_forbidden_words(content)
        
        if found_words:
            # 按类型分组
            by_category = {}
            for word, count in found_words.items():
                category = self._categorize_word(word)
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(f"'{word}'({count}次)")
            
            # 生成错误信息
            error_msgs = []
            for category, words in by_category.items():
                error_msgs.append(f"{category}: {', '.join(words)}")
            
            result.add_check(
                "AI词汇检测",
                False,
                f"发现{len(found_words)}处AI词汇 - " + "; ".join(error_msgs[:3])
            )
        else:
            result.add_check("AI词汇检测", True, "未发现AI词汇")
        
        # 检测禁用模式
        found_patterns = self._check_forbidden_patterns(content)
        
        if found_patterns:
            result.add_check(
                "AI结构检测",
                False,
                f"发现{len(found_patterns)}种AI常用结构"
            )
        else:
            result.add_check("AI结构检测", True, "未发现AI结构")
        
        # 综合判断
        if found_words or found_patterns:
            result.add_check(
                "AI去味",
                False,
                "存在AI写作痕迹，请修改"
            )
        else:
            result.add_check("AI去味", True, "通过AI去味检查")
    
    def _strip_metadata(self, content: str) -> str:
        """去除元数据头"""
        pattern = r'^---.*?^---'
        return re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE).strip()
    
    def _check_forbidden_words(self, content: str) -> dict:
        """检测禁用词汇"""
        found = {}
        
        for word in self.forbidden_words:
            # 不区分大小写搜索
            count = len(re.findall(re.escape(word), content, re.IGNORECASE))
            if count > 0:
                found[word] = count
        
        return found
    
    def _check_forbidden_patterns(self, content: str) -> list:
        """检测禁用模式"""
        found = []
        
        for pattern in self.forbidden_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                found.append(pattern)
        
        return found
    
    def _categorize_word(self, word: str) -> str:
        """对词汇进行分类"""
        if word in ["首先", "其次", "最后", "总之"]:
            return "过渡词"
        elif word in ["此外", "与此同时"]:
            return "连接词"
        elif word in ["至关重要", "深入探讨"]:
            return "强调词"
        elif "方面" in word:
            return "结构词"
        else:
            return "填充词"
    
    def highlight_issues(self, content: str) -> str:
        """
        高亮问题（用于人工检查）
        
        返回带标记的内容
        """
        result = content
        
        # 高亮禁用词汇
        for word in self.forbidden_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(f"**[{word}]**", result)
        
        # 高亮禁用模式（简化处理）
        for pattern in self.forbidden_patterns[:3]:
            result = re.sub(pattern, f"**[{pattern}]**", result, flags=re.DOTALL)
        
        return result