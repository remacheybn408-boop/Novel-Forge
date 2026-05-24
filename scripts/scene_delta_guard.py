#!/usr/bin/env python3
"""
scene_delta_guard.py — 场景推进证据门禁 v0.3.1-calibrated

split_scene_or_beats: 显式转场 → narrative beat → paragraph window → single scene multi-delta
不再因为 scene_count=1 直接 FAIL。
"""
import re, json, sys, argparse
from pathlib import Path


# ═══════════════════════════════════════════════════
# 场景/节拍拆分
# ═══════════════════════════════════════════════════

STRONG_SCENE_MARKERS = [
    r'^(第.{1,4}天|早上|傍晚|晚上|深夜|第二天|次日|清晨|黄昏|午后|下午|当天|不久之后|与此同时|另一边)',
    r'^(回到|来到|走进|出了|站在|蹲在|坐在|躺在|来到)',
    r'^(\*{3,}|-{3,}|#{1,3}\s)',
    r'^(……|\.{4,})',
]

# Narrative beat markers
BEAT_OBSERVATION = re.compile(r'(发现|察觉|注意|看到|观察到|判断|推测|看出|注意到|测量|验证|确认|检测)')
BEAT_CONFLICT = re.compile(r'(质疑|对峙|僵|反问|压迫|阻拦|阻止|反对|对抗|冲突|矛盾|争执|较量|斗法|战斗|打斗|瞪|挑衅|威逼|刁难|威胁)')
BEAT_ACTION = re.compile(r'(尝试|测量|推演|验证|触碰|调整|测试|试|试验|搬|劈|挖|运|炼|烧|刮|磨|刻|写|画)')
BEAT_REACTION = re.compile(r'(沉默|犹豫|改变态度|退让|接受|怀疑|认命|不甘|愤怒|紧张|镇静|冷静|决定|选择|放弃|坚持|转变|动摇|坚定)')
BEAT_RESULT = re.compile(r'(得出|出现|被验证|失败|成立|成功|完成|确认|证实|了结|结束)')
BEAT_HOOK = re.compile(r'(但.{0,20}(?:突然|忽然|竟然|却)|然而.{0,20}(?:发现|出现)|而.{0,10}(?:不知|还没|尚未)|留下|遗留|新的|异常|奇怪|不对)')

BEAT_PATTERNS = [
    ("observation_beat", BEAT_OBSERVATION),
    ("conflict_beat", BEAT_CONFLICT),
    ("action_beat", BEAT_ACTION),
    ("reaction_beat", BEAT_REACTION),
    ("result_beat", BEAT_RESULT),
    ("hook_beat", BEAT_HOOK),
]


def split_by_strong_markers(paragraphs):
    """按显式场景标记拆分"""
    boundaries = [0]
    for i, p in enumerate(paragraphs[1:], 1):
        for marker in STRONG_SCENE_MARKERS:
            if re.match(marker, p):
                boundaries.append(i)
                break
    if len(boundaries) < 2:
        return []
    scenes = []
    for j, start_idx in enumerate(boundaries):
        end_idx = boundaries[j+1] if j+1 < len(boundaries) else len(paragraphs)
        scene_text = "\n".join(paragraphs[start_idx:end_idx])
        if len(scene_text.strip()) > 50:
            scenes.append({"text": scene_text, "start": start_idx, "end": end_idx-1})
    # Merge small opening scenes into next
    MIN_SCENE_CHARS = 300
    merged = []
    for s in scenes:
        cn = len([c for c in s["text"] if '\u4e00' <= c <= '\u9fff'])
        if merged and cn < MIN_SCENE_CHARS:
            merged[-1]["text"] += "\n" + s["text"]
            merged[-1]["end"] = s["end"]
        else:
            merged.append(s)
    return merged if len(merged) >= 2 else []


