"""在 CI 上真跑一次安装，验证「装完之后目录里到底有什么」。

Windows 实测清单 1.2 问的就是这件事：观众说完那句安装口令，豆包把 Skill 装到
`.user_skills` 底下之后，那个目录里有没有 `editaplot.cmd`、有没有 scripts、有没有
选择器。这一条以前只能靠真人开一台干净的 Windows 去看。

这里把它搬进 CI：真跑 `install_skill`，真复制文件，真检查落位，只把最后
「装 10 个依赖库」那一步换掉——那一步要下 45 MB，CI 每跑一次就是十几分钟，
而它验的是 pip 的行为，不是我们的代码。

跑在 windows-latest 上，Python 3.10 / 3.11 / 3.12 三档都会过一遍。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill" / "doubaoplot" / "scripts"))

import bootstrap_editaplot as bootstrap  # noqa: E402

SKILL_SOURCE = ROOT / "skill" / "doubaoplot"


def _fake_managed_environment(engine_home, *, valid: bool):
    """假装那个装依赖用的虚拟环境已经建好（或没建好）。"""
    environment = Path(engine_home) / ".editaplot-venv"
    return {
        "exists": valid,
        "valid": valid,
        "environment": str(environment),
        "python_executable": sys.executable,
        "fingerprint": str(environment / ".editaplot-environment.json"),
        "dependency_lock_sha256": (
            bootstrap._skill_dependency_lock_sha(SKILL_SOURCE) if valid else None
        ),
    }


@pytest.fixture
def installer(monkeypatch):
    """把安装拆到「复制文件」为止：那之后是 pip 的事，不是我们的代码。

    换掉的只有三样：宿主检查、Python 探测、跑子进程装依赖。它们各自已经有专门的
    用例，而且都要真 Windows + 45 MB 下载才能跑，留在这里只会让这组用例变成
    「十几分钟一次、还只能在 CI 里跑」。复制文件、落启动器、清中间产物、
    失败回滚——这些是我们自己的代码，全部真跑。
    """
    monkeypatch.setattr(bootstrap, "windows_host_compatibility", lambda: {"compatible": True})
    monkeypatch.setattr(
        bootstrap,
        "discover_python",
        lambda engine_home: {
            "selected": {"source": "test_double", "executable": sys.executable},
            "attempts": [],
        },
    )
    monkeypatch.setattr(
        bootstrap,
        "managed_environment_status",
        lambda engine_home: _fake_managed_environment(engine_home, valid=True),
    )

    calls: list[dict] = []

    def _fake_subprocess_step(command, *, environment, timeout=1500):
        calls.append({"command": list(command), "environment": dict(environment)})
        if "doctor" in command:
            return 0, {"ok": True, "ready_for_analysis": True, "ready_for_render": True}
        return 0, {"ok": True, "status": "environment_ready"}

    monkeypatch.setattr(bootstrap, "_run_json_command", _fake_subprocess_step)
    return calls


def _install_into(tmp_path: Path) -> tuple[int, Path]:
    target = tmp_path / "skills" / "doubaoplot"
    return bootstrap.install_skill(["--target", str(target)]), target


# ── 装完之后，目录里该有的东西 ────────────────────────────────────────────────


def test_setup_lands_everything_doubao_needs_to_launch(installer, tmp_path, capsys):
    """实测清单 1.2：装完的目录里必须能直接跑起来。

    少了 editaplot.cmd，豆包就会在目标目录里到处翻找入口——上次实跑在这里烧了 7 个回合。
    """
    returncode, target = _install_into(tmp_path)
    capsys.readouterr()

    assert returncode == 0, "安装没成功"
    for relative in (
        "SKILL.md",
        "scripts/bootstrap_editaplot.py",
        "scripts/editaplot.py",
        "scripts/editaplot_core.py",
        "scripts/requirements-runtime.lock",
        "selector/selector.py",
        "selector/chart-selector.html",
    ):
        assert (target / relative).is_file(), f"装完少了 {relative}"

    assert (target / "editaplot.cmd").is_file(), (
        "启动器没落到目标目录里。它不在 skill/doubaoplot/ 下，是从仓库根目录复制过去的，"
        "这条链路一断，豆包就找不到入口"
    )


def test_setup_leaves_no_lock_and_no_staging_directory_behind(installer, tmp_path, capsys):
    """装成功之后，宿主的 skills 目录里不该多出任何中间产物。

    上次实跑就在观众的 skills 目录里留了一个 .lock。已有的用例只盖了失败路径，
    这条盖成功路径。
    """
    returncode, target = _install_into(tmp_path)
    capsys.readouterr()

    assert returncode == 0
    siblings = sorted(path.name for path in target.parent.iterdir())
    assert siblings == ["doubaoplot"], f"skills 目录里留下了多余的东西：{siblings}"


def test_setup_does_not_touch_the_source_tree(installer, tmp_path, capsys):
    """装机只许往外拷，不许回头改仓库自己。"""
    before = {
        path.relative_to(SKILL_SOURCE): path.stat().st_mtime_ns
        for path in sorted(SKILL_SOURCE.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }

    returncode, _target = _install_into(tmp_path)
    capsys.readouterr()
    assert returncode == 0

    after = {
        path.relative_to(SKILL_SOURCE): path.stat().st_mtime_ns
        for path in sorted(SKILL_SOURCE.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert before == after, "安装过程改动了源码目录"


def test_setup_hands_the_engine_home_to_the_dependency_step(installer, tmp_path, capsys):
    """装依赖那一步要靠 EDITAPLOT_ENGINE_HOME 才知道往哪个引擎里装。

    这个变量传丢了，依赖会装到一个没人用的地方，而且不会报错。
    """
    returncode, target = _install_into(tmp_path)
    capsys.readouterr()

    assert returncode == 0

    repair = [call for call in installer if "repair-environment" in call["command"]]
    doctor = [call for call in installer if "doctor" in call["command"]]
    assert len(repair) == 1, "装依赖那一步应该正好跑一次"
    assert len(doctor) == 1, "装完之后应该自检一次，别把「装完了」和「能用」混为一谈"

    assert str(target / "scripts" / "editaplot.py") in repair[0]["command"], (
        "装依赖要用装好的那份 CLI，不是源码目录里的那份"
    )

    engine_home = repair[0]["environment"].get("EDITAPLOT_ENGINE_HOME")
    assert engine_home, "没有把引擎位置传给装依赖那一步"
    assert Path(engine_home).is_dir()


def test_setup_can_run_twice_without_breaking_the_install(installer, tmp_path, capsys):
    """观众重说一遍安装口令是常事，第二次不能把第一次装好的弄坏。"""
    first_code, target = _install_into(tmp_path)
    capsys.readouterr()
    assert first_code == 0

    second_code, _ = _install_into(tmp_path)
    capsys.readouterr()

    assert second_code == 0, "重装一次就失败了"
    assert (target / "editaplot.cmd").is_file()
    assert (target / "SKILL.md").is_file()
    siblings = sorted(path.name for path in target.parent.iterdir())
    assert siblings == ["doubaoplot"], f"重装留下了残留：{siblings}"


# ── 装错地方要拦住 ──────────────────────────────────────────────────────────


def test_setup_refuses_a_target_that_is_not_this_skill(installer, tmp_path, capsys):
    """目标目录里已经有别的东西时，不许覆盖。

    这道校验就是 09-06 那次「豆包上装两次都失败」的根因所在：它当时写死只认上游名
    `editaplot`，把本项目的 `doubaoplot` 判成了外人。这里正着反着各钉一遍。
    """
    stranger = tmp_path / "skills" / "somebody-elses-skill"
    stranger.mkdir(parents=True)
    (stranger / "SKILL.md").write_text("---\nname: something-else\n---\n", encoding="utf-8")

    returncode = bootstrap.install_skill(["--target", str(stranger)])
    capsys.readouterr()

    assert returncode != 0, "装进了一个不属于本 skill 的目录"
    assert not (stranger / "editaplot.cmd").exists(), "被拒绝之后不该留下任何文件"
    assert (stranger / "SKILL.md").read_text(encoding="utf-8").strip().endswith("---"), (
        "被拒绝之后不该改动人家原有的内容"
    )


def test_installer_identity_check_accepts_this_forks_own_name(installer, tmp_path, capsys):
    """反过来：本仓库自己的名字必须被认。

    09-06 之前这里认的是上游名，导致装到第二次就报「请给写权限」——一句和真实原因
    完全无关的话，排查时被它带偏过。
    """
    returncode, target = _install_into(tmp_path)
    capsys.readouterr()
    assert returncode == 0

    # 已经装好的目录，就是一个合法的重装目标。
    assert bootstrap._is_recognized_editaplot_skill(target)


def test_a_failed_dependency_step_rolls_the_whole_install_back(monkeypatch, tmp_path, capsys):
    """依赖没装成，整个安装要退回去，不许在观众的 skills 目录里留个半成品。

    半成品比装不上更糟：目录看着是有的，豆包会以为装好了，直接去跑，
    然后在一个完全无关的地方报错。
    """
    monkeypatch.setattr(bootstrap, "windows_host_compatibility", lambda: {"compatible": True})
    monkeypatch.setattr(
        bootstrap,
        "discover_python",
        lambda engine_home: {
            "selected": {"source": "test_double", "executable": sys.executable},
            "attempts": [],
        },
    )
    # 依赖那一步跑完了，但环境并没有真的建起来——这正是网络超时后的样子。
    monkeypatch.setattr(
        bootstrap,
        "managed_environment_status",
        lambda engine_home: _fake_managed_environment(engine_home, valid=False),
    )
    monkeypatch.setattr(
        bootstrap,
        "_run_json_command",
        lambda command, *, environment, timeout=1500: (0, {"ok": True}),
    )

    returncode, target = _install_into(tmp_path)
    capsys.readouterr()

    assert returncode != 0, "依赖没装成却报了成功"
    assert not target.exists(), "失败之后把半成品留在了 skills 目录里"
    leftovers = sorted(path.name for path in target.parent.iterdir())
    assert leftovers == [], f"失败之后留下了残留：{leftovers}"
