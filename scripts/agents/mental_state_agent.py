#!/usr/bin/env python3
"""mental_state_agent.py — 精神状态深度审核 Agent v0.7.1

检查角色精神状况描写是否合理、一致、自然融入叙事。
仅参与 --mode full 审核。

3 条规则：
  1. trigger-manifest 匹配 —— 触发词出现时附近应有对应表现
  2. severity 合理性 —— 文本情感强度与设定 severity 匹配
  3. 自然度 —— 精神状况描写是否自然融入叙事
"""
import re
from pathlib import Path
from .base_agent import BaseAgent


# 情绪极端词（用于 severity 合理性判断）
EXTREME_EMOTION_WORDS = {
    "极度": 5, "非常": 3, "无比": 4, "万分": 4, "极其": 4, "绝顶": 4,
    "撕心裂肺": 5, "痛不欲生": 5, "生不如死": 5, "肝肠寸断": 5,
    "欣喜若狂": 4, "暴跳如雷": 4, "怒不可遏": 4, "惊恐万状": 5,
    "毛骨悚然": 4, "魂飞魄散": 5, "肝胆俱裂": 5,
    "微微": 1, "些许": 1, "有点": 1, "有些": 1,
}

# 渐进铺垫词（自然度正向信号）
PROGRESSIVE_WORDS = [
    "渐渐", "慢慢", "越来越", "日益", "日复一日", "反复",
    "开始", "有些", "有点", "似乎", "仿佛", "隐约",
]

# 生硬插入词（自然度负向信号）
ABRUPT_WORDS = [
    "突然", "忽然", "猛地", "一下子", "毫无征兆",
    "莫名其妙", "不知道为什么", "毫无理由",
]

# 精神病理直接标签（自然度负向信号）
DIAGNOSTIC_LABELS = [
    "他疯了", "她疯了", "他精神", "她精神", "心理变态",
    "神经病", "精神病", "他有病", "她有病",
]


