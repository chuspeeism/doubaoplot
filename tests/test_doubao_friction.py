"""Doubao installation and discoverability regressions; no Origin required."""
import sys
import threading
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skill/doubaoplot/scripts'))
sys.path.insert(0, str(ROOT / 'skill/doubaoplot/selector'))
sys.path.insert(0, str(ROOT / 'runtime/src'))
import bootstrap_editaplot as bootstrap  # noqa: E402
import editaplot  # noqa: E402
import editaplot_core as core  # noqa: E402
import selector as chart_selector  # noqa: E402
from origin_sciplot.scientific_workflow import (  # noqa: E402
    ScientificWorkflowError,
    apply_scientific_palette_override,
)

SKILL_ROOT = ROOT / 'skill/doubaoplot'


def test_real_doubao_skill_root(monkeypatch, tmp_path):
    for key in ('EDITAPLOT_SKILL_DIR', 'DOUBAO_HOME', 'DOUBAO_WORK_HOME', 'CODEX_HOME', 'LOCALAPPDATA'):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    root = tmp_path / 'AppData/Local/Doubao/User Data/Default/.doubao/agent_mode/workspace/.user_skills'
    root.mkdir(parents=True)
    assert bootstrap.resolve_skill_target()[0] == root / 'doubaoplot'


def test_relocated_localappdata(monkeypatch, tmp_path):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    root = tmp_path / 'Doubao/User Data/Default/.doubao/agent_mode/workspace/.user_skills'
    assert root in bootstrap._candidate_skill_roots()


def test_palette_cli_template_option():
    assert editaplot.build_parser().parse_args(['palettes', '--template-id', 'trend']).template_id == 'trend'


@pytest.mark.parametrize('public_only', [True, False])
def test_trend_palette_filter(public_only):
    result = core.palette_catalog(engine_home=ROOT / 'runtime', template_id='trend', public_only=public_only)
    assert result['palettes']
    assert all('sequential' in p['allowed_modes'] for p in result['palettes'])
    assert 'ocean_coral' not in [p['palette_id'] for p in result['palettes']]


def test_semantic_palette_and_unknown_template():
    assert core.palette_catalog(engine_home=ROOT / 'runtime', template_id='heatmap')['palettes'] == []
    with pytest.raises(core.EditaPlotError) as exc:
        core.palette_catalog(engine_home=ROOT / 'runtime', template_id='not_a_template')
    assert exc.value.code == 'template_unknown'


def test_palette_error_lists_alternatives():
    with pytest.raises(ScientificWorkflowError) as exc:
        apply_scientific_palette_override(SimpleNamespace(template_id='trend'), palette_id='ocean_coral')
    assert exc.value.code == 'palette_mode_incompatible'
    assert 'deep_sea_gold' in str(exc.value)


def test_mapping_error_lists_trend_roles():
    with pytest.raises(core.EditaPlotError) as exc:
        core._prepare_template_for_understanding(
            ROOT / 'runtime/templates/trend/example_standard.csv',
            template_id='trend',
            mapping={},
            engine_home=ROOT / 'runtime',
        )
    assert exc.value.code == 'mapping_invalid'
    assert 'series' in str(exc.value) and 'x' in str(exc.value)


# ── 安装身份校验 ────────────────────────────────────────────────────────────
# 本仓库把 SKILL.md 的 name 从 editaplot 改成了 doubaoplot。安装器的身份校验一旦只认
# 旧名字，每次安装都会在暂存目录上失败（还会伪装成"写不进去"），重装时更会把已经装好的
# 目录判成"不是 EditaPlot"直接拒绝。这三条测试把这条线钉死。


def test_shipped_skill_passes_installer_identity_check():
    assert bootstrap._is_recognized_editaplot_skill(SKILL_ROOT)


def test_identity_check_still_accepts_upstream_name(tmp_path):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts' / 'editaplot.py').write_text('', encoding='utf-8')
    (tmp_path / 'scripts' / 'bootstrap_editaplot.py').write_text('', encoding='utf-8')
    (tmp_path / 'SKILL.md').write_text('---\nname: editaplot\n---\n', encoding='utf-8')
    assert bootstrap._is_recognized_editaplot_skill(tmp_path)


def test_identity_check_rejects_unrelated_directory(tmp_path):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts' / 'editaplot.py').write_text('', encoding='utf-8')
    (tmp_path / 'scripts' / 'bootstrap_editaplot.py').write_text('', encoding='utf-8')
    (tmp_path / 'SKILL.md').write_text('---\nname: something-else\n---\n', encoding='utf-8')
    assert not bootstrap._is_recognized_editaplot_skill(tmp_path)


