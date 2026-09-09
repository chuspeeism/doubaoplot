"""装机链路的契约测试：SKILL.md 写给豆包的指令，必须和脚本的真实行为对得上。

这一层的东西很容易悄悄坏掉。SKILL.md 里那些「先跑 --diagnose 读四个字段」「超时
了就换镜像」「没有 git 就下 ZIP」全是自然语言指令，不是代码约束：字段名改了、
错误码改了、仓库改名了，没有任何测试会红，只会让豆包在真机上照着一份过期说明干活，
然后卡住——而卡住的现场在观众的电脑里，我们看不到。

所以这个文件不测绘图，只做一件事：把「指令说的」和「代码做的」钉在一起。
GitHub Actions 跑在 windows-latest 上，这些用例每次推代码都会在真正的 Windows 上过一遍。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skill" / "doubaoplot"
SKILL_MD = SKILL_ROOT / "SKILL.md"
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_editaplot.py"
CORE = SKILL_ROOT / "scripts" / "editaplot_core.py"


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _run_diagnose() -> dict:
    completed = subprocess.run(  # noqa: S603 - 固定解释器、固定脚本，参数不来自外部输入
        [sys.executable, str(BOOTSTRAP), "--diagnose"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=120,
    )
    assert completed.stdout.strip(), f"--diagnose 没有任何输出：{completed.stderr[:400]}"
    return json.loads(completed.stdout)


# ── --diagnose：豆包第一步就跑它，它必须在任何机器上都能跑出结果 ────────────────


def test_diagnose_runs_even_without_an_engine_or_windows():
    """SKILL.md 承诺「这条命令不依赖引擎，缺引擎时也能跑」。

    这是豆包为一台新机器干活时的第一条命令。它要是在缺引擎的机器上直接崩了，
    豆包就没有任何依据去判断「还差哪几步」，只能瞎猜——上次实跑烧掉的回合数
    大半来自这种瞎猜。
    """
    payload = _run_diagnose()

    assert payload["schema_version"], "输出必须自带 schema 版本，否则日后没法判断字段变没变"
    assert "ok" in payload


def test_diagnose_reports_every_field_the_skill_tells_doubao_to_read():
    """SKILL.md 里有一张表，点名让豆包从 --diagnose 的输出里读四个字段。

    这张表是「指令 ↔ 代码」最脆的接缝：谁改了输出结构，表就过期，
    而豆包会去读一个不存在的字段。
    """
    payload = _run_diagnose()
    text = _skill_text()

    assert isinstance(payload.get("host"), dict), "输出里必须有 host 对象"
    assert "compatible" in payload["host"], "SKILL.md 让豆包读 host.compatible"
    assert "engine_home" in payload, "SKILL.md 让豆包读 engine_home 判断引擎在不在"
    assert "selected" in payload, "SKILL.md 让豆包读 selected 判断有没有可用的 Python"

    # selected 为 null 时读不到 source，但字段契约仍要成立：有 selected 就必须有 source。
    selected = payload.get("selected")
    if selected is not None:
        assert "source" in selected, "SKILL.md 让豆包用 selected.source 判断依赖库是否就位"

    for field in ("host.compatible", "engine_home", "selected", "selected.source"):
        assert f"`{field}`" in text, f"SKILL.md 的字段表里少了 {field}，指令和输出对不上了"


def test_diagnose_marks_a_non_windows_host_as_incompatible():
    """Windows 之外的机器必须被明确判成走不通，而不是含糊地继续往下走。

    SKILL.md 要求 host.compatible 为 false 时「直接说清这条路走不了，不要再往下走」。
    """
    payload = _run_diagnose()
    compatible = payload["host"]["compatible"]

    assert isinstance(compatible, bool), "compatible 必须是 true/false，别给豆包一个含糊的值"
    if sys.platform != "win32":
        assert compatible is False
        assert payload["ok"] is False


# ── 换镜像那条路：SKILL.md 报的数字和错误码，代码里必须真有 ──────────────────


def test_dependency_timeout_matches_the_number_printed_in_the_skill():
    """SKILL.md 告诉豆包「上限 900 秒，超了报 dependency_install_timeout」。

    豆包就是靠这个错误码决定要不要换国内镜像重跑。数字或码改了而文档没改，
    这条自救路径就断了——而且断得无声无息。
    """
    core = CORE.read_text(encoding="utf-8")
    text = _skill_text()

    assert "timeout=900," in core, "依赖安装的超时不再是 900 秒，SKILL.md 里的数字就过期了"
    assert '"dependency_install_timeout"' in core
    assert "900 秒" in text
    assert "`dependency_install_timeout`" in text


def test_mirror_rules_forbid_turning_off_certificate_checks():
    """换源只许换这两个官方镜像，且不许拿关证书校验去换速度。"""
    text = _skill_text()

    assert "--trusted-host" in text, "禁用 --trusted-host 的那条规矩不见了"
    assert "不要用 `--trusted-host` 关掉证书校验" in text
    assert "默认仍然走官方 PyPI" in text
    assert "requirements-runtime.lock" in text, "必须写明换源不改版本"


def test_user_facing_docs_mention_only_error_codes_that_exist():
    """README 和使用说明里给用户看的错误码，代码里必须真的会抛。

    用户拿着一个查不到的错误码去搜，只会更慌。
    """
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (CORE, BOOTSTRAP)
    )
    docs = ("README.md", "README.en.md", "豆包工作使用说明.md")
    seen: set[str] = set()
    for name in docs:
        path = ROOT / name
        if not path.is_file():
            continue
        seen.update(re.findall(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+){2,})\b", path.read_text(encoding="utf-8")))

    codes = {word for word in seen if word.endswith(("_timeout", "_failed", "_invalid", "_incompatible"))}
    assert codes, "文档里一个错误码都没提到，这条测试的前提没了"
    missing = sorted(code for code in codes if f'"{code}"' not in sources)
    assert not missing, f"文档提到了代码里不存在的错误码：{missing}"


# ── Windows 上的三条硬规矩：实跑记录里连着栽过 ────────────────────────────────


def test_zip_fallback_points_at_this_fork_and_stays_self_consistent():
    """没有 git 时的 ZIP 兜底，地址必须指向本仓库，解压目录名必须和分支对得上。

    这条最容易在改名之后悄悄坏掉：地址还留着上游的 hang-jin/editaplot，
    或者下 main.zip 却让 setup 去 doubaoplot-master 里跑。
    """
    text = _skill_text()

    match = re.search(r"https://github\.com/([\w.-]+)/([\w.-]+)/archive/refs/heads/([\w.-]+)\.zip", text)
    assert match, "SKILL.md 里的 ZIP 兜底地址没了"
    owner, repo, branch = match.groups()

    assert (owner, repo) == ("chuspeeism", "doubaoplot"), "ZIP 还指着别人的仓库"
    assert f"`{repo}-{branch}`" in text, f"解压出来的目录叫 {repo}-{branch}，SKILL.md 得原样写出来"
    assert "hang-jin/editaplot" not in text, "安装指令里不该再出现上游仓库地址"


def test_windows_command_rules_cover_the_three_traps_we_actually_hit():
    """PowerShell 不是 bash。这三条都是实跑记录里真栽过的。"""
    text = _skill_text()

    assert "不要用 POSIX 写法" in text
    assert "Get-ChildItem" in text, "得给出 ls 的 PowerShell 替代写法"
    assert "-ErrorAction SilentlyContinue" in text, "得给出 2>/dev/null 的替代写法"
    assert "不要假设机器上有 git" in text
    assert "不要用 GitHub API 去列仓库目录" in text


def test_skill_code_blocks_are_powershell_not_bash():
    """指令自己别打脸：SKILL.md 教豆包别写 POSIX，自己的代码块里就不能出现 POSIX 写法。"""
    blocks = re.findall(r"```(\w*)\n(.*?)```", _skill_text(), re.S)
    assert blocks, "SKILL.md 里一个代码块都没有"

    posix_only = ("2>/dev/null", "&&", "$(", "`ls ")
    offenders = [
        (lang or "无标注", token)
        for lang, body in blocks
        for token in posix_only
        if token in body
    ]
    assert not offenders, f"SKILL.md 的代码块里混进了 POSIX 写法：{offenders}"


# ── 报账：用户的挫败感来自「不知道还有几步」，不是等待本身 ────────────────────


def test_skill_tells_doubao_to_report_the_plan_before_working():
    """09-06 定的规矩：先报账再干活，已经具备的要点名说「跳过」。

    这段指令没有任何代码在兜底，被改掉不会有人发现，所以逐条钉住。
    """
    text = _skill_text()

    assert "先报账，再干活" in text
    assert "--diagnose" in text, "报账的依据来自 --diagnose，命令不能丢"
    assert "四件事" in text, "得把整条链路拆成四件事讲给用户"
    assert "跳过" in text, "已经具备的要点名说跳过，那是用户能感知到的「更快」"
    assert "报完就接着做，不要停下来等一句" in text, "报账是告知不是请示"
    assert "装 Python" in text, "四件事里只有装 Python 属于系统级变更，需要先征得同意"


def test_bootstrap_still_exposes_the_commands_the_skill_hands_to_doubao():
    """SKILL.md 让豆包敲的那些子命令，脚本里必须还认得。"""
    text = _skill_text()
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

    for command in ("setup", "repair-environment"):
        if f"`{command}`" in text or f" {command} " in text:
            assert f'"{command}"' in bootstrap, f"SKILL.md 还在让豆包跑 {command}，脚本已经不认了"
