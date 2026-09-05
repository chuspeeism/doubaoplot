# Scientific data understanding and element confirmation

Use this gate after selecting a candidate template and before creating a render plan.

## The five data dispositions

Every source column must appear exactly once:

- `render_primary`: the main evidence shown in the figure;
- `render_secondary`: background, fit, residual, reference, phase tick, or another visible aid;
- `support_only`: used for validation, filtering, weighting, coordinate choice, or layout control,
  but not drawn as a curve or mark;
- `retain_not_render`: preserved for provenance/editability and not used by the visible figure;
- `uncertain`: scientific meaning is unresolved; planning is blocked.

Do not use `ignored` as an unexplained wastebasket. Explain why each non-rendered numeric column is
support-only or retained.

## Required sequence

1. Prepare the selected template with the proposed or corrected column mapping.
2. Run `understand` using that exact mapping.
3. Summarize in natural language:
   - what kind of experiment/table this appears to be;
   - what will be drawn;
   - what is retained or used only as support;
   - what approved display helpers are proposed;
   - what the drawing layer will not calculate;
   - any focused unresolved scientific questions.
4. If an item is uncertain, obtain a corrected mapping and return to step 2.
5. Ask the user to confirm the concise summary.
6. Pass the exact proposal hash, approved helper IDs, and ambiguity resolutions to `plan`.

A different source hash, mapping, or proposal hash invalidates the confirmation. Never edit a
confirmed JSON plan by hand.

## Derived data

Source columns and derived helpers are separate objects. A helper requires:

- an allow-listed deterministic operation;
- complete source-item lineage;
- explicit user approval;
- a stated scientific/display purpose;
- a renderable disposition when visible.

Do not silently fit, smooth, remove outliers, calculate error bars, identify phases, calculate
background, derive band gaps, calculate SHAP, or create statistics. Simple display helpers such as
an X-axis sign transform, percentage-of-row total, or a phase-tick Y lane remain explicit and never
overwrite source values.

## GSAS/GSAS-II Rietveld example

A suitable short confirmation is:

> 我理解这是 XRD Rietveld 精修结果。要画：2θ、实测点、计算线、文件中已提供的背景/差值和两组物相刻线。只保留不画：weight、Q、Used、diff/sigma 与轴控制列。不会自动计算背景、差值、Rwp、χ²、物相或峰归属。Publication Diff 将按源值直接绘制，不再偏移。这个理解是否正确？

If a numeric column such as Temperature is not part of a recognized contract, do not guess. Ask
whether it is a plotted condition, support metadata, an alternative coordinate, or a column that
should be retained without display, then regenerate the proposal.

## Conversation contract

Keep the first response compact. The full JSON is audit evidence for Codex and advanced users, not
the default beginner explanation. Ask only questions that can change the scientific meaning or
visible elements.

## mapping.json：明确指定每一列的角色

`assignments` 的键是源文件的完整列名，值是下表中的角色名；不是反过来。
所有列必须各出现一次。不画的列用 `ignored`，并在语义确认中说明保留而不绘制的理由。
例如，trend 数据表有 `Time`、`Control`、`Treatment`、`Notes` 四列：

```json
{
  "assignments": {
    "Time": "x",
    "Control": "series",
    "Treatment": "series",
    "Notes": "ignored"
  }
}
```

trend 需要一个 `x` 和至少一个 `series`，多个系列各自填 `series`。
把列名替换为真实表头；同一份 mapping 同时传给 `understand` 和 `plan`：
`python "<skill目录>\scripts\bootstrap_editaplot.py" understand "<数据文件>" --template-id trend --mapping-json "<mapping.json>"`。
需要上下文的模板可另加顶层 `plot_mode`（XPS 用 `energy_kind`）；可选值以该次
`mapping_request.context_options` / `energy_kind_options` 为准，不要猜测。