class MentalStateAgent(BaseAgent):
    """精神状态深度审核 Agent"""

    def __init__(self, config: dict = None):
        super().__init__(name="mental_state", config=config)

    def review(self, content: str, chapter_no: int = 0,
               context: dict = None) -> dict:
        findings = []
        score = 60
        ctx = context or {}

        # 获取所有角色精神状态
        cards = self._load_mental_states(ctx)
        if not cards:
            return self._build_result(
                100, "PASS",
                [self._make_finding("PASS", "无角色精神状态数据，跳过审核")],
            )

        total_chars = len(content)

        for card in cards:
            name = card.get("name", "?")
            ms = card.get("mental_state", {})
            if not ms:
                continue

            for cat, data in ms.items():
                if data is None:
                    continue
                severity = data.get("severity", 0)
                if severity == 0:
                    continue

                triggers = data.get("triggers", [])
                manifestations = data.get("manifestations", [])

                # ── Rule 1: trigger-manifest 匹配 ──
                if triggers:
                    active_triggers = []
                    for t in triggers:
                        t_pos = content.find(t)
                        if t_pos >= 0:
                            active_triggers.append((t, t_pos))
                    if active_triggers:
                        # 检查每个 trigger 附近是否有 manifestation
                        missing_manifests = []
                        for t, pos in active_triggers:
                            window = content[max(0, pos - 100):pos + 300]
                            has_manifest = False
                            for m in manifestations:
                                if m in window:
                                    has_manifest = True
                                    break
                            if not has_manifest:
                                missing_manifests.append(t)

                        if missing_manifests:
                            findings.append(self._make_finding(
                                "WARN",
                                f"「{name}」的「{cat}」触发词「{'/'.join(missing_manifests[:3])}」"
                                f"出现在文本中但附近未见对应症状表现",
                                evidence=content[max(0, active_triggers[0][1] - 50):active_triggers[0][1] + 150],
                                suggestion=f"在触发场景附近加入「{name}」的{cat}反应描写，"
                                           f"如: {'/'.join(manifestations[:3]) if manifestations else '颤抖、回避、闪回等'}",
                            ))
                            score -= 15

                # ── Rule 2: severity 合理性（仅分析角色附近文本）──
                if severity > 0:
                    char_text = self._get_char_text_segments(content, name)
                    extreme_score = self._calc_emotion_intensity(char_text)
                    expected_score = severity * 10  # severity 1→10, 5→50
                    deviation = abs(extreme_score - expected_score)

                    if deviation > 15:
                        direction = "偏高" if extreme_score > expected_score else "偏低"
                        level = "FAIL" if deviation > 25 else "WARN"
                        score -= 20 if deviation > 25 else 15
                        findings.append(self._make_finding(
                            level,
                            f"「{name}」的「{cat}」设定 severity={severity}，"
                            f"但本章情绪极端词强度 {extreme_score}，{direction}约 {deviation} 分",
                            suggestion=("情绪描写过重，请收敛极端用词" if direction == "偏高"
                                       else f"增加对「{name}」{cat}症状的正面描写以匹配设定严重度"),
                        ))

                # ── Rule 3: 自然度 ──
                naturality_score = self._check_naturality(content, cat, severity)
                if naturality_score < 0:
                    findings.append(self._make_finding(
                        "WARN" if naturality_score > -3 else "FAIL",
                        f"「{name}」的「{cat}」描写缺乏渐进铺垫"
                        if naturality_score > -3
                        else f"「{name}」的「{cat}」描写生硬，使用了直接诊断式语言",
                        suggestion="建议通过行为、微表情、环境互动渐进式展现精神状态，"
                                   "避免直接给角色贴精神病理标签",
                    ))
                    score -= 15 if naturality_score > -3 else 25

        # 汇总
        score = max(0, min(100, score))
        status = "PASS" if score >= 45 else ("WARNING" if score >= 30 else "FAIL")

        if not findings:
            findings.append(self._make_finding(
                "PASS", "角色精神状态描写合理，无显著问题"))

        return self._build_result(score, status, findings)

    def _load_mental_states(self, context: dict) -> list:
        """从当前 slot 加载所有角色的精神状态数据."""
        try:
            from src.guards.human_texture.mental_state_crud import list_mental_states
            from src.cli.shared import PROJECT_ROOT
            return list_mental_states(PROJECT_ROOT)
        except Exception:
            return []

    def _calc_emotion_intensity(self, text: str) -> int:
        """计算文本情绪极端词强度总分."""
        total = 0
        for word, weight in EXTREME_EMOTION_WORDS.items():
            count = text.count(word)
            total += count * weight
        return total

    def _get_char_text_segments(self, content: str, char_name: str, window: int = 200) -> str:
        """提取角色名附近文本段用于 per-character 分析."""
        segments = []
        pos = 0
        while True:
            idx = content.find(char_name, pos)
            if idx == -1:
                break
            start = max(0, idx - window)
            end = min(len(content), idx + len(char_name) + window)
            segments.append(content[start:end])
            pos = end
        return " ".join(segments)

    def _check_naturality(self, text: str, category: str, severity: int) -> int:
        """检查精神状况自然度评分.

        Returns:
            正分 = 自然, 负分 = 生硬, 0 = 中性
        """
        progressive_count = sum(1 for w in PROGRESSIVE_WORDS if w in text)
        abrupt_count = sum(1 for w in ABRUPT_WORDS if w in text)
        label_count = sum(1 for w in DIAGNOSTIC_LABELS if w in text)

        # 低 severity 使用渐进词是好的
        if severity <= 2 and progressive_count > 0:
            return 1

        # 直接诊断标签 → 生硬
        if label_count > 0:
            return -5

        # 突兀词过多 → 生硬
        if abrupt_count > 3:
            return -2

        # 高 severity 但无渐进铺垫 → 略生硬
        if severity >= 4 and progressive_count == 0:
            return -1

        return 0
