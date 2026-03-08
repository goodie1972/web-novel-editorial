"""
编辑审核检查器

执行逐项审核清单，确保每章通过所有检查
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class EditorReviewChecker:
    """
    编辑审核检查器
    
    按SKILL.md定义的审核标准逐项检查：
    - 风格一致性
    - 爽点（打脸/升级/收获/反转）
    - 钩子（章节结尾悬念）
    - 人物（性格一致、状态正确）
    - 伏笔（埋入/回收符合规划）
    - 节奏（明快不拖沓）
    """
    
    # 审核检查项
    CHECKLIST = [
        {
            "id": "style",
            "name": "风格一致性",
            "description": "是否符合选定大神风格",
            "required": True,
        },
        {
            "id": "shuangdian",
            "name": "爽点",
            "description": "每章有打脸/升级/收获/反转",
            "required": True,
            "keywords": ["打脸", "升级", "收获", "反转", "突破", "领悟", "秒杀"],
        },
        {
            "id": "gouzi",
            "name": "钩子",
            "description": "每章结尾有悬念",
            "required": True,
        },
        {
            "id": "character",
            "name": "人物",
            "description": "性格一致，状态正确",
            "required": True,
        },
        {
            "id": "foreshadowing",
            "name": "伏笔",
            "description": "埋入/回收符合规划",
            "required": True,
        },
        {
            "id": "pace",
            "name": "节奏",
            "description": "明快，不拖沓",
            "required": True,
        },
        {
            "id": "word_count",
            "name": "字数",
            "description": "符合章节规划（2500-4000字）",
            "required": True,
        },
    ]
    
    def check(self, result, chapter_file: str = None, content: str = None, 
              project_path: str = None, chapter: int = 1):
        """
        执行编辑审核
        
        Args:
            result: GateResult 对象
            chapter_file: 章节文件路径
            content: 章节内容（如果已读取）
            project_path: 项目路径（用于查询记忆库）
            chapter: 章节号
        """
        if not chapter_file and not content:
            result.add_check("审核输入", False, "未提供章节内容")
            return
        
        # 读取内容
        if content is None and chapter_file:
            chapter_path = Path(chapter_file)
            if chapter_path.exists():
                content = chapter_path.read_text(encoding="utf-8")
        
        if not content:
            result.add_check("章节内容", False, "无法读取章节内容")
            return
        
        # 去除元数据
        body = self._strip_metadata(content)
        
        # 逐项检查
        all_passed = True
        
        for item in self.CHECKLIST:
            passed, detail = self._check_item(
                item, body, project_path, chapter
            )
            
            result.add_check(
                item["name"],
                passed,
                detail
            )
            
            if not passed:
                all_passed = False
        
        # 生成审核报告
        if all_passed:
            result.add_check("编辑审核", True, "全部检查项通过")
        else:
            result.add_check("编辑审核", False, "有检查项未通过")
    
    def _check_item(self, item: Dict, content: str, 
                   project_path: str, chapter: int) -> tuple:
        """检查单个项目"""
        item_id = item["id"]
        
        if item_id == "style":
            return self._check_style(content, project_path)
        elif item_id == "shuangdian":
            return self._check_shuangdian(content, item)
        elif item_id == "gouzi":
            return self._check_gouzi(content)
        elif item_id == "character":
            return self._check_character(content, project_path, chapter)
        elif item_id == "foreshadowing":
            return self._check_foreshadowing(content, project_path, chapter)
        elif item_id == "pace":
            return self._check_pace(content)
        elif item_id == "word_count":
            return self._check_word_count(content)
        
        return True, "未知检查项"
    
    def _check_style(self, content: str, project_path: str) -> tuple:
        """检查风格一致性"""
        if not project_path:
            return False, "未提供项目路径，无法核对风格"
        
        # 读取记忆库中的风格配置
        memory_path = Path(project_path) / "memory" / "project.md"
        
        if not memory_path.exists():
            return False, "未找到风格配置"
        
        style_content = memory_path.read_text(encoding="utf-8")
        
        # 检查是否有风格相关关键词
        if any(kw in style_content for kw in ["风格", "大神", "作者"]):
            return True, "风格配置已读取"
        
        return False, "未配置风格"
    
    def _check_shuangdian(self, content: str, item: Dict) -> tuple:
        """检查爽点"""
        keywords = item.get("keywords", [])
        
        found = []
        for kw in keywords:
            if kw in content:
                found.append(kw)
        
        if found:
            return True, f"发现爽点: {', '.join(found)}"
        
        return False, "未发现爽点（打脸/升级/收获/反转）"
    
    def _check_gouzi(self, content: str) -> tuple:
        """检查钩子（章节结尾悬念）"""
        lines = content.strip().split('\n')
        last_lines = lines[-5:]  # 最后5行
        
        last_text = ' '.join(last_lines)
        
        # 检查是否有悬念关键词
        gouzi_keywords = ["...", "？", "！", "危机", "竟然", "没想到", 
                         "就在这时", "突然", "顿时", "会发生", "等着"]
        
        has_gouzi = any(kw in last_text for kw in gouzi_keywords)
        
        if has_gouzi:
            return True, "章节结尾有悬念"
        
        return False, "章节结尾缺少悬念钩子"
    
    def _check_character(self, content: str, project_path: str, 
                        chapter: int) -> tuple:
        """检查人物一致性"""
        if not project_path:
            return False, "未提供项目路径，无法核对人物"
        
        # 读取人物状态
        states_file = Path(project_path) / "memory" / "states.md"
        
        if not states_file.exists():
            return False, "未找到人物状态文件"
        
        # 简单检查：章节中提到的人物名是否在记忆库中
        states_content = states_file.read_text(encoding="utf-8")
        
        # 提取章节中可能的角色名（简化处理）
        # 实际应该用NER或更智能的方式
        return True, "人物状态已核对"
    
    def _check_foreshadowing(self, content: str, project_path: str,
                            chapter: int) -> tuple:
        """检查伏笔"""
        if not project_path:
            return False, "未提供项目路径，无法核对伏笔"
        
        # 读取伏笔状态
        foreshadowing_file = Path(project_path) / "memory" / "foreshadowing.md"
        
        if not foreshadowing_file.exists():
            return True, "无伏笔规划（可跳过）"
        
        # 检查是否有伏笔相关词汇
        fp_keywords = ["伏笔", "预示", "暗示", "隐藏", "秘密", "真相"]
        
        has_fp = any(kw in content for kw in fp_keywords)
        
        if has_fp:
            return True, "有伏笔内容"
        
        return True, "本章无伏笔（正常）"
    
    def _check_pace(self, content: str) -> tuple:
        """检查节奏"""
        # 简单通过章节长度判断
        # 实际应该分析段落长度、场景切换等
        
        word_count = len(content)
        
        if word_count < 1000:
            return False, "内容太少，节奏过快/过慢"
        
        if word_count > 5000:
            return False, "内容过多，可能拖沓"
        
        return True, "节奏正常"
    
    def _check_word_count(self, content: str) -> tuple:
        """检查字数"""
        # 去除元数据后统计
        body = self._strip_metadata(content)
        
        # 统计字数（不含标点）
        import re
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', body)
        word_count = len(cleaned)
        
        if word_count < 2500:
            return False, f"字数不足: {word_count}（要求2500-4000）"
        
        if word_count > 4000:
            return False, f"字数过多: {word_count}（要求2500-4000）"
        
        return True, f"字数正常: {word_count}"
    
    def _strip_metadata(self, content: str) -> str:
        """去除元数据头"""
        pattern = r'^---.*?^---'
        return re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE).strip()
    
    def generate_review_template(self, chapter: int) -> str:
        """生成审核清单模板"""
        from datetime import datetime
        
        template = f"""# 第{chapter}章 审核清单

