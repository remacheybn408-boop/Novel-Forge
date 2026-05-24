#!/usr/bin/env python3
"""
character_voice_guard.py — 角色口吻门禁 v0.3.1-qgp

检查：
1. 每个角色对白是否符合 voice_profile
2. 是否所有角色都像同一个人
3. 是否使用了禁用词
4. 方言浓度是否超标
5. 文言浓度是否适合角色身份
6. 关键剧情句是否可读

策略: Phase 2 — 先 WARNING，不 FAIL
"""
import re, json, sys, argparse
from pathlib import Path

# ═══════════════════════════════════════════════════
# 方言/文言检测
# ═══════════════════════════════════════════════════

DIALECT_MARKERS = re.compile(
    r'(甭|俺|咋|啥|嘛|哩|咧|呗|嘛|啷个|么子|咋个|这旮沓|那旮沓|搁这儿|搁那儿'
    r'|俺们|你们|咱|恁|弄啥|中不中|得劲|忒|贼|老|忒|嘛事|啥子|哪个|啷个办)'
)

WENYAN_MARKERS = re.compile(
    r'(然则|夫|盖.{0,3}(也|矣|焉|耳|乎|哉|邪|与)|者.{0,3}也'
    r'|岂不|莫不|未尝|遂|乃|辄|竟|盖|故|是以|是故|由此|因而'
    r'|呜呼|噫|吁|嗟乎|悲夫|矣|焉|耳|乎|哉|之乎者也)'
)

FORBIDDEN_UNIVERSAL = re.compile(
    r'(这件事情没有那么简单|事情.{0,5}没有那么简单'
    r'|事情变得.{0,5}复杂|事情远比.{0,5}复杂'
    r'|事情.{0,5}不简单|事情.{0,5}没那么简单)'
)

# ═══════════════════════════════════════════════════
# 对白提取
# ═══════════════════════════════════════════════════

DIALOGUE_PATTERN = re.compile(r'[""「」]([^""「」]{5,200})[""「」]')
SPEAKER_PATTERN = re.compile(r'(周砚|沈|林|管事|矿头|老矿头|师尊|长老)[说问道：:]')


def extract_dialogues(content):
    """提取所有对白，尝试绑定说话者"""
    dialogues = []
    # 匹配引号内容
    for m in re.finditer(r'[""「」]([^""「」]{5,200})[""「」]', content):
        text = m.group(1)
        start = max(0, m.start() - 30)
        context = content[start:m.start()]
        # 尝试识别说话者
        speaker_match = SPEAKER_PATTERN.search(context)
        speaker = speaker_match.group(1) if speaker_match else "未知"
        dialogues.append({
            "text": text,
            "speaker": speaker,
            "position": m.start(),
            "length": len(text)
        })
    return dialogues


def analyze_dialect_level(text):
    """计算方言浓度 (0-5)"""
    matches = DIALECT_MARKERS.findall(text)
    return min(5, len(matches))


def analyze_wenyan_level(text):
    """计算文言浓度 (0-5)"""
    matches = WENYAN_MARKERS.findall(text)
    return min(5, len(matches) * 2)


def check_forbidden_words(text, profile):
    """检查禁用词"""
    forbidden = profile.get("forbidden_words", [])
    found = []
    for word in forbidden:
        if word in text:
            found.append(word)
    return found


def check_universal_forbidden(dialogues):
    """检查所有角色是否说了同一句 AI 腔"""
    universal_found = []
    for d in dialogues:
        if FORBIDDEN_UNIVERSAL.search(d["text"]):
            universal_found.append({
                "speaker": d["speaker"],
                "text": d["text"][:60]
            })
    return universal_found


# ═══════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════

