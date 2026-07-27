#!/usr/bin/env python3
"""Report Chinese template-writing risks without changing source files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst"}

LINE_PATTERNS = {
    "模板对立": re.compile(
        r"(?:不是|并不是|并非|不在于|真正.{0,12}不是|关键.{0,8}不在于)"
        r".{0,55}(?:而是|而在于|在于)"
    ),
    "否定辨析密集": re.compile(
        r"(?:不等于|不意味着|并不意味着|不能只(?:看|关注|依赖)|不能仅(?:看|关注|依赖)|"
        r"与其说.{0,35}不如说)"
    ),
    "伪深刻": re.compile(
        r"(?:真正.{0,20}的是|归根结底|从本质上说|本质上|核心本质|关键所在)"
    ),
    "元话语": re.compile(
        r"(?:下面让我们|接下来(?:我们)?将|让我们(?:一起)?(?:深入|探索|分析)|"
        r"希望(?:以上|这些)?内容.{0,12}帮助)"
    ),
    "回应式开场": re.compile(
        r"(?:你说得对|你提到的.{0,12}(?:很重要|很准确)|这个问题(?:很|非常)重要|"
        r"针对(?:这个|上述)问题|关于这一点|这里(?:需要|要)(?:说明|强调|指出)|"
        r"需要(?:先)?(?:说明|强调|指出)的是)"
    ),
    "预设读者误解": re.compile(
        r"(?:你可能会问|有人(?:可能)?会问|很多人(?:会|可能会)?(?:认为|以为)|"
        r"读者(?:可能|往往)会(?:认为|以为|觉得)|常见(?:的)?误解是)"
    ),
    "空泛开场": re.compile(
        r"(?:在当今.{0,35}背景下|随着.{0,35}不断发展|在这个.{0,20}时代|"
        r"当前.{0,25}日益(?:重要|突出))"
    ),
    "宣传腔": re.compile(
        r"(?:赋能|助力|全方位|多维度|生态闭环|深度融合|至关重要|不可或缺|"
        r"里程碑式|全面升级|强大能力)"
    ),
    "总结套话": re.compile(
        r"(?:综上所述|总的来说|总体而言|不难发现|毋庸置疑|值得注意的是|"
        r"由此可见|显而易见)"
    ),
    "机械连接": re.compile(
        r"(?:首先|其次|再次|最后|一方面|另一方面|除此之外|与此同时|换言之|也就是说)"
    ),
    "对冲词": re.compile(
        r"(?:通常|往往|一般而言|一般来说|可能|相对而言|一定程度上|某种程度上)"
    ),
    "服务式话语": re.compile(
        r"(?:当然可以|很高兴为你|希望.{0,16}(?:有所帮助|帮助到你)|如有任何问题|"
        r"如果你愿意|如果需要|需要的话我可以|还可以继续|欢迎继续)"
    ),
    "AI标记残留": re.compile(
        r"(?:citeturn\d+search\d+|contentReference\[|oai_citation|\[attached_file:\d+\])"
    ),
    "AI链接参数": re.compile(
        r"(?:utm_source=(?:chatgpt\.com|copilot\.com|openai|claude\.ai|perplexity\.ai)|"
        r"referrer=grok\.com)"
    ),
    "句中加粗": re.compile(r"\*\*[^*\n]+\*\*"),
    "表演式引号": re.compile(r"[“\"](?:能出图|跑得快|真正落地|看得见|更高级|一键|闭环)[”\"]"),
}

SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])")
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")
HEADING_OR_LIST = re.compile(r"^\s*(?:#{1,6}\s|[-+*]\s|\d+[.)、]\s*)")


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
            continue
        if path.is_dir():
            files.extend(
                item for item in path.rglob("*")
                if item.is_file() and item.suffix.lower() in TEXT_EXTENSIONS
            )
            continue
        raise FileNotFoundError(path)
    return sorted(set(files))


def source_lines(text: str) -> list[tuple[int, str]]:
    """Return prose lines while excluding fenced code blocks and YAML frontmatter."""
    output: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    for number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        output.append((number, raw_line))
    return output


def add_finding(
    findings: list[dict[str, object]],
    path: Path,
    line: int,
    kind: str,
    text: str,
    matches: list[str],
    severity: str = "medium",
) -> None:
    findings.append({
        "file": str(path),
        "line": line,
        "type": kind,
        "severity": severity,
        "matches": matches,
        "text": text.strip(),
    })


def audit_lines(path: Path, lines: list[tuple[int, str]], strict: bool) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    hedge_limit = 2 if strict else 3
    connector_limit = 2 if strict else 3

    for line_number, line in lines:
        if not line.strip():
            continue
        scan_line = URL.sub("", INLINE_CODE.sub("", line))
        for label, pattern in LINE_PATTERNS.items():
            matches = [match.group(0) for match in pattern.finditer(scan_line)]
            if not matches:
                continue
            if label == "对冲词" and len(matches) < hedge_limit:
                continue
            if label == "机械连接" and len(matches) < connector_limit:
                continue
            severity = "high" if label in {"AI标记残留", "AI链接参数"} else "medium"
            add_finding(findings, path, line_number, label, line, matches, severity)
    return findings


def paragraphs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    start = 0
    buffer: list[str] = []
    for number, line in lines + [(0, "")]:
        stripped = line.strip()
        if stripped and not HEADING_OR_LIST.match(stripped):
            if not buffer:
                start = number
            buffer.append(stripped)
            continue
        if buffer:
            result.append((start, "".join(buffer)))
            buffer = []
    return result


def audit_paragraphs(path: Path, prose: list[tuple[int, str]], strict: bool) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    short_limit = 16 if strict else 13
    short_ratio_limit = 0.60 if strict else 0.72

    starts: list[tuple[int, str, str]] = []
    lengths: list[tuple[int, int]] = []
    for line_number, paragraph in paragraphs(prose):
        sentences = [item.strip() for item in SENTENCE_SPLIT.split(paragraph) if item.strip()]
        if len(sentences) >= 4:
            short_count = sum(len(sentence) <= short_limit for sentence in sentences)
            if short_count / len(sentences) >= short_ratio_limit:
                add_finding(
                    findings, path, line_number, "连续短句", paragraph,
                    [f"短句 {short_count}/{len(sentences)}"], "low"
                )
        for sentence in sentences:
            prefix_match = re.match(r"^(?:对于|通过|在.{0,8}方面|这(?:说明|意味着|表明)|因此|同时)", sentence)
            if prefix_match:
                starts.append((line_number, prefix_match.group(0), sentence))
        lengths.append((line_number, len(paragraph)))

    start_counts = Counter(prefix for _, prefix, _ in starts)
    repeat_limit = 3 if strict else 4
    for prefix, count in start_counts.items():
        if count < repeat_limit:
            continue
        examples = [sentence for _, item_prefix, sentence in starts if item_prefix == prefix][:3]
        first_line = next(line for line, item_prefix, _ in starts if item_prefix == prefix)
        add_finding(
            findings, path, first_line, "重复句首", " / ".join(examples),
            [f"{prefix} × {count}"], "low"
        )

    if len(lengths) >= 4:
        for index in range(len(lengths) - 3):
            window = lengths[index:index + 4]
            values = [length for _, length in window]
            mean = sum(values) / len(values)
            if mean >= 45 and max(values) - min(values) <= max(12, mean * 0.18):
                add_finding(
                    findings, path, window[0][0], "段落等长",
                    "连续四段长度接近", ["/".join(map(str, values))], "low"
                )
                break
    return findings


def audit_document_stance(path: Path, prose: list[tuple[int, str]], strict: bool) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    correction_patterns = (LINE_PATTERNS["模板对立"], LINE_PATTERNS["否定辨析密集"])
    stance_labels = ("回应式开场", "预设读者误解", "服务式话语", "元话语")

    corrections: list[tuple[int, str]] = []
    stance_hits: list[tuple[int, str, str]] = []
    for line_number, line in prose:
        scan_line = URL.sub("", INLINE_CODE.sub("", line))
        for pattern in correction_patterns:
            corrections.extend((line_number, match.group(0)) for match in pattern.finditer(scan_line))
        for label in stance_labels:
            stance_hits.extend(
                (line_number, label, match.group(0))
                for match in LINE_PATTERNS[label].finditer(scan_line)
            )

    correction_limit = 3 if strict else 5
    if len(corrections) >= correction_limit:
        add_finding(
            findings, path, corrections[0][0], "纠正式推进密集",
            "全文多次通过否定和纠正推进内容",
            [f"命中 {len(corrections)} 处"], "medium"
        )

    stance_limit = 2 if strict else 3
    if len(stance_hits) >= stance_limit:
        type_counts = Counter(label for _, label, _ in stance_hits)
        summary = "、".join(f"{label} {count}" for label, count in type_counts.items())
        add_finding(
            findings, path, stance_hits[0][0], "回答者姿态密集",
            "全文多次保留确认、预设误解、服务或元话语",
            [summary], "medium"
        )
    return findings


def audit(path: Path, strict: bool = False) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig")
    prose = source_lines(text)
    return (
        audit_lines(path, prose, strict)
        + audit_paragraphs(path, prose, strict)
        + audit_document_stance(path, prose, strict)
    )


def print_text(findings: list[dict[str, object]], files: list[Path]) -> None:
    severity_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda item: (
        severity_order.get(str(item["severity"]), 9),
        str(item["file"]), int(item["line"]), str(item["type"]),
    ))
    counts = Counter(str(item["type"]) for item in findings)
    for item in findings:
        matches = "、".join(str(value) for value in item["matches"])
        print(f"{item['file']}:{item['line']} [{item['severity']}/{item['type']}] {matches}")
        print(f"  {item['text']}")
    summary = " ".join(f"{kind}={count}" for kind, count in counts.most_common())
    print(f"files={len(files)} findings={len(findings)}" + (f" {summary}" if summary else ""))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="UTF-8 text files or directories")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true", help="lower density thresholds")
    args = parser.parse_args()

    try:
        files = iter_files(args.paths)
    except FileNotFoundError as error:
        parser.error(f"path does not exist: {error.args[0]}")
    if not files:
        parser.error("no supported text files found")

    all_findings: list[dict[str, object]] = []
    for path in files:
        try:
            all_findings.extend(audit(path, strict=args.strict))
        except UnicodeDecodeError as error:
            parser.error(f"not UTF-8 text: {path}: {error}")

    if args.as_json:
        print(json.dumps({"files": [str(path) for path in files], "findings": all_findings}, ensure_ascii=False, indent=2))
    else:
        print_text(all_findings, files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