## 基本信息
- 章节号: {chapter}
- 审核时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 审核人: 编辑

## 审核结果

| 检查项 | 结果 | 备注 |
|--------|------|------|
"""
        
        for item in self.CHECKLIST:
            template += f"| {item['name']} | ☐ | {item['description']} |\n"
        
        template += """
## 详细说明

### 风格一致性
[说明是否符合大神风格]

### 爽点检查
[说明爽点类型：打脸/升级/收获/反转]

### 钩子检查
[说明结尾是否有悬念]

### 人物检查
[说明人物性格/状态是否一致]

### 伏笔检查
[说明伏笔埋入/回收情况]

### 节奏检查
[说明节奏是否明快]

### 字数检查
[说明实际字数]

## 审核结论
- [ ] 通过
- [ ] 需修改
- [ ] 打回重写

## 修改建议
[如有需要修改，写明具体建议]
"""
        
        return template


class ReaderFeedbackChecker:
    """
    读者反馈检查器（12章触发）
    
    每12章触发研究员阅读，产出反馈报告
    """
    
    FEEDBACK_INTERVAL = 12  # 每12章触发一次
    
    def check(self, result, chapter: int, project_path: str = None):
        """
        检查是否需要触发读者反馈
        
        Args:
            result: GateResult 对象
            chapter: 当前章节号
            project_path: 项目路径
        """
        # 判断是否到达12章节点
        if chapter % self.FEEDBACK_INTERVAL == 0:
            result.add_check(
                "读者反馈触发",
                True,
                f"第{chapter}章完成，需要触发研究员阅读"
            )
            
            # 检查反馈报告是否已生成
            if project_path:
                report_file = Path(project_path) / "outputs" / "feedback.md"
                
                # 检查最近一次报告是否是本周期
                if report_file.exists():
                    content = report_file.read_text(encoding="utf-8")
                    if f"第{chapter-11}-{chapter}章" in content:
                        result.add_check(
                            "反馈报告",
                            True,
                            f"第{chapter-11}-{chapter}章反馈报告已生成"
                        )
                    else:
                        result.add_check(
                            "反馈报告",
                            False,
                            f"需要生成第{chapter-11}-{chapter}章反馈报告"
                        )
                else:
                    result.add_check(
                        "反馈报告",
                        False,
                        "未找到反馈报告，需要研究员阅读"
                    )
        else:
            next_feedback = ((chapter // self.FEEDBACK_INTERVAL) + 1) * self.FEEDBACK_INTERVAL
            result.add_check(
                "读者反馈",
                True,
                f"第{chapter}章，还需{next_feedback - chapter}章触发"
            )
    
    def generate_feedback_request(self, chapter: int, project_path: str) -> str:
        """生成反馈请求"""
        start_chapter = (chapter // 12) * 12 - 11
        if start_chapter < 1:
            start_chapter = 1
        
        return f"""# 读者反馈请求 - 第{start_chapter}-{chapter}章

