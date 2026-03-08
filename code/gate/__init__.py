"""
网文编辑部 - 自动化门禁检查器

职责：在每个关键节点自动检查，发现问题立即阻断
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 检查器模块
from .checks.metadata import MetadataChecker
from .checks.wordcount import WordCountChecker
from .checks.ai_detector import AIDetector
from .checks.memory_query import MemoryQueryChecker
from .checks.editor_review import EditorReviewChecker, ReaderFeedbackChecker


class GateType(Enum):
    WRITER_BEFORE_WRITE = "写手写作前"      # 检查记忆库查询
    WRITER_AFTER_WRITE = "写手写作后"      # 检查元数据+字数
    EDITOR_BEFORE_REVIEW = "编辑审核前"     # 检查记忆库
    EDITOR_REVIEW = "编辑审核"             # 逐项审核清单
    EDITOR_AFTER_REVIEW = "编辑审核后"     # 审核结果
    EDITOR_BEFORE_CONFIRM = "总编确认前"    # 检查元数据+AI去味
    READER_FEEDBACK = "读者反馈"            # 12章触发研究员
    CHECKPOINT = "检查点"                   # 3章完成触发


@dataclass
class GateResult:
    """门禁检查结果"""
    gate_type: GateType
    passed: bool
    checks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_check(self, name: str, passed: bool, detail: str = ""):
        self.checks.append({
            "name": name,
            "passed": passed,
            "detail": detail
        })
        if not passed:
            self.errors.append(f"❌ {name}: {detail}")
        elif detail:
            self.warnings.append(f"⚠️ {name}: {detail}")
    
    def summary(self) -> str:
        status = "✅ 通过" if self.passed else "❌ 阻断"
        lines = [f"\n{'='*50}", f"门禁检查: {self.gate_type.value}", f"状态: {status}"]
        
        if self.errors:
            lines.append("\n【错误 - 必须修复】")
            for e in self.errors:
                lines.append(f"  {e}")
        
        if self.warnings:
            lines.append("\n【警告】")
            for w in self.warnings:
                lines.append(f"  {w}")
        
        lines.append(f"\n时间: {self.timestamp}")
        lines.append(f"{'='*50}")
        
        return "\n".join(lines)


class GateChecker:
    """
    自动化门禁检查器
    
    使用方法:
        gate = GateChecker(project_path)
        
        # 写手写作前检查
        result = gate.check(GateType.WRITER_BEFORE_WRITE)
        if not result.passed:
            print(result.summary())
            sys.exit(1)
        
        # 写手写作后检查
        result = gate.check(GateType.WRITER_AFTER_WRITE, chapter_file="chapters/03.md")
    """
    
    # AI词汇黑名单
    AI_FORBIDDEN_WORDS = [
        "值得注意的是", "需要强调的是", "事实上", "实际上", 
        "首先", "其次", "最后", "总之", "综上所述",
        "此外", "与此同时", "至关重要", "深入探讨",
    ]
    
    AI_FORBIDDEN_PATTERNS = [
        r"不仅.*而且.*", r"从\d+到\d+", r"这不仅仅是.*而是.*",
        r"\d+个?方面", r"第一.*第二.*第三", r"一方面.*另一方面.*",
    ]
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_path = self.project_path / "memory"
        self.outputs_path = self.project_path / "outputs"
        self.chapters_path = self.outputs_path / "chapters"
        
        # 初始化检查器
        self.checkers = {
            "metadata": MetadataChecker(),
            "wordcount": WordCountChecker(),
            "ai_detector": AIDetector(self.AI_FORBIDDEN_WORDS, self.AI_FORBIDDEN_PATTERNS),
            "memory_query": MemoryQueryChecker(),
            "editor_review": EditorReviewChecker(),
            "reader_feedback": ReaderFeedbackChecker(),
        }
    
    def check(self, gate_type: GateType, **kwargs) -> GateResult:
        """执行门禁检查"""
        result = GateResult(gate_type=gate_type, passed=True)
        role = kwargs.get("role", "writer")
        
        # 根据门禁类型执行不同检查
        if gate_type == GateType.WRITER_BEFORE_WRITE:
            self._check_writer_before_write(result, **kwargs)
        elif gate_type == GateType.WRITER_AFTER_WRITE:
            self._check_writer_after_write(result, **kwargs)
        elif gate_type == GateType.EDITOR_BEFORE_REVIEW:
            self._check_editor_before_review(result, **kwargs)
        elif gate_type == GateType.EDITOR_REVIEW:
            self._check_editor_review(result, **kwargs)
        elif gate_type == GateType.EDITOR_AFTER_REVIEW:
            self._check_editor_after_review(result, **kwargs)
        elif gate_type == GateType.EDITOR_BEFORE_CONFIRM:
            self._check_editor_before_confirm(result, **kwargs)
        elif gate_type == GateType.READER_FEEDBACK:
            self._check_reader_feedback(result, **kwargs)
        elif gate_type == GateType.CHECKPOINT:
            self._check_checkpoint(result, **kwargs)
        
        # 判断是否通过（有任何错误就阻断）
        result.passed = len(result.errors) == 0
        
        return result
    
    def _check_writer_before_write(self, result: GateResult, **kwargs):
        """写手写作前检查：必须查询记忆库"""
        chapter = kwargs.get("chapter", 1)
        
        # 检查是否查询了记忆库
        query_record = self.memory_path / "query_log.md"
        if not query_record.exists():
            result.add_check(
                "记忆库查询",
                False,
                f"第{chapter}章写作前必须查询记忆库，请先查询后再开始写作"
            )
            return
        
        # 读取查询记录，检查是否包含本章相关内容
        content = query_record.read_text(encoding="utf-8")
        has_query = (
            f"第{chapter}章" in content or 
            f"chapter {chapter}" in content.lower() or
            "人物状态" in content or
            "伏笔" in content
        )
        
        if not has_query:
            result.add_check(
                "记忆库查询",
                False,
                f"未找到第{chapter}章的查询记录，请先查询记忆库"
            )
        else:
            result.add_check("记忆库查询", True, "已查询记忆库")
        
        # 检查风格文件
        style_file = self.memory_path / "project.md"
        if not style_file.exists():
            result.add_check("风格文件", False, "未找到风格配置")
        else:
            result.add_check("风格文件", True, "已读取风格配置")
        
        # 检查前一章摘要（如果是第2章及以上）
        if chapter > 1:
            chapters_file = self.memory_path / "chapters.md"
            if not chapters_file.exists():
                result.add_check(
                    "前一章摘要",
                    False,
                    f"未找到前一章摘要，请等待编辑整理第{chapter-1}章摘要"
                )
                return
            
            # 检查前一章是否有摘要
            chapters_content = chapters_file.read_text(encoding="utf-8")
            prev_chapter_patterns = [
                f"chapter: {chapter-1}",
                f"章节: {chapter-1}",
                f"第{chapter-1}章"
            ]
            
            has_prev_summary = any(p in chapters_content for p in prev_chapter_patterns)
            
            if not has_prev_summary:
                result.add_check(
                    "前一章摘要",
                    False,
                    f"第{chapter-1}章摘要尚未整理，请等待编辑完成后再开始写作"
                )
            else:
                result.add_check("前一章摘要", True, "已存在")
    
    def _check_writer_after_write(self, result: GateResult, **kwargs):
        """写手写作后检查：元数据 + 字数"""
        chapter_file = kwargs.get("chapter_file")
        target_words = kwargs.get("target_words", 3000)
        
        if not chapter_file:
            result.add_check("章节文件", False, "未提供章节文件路径")
            return
        
        chapter_path = self.chapters_path / chapter_file
        if not chapter_path.exists():
            result.add_check("章节文件", False, f"文件不存在: {chapter_path}")
            return
        
        content = chapter_path.read_text(encoding="utf-8")
        
        # 检查元数据（写手角色）
        self.checkers["metadata"].check(content, result, role="writer")
        
        # 检查字数（由编辑器统计的实际字数）
        if self.checkers["metadata"]._extract_metadata_from_end(content):
            metadata = self.checkers["metadata"]._extract_metadata_from_end(content)
            word_count = metadata.get("draft_word_count", "0")
            if word_count and word_count.isdigit():
                wc = int(word_count)
                percentage = wc / target_words * 100 if target_words > 0 else 0
                if wc >= target_words:
                    result.add_check("字数", True, f"{wc}字 (目标{target_words}字)")
                elif wc >= target_words * 0.8:
                    result.add_check("字数", True, f"{wc}字 (最低{target_words*0.8}字)")
                else:
                    result.add_check("字数", False, f"字数不足: {wc}/{target_words}字 ({percentage:.0f}%)")
            else:
                result.add_check("字数", False, "字数未填写或格式错误")
    
    def _check_editor_before_review(self, result: GateResult, **kwargs):
        """编辑审核前检查"""
        # 检查是否有待审核章节
        chapter = kwargs.get("chapter", 1)
        chapter_file = self.chapters_path / f"chapter-{chapter:02d}.md"
        
        if not chapter_file.exists():
            result.add_check("待审章节", False, f"第{chapter}章不存在")
        else:
            result.add_check("待审章节", True, f"第{chapter}章待审核")
    
    def _check_editor_after_review(self, result: GateResult, **kwargs):
        """编辑审核后检查"""
        review_status = kwargs.get("status")  # "pass" or "reject"
        
        if review_status == "pass":
            result.add_check("审核结果", True, "审核通过")
        elif review_status == "reject":
            result.add_check("审核结果", False, "审核被拒绝，需修改后重审")
        else:
            result.add_check("审核结果", False, f"未知状态: {review_status}")
    
    def _check_editor_review(self, result: GateResult, **kwargs):
        """编辑逐项审核检查"""
        chapter_file = kwargs.get("chapter_file")
        
        if not chapter_file:
            result.add_check("审核输入", False, "未提供章节文件")
            return
        
        chapter_path = self.chapters_path / chapter_file
        if not chapter_path.exists():
            result.add_check("章节文件", False, f"文件不存在: {chapter_path}")
            return
        
        content = chapter_path.read_text(encoding="utf-8")
        
        # 执行编辑审核清单
        reviewer = self.checkers.get("editor_review")
        if reviewer:
            reviewer.check(result, chapter_file=str(chapter_path), 
                         content=content, 
                         project_path=str(self.project_path),
                         chapter=kwargs.get("chapter", 1))
        else:
            result.add_check("审核检查器", False, "未找到审核检查器")
    
    def _check_reader_feedback(self, result: GateResult, **kwargs):
        """读者反馈检查（12章触发）"""
        chapter = kwargs.get("chapter", 0)
        
        checker = self.checkers.get("reader_feedback")
        if checker:
            checker.check(result, chapter=chapter, 
                        project_path=str(self.project_path))
        else:
            result.add_check("读者反馈检查器", False, "未找到检查器")
    
    def _check_editor_before_confirm(self, result: GateResult, **kwargs):
        """总编确认前检查：元数据 + AI去味 + 字数"""
        chapter_file = kwargs.get("chapter_file")
        role = kwargs.get("role", "editor_chief")
        
        if chapter_file:
            chapter_path = self.chapters_path / chapter_file
            if chapter_path.exists():
                content = chapter_path.read_text(encoding="utf-8")
                
                # 元数据检查（总编角色）
                self.checkers["metadata"].check(content, result, role=role)
                
                # AI去味检查
                self.checkers["ai_detector"].check(content, result)
                
                # 字数检查（从元数据获取实际统计值）
                metadata = self.checkers["metadata"]._extract_metadata_from_end(content)
                if metadata:
                    final_word_count = metadata.get("final_word_count", metadata.get("editor_word_count", "0"))
                    if final_word_count and final_word_count.isdigit():
                        wc = int(final_word_count)
                        target = kwargs.get("target_words", 3000)
                        percentage = wc / target * 100 if target > 0 else 0
                        if wc >= target * 0.8:
                            result.add_check("实际字数", True, f"{wc}字 (统计)")
                        else:
                            result.add_check("实际字数", False, f"字数不足: {wc}/~{target}字")
                    else:
                        result.add_check("实际字数", False, "未填写最终字数")
        
        # 检查章节元数据是否完整
        chapter = kwargs.get("chapter", 1)
        chapters_meta = self.memory_path / "chapters.md"
        
        if not chapters_meta.exists():
            result.add_check("记忆库章节记录", False, "未找到章节记录")
        else:
            result.add_check("记忆库章节记录", True, "已记录")
    
    def _check_checkpoint(self, result: GateResult, **kwargs):
        """检查点触发检查"""
        chapter = kwargs.get("chapter", 0)
        
        # 必须满足3章条件
        if chapter % 3 != 0:
            result.add_check(
                "检查点条件",
                False,
                f"第{chapter}章不是3的倍数，无法触发checkpoint"
            )
            return
        
        # 检查前3章是否都已完成审核
        for i in range(1, chapter + 1):
            chapter_file = self.chapters_path / f"chapter-{i:02d}.md"
            if not chapter_file.exists():
                result.add_check(
                    "章节完整性",
                    False,
                    f"第{i}章不存在，无法生成checkpoint"
                )
                continue
            
            # 检查审核是否通过（必须有editor_review_time和final_time）
            content = chapter_file.read_text(encoding="utf-8")
            metadata = self.checkers["metadata"]._extract_metadata_from_end(content)
            
            if not metadata:
                result.add_check(
                    f"第{i}章元数据",
                    False,
                    f"第{i}章缺少元数据"
                )
                continue
            
            # 检查编辑审核时间
            if not metadata.get("editor_review_time"):
                result.add_check(
                    f"第{i}章编辑审核",
                    False,
                    f"第{i}章编辑尚未审核通过"
                )
            
            # 检查总编确认时间
            if not metadata.get("final_time"):
                result.add_check(
                    f"第{i}章总编确认",
                    False,
                    f"第{i}章总编尚未确认"
                )
        
        if not result.errors:
            result.add_check(
                "检查点条件",
                True,
                f"第{chapter}章完成，3章审核全部通过，可生成checkpoint"
            )
    
    def log_gate_result(self, result: GateResult):
        """记录门禁检查结果"""
        log_dir = self.project_path / "monitoring"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "gate_log.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"\n## [{timestamp}] {result.gate_type.value}\n"
        log_entry += f"**状态**: {'✅ 通过' if result.passed else '❌ 阻断'}\n\n"
        
        if result.checks:
            log_entry += "| 检查项 | 结果 | 详情 |\n"
            log_entry += "|--------|------|------|\n"
            for check in result.checks:
                status = "✅" if check["passed"] else "❌"
                log_entry += f"| {check['name']} | {status} | {check['detail']} |\n"
        
        if result.errors:
            log_entry += "\n**错误**:\n"
            for e in result.errors:
                log_entry += f"- {e}\n"
        
        log_entry += "\n---\n"
        
        # 追加写入
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def auto_checkpoint(self, chapter: int) -> Optional[Path]:
        """自动生成检查点"""
        if chapter % 3 != 0:
            return None
        
        checkpoint_dir = self.memory_path / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint-{chapter:03d}.yaml"
        
        # 生成checkpoint内容
        from .checkpoint import generate_checkpoint
        
        content = generate_checkpoint(
            project_path=str(self.project_path),
            chapter=chapter
        )
        
        checkpoint_file.write_text(content, encoding="utf-8")
        
        return checkpoint_file


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="网文编辑部 - 门禁检查器")
    parser.add_argument("project", help="项目路径")
    parser.add_argument("gate", choices=[
        "writer-before", "writer-after", 
        "editor-before", "editor-review", "editor-after",
        "editor-confirm", "reader-feedback", "checkpoint"
    ], help="门禁类型")
    parser.add_argument("--chapter", type=int, default=1, help="章节号")
    parser.add_argument("--file", help="章节文件路径")
    parser.add_argument("--target-words", type=int, default=3000, help="目标字数")
    parser.add_argument("--review-status", choices=["pass", "reject"], help="审核状态")
    parser.add_argument("--auto-checkpoint", action="store_true", help="自动生成checkpoint")
    
    args = parser.parse_args()
    
    # 映射到GateType
    gate_map = {
        "writer-before": GateType.WRITER_BEFORE_WRITE,
        "writer-after": GateType.WRITER_AFTER_WRITE,
        "editor-before": GateType.EDITOR_BEFORE_REVIEW,
        "editor-review": GateType.EDITOR_REVIEW,
        "editor-after": GateType.EDITOR_AFTER_REVIEW,
        "editor-confirm": GateType.EDITOR_BEFORE_CONFIRM,
        "reader-feedback": GateType.READER_FEEDBACK,
        "checkpoint": GateType.CHECKPOINT,
    }
    
    gate_type = gate_map[args.gate]
    
    # 执行检查
    gate = GateChecker(args.project)
    result = gate.check(
        gate_type,
        chapter=args.chapter,
        chapter_file=args.file,
        target_words=args.target_words,
        status=args.review_status,
    )
    
    # 打印结果
    print(result.summary())
    
    # 记录日志
    gate.log_gate_result(result)
    
    # 自动checkpoint
    if args.auto_checkpoint and result.passed:
        checkpoint_file = gate.auto_checkpoint(args.chapter)
        if checkpoint_file:
            print(f"\n✅ 已生成检查点: {checkpoint_file}")
    
    # 返回退出码
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()