以下角色直接核对 `runtime/templates/*/service.py` 注册的服务，以及
`runtime/src/origin_sciplot/scientific_workflow.py::role_options`、
`template_service.py::XpsTemplateService._ROLE_OPTIONS`。列出的是允许角色，
具体必填数量、数值与布局限制仍由各模板数据契约和 `confirm_mapping` 校验。

| template_id | assignments 可用角色名 |
|---|---|
| `xps` | `x`, `raw`, `background`, `envelope`, `residual`, `component`, `ignored` |
| `eis` | `z_real`, `z_imag`, `frequency`, `magnitude`, `phase`, `ignored` |
| `trajectory3d` | `x3d`, `y3d`, `z3d`, `series_id`, `ignored` |
| `density_ridgeline3d` | `condition_id`, `condition_position`, `density_x`, `density_solid`, `density_dashed`, `focal_x`, `ignored` |
| `cv` | `x`, `series`, `ignored` |
| `lsv` | `x`, `series`, `ignored` |
| `xas` | `x`, `series`, `ignored` |
| `pl` | `x`, `series`, `fit`, `ignored` |
| `xps_compare` | `x`, `series`, `ignored` |
| `uv_vis` | `x`, `series`, `photon_energy`, `tauc`, `tauc_fit`, `bandgap`, `ignored` |
| `ftir` | `x`, `series`, `ignored` |
| `nmr` | `x`, `series`, `ignored` |
| `dsc` | `x`, `series`, `ignored` |
| `xrd` | `x`, `observed`, `calculated`, `background`, `difference`, `phase_tick`, `support`, `series`, `ignored` |
| `bar` | `category`, `series`, `error`, `ignored` |
| `horizontal_bar` | `category`, `series`, `error`, `ignored` |
| `stacked_bar` | `category`, `series`, `error`, `ignored` |
| `percent_stacked_bar` | `category`, `series`, `ignored` |
| `pie` | `category`, `series`, `ignored` |
| `sankey` | `source`, `target`, `value`, `ignored` |
| `trend` | `x`, `series`, `ignored` |
| `radar` | `category`, `series`, `ignored` |
| `circular_network` | `panel`, `source`, `target`, `value`, `sign`, `source_group`, `target_group`, `edge_label`, `ignored` |
| `heatmap` | `category`, `series`, `ignored` |
| `scatter` | `x`, `series`, `ignored` |
| `line_error` | `x`, `series`, `error`, `ignored` |
| `grouped_box` | `series`, `ignored` |
| `raw_summary` | `series`, `ignored` |
| `violin` | `series`, `ignored` |
| `histogram` | `series`, `ignored` |
| `forest` | `category`, `estimate`, `lower`, `upper`, `reference`, `ignored` |
| `bubble` | `x`, `series`, `size`, `ignored` |
| `diagnostic_curve` | `x`, `series`, `reference`, `ignored` |
| `confusion_matrix` | `category`, `series`, `ignored` |
| `calibration_curve` | `x`, `series`, `count`, `ignored` |
| `bland_altman` | `mean`, `difference`, `bias`, `loa_lower`, `loa_upper`, `ignored` |
| `decision_curve` | `x`, `series`, `treat_all`, `treat_none`, `ignored` |
| `paired_trajectory` | `x`, `series`, `ignored` |
| `raincloud` | `series`, `ignored` |
| `shap_summary` | `feature`, `shap`, `feature_value`, `sample_id`, `feature_order`, `mean_abs_shap`, `feature_group`, `group_contribution`, `ignored` |

`xps_c1s_fit`、`xps_adaptive` 是内部渲染模板，不接受独立的公共 `template_id` 映射请求；通过 `xps` 服务使用上述 XPS 角色。

## 按模板选配色

用 `palettes --template-id trend` 只查支持 trend 模式的公开配色；加 `--all` 包括高级配色。
保留语义色彩契约、不支持覆盖的模板返回空列表。筛选只判断模板模式兼容性，
系列数量上限等依赖具体数据的条件仍在 `plan` 阶段检查。
