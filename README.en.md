<div align="center">
  <h1>DoubaoPlot</h1>
  <p><strong>Editable Origin figures from your scientific data, inside 豆包工作 (Doubao Work)</strong></p>
  <p>A derivative work of <a href="https://github.com/hang-jin/editaplot">hang-jin/editaplot</a> · Apache-2.0</p>
  <p>
    <img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-4c6ef5">
    <img alt="Platform: Windows 10/11 x64 only" src="https://img.shields.io/badge/platform-Windows%2010%2F11%20x64%20only-0078d4">
    <img alt="Python 3.10–3.12" src="https://img.shields.io/badge/Python-3.10%E2%80%933.12-3776ab">
    <img alt="Doubao Work Skill" src="https://img.shields.io/badge/Doubao%20Work-Skill-7c3aed">
    <img alt="Origin 2021–2026b compatibility target" src="https://img.shields.io/badge/Origin-2021%E2%80%932026b%20target-2563eb">
    <img alt="Fully verified with Origin 2024b" src="https://img.shields.io/badge/fully%20verified-2024b-0f766e">
    <a href="https://github.com/hang-jin/editaplot"><img alt="Upstream EditaPlot GitHub Stars" src="https://img.shields.io/github/stars/hang-jin/editaplot?style=social"></a>
  </p>
  <p><a href="README.md">中文说明</a> · Chinese is the primary documentation language</p>
</div>

## What this is

Hand your experimental table (CSV, TXT, XLS, XLSX) to Doubao Work. It reads every column, recommends a chart, asks you to confirm, then drives the Origin installation already on your computer to draw it.

**What you get back is not a picture. It is an editable Origin project (`.opju`)**, plus PNG, PDF, and TIF. Double-click it and keep editing colours, axes, legends, and text.

This is not a "replace the numbers" template, and a Python preview is never passed off as an Origin result. When a column is ambiguous it stops and asks, instead of inventing columns, fits, or conclusions.

Three things to know first:

- **Physical Windows 10/11 x64 only.** Origin is Windows software; macOS, Linux, WSL, and virtual machines cannot run the workflow.
- **Origin is yours to install.** This only calls an Origin or OriginPro already on your computer; it never installs or modifies it.
- **It does not compute your data for you.** No smoothing, fitting, outlier removal, or significance testing. Compute those yourself and it will draw them.

## What the figures look like

<div align="center">
  <img src="assets/gallery/xps-fit.png" alt="XPS peak fit" width="31%">
  <img src="assets/gallery/medical-grouped-box.png" alt="Medical grouped box plot" width="31%">
  <img src="assets/gallery/uv-vis-tauc.png" alt="UV–Vis with Tauc inset" width="31%">
  <img src="assets/gallery/percent-composition.png" alt="Percent stacked composition" width="31%">
  <img src="assets/gallery/medical-shap.png" alt="Composite SHAP contribution figure" width="31%">
  <img src="assets/gallery/circular-network.png" alt="Multi-panel circular directed weighted network" width="31%">
</div>

All rendered on a real machine running Origin 2024b and checked by eye, using synthetic teaching data that represents no real measurement.

➡️ [All 45 examples and what each is for](docs/gallery.en.md)

## What it can draw

40 plotting routes:

| Area | Charts |
|---|---|
| Materials and spectroscopy | XPS scan/fit, XPS multi-spectrum comparison, XRD, GSAS/GSAS-II XRD Rietveld, XAS, FTIR/IR, NMR, DSC, PL/TRPL, UV–Vis/Tauc, EIS, CV, LSV, 3D multi-condition Nyquist |
| General statistics | Bar/column, error bars, stacked and percent-stacked, pie, Sankey, multi-panel circular directed weighted network, line, trend, scatter, bubble, radar, heatmap (dense matrices get an adaptive layout) |
| Distributions and effects | Raw-point summaries, box, violin, raincloud, histogram, forest, 3D dual-density ridgelines |
| Medical and machine learning | ROC, PR, calibration, DCA, confusion matrix, Bland–Altman, paired longitudinal trajectories, grouped box, composite precomputed SHAP |

### The 17 it cannot draw

Origin can draw these, but this Skill has no route for them. Ask for one and it says so plainly instead of attempting a run that fails:

| Category | Not covered |
|---|---|
| Basic statistics | Area chart, ECDF, Q-Q plot |
| Specialist | Ternary phase diagram, **Kaplan-Meier survival curve** |
| Multivariate | Broken axis, polar / wind rose, pair plot, parallel coordinates, scatter matrix |
| 3D | Contour, surface, 3D bar, volume, slice, vector field, isosurface |

The one asked about most is the **survival curve**: the medical group covers ROC, PR, DCA, calibration, confusion matrix, and Bland–Altman, but not Kaplan-Meier.

**PCA / t-SNE / UMAP are not on this list** and can be drawn. But you compute the embedding first; the Skill only plots finished coordinates as a grouped scatter.

### Palettes

![Scientific palettes](assets/palettes/palette-selector-public.zh-CN.png)

Ten scientific palettes, eight on the first screen and two advanced. The chart selector recommends palettes for whichever chart you pick and pushes colour-blind-risky ones down the list. Colours that carry scientific meaning, such as XPS components, positive and negative values, heatmaps, and diagnostic reference lines, are never changed to look nicer.

The palettes were designed and abstracted independently. They do not copy journal covers, watermarks, or layouts, and they are not the official template of any journal.

## Install

**Say this in Doubao Work:**

```text
帮我安装 GitHub 上 chuspeeism 的 doubaoplot Skill
```

("Install the doubaoplot Skill from chuspeeism on GitHub.") In Codex or Claude Code, say the same thing.

Open a new task afterwards and it is ready. **Remember to install Origin yourself.**

**It tells you the plan before it starts.** Before the first render it walks through the four things this route needs — the Skill, the rendering engine, the ten dependency libraries, and a usable Python — and names the ones your machine already has so you can see them being skipped. It fills in the missing ones itself; only installing Python stops to ask you. You never have to guess what it is waiting on.

<details>
<summary><b>If it reports that the rendering engine is missing (engine_not_found)</b></summary>

The rendering engine is not inside the Skill; it lives in `runtime/` in the complete repository. Some hosts install only the Skill subfolder, which leaves the engine behind.

**The agent fetches it on its own.** The Skill instructs the agent to download the complete repository and run `setup` without asking you first and without handing the download back to you. It stops to ask only when your machine has no 64-bit Python 3.10–3.12 and one must be installed, which is a system-level change.

To do it yourself, download the complete repository and run `setup` inside it:

```powershell
git clone https://github.com/chuspeeism/doubaoplot.git
Set-Location doubaoplot
.\editaplot.cmd setup
```

If git is unfamiliar, download the Source ZIP from the GitHub page, **extract all of it**, and run the same `setup` in that folder.

`setup` does three things: find an existing 64-bit Python 3.10–3.12, create a Python environment used only by this project, and install the Skill into the host directory it detects, **printing the path it actually chose**. When no suitable Python exists, it explains that installing one is a separate system change and waits for your consent before installing Python 3.12. It never installs or modifies Origin.

</details>

<details>
<summary><b>If your agent does not list the Skill after installing</b></summary>

It probably went somewhere else. Resolution order:

1. `EDITAPLOT_SKILL_DIR`, if you set it
2. An existing host directory. On Windows, Doubao Work uses `%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills`; `~/.doubao/skills`, `~/.doubao-work/skills`, and `~/.codex/skills` are also probed
3. Otherwise it falls back to `~/.codex/skills/doubaoplot`

`setup` prints the target it chose. If your agent reads a different directory, point at it and run again:

```powershell
$env:EDITAPLOT_SKILL_DIR = "<your agent's skills directory>\doubaoplot"
.\editaplot.cmd setup
```

</details>

<details>
<summary><b>If the dependency install is very slow, or reports dependency_install_timeout</b></summary>

The ten dependency libraries are about 45 MB, the slowest step of the whole install (fetching the repository is only 7.7 MB). They come from PyPI by default, which is slow from mainland China and can hit the 900-second cap on that step.

**The agent retries through a Chinese mirror on its own** — Tsinghua TUNA first, Aliyun if that fails — and tells you which one it used. You can also set it yourself before installing:

```powershell
$env:PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

A mirror only changes where the files come from; the versions installed are still the ones pinned in the lock file.

</details>

<details>
<summary><b>If installation fails, mentions editaplot, or claims it cannot write</b></summary>

Update to the latest version and install again. Every version before 2026-09-06 fails deterministically: before writing the Skill out, the installer runs an identity check that recognized only the upstream name `editaplot`, while this project's SKILL.md declares `doubaoplot`.

- First attempt: the staged copy fails that check, and older versions disguise it as “cannot write, grant write access”.
- Second attempt: `skill_destination_not_editaplot` — “this non-empty directory is not a Skill I recognize, refusing to overwrite”.

Neither is a permission problem. Do not change folder permissions and do not rerun as administrator; pull the latest code and run `setup` again.

**Also, do not hand-copy files instead of running `setup`.** Copying `skill/doubaoplot` into a skills directory installs the Skill but neither the rendering engine nor its project-local Python environment, and you only find out when the first render fails.

</details>

## Two ways to use it

### Way 1: you have a reference figure

You saw a figure you like and want your own data drawn that way. Attach the **reference figure** and **your data file** together, then say:

```text
帮我在 Origin 中，用我的数据复刻这张参考图的绘图风格
```

("Reproduce this reference figure's plotting style in Origin with my data.") It analyses the reference's layout, palette, and plotting details first, then draws with your data.

**The reference shapes style, never data.** Anything absent from your table is not invented to match the picture.

### Way 2: you do not know which chart to draw

The more common case: you have the data, but box plot or violin plot? And how do you describe that to an AI so it gets it right the first time?

Invoke the Skill and say:

```text
我不知道该画什么图，帮我看看
```

("I don't know which chart to draw, help me look.") The **chart selector** opens **inside Doubao Work's own browser**: 45 real Origin figures laid out and grouped by field, from materials characterization and electrochemistry through medical and machine-learning evidence to general statistics and distributions.

The selector is a loopback-only page (`http://127.0.0.1:17864/`); it does not pop a separate Chrome window at you. Only an agent with no browser of its own falls back to the system default browser.

Click one and the right panel shows:

- **which columns your data needs** for this figure, the single most useful line
- the route's boundaries, including what it will not compute for you
- recommended palettes, output size, error bars, significance markers

Click "发送给豆包" (send) when done, or "复制" (copy) and paste it back. The page **always puts the text on your clipboard first** and only then tries to auto-send, so a failed auto-send costs you one paste, never a dead end.

The required-column list is a hint, not a verdict. Whether your table really has those columns is checked column by column before anything is drawn, and a missing one is reported as usual.

### A prompt for the first run

Attach the file and send:

```text
Draw this data. Do not modify the source file. First tell me which columns you recognized and
which chart you recommend. Then classify every column as drawn, support/validation only, retained
without rendering, or uncertain; list the final figure elements and the calculations that will not
be performed. Ask me about uncertain roles instead of guessing. Ask before installing Python; do
not install or modify Origin. I do not need to open Origin first. Doctor is read-only, so run the
real smoke test before rendering, start a dedicated Origin instance, and continue according to the
detected version and template capabilities. Do not ask me to copy PowerShell, use administrator
rights, or change DCOM or the registry.
```

If you also give it a reference figure, add:

```text
Treat the reference figure only as a visual brief. Summarize its marks, layout, encodings, and
safely adaptable style without copying its data, labels, fits, phase assignments, logos, or
watermarks, and do not embed the bitmap. Ask separately for my exact series colors, line widths,
fill transparency, page/aspect ratio, and legend show/hide, borderless, or position choices. My
explicit choices take precedence over the reference. List what will be applied, kept as the
template default retained, rejected, or still needs clarification; mark a field applied only when
the selected renderer has verified it and can read it back. Then wait for my confirmation.
```

## What you get at the end

**A folder, not a picture**, created beside your data file and named `<data-file-stem>_EditaPlot_<timestamp>`.

| File | What it is |
|---|---|
| **`result.opju`** | **The Origin project. This is the deliverable.** Double-click and keep editing colours, axes, legends, text |
| `result.png` | For Word documents and chat |
| `result.pdf` | Vector, often required for submission |
| `result.tif` | The format journals name most often |
| `origin_verify_report.json` | The readback report: axes, fonts, and layers re-read from Origin after rendering |

That last report is the difference from "export a PNG and call it done": after rendering, objects are read back out of Origin, and a mismatch counts as a failure.

The Origin window stays open by default, so the figure is right there to edit. Your source file is never overwritten, and the destination changes only when you ask for another location.

**To edit in Origin, double-click `result.opju` yourself.** The agent shows you `result.png`, because its screenshot channel cannot see the Origin window it launched. That step is a person's job.