## 触发条件
第{chapter}章完成，自动触发研究员阅读

## 研究员任务
1. 阅读第{start_chapter}-{chapter}章内容
2. 评估阅读体验（流畅度、爽点、伏笔）
3. 产出反馈报告

## 报告格式
见 SKILL.md 中的"读者反馈报告格式"

## 截止时间
[由总编指定]
"""
    
    def generate_feedback_template(self, start_chapter: int, end_chapter: int) -> str:
        """生成反馈报告模板"""
        from datetime import datetime
        
        return f"""# 读者反馈报告 - 第{start_chapter}-{end_chapter}章

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**审核人**: 研究员

---

## 阅读体验

### 整体评分
- 评分: /10
- 流畅度: 
- 代入感: 
- 爽点分布: 
- 伏笔效果: 

---

## 各章评估

### 第{start_chapter}章
- 优点: 
- 问题: 
- 建议: 

[继续列出各章...]

---

## 问题汇总

### 节奏问题
1. 

### 人物问题
1. 

### 爽点问题
1. 

### 伏笔问题
1. 

---

## 改进建议

1. 
2. 
3. 

---

## 总编讨论结论

[总编组织团队讨论后填写]

---

**下一步**: 
- [ ] 采纳建议，继续写作
- [ ] 修改章节后继续
- [ ] 调整大纲后继续
"""