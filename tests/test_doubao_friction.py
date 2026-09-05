"""Doubao installation and discoverability regressions; no Origin required."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skill/editaplot/scripts'))
sys.path.insert(0, str(ROOT / 'runtime/src'))
import bootstrap_editaplot as bootstrap
import editaplot
import editaplot_core as core
from origin_sciplot.scientific_workflow import apply_scientific_palette_override, ScientificWorkflowError


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
