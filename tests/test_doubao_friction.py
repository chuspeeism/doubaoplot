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
import bootstrap_editaplot as bootstrap
import editaplot
import editaplot_core as core
import selector as chart_selector
from origin_sciplot.scientific_workflow import apply_scientific_palette_override, ScientificWorkflowError

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
        core._prepare_template_for_understanding(ROOT / 'runtime/templates/trend/example_standard.csv', template_id='trend', mapping={}, engine_home=ROOT / 'runtime')
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
        with urllib.request.urlopen(f'{base}/') as response:
            assert response.read() == b'<html>selector</html>'
            assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        with urllib.request.urlopen(f'{base}/pick?d=' + urllib.parse.quote('画个雨云图')) as response:
            assert response.headers['Content-Type'] == 'image/gif'
        assert chart_selector._Handler.result['prompt'] == '画个雨云图'
    finally:
        server.server_close()
        chart_selector._Handler.page_bytes = b''
        chart_selector._Handler.result = {}


def test_selector_does_not_open_a_system_browser_by_default(monkeypatch, capsys):
    opened: list[str] = []
    monkeypatch.setattr(chart_selector, '_open_in_browser', lambda target: opened.append(target) or True)
    chart_selector.main(['--timeout', '0.2'])
    assert opened == []
    assert 'http://127.0.0.1:' in capsys.readouterr().out


def test_selector_open_flag_opens_the_http_address(monkeypatch, capsys):
    opened: list[str] = []
    monkeypatch.setattr(chart_selector, '_open_in_browser', lambda target: opened.append(target) or True)
    chart_selector.main(['--timeout', '0.2', '--open'])
    capsys.readouterr()
    assert opened and opened[0].startswith(('http://127.0.0.1:', 'file://'))