# ── 选择器：页面走本机 HTTP，默认不弹系统浏览器 ─────────────────────────────


def test_selector_serves_page_and_receives_pick():
    chart_selector._Handler.page_bytes = b'<html>selector</html>'
    chart_selector._Handler.result = {}
    server = ThreadingHTTPServer(('127.0.0.1', 0), chart_selector._Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_address[1]}'
    try:
        with urllib.request.urlopen(f'{base}/') as response:  # noqa: S310  地址是本机回环，非用户输入
            assert response.read() == b'<html>selector</html>'
            assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        pick = f'{base}/pick?d=' + urllib.parse.quote('画个雨云图')
        with urllib.request.urlopen(pick) as response:  # noqa: S310  地址是本机回环，非用户输入
            assert response.headers['Content-Type'] == 'image/gif'
        assert chart_selector._Handler.result['prompt'] == '画个雨云图'
    finally:
        server.server_close()
        chart_selector._Handler.page_bytes = b''
        chart_selector._Handler.result = {}


def test_selector_records_the_pick_before_replying(monkeypatch):
    """回执一旦发出，页面就认定这次选择已送达，所以落地必须发生在回执之前。

    反过来写会在「拿到 200」和「读得到 prompt」之间留一个空窗；
    Windows CI 上就是在这个空窗里偶发 KeyError: 'prompt'。
    """
    seen: list[dict] = []
    original_reply = chart_selector._Handler._reply

    def _spy(handler, code):
        seen.append(dict(chart_selector._Handler.result))
        original_reply(handler, code)

    monkeypatch.setattr(chart_selector._Handler, '_reply', _spy)
    chart_selector._Handler.result = {}
    server = ThreadingHTTPServer(('127.0.0.1', 0), chart_selector._Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    pick = f'http://127.0.0.1:{server.server_address[1]}/pick?d=' + urllib.parse.quote('画个雨云图')
    try:
        with urllib.request.urlopen(pick):  # noqa: S310  地址是本机回环，非用户输入
            pass
    finally:
        server.server_close()
        chart_selector._Handler.result = {}

    assert seen == [{'prompt': '画个雨云图'}]


def test_selector_does_not_open_a_system_browser_by_default(monkeypatch, capsys):
    opened: list[str] = []
    # 端口交给系统分配，别去抢 17864 那三个——真机上可能正被占着
    monkeypatch.setattr(chart_selector, 'PORTS', [0])
    monkeypatch.setattr(chart_selector, '_open_in_browser', lambda target: opened.append(target) or True)
    chart_selector.main(['--timeout', '0.2'])
    assert opened == []
    assert 'http://127.0.0.1:' in capsys.readouterr().out


def test_selector_open_flag_opens_the_http_address(monkeypatch, capsys):
    opened: list[str] = []
    monkeypatch.setattr(chart_selector, 'PORTS', [0])
    monkeypatch.setattr(chart_selector, '_open_in_browser', lambda target: opened.append(target) or True)
    chart_selector.main(['--timeout', '0.2', '--open'])
    capsys.readouterr()
    assert opened and opened[0].startswith(('http://127.0.0.1:', 'file://'))


def test_setup_does_not_leave_a_lock_file_behind(tmp_path, monkeypatch, capsys):
    """装完（或装失败）都不该在宿主的 skills 目录里留下 .lock。上次实跑就留了一个。"""

    monkeypatch.setattr(bootstrap, 'windows_host_compatibility', lambda: {'compatible': True})
    monkeypatch.setattr(bootstrap, '_resolve_engine', lambda argv: (None, {}))
    skills = tmp_path / 'skills'
    returncode = bootstrap.install_skill(['--target', str(skills / 'doubaoplot')])
    capsys.readouterr()

    assert returncode == 3
    assert list(skills.glob('*.lock')) == []


def test_skill_pins_the_two_allowed_pypi_mirrors():
    """换源只许换这两个官方镜像，默认仍走 PyPI —— 别让 Agent 自己去挑一个"更快的源"。"""

    text = (SKILL_ROOT / 'SKILL.md').read_text(encoding='utf-8')
    assert 'https://pypi.tuna.tsinghua.edu.cn/simple' in text
    assert 'https://mirrors.aliyun.com/pypi/simple/' in text
    assert '只许用这两个源' in text
    assert '默认仍然走官方 PyPI' in text
    assert 'requirements-runtime.lock' in text