## How long is normal, and what to check

With the environment ready, a normal-sized table, and confirmations done, 4–5 minutes from inspection to verified export is reasonable, with the Origin connection test and the render taking roughly ten to fifteen seconds each. First-time dependency installs, large Excel files, complex layers, slow disks, and Windows security scans all add time.

**Nothing waiting on you, no new progress, and more than 30 minutes gone is not normal.** Ask which stage it is in, then check this table:

| Symptom | Usually |
|---|---|
| Your agent does not list the Skill after install | It went to another directory; see the second collapsed block under Install |
| `engine_not_found` | The rendering engine never arrived; see the first collapsed block under Install |
| Stuck in setup or downloading dependencies | Network, proxy, or package index, not Origin |
| Stuck understanding the data | It is waiting for your reply or a permission approval |
| Stuck starting Origin | Run `editaplot.cmd doctor` to see the stage. Then check for an Origin dialog, a non-writable output folder, or a sync tool holding the files |
| The selector will not open | Have the agent open the printed `http://127.0.0.1:…` address in its own browser. If ports 17864/17865/17866 are all busy it prints a local file path instead: open it yourself, click copy, paste back |
| "Send to Doubao" does nothing | The text is already on your clipboard; paste it |
| The figure is not what you wanted | Edit it in Origin; that is what the OPJU is for |

Only one Origin rendering job runs at a time per Windows session; the rest queue, so do not restart a job when you see the queue notice. Rendering itself needs no network; that is only for the first download, updates, and locked dependencies.

## Command line (optional)

```powershell
.\editaplot.cmd doctor
.\editaplot.cmd inspect <data.csv>
.\editaplot.cmd recommend <data.csv> --intent "compare models with uncertainty"
.\editaplot.cmd understand <data.csv> --template-id xrd --output data-understanding.json
.\editaplot.cmd palettes --template-id trend
.\editaplot.cmd plan <data.csv> --template-id bar --claim "Model A performs better" --evidence-role comparison --palette-id ocean_coral --semantic-confirmation-json semantic-confirmation.json --output render-plan.json
$smokeDir = Join-Path $env:TEMP ("EditaPlot-origin-smoke-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
.\editaplot.cmd origin-smoke --output-dir $smokeDir
.\editaplot.cmd render render-plan.json
.\editaplot.cmd verify <Origin-output-directory>
```

`palettes --template-id` lists only the palettes usable with that chart. `origin-smoke` starts an isolated Origin instance and completes a minimal export loop; the formal render runs only after it passes. Ignore `--engine-home` in normal use, and omit `--output-dir` on `render` so the output lands beside your source data.

When the Skill folder has no `editaplot.cmd` (a host that installed only the Skill subfolder), replace every `.\editaplot.cmd` above with `python "<skill directory>\scripts\bootstrap_editaplot.py"`; the arguments are identical.

## What permissions it needs

Approve only this much. There is no reason to hand over the whole computer:

| Allowed scope | Why |
|---|---|
| Read the complete repository, your table, and an optional reference image | Install the Skill, understand columns, prepare the plan |
| Write to this repository and the current user's skill directory | Create the project environment and install or update the Skill |
| Write to the source data folder | Create one timestamped delivery folder beside the source without overwriting it |
| Run local `editaplot.cmd`, PowerShell, and Python, and start Origin in the same interactive Windows session | Diagnose, run the connection test, render, export, read back |
| Reach GitHub and the Python package index on first install or update | Download the public source and locked dependencies |

Normal use does **not** need administrator rights, mouse control, whole-drive write access, or changes to DCOM, the registry, the firewall, or the Origin installation. If Controlled Folder Access, an organization policy, cloud sync, or a read-only directory blocks output, allow just the repository and the current data folder, or name another writable destination. Do not reach for global elevation as a fix.

Some hosts run ordinary commands under an isolated account that lacks your signed-in right to start Origin. So it reads the process's real Windows security token rather than trusting environment variables. On detecting an isolated context it stops before calling Origin and requests narrowly scoped local execution for that one exact command, rerunning only if approved. You never need to copy a command into your own PowerShell, run as administrator, or edit the registry.

The bundled Python runtime and Origin automation **do not initiate a network upload** of your data. A file you hand to the agent is still governed by your account's and your organization's data policies. Deidentify medical data and reference images according to your institution's rules and check for burned-in identifiers before sharing them; **automatic PHI detection is not promised**.