def split_by_narrative_beats(paragraphs):
    """按叙事节拍拆分，合并过小的相邻 beat"""
    beats = []
    current = []
    current_beat_type = None

    for p in paragraphs:
        p = p.strip()
        if not p or p.startswith("="):
            if current:
                beats.append({"text": "\n".join(current), "beat_type": current_beat_type or "transition"})
                current = []
                current_beat_type = None
            continue

        matched = False
        for beat_name, pattern in BEAT_PATTERNS:
            if pattern.search(p):
                if current and current_beat_type and current_beat_type != beat_name:
                    beats.append({"text": "\n".join(current), "beat_type": current_beat_type})
                    current = []
                current.append(p)
                current_beat_type = beat_name
                matched = True
                break

        if not matched:
            current.append(p)

    if current:
        beats.append({"text": "\n".join(current), "beat_type": current_beat_type or "transition"})

    # 合并过小的 beat（< 200 中文字符）
    MIN_BEAT_CHARS = 200
    merged = []
    for b in beats:
        cn_chars = len([c for c in b["text"] if '\u4e00' <= c <= '\u9fff'])
        if merged and cn_chars < MIN_BEAT_CHARS:
            merged[-1]["text"] += "\n" + b["text"]
        else:
            merged.append(b)

    if len(merged) < 2:
        return []
    return merged


def split_by_paragraph_window(paragraphs, window_size=4):
    """按固定窗口拆分（兜底）"""
    windows = []
    for i in range(0, len(paragraphs), window_size):
        chunk = paragraphs[i:i+window_size]
        text = "\n".join(chunk)
        if len(text.strip()) > 50:
            windows.append({"text": text, "beat_type": "window"})
    if len(windows) < 2:
        return []
    return windows


def split_scene_or_beats(content):
    """
    三层 fallback：
    1. 显式场景标记 → scenes
    2. 叙事节拍 → beats
    3. 段落窗口 → windows
    4. 单场景多 delta → single
    """
    paragraphs = [p.strip() for p in content.split("\n") if p.strip() and not p.startswith("=")]

    # 1. Scene markers
    scenes = split_by_strong_markers(paragraphs)
    if scenes:
        return "scene_marker", scenes

    # 2. Narrative beats
    beats = split_by_narrative_beats(paragraphs)
    if beats:
        return "narrative_beat", beats

    # 3. Paragraph windows
    windows = split_by_paragraph_window(paragraphs)
    if windows:
        return "paragraph_window", windows

    # 4. Single scene
    return "single_scene_multi_delta", [{"text": content, "beat_type": "continuous", "start": 0, "end": len(paragraphs)-1}]


# ═══════════════════════════════════════════════════
# Delta 分析
# ═══════════════════════════════════════════════════

def analyze_scene_delta(item):
    """分析单个场景/节拍的推进量"""
    text = item["text"]
    wc = len([c for c in text if '\u4e00' <= c <= '\u9fff'])

    delta = {
        "plot": "",
        "character_state": "",
        "relationship": "",
        "conflict": "",
        "worldbuilding": "",
        "reader_promise": "",
        "next_hook": ""
    }

    if re.search(r'(发现|察觉|注意|看到|听到|找到|获得|失去|完成|失败|成功|判断|推测|看出|注意到|观察到|测量|验证|确认)', text):
        delta["plot"] = "新发现或事件推进"
    if re.search(r'(决定|选择|放弃|坚持|改变|转变|动摇|坚定|犹豫|认命|不甘|愤怒|紧张|镇静|冷静)', text):
        delta["character_state"] = "人物状态变化"
    if re.search(r'(争吵|和解|合作|背叛|信任|怀疑|感激|怨恨|试探|打量|审视)', text):
        delta["relationship"] = "关系互动或变化"
    if re.search(r'(阻止|反对|对抗|冲突|矛盾|争执|较量|斗法|战斗|打斗|对峙|僵|瞪|挑衅|威逼|刁难|威胁)', text):
        delta["conflict"] = "冲突升级或解决"
    if re.search(r'(规则|法则|定律|原理|机制|体系|结构|本源|天道|灵力|灵气)', text):
        delta["worldbuilding"] = "世界观揭示或深化"
    if re.search(r'(约定|承诺|答应|保证|誓言|一定会|必须|早晚有一天)', text):
        delta["reader_promise"] = "读者承诺推进"
    if re.search(r'(但.{0,20}(?:突然|忽然|竟然|却)|然而.{0,20}(?:发现|出现)|而.{0,10}(?:不知|还没|尚未))', text):
        delta["next_hook"] = "留下悬念或钩子"

    delta_count = sum(1 for v in delta.values() if v)
    item_type = item.get("beat_type", "scene")

    return {
        "scene_no": 0,  # filled later
        "scene_role": item_type,
        "word_count": wc,
        "delta": delta,
        "delta_count": delta_count,
        "scene_passed": delta_count >= 2
    }


