"""同一个事实写在两个地方时，谁也不保证它们一直一致。

Windows 实测清单里剩下能自动化的几条，本质上是同一类毛病：选择器的端口写在 Python 里
也写在页面里；trend 需要哪些角色写在 schema 里也写在给豆包看的参考文档里；「别把 Origin
窗口调到前台」这条禁令写在 SKILL.md 里，而我们自己的代码里也不该出现那几个 Win32 调用。

改了一边忘了另一边，**没有任何测试会红**——只有真机上才会暴露，而现场在观众的电脑里。
这个文件把这些成对的事实钉在一起。

对应清单：2.2 / 2.3 / 2.7 / 4.3 和 1.4 的兜底指引。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skill" / "doubaoplot"
SELECTOR_DIR = SKILL_ROOT / "selector"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import bootstrap_editaplot as bootstrap  # noqa: E402

# ── 4.3 选择器端口：Python 和页面各写了一份，必须一致 ────────────────────────


def test_selector_ports_match_between_python_and_the_page():
    """页面挨个去试这几个端口，Python 也挨个去占这几个。两边对不上，页面就永远收不到回传。

    清单 4.3 要真人去确认这台机器上端口没被占；端口本身对不对得上，CI 就能管。
    """
    source = (SELECTOR_DIR / "selector.py").read_text(encoding="utf-8")
    page = (SELECTOR_DIR / "chart-selector.html").read_text(encoding="utf-8")

    match = re.search(r"^PORTS\s*=\s*\[([^\]]+)\]", source, re.M)
    assert match, "selector.py 里找不到 PORTS"
    python_ports = [int(item) for item in re.findall(r"\d+", match.group(1))]
    assert python_ports, "PORTS 是空的"

    page_ports = sorted({int(item) for item in re.findall(r"\b(178\d\d)\b", page)})
    assert page_ports, "页面里一个端口都没有，回传地址可能被改成别的写法了"
    assert sorted(python_ports) == page_ports, (
        f"页面试的端口 {page_ports} 和 selector.py 占的端口 {sorted(python_ports)} 对不上，"
        "用户点了图也回传不回来"
    )


def test_selector_page_and_script_ship_together():
    """页面和脚本必须一起装过去，少一个选择器就打不开。"""
    assert (SELECTOR_DIR / "selector.py").is_file()
    assert (SELECTOR_DIR / "chart-selector.html").is_file()


# ── 2.3 角色名：schema 是权威，给豆包看的文档必须跟上 ────────────────────────


def _templates_with_schema() -> list[Path]:
    return sorted(ROOT.glob("runtime/templates/*/schema.json"))


def test_reference_doc_lists_the_roles_the_trend_schema_actually_requires():
    """豆包填 assignments 时要从 references/semantic-understanding.md 读角色名。

    schema 改了角色名而这份文档没跟上，豆包就会填一个模板不认的角色，然后开始翻源码
    找答案——上次实跑在这里烧了 12 个回合，那次修的就是「把角色名写进参考文档」。
    """
    schema = json.loads((ROOT / "runtime/templates/trend/schema.json").read_text(encoding="utf-8"))
    required = schema.get("required_roles")
    assert required, "trend 的 schema 里没有 required_roles，这条测试的前提没了"

    doc = (SKILL_ROOT / "references" / "semantic-understanding.md").read_text(encoding="utf-8")
    missing = [role for role in required if f"`{role}`" not in doc]
    assert not missing, (
        f"trend 需要角色 {missing}，但给豆包看的 semantic-understanding.md 里没写。"
        "豆包会去翻 runtime/src 找答案"
    )


# 角色契约有三种写法：多数模板用 required_roles；eis 是「两组任选其一」用
# required_role_sets；xps 那几个按列自适应，用 required。三种都算数，但必须有一种——
# 一个都不声明，mapping_invalid 报错时就列不出角色名，豆包只能去翻源码。
ROLE_CONTRACT_KEYS = ("required_roles", "required_role_sets", "required")


@pytest.mark.parametrize("schema_path", _templates_with_schema(), ids=lambda p: p.parent.name)
def test_every_template_schema_declares_a_role_contract(schema_path: Path):
    """每个模板都得说清自己要哪些角色，报错时才列得出来。"""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    declared = [key for key in ROLE_CONTRACT_KEYS if key in schema]

    assert declared, (
        f"{schema_path.parent.name} 一个角色契约字段都没有，"
        f"三种写法任选其一：{ROLE_CONTRACT_KEYS}"
    )
    for key in declared:
        assert isinstance(schema[key], list), f"{schema_path.parent.name} 的 {key} 不是列表"


# ── 2.7 成品展示：禁令写在 SKILL.md 里，代码自己也得守 ──────────────────────


FOREGROUND_CALLS = (
    "SetForegroundWindow",
    "ShowWindow",
    "AttachThreadInput",
    "BringWindowToTop",
    "SwitchToThisWindow",
)


def test_our_own_code_never_drags_the_origin_window_to_the_front():
    """SKILL.md 禁止豆包去抢窗口前台，我们自己的代码里也不能有这些调用。

    上次实跑在「展示成品」这一步烧了 19 个回合，全花在找窗口上。
    禁令只写给豆包、自己代码里却留着后门，这条禁令迟早会被当成建议。
    """
    offenders: list[str] = []
    for path in [*ROOT.glob("runtime/src/**/*.py"), *SKILL_ROOT.rglob("*.py")]:
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        offenders.extend(
            f"{path.relative_to(ROOT)}:{call}" for call in FOREGROUND_CALLS if call in text
        )

    assert not offenders, f"代码里出现了抢窗口前台的调用：{offenders}"


def test_showcase_rule_tells_doubao_what_to_do_instead():
    """光禁止没用，得告诉它改用什么——不然它还是会去试别的花招。"""
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "不要尝试把 Origin 窗口调到前台" in text
    assert "result.png" in text, "得给出替代做法：展示导出的 result.png"
    assert "result.opju" in text, "得说清要在 Origin 里编辑就由真人打开 result.opju"
    for call in ("ShowWindow", "SetForegroundWindow", "AttachThreadInput"):
        assert call in text, f"禁令里得点名 {call}，泛泛说「别抢窗口」豆包会自己找变通办法"


# ── 2.2 / 1.4 引擎缺失时的兜底：那条报错是豆包唯一的指引 ────────────────────


def test_missing_engine_hands_doubao_a_fallback_that_actually_works(monkeypatch, tmp_path, capsys):
    """缺引擎是最容易卡住的时刻，而豆包只看得到这一条报错。

    这条消息得同时说清三件事：Skill 没被改坏、没有 editaplot.cmd 时改用 bootstrap 当入口、
    以及怎么把引擎位置告诉它。上次实跑因为找不到入口，在这里烧了 7 个回合。
    """
    monkeypatch.setattr(bootstrap, "windows_host_compatibility", lambda: {"compatible": True})
    monkeypatch.setattr(bootstrap, "_resolve_engine", lambda argv: (None, {}))

    returncode = bootstrap.install_skill(["--target", str(tmp_path / "skills" / "doubaoplot")])
    captured = capsys.readouterr()

    assert returncode != 0
    payload = json.loads(captured.err.strip())
    error = payload.get("error", {})
    assert error.get("code") == "engine_not_found", f"报的不是 engine_not_found：{captured.err[:300]}"

    message = error.get("message", "")
    assert "unchanged" in message, "得说清已装好的 Skill 没被这次失败改坏，否则豆包会去重装"
    assert "bootstrap_editaplot.py" in message, "得给出没有 editaplot.cmd 时的替代入口"
    assert "--engine-home" in message, "得告诉它怎么把引擎位置传进来"


def test_the_fallback_entry_point_really_accepts_engine_home():
    """上一条那句指引让豆包跑 `bootstrap_editaplot.py <子命令> --engine-home`。

    那 bootstrap 就必须真的认这个参数——指引指向一个不存在的用法，比不给指引更糟。
    """
    source = (SKILL_ROOT / "scripts" / "bootstrap_editaplot.py").read_text(encoding="utf-8")
    assert '"--engine-home"' in source, "报错里让豆包用 --engine-home，脚本却不认这个参数"