## What it will not do for you

A deliberate boundary, and one worth not working around:

- Your source file is read-only. Helper columns exist only in memory or in the editable Origin workbook
- Every column's use is explained before planning. An unresolved numeric column never quietly becomes a curve
- A missing column is reported as missing, **never fabricated**
- No smoothing, outlier removal, peak filling, error calculation, curve fitting, or significance testing on your behalf
- No phase identification, band-gap or lifetime calculation, or model training. Supply those results and it will draw them
- A reference figure influences only grammar and style your confirmed data supports; it cannot add evidence or hide required elements. Your explicit style choices win and are each reported as applied, template default retained, or rejected
- 3D only when the third axis carries real experimental meaning, never for decoration
- A legend can be moved later in the OPJU, but missing axes, inconsistent fonts, overlapping colour bars, and clipped text still count as failures

## Where this came from

**DoubaoPlot is a derivative work of [hang-jin](https://github.com/hang-jin)'s [EditaPlot](https://github.com/hang-jin/editaplot), based on upstream commit `4aa986f` and released under the same Apache-2.0 license.**

Nearly everything described on this page is hang-jin's work. Having an AI understand scientific data, recommend a figure, and drive a local Origin to produce something you can keep editing, that idea and its entire implementation come from EditaPlot: the 40 plotting routes, the verification that reads objects back out of Origin after every render, the 45 real example figures, the 10 scientific palettes. None of it was swapped out.

What this derivative adds is the layer around it, so the thing installs, runs, and can be asked for the right chart inside Doubao Work:

| Added | Why |
|---|---|
| The Skill installs into Doubao Work | Upstream hard-codes `~/.codex/skills`, which Doubao Work never reads, so an install looked successful while landing nowhere. Host directories are now probed and the chosen path printed; when a host installs only the Skill subfolder and the launcher is missing, an equivalent entry point is documented |
| The chart selector | Users often cannot name the chart they need. Letting them **look and pick** beats making them **describe**. It only clarifies the request; it changes no plotting behaviour and skips no confirmation step |
| The list of 17 charts with no route | Previously each of those meant a failed run, several wasted minutes, and a user assuming their own data was at fault |
| Errors that name the valid options | A wrong column role or an incompatible palette used to fail with just "invalid", leaving the agent to read source code. One error message and one palette lookup were changed for this; **rendering logic was not** |
| User-facing docs and prompts | Upstream documentation is written with Codex as the host |

**No plotting behaviour, data contract, or verification gate was modified.** The itemized statement of changes is in [NOTICE](NOTICE).

The name DoubaoPlot belongs to this derivative alone and implies no endorsement by or involvement of hang-jin.

**If this was useful, go star [hang-jin/editaplot](https://github.com/hang-jin/editaplot).** That project is what actually draws publication-quality figures; this one carried it into Doubao Work.

<div align="center">
  <a href="https://github.com/hang-jin/editaplot"><img src="https://raw.githubusercontent.com/hang-jin/editaplot/metrics/assets/star-trend/stars.svg" width="760" alt="EditaPlot GitHub Star trend"></a>
</div>

<p align="center"><sub>Star trend of upstream EditaPlot, generated by the upstream repository. Aggregate repository count only, with no Stargazer list, username, or personal star timestamp involved.</sub></p>

**Other agents work too.** This is a standard SKILL.md skill, so Codex, Claude Code, and anything else that reads SKILL.md can install and run it with identical plotting behaviour. Directory probing, doc tone, prompt wording, and the selector interaction are simply built for Doubao Work users; elsewhere those conveniences just do not apply. Read "Doubao Work" above as whichever agent you use.

## Independent project notice

This project calls an Origin or OriginPro already installed on your computer and by default starts an instance it owns, so no window has to be open in advance. It does not bundle, install, or modify that application, and it does not expose its Automation Server over a network or the cloud. It is not affiliated with, sponsored by, or endorsed by OriginLab Corporation; Origin and OriginPro are trademarks of OriginLab, used here only to describe compatibility.

## License

[Apache License 2.0](LICENSE), same as upstream. Every change relative to upstream is itemized in [NOTICE](NOTICE).

The badges and the Star trend chart use only GitHub's aggregate repository count. No Stargazer lists, usernames, account IDs, or personal star timestamps are requested, stored, or displayed.