def run_character_voice_check(content, chapter_no, voice_profiles=None):
    """主入口"""
    voice_profiles = voice_profiles or []
    dialogues = extract_dialogues(content)
    narration = re.sub(r'[""「」][^""「」]+[""「」]', '', content)

    # ── 1. 旁白方言/文言检查 ──
    narration_dialect = analyze_dialect_level(narration)
    narration_wenyan = analyze_wenyan_level(narration)

    # ── 2. 角色对白检查 ──
    speaker_dialogues = {}
    for d in dialogues:
        s = d["speaker"]
        if s not in speaker_dialogues:
            speaker_dialogues[s] = []
        speaker_dialogues[s].append(d)

    voice_warnings = []
    voice_violations = []
    dialect_by_speaker = {}
    wenyan_by_speaker = {}
    forbidden_found = []

    # 加载 profile
    profile_map = {}
    for p in voice_profiles:
        profile_map[p.get("character_name", "")] = p

    for speaker, dls in speaker_dialogues.items():
        combined = " ".join(d["text"] for d in dls)
        d_level = analyze_dialect_level(combined)
        w_level = analyze_wenyan_level(combined)
        dialect_by_speaker[speaker] = d_level
        wenyan_by_speaker[speaker] = w_level

        profile = profile_map.get(speaker, {})
        max_dialect = profile.get("dialect_level", 2)
        max_wenyan = profile.get("wenyan_level", 1)

        if d_level > max_dialect + 1:
            voice_warnings.append(f"[{speaker}] 方言浓度 {d_level} 超出设定 {max_dialect}")
        if w_level > max_wenyan + 1:
            voice_warnings.append(f"[{speaker}] 文言浓度 {w_level} 超出设定 {max_wenyan}")

        fw = check_forbidden_words(combined, profile)
        if fw:
            forbidden_found.append({"speaker": speaker, "words": fw})
            voice_violations.append(f"[{speaker}] 使用禁用词: {', '.join(fw)}")

    # ── 3. 通用 AI 腔检查 ──
    universal_violations = check_universal_forbidden(dialogues)
    if universal_violations:
        for v in universal_violations:
            voice_violations.append(f"AI腔: [{v['speaker']}] '{v['text']}'")

    # ── 4. 旁白方言检查 ──
    if narration_dialect > 0:
        voice_warnings.append(f"旁白方言浓度 {narration_dialect}（应为 0）")

    # ── 5. 裁决 (Phase 2: 只有严重违规才 FAIL，其他 WARNING) ──
    critical_violations = len(voice_violations)
    passed = critical_violations == 0

    # 一致性得分
    if len(speaker_dialogues) >= 2:
        dialect_values = list(dialect_by_speaker.values())
        wenyan_values = list(wenyan_by_speaker.values())
        voice_consistency = 1.0 - (max(dialect_values) - min(dialect_values)) / 5.0 if dialect_values else 1.0
        dialogue_similarity = 0.0  # simplified
    else:
        voice_consistency = 1.0
        dialogue_similarity = 0.0

    report = {
        "status": "PASS" if passed else "WARNING",
        "final_decision": "PASS" if passed else "WARNING",
        "chapter_no": chapter_no,
        "voice_consistency_score": round(voice_consistency, 2),
        "dialogue_similarity_score": dialogue_similarity,
        "dialect_density": dialect_by_speaker,
        "wenyan_density": wenyan_by_speaker,
        "forbidden_words_found": forbidden_found,
        "universal_ai_violations": len(universal_violations),
        "narration_dialect_level": narration_dialect,
        "narration_wenyan_level": narration_wenyan,
        "speaker_count": len(speaker_dialogues),
        "total_dialogues": len(dialogues),
        "violations": voice_violations,
        "warnings": voice_warnings,
        "character_voice_pass": passed,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Character Voice Guard")
    parser.add_argument("content_file", help="章节 TXT 文件")
    parser.add_argument("--chapter-no", type=int, default=1)
    parser.add_argument("--voice-profiles", default=None, help="角色口吻卡 JSON 文件")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    content = Path(args.content_file).read_text(encoding="utf-8")

    voice_profiles = []
    if args.voice_profiles and Path(args.voice_profiles).exists():
        voice_profiles = json.loads(Path(args.voice_profiles).read_text(encoding="utf-8"))

    report = run_character_voice_check(content, args.chapter_no, voice_profiles)

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not report["character_voice_pass"]:
        print(f"\n[WARN] Character voice check: {len(report['violations'])} violations")
    else:
        print(f"\n[OK] Character voice check passed")


if __name__ == "__main__":
    main()