# ═══════════════════════════════════════════════════
# 单场景多 delta 判定
# ═══════════════════════════════════════════════════

def check_single_scene_multi_delta(analyzed, content, padding_score=0):
    """全章只有一个场景/节拍时的特殊判定"""
    if len(analyzed) != 1:
        return False

    s = analyzed[0]
    d = s["delta"]

    conditions = [
        bool(d["plot"]),
        bool(d["conflict"] or d["character_state"]),
        bool(d["reader_promise"] or d["next_hook"]),
        s["word_count"] >= 1900,
        padding_score <= 60,
    ]
    return all(conditions)


# ═══════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════

def run_scene_delta_check(content, chapter_type="normal", padding_score=0):
    """主入口"""

    split_mode, items = split_scene_or_beats(content)

    if not items:
        return {
            "scenes": [],
            "split_mode": "none",
            "scene_or_beat_count": 0,
            "effective_scene_delta_count": 0,
            "single_scene_but_multi_delta": False,
            "low_delta_scenes": [],
            "overall_passed": False,
        }

    analyzed = [analyze_scene_delta(item) for item in items]
    for i, a in enumerate(analyzed):
        a["scene_no"] = i + 1

    effective_delta_count = sum(s["delta_count"] for s in analyzed)
    low_delta = [s for s in analyzed if s["delta_count"] < 2]

    is_short = chapter_type in ("authorized_short", "fragment", "short")

    # 单场景多 delta 判定
    single_multi = check_single_scene_multi_delta(analyzed, content, padding_score)

    if is_short:
        passed = effective_delta_count >= 1
    elif single_multi:
        passed = True
    elif split_mode == "single_scene_multi_delta":
        # 单场景但不是多 delta → fail
        passed = False
    else:
        # 标准判定：总delta足够 OR 低delta数可控
        min_delta = 3
        max_low = max(1, len(analyzed) // 2)
        passed = (
            effective_delta_count >= min_delta and len(low_delta) <= max_low
        ) or (
            # 高总delta可补偿分布不均
            effective_delta_count >= 5 and len(analyzed) >= 3
        )

    report = {
        "scenes": analyzed,
        "split_mode": split_mode,
        "scene_or_beat_count": len(analyzed),
        "single_scene_but_multi_delta": single_multi,
        "effective_scene_delta_count": effective_delta_count,
        "low_delta_scenes": [s["scene_no"] for s in low_delta],
        "overall_passed": passed,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Scene Delta Guard")
    parser.add_argument("content_file", help="章节 TXT 文件")
    parser.add_argument("--chapter-type", default="normal",
                        choices=["normal", "climax", "final", "short", "authorized_short", "fragment"])
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    content = Path(args.content_file).read_text(encoding="utf-8")
    report = run_scene_delta_check(content, args.chapter_type)

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[OK] report saved: {args.output}")

    if not report["overall_passed"]:
        print(f"\n[FAIL] Scene delta check failed")
        print(f"  split_mode: {report['split_mode']}")
        print(f"  effective_delta: {report['effective_scene_delta_count']}")
        sys.exit(1)
    else:
        print(f"\n[OK] Scene delta check passed ({report['split_mode']}, {report['effective_scene_delta_count']} deltas)")


if __name__ == "__main__":
    main()
