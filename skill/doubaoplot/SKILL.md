---
name: doubaoplot
description: DoubaoPlot。针对豆包/豆包工作优化，Codex、Claude Code 等 Agent 同样可用。把本地科研数据（CSV/TXT/XLS/XLSX）画成可继续编辑的 Origin 图。两种用法：① 用户给了参考图就复刻其绘图风格；② 用户只有数据、说不清要画什么图时，弹出图表选择器让他从 45 张真机示例里点一张。覆盖 XPS、XRD、XAS、PL/TRPL、DSC、NMR、FTIR/IR、UV-Vis、电化学、医学与机器学习证据图、分布、关系、误差棒、柱状、堆叠、饼图、桑基、雷达、热力图以及已验证的三维路线；产出可编辑 OPJU 并导出 PNG/PDF/TIF。Analyze local scientific CSV, TXT, XLS, or XLSX data; recommend publication-informed charts and Chinese scientific palettes; freeze a reproducible plan; and automate editable figures through a callable local Origin/OriginPro installation on physical Windows 10/11 x64. Do not use on macOS, Linux, WSL, Wine/CrossOver, Parallels, or other VMs; to install or modify Origin; to redistribute reference images; or to claim an unverified Origin route.
---

# EditaPlot

Turn a scientific question and a read-only table into an auditable, editable Origin figure. Keep
the beginner experience conversational; use the deterministic engine for inspection, planning,
rendering, exporting, and readback.

## 先把安装这件事讲清楚（豆包工作版新增）

第一次为某台机器干活时，**先报账，再干活**。用户的挫败感几乎都来自"不知道要等什么、
不知道还有几步"，而不是等待本身。

先跑一次（这条命令不依赖引擎，缺引擎时也能跑）：

```
python "<skill目录>\scripts\bootstrap_editaplot.py" --diagnose
```

从输出里读四件事：

| 字段 | 说明什么 |
|---|---|
| `host.compatible` | 是不是 64 位 Windows。`false` 就直接说清这条路走不了，不要再往下走 |
| `engine_home` | 绘图引擎在不在。`null` = 还得把完整仓库取下来 |
| `selected` | 有没有可用的 64 位 CPython 3.10–3.12。`null` = 需要装 Python |
| `selected.source` | 等于 `managed_environment` 说明依赖库也已经就位 |

然后用一段话把整条链路讲给用户，**已经具备的要点名说"跳过"**——那是他能感知到的"更快"，
不要沉默略过：

> 画图这条链路一共四件事：① 装 Skill（已完成）② 取绘图引擎 ③ 装 10 个依赖库
> ④ 有一个能用的 Python。你这台机器上 ③ ④ 现成，直接跳过；只差 ②，我去取一下，
> 大概一两分钟，装完常驻，以后画图不再等这一步。Origin 你已经装好了，我只调用它。

规则：

- **每一步开始前先说一句**，别让用户在等待里猜你在干什么。下载、解压、建环境都要报。
- **报完就接着做，不要停下来等一句"好"。** 这是告知，不是请示。
- 四件事里只有**装 Python** 需要先征得同意（系统级变更）；取仓库、装依赖属于已声明的用途，
  直接做完再汇报。
- 全部现成时也要说一句："都现成，直接开画。"

### 依赖装得慢就换国内镜像（中国大陆网络）

装那 10 个依赖库要下大约 45 MB（numpy 15.5、pandas 11、matplotlib 8.2、Pillow 7.2 是大头），
这是整个安装里最花时间的一步 —— 相比之下取仓库才 7.7 MB。安装脚本给这一步的上限是
**900 秒**，超了直接报 `dependency_install_timeout`。国内直连 PyPI 常见几十到几百 KB/s，
很容易撞上这个上限。

**这一步明显卡住（两三分钟没进展），或者已经报过 `dependency_install_timeout`，就换国内镜像
重跑一次。** 在启动 `setup` / `repair-environment` 的那条命令之前设好环境变量即可，它会一路
传到底层的 pip：

```powershell
$env:PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

清华源连不上就换阿里云：`https://mirrors.aliyun.com/pypi/simple/`。

规矩：

- **只许用这两个源**（清华 TUNA、阿里云），它们是 PyPI 的官方镜像。**不要自己去找别的"更快的
  源"**，也不要用 `--trusted-host` 关掉证书校验。
- **默认仍然走官方 PyPI。** 只有慢到影响使用、或者已经超时了才换，不要一上来就换。
- 换了要**告诉用户换成了哪个源、为什么换**，一句话说清，不用停下来等他同意。
- 换源换的只是"从哪儿下载"，装的仍然是 `requirements-runtime.lock` 里钉死的那些版本，
  版本一个都不会变。

### 在 Windows 上跑命令的硬规矩

宿主是 Windows PowerShell，不是 bash。实跑记录里在这里连着栽过三次，逐条避开：

- **不要用 POSIX 写法。** `ls`、`2>/dev/null`、`&&`、反引号、单引号包 Windows 路径都会报错。
  列目录用 `Get-ChildItem`，忽略错误用 `-ErrorAction SilentlyContinue`，连续执行用 `;`。
  路径统一用双引号包起来。
- **不要假设机器上有 git。** 先 `git --version` 探一下；没有就直接下 ZIP，不要在 git 上反复重试：

  ```powershell
  Invoke-WebRequest -Uri "https://github.com/chuspeeism/doubaoplot/archive/refs/heads/main.zip" -OutFile "$env:TEMP\doubaoplot.zip"
  Expand-Archive -Path "$env:TEMP\doubaoplot.zip" -DestinationPath "$env:USERPROFILE\doubaoplot" -Force
  ```

  解压出来的目录叫 `doubaoplot-main`，`setup` 要在那个目录里跑。
- **不要用 GitHub API 去列仓库目录再挑文件。** 整包取下来最快，也不会漏东西。
- **下载和解压本来就慢**（整包十几 MB、上千个文件）。命令超时不等于失败：先告诉用户这一步要等，
  用更长的超时或后台方式跑，跑完确认目录里有 `runtime\` 和 `editaplot.cmd` 再继续。

## 先决定走哪条路（豆包工作版新增）

用户一进来，先看他手上有什么，再决定怎么走。**不要在用户没给方向的时候就开始猜图型。**

| 用户给了什么 | 走哪条 | 怎么做 |
|---|---|---|
| **一张参考图**（"照这个画""复刻这个风格"） | **参考图模式** | 走原有流程，从第 10 步 `reference-inspect` 进入。参考图只影响已确认数据支撑得住的图形语法与安全样式，不新增证据、不隐藏必需元素。 |
| **点名了图型**（"画个雨云图""ROC 曲线"） | **直接模式** | 走原有流程。先对照 `references/not-covered.md`；如果用户要的图在那张表里，直接说清楚没有这条路线，别硬试。 |
| **只有数据，没说要什么图**，或明说"不知道该画哪种" | **选择器模式** | 见下方。这是本版新增的路径，也是最常见的情况。 |

### 选择器模式

用户不知道自己要什么图的时候，让他**看着选**，比让他**描述**准得多。

1. 运行 `python selector/selector.py`。它**不会自己弹浏览器窗口**，只起一个监听本机的服务，
   并打印一行 `选择器地址：http://127.0.0.1:<端口>/`。
2. **把这个地址用你自己的内置浏览器打开。** 用户已经在豆包工作里了，另外弹一个 Chrome 窗口
   是打断他，不要这么做，也不要把地址甩给用户让他自己去开外部浏览器。
   - 只有当你确实没有任何打开网页的能力时，才改成 `python selector/selector.py --open`，
     让脚本用系统默认浏览器打开，并明确告诉用户你为什么这么做。
   - 页面就是这个服务发出来的，45 张真机跑出来的 Origin 示例图按方向分好类；
     用户点中一张，右侧会显示这张图**需要哪几列数据**，并自动拼好一段完整请求。
3. 用户在页面上点「发送给豆包」，脚本会把拼好的请求收下来打到标准输出；
   点「复制」的话内容在他剪贴板里，请他粘过来。**两条路都通，别只等一条。**
4. 拿到这段请求后，**回到原有流程的第 6 步**继续（`start` → `understand` → 确认 → `plan` → 渲染 → 验证）。
   选择器只负责把需求问清楚，它不改变任何绘图行为，也不跳过任何确认环节。

**选择器给出的「需要哪几列」是提示，不是结论。** 用户的数据到底有没有这些列，仍然由第 7 步
`understand` 逐列核对；缺列就照常告诉用户缺什么，不要因为他在页面上点过就默认数据齐了。

如果 `selector.py` 起不来（`17864 / 17865 / 17866` 三个端口全被占），它会改打印
`页面地址（本地文件）：file:///…`。不要卡住：用这个地址打开页面，或者把本地文件路径给用户
让他自己双击打开，点「复制」再粘回来，流程照旧。

## Request only scoped Windows permissions

- Read the complete repository, selected table, and optional local reference image.
- Write only to the EditaPlot repository, the current user's skill directory (豆包工作 or Codex), and the selected
  source file's parent folder for source-adjacent deliverables.
- Run the local launcher, PowerShell/Python subprocesses, and an EditaPlot-owned Origin instance in
  the same active interactive Windows user session.
- A normal host command may first run under an isolated account. If the Origin worker returns
  `origin_codex_sandbox_context`, submit a formal, narrowly scoped local-execution request for that
  exact `origin-smoke` or `render` command. Rerun it only if that exact request is approved, either
  by the user when prompted or by the host's configured auto-reviewer. Approval is not guaranteed,
  and this handoff is not a sandbox bypass. Never ask the user to copy the command into a separate
  PowerShell window or broaden the request to administrator or system-configuration access.
- Use network access only for repository download/update and locked dependency retrieval. Treat a
  user-scope winget Python installation as a separate system change that still requires explicit
  consent.
- Do not request administrator rights, mouse control, whole-drive write access, cloud upload of
  private inputs, or DCOM, registry, firewall, user-group, or Origin-installation changes. When
  Controlled Folder Access, an organization policy, cloud sync, or a read-only location blocks
  writes, request access only to the affected folder or ask for an explicit alternate output folder.

## 成品展示约束

不要尝试把 Origin 窗口调到前台（foreground）截图。豆包 agent 的截图通道看不到 Bash
启动的 Origin 窗口；禁止反复点任务栏、ShowWindow/SetForegroundWindow、AttachThreadInput
或切虚拟桌面来找窗口。要展示成品就展示导出的 `result.png`；需要在 Origin 内编辑时由真人打开 `result.opju`。

## Start with the beginner path

1. Reject unsupported platforms before installing anything. Support the CLI/dependency layer only
   on physical Windows 10/11 x64 with 64-bit CPython 3.10–3.12. Target Origin/OriginPro 2021 and
   later through external `originpro`; Origin 2020b and earlier are unsupported by this route.
   The fully verified live baseline is CPython 3.10 + Origin 2024b / 10.15. Treat another 2021+
   version as capability-gated, not automatically verified, until its smoke and complete artifacts
   pass. State plainly that macOS (Intel/Apple Silicon), Linux, WSL,
   Wine/CrossOver, Parallels, and other VMs are unsupported in V1. `doctor` cannot reliably detect
   every VM, so ask the user to confirm a physical Windows host when that fact is unknown.
2. 豆包可能只安装 `skill/doubaoplot/` 子目录，里面没有 `editaplot.cmd` 或 `runtime/`。
   真实安装位置为（`%LOCALAPPDATA%` 即当前用户的 `AppData/Local`） `%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\<skill名>`。
   找不到启动器时，不要继续全盘搜索；用 `python "<skill目录>\scripts\bootstrap_editaplot.py" <子命令>`
   作为等效入口，后续参数完全一致。已有完整 runtime 时可加 `--engine-home "<完整仓库>\runtime"`；
   bootstrap 本身不包含 runtime，也不能凭空补齐它。**缺 runtime 时不要停在报错上，不要让用户自己
   去下载，也不要为「要不要下载」再问一次。** 取本项目仓库属于本 Skill 已声明的网络用途，直接去取：
   `git clone https://github.com/chuspeeism/doubaoplot.git`（不方便用 git 就下载 Source ZIP 并完整
   解压），进入仓库目录运行 `.\editaplot.cmd setup`，之后用 `--engine-home "<完整仓库>\runtime"`
   继续原来的命令。只把结果告诉用户：引擎补在哪儿了、下一步做什么。**唯一仍须先征得同意的是安装
   Python**（机器上没有 64 位 CPython 3.10–3.12 时），那是系统级变更，按下面第 4 条处理。
   Locate `editaplot.cmd` in the installed Skill directory; when working from a cloned repository,
   use the repository-root `editaplot.cmd`. Use an absolute launcher path in commands. Do not make
   beginners select a Python executable or invoke `scripts/editaplot.py` directly.
3. Require the complete repository for first installation. Run repository-root
   `editaplot.cmd setup`; never instruct users to copy only `skill/doubaoplot`, because that omits
   the runtime. Read `references/runtime.md` for setup, discovery, and command details.
4. Reuse an existing compatible Python. If none exists, explain in Chinese that installing Python
   is a system-level change. Run `winget show` first and explain the exact publisher, source, and
   agreements. Only explicit user confirmation permits a later non-interactive installation of
   `Python.Python.3.12` with user scope and x64 architecture. If winget is unavailable, provide the
   official python.org Windows installation instructions and wait for the user; never use an
   untrusted mirror or silently install Python.
5. Run `editaplot.cmd doctor` for each new workflow. Allow `doctor --repair` only for the reported
   project-local Python dependency repair. Keep all Python packages in `.editaplot-venv`. Treat
   Origin as a locally installed user-managed application; never install or modify it during repair.
6. Run `editaplot.cmd start <data-file>` for a new table. Add `--intent "<user intent>"` when the
   user states a goal. Treat its inspection and recommendation payload as internal working state.
   Use the original local source path exposed by the attachment. If the host provides only a
   temporary copied attachment and the original folder cannot be recovered, ask once for the intended
   local source/output folder before rendering; never guess an unrelated workspace destination.
7. After selecting a candidate template, run `editaplot.cmd understand <data-file>
   --template-id <id>` with the same confirmed mapping that will be used for planning. See `references/semantic-understanding.md`
   for the complete `mapping.json` example and per-template `assignments` roles. Group its
   result into a short checklist: data type; columns to draw; columns used only for support or
   validation; columns retained but not drawn; proposed figure elements; and calculations that
   will **not** be performed. Every source column must appear exactly once. If any item is
   `uncertain`, ask for a corrected mapping and run `understand` again; do not confirm or plan it.
8. Tell a beginner only: what was recognized, the best one to three chart choices, why they fit,
   and the smallest scientific decision still required. Do not dump an
   `inspect → recommend → understand → plan` pipeline or raw JSON unless they ask for technical
   detail.
9. Ask the user to confirm both a one-sentence scientific purpose and the concise element checklist.
   Freeze the exact `proposal_hash`, approved derived-item IDs, and resolved ambiguity choices in
   `--semantic-confirmation-json`. Never reuse a confirmation after the source, mapping, purpose, or
   proposal hash changes. When confidence is low, candidate margins are small, roles or units are
   ambiguous, or a display transformation is proposed, ask only the additional focused questions
   needed.
10. If the user supplies a reference figure, first run `reference-inspect`. You may then describe
   only its panel/mark/encoding/layout/style grammar in the strict ReferenceFigureSpec JSON and run
   `reference-review`; the runtime performs no OCR or model inference. Show the adopted and rejected
   features, bind every essential mark to confirmed renderable user data, and obtain a separate
   hash-bound confirmation. Never copy reference values, labels, fits, phase assignments, author
   text, logos, watermarks, or the bitmap into the Origin project. Prefer verified
   `template_adaptation`; keep `controlled_composition` blocked until that exact composition has
   passed the full Origin evidence gate. A reference cannot add missing evidence or change the
   confirmed scientific element list.
   Treat style inferred from the reference as a suggestion, not as the user's instruction. Ask
   the user to choose one of three modes: keep the verified template default; use a confirmed,
   allow-listed approximation suggested by the reference; or provide exact custom values. For the
   exact mode, ask separately for colors, physical line width, fill transparency, page size, and
   legend visibility, frame, or position. An explicit user choice has precedence over a conflicting
   reference token. Freeze each reference suggestion as `applied`,
   `retained_template_default`, or `rejected`; never claim a request was applied unless the selected
   template has the same verified preview/Origin route and the required Origin object readback.
11. When color is user-selectable, run `editaplot.cmd palettes`, show
   `assets/palettes/palette-selector-public.zh-CN.png`, and recommend no more than two compatible
   `palette_id` values. Read `references/palettes.md` before freezing one.
12. Internally freeze the confirmed choice with `editaplot.cmd plan`; never hand-edit a plan or write
   a decision back to the source file. For an exact XPS request, write the confirmed values to a
   separate JSON object and pass its path with `--visual-style-json`. The supported exact fields are
   `series_colors`, `line_width_pt`, `fill_transparency_percent`, `page_size_cm`, `legend_visible`,
   `legend_position`, and `legend_frame`. Invalid explicit fields or values must fail fast and be
   corrected with the user; never silently discard them or fall back to a reference/default style.
   The render command copies this approved plan into the final output folder as `render-plan.json`.
13. Treat Origin readiness as technical state only. Doctor performs read-only discovery of
    `Origin.Application`, `Origin.ApplicationSI`, installed candidates, Python, `originpro`, and
    `OriginExt`; it never launches Origin and `ready_for_render` never means a live connection
    succeeded. If the default launch registration is present, proceed to the real pre-render smoke
    without asking the user to open Origin or confirm it again. Keep beginner output to one to three
    plain-language sentences; leave CLSIDs, registry views, candidates, and stages in JSON.
    Read the redacted `origin_execution_context` separately from `ready_for_render`. A
    `codex_sandbox` status requires the exact-command approval handoff above before COM is called;
    only an approved request may be rerun. Auto-review evaluates that individual request and does
    not pre-grant Origin access. An `unknown` Windows execution context is fail-closed and is not an
    approval request: stop before COM and report that the current Windows identity could not be
    verified.
14. Run `editaplot.cmd origin-smoke --output-dir <unique-smoke-directory>` with
    `launch_isolated`: start and own a dedicated Origin instance, perform the live smoke and version
    handshake, then apply the template capability decision. This command is mandatory after planning
    and before formal rendering. `attach_existing` is an explicit advanced mode only; never reset,
    overwrite, or close a user-owned project, and detach instead of exiting. Report failures by
    technical stage and next step without speculation.
    Never use mouse automation or provide application patches or bypass instructions. The runtime
    must attempt to clean a partial EditaPlot-owned activation and may try one fresh isolated
    instance for a retryable startup code only if cleanup succeeds. Cleanup failure returns
    `origin_activation_cleanup_failed` and stops. It must then wait with `sec -poc 30` and confirm
    `run.isOCready()` before reading the version or creating a project. Never loop, switch to
    `ApplicationSI`, edit DCOM/registry permissions, or tell a beginner to run the whole workflow as
    administrator. After the automatic attempt is exhausted, request approval for at most one retry
    in the same active Windows-user context and use a fresh empty sibling smoke directory so the
    first report remains intact. `origin_com_class_not_registered` and
    `origin_com_activation_access_denied` stop without automatic retry. Do not force-terminate a
    Python worker merely because it has run for a long time: it may own a hidden Origin instance.
    Preserve diagnostics and report the last progress stage before proposing any user-controlled
    cancellation.
    Keep the sandbox approval handoff distinct from an activation retry: the former happens before
    COM, while the latter is available only after the bounded activation/cleanup policy has run.
    When primary activation and cleanup both fail, expose only
    `primary_activation_code`, `primary_activation_stage`, `cleanup_error_code`, and
    `cleanup_error_stage`. Never include a Windows account name, local path, raw HRESULT, or raw COM
    text in that structured diagnostic payload, and never retry because both pairs are present.
    Current EditaPlot workers serialize only their active `origin-smoke` / `render` Origin section
    within one signed-in Windows session; data inspection, recommendation, and planning may remain
    concurrent. Respect `origin_job_queue` progress, which is emitted immediately when waiting and
    then about every 30 seconds. Ordering is not guaranteed to be strict FIFO. The 30-minute limit
    applies only to the waiting job: it stops that waiter without killing or interrupting the active
    holder. Do not submit a duplicate while a queue message is visible. Manual scripts, older
    EditaPlot releases, and unrelated programs are outside this coordination boundary.
15. Only after that smoke passes, render an allowed template route with
    `editaplot.cmd render <plan>`. Keep an EditaPlot-owned Origin instance open after success unless
    the user requests otherwise. By default, let the runtime create a direct sibling of the source
    file named `<source_stem>_EditaPlot_YYYYMMDD_HHMMSS`; keep all formal artifacts in that folder.
    Do not redirect ordinary runs to the repository, Skill directory, current working directory, or
    a shared global output folder. Use `--output-dir` only when the user explicitly requests another
    location.
16. Run `editaplot.cmd verify <output-directory>` against that source-adjacent folder and perform
    human visual QA. If smoke or render fails, a Python preview or standalone PNG/PDF/SVG is only
    a preview and must not be presented as completed Origin work. Formal success requires the
    editable OPJU, PNG, PDF, TIF, object readback, and human visual QA together.

Before any render, read `references/origin-safety.md`, `references/figure-contract.md`, and
`references/verification.md`. For a new table or chart decision, read
`references/data-contracts.md`, `references/chart-selection.md`, and
`references/semantic-understanding.md`. When a reference image is supplied, also read
`references/reference-figures.md`.

## Keep scientific decisions with the user

- Treat the original data file as immutable. Never overwrite it, fill missing source columns, or
  invent measurements. Permit helper columns only in memory or the editable Origin project.
- Classify every source column before planning as primary render, secondary render, support-only,
  retain-not-render, or uncertain. Support-only and retained columns cannot become visible through
  a reference image. An unknown numeric column is a question, not another automatic curve.
- Distinguish scientific analysis from display transformation. Never silently normalize, smooth,
  fit, remove outliers, calculate error bars, identify phases, or infer material peaks.
- For GSAS/GSAS-II Rietveld data, distinguish Observed, Calculated, optional Background, supplied
  Difference, explicit Phase positions, and non-rendering control/diagnostic columns. Preserve an
  upstream Publication `Diff` exactly; never apply a second display offset.
- For XPS, keep cosmetic preferences separate from the scientific contract. A user may explicitly
  request exact series colors, physical line widths, fill transparency, a safe page/aspect ratio,
  and legend show/hide, borderless, or position choices. Apply only fields supported and read back
  by the selected verified XPS renderer; otherwise retain the default or reject the field visibly.
  Neither a user style request nor a reference image may change source values or column roles, the
  high-to-low binding-energy axis contract, component identity, residual disposition, or the
  verified single-region `set_fill_area(..., type=9)` / `-pfm 3` fill implementation.
- For SHAP, accept only externally precomputed per-sample contributions. Never train a model or
  invoke SHAP. Mean |SHAP| and optional group percentages may only summarize those supplied rows
  with the allow-listed formulas recorded in the semantic proposal and explicitly approved; never
  invent contributions or silently reorder features.
- Confirm unknown units, error semantics, percentage denominators, meaningful order, dual axes,
  and any other choice that can change the claim.
- Recommend from the scientific question and data structure, not aesthetics alone. Refuse a
  misleading chart even when technically renderable.
- Keep template route status (`verified`, `experimental`, or `unsupported`) separate from current
  host compatibility (`verified`, `compatible_unverified`, or `blocked`). Never relabel a
  `compatible_unverified` Origin version as verified; continue only when its smoke succeeds and the
  selected template's required capabilities are available.
- Reject decorative 3D. Require a scientifically meaningful third axis; keep a new 3D route
  experimental until Z-axis, camera, OpenGL type, source mapping, four exports, editable OPJU,
  readback, and visual QA pass.
- 对于已验证的 `density_ridgeline3d`，我只接受 2–6 个真实带单位条件的 mixed-wide
  六角色表：上游提供同语义同单位的实线/虚线预计算密度，并为每组提供恰好一个 `Focal X`。
  焦点固定为 Z=0 基线 locator；不要计算 KDE、峰值、阈值、交点或焦点。当前主机还必须先通过
  实时 smoke 与 `OPEN_GL_3D` 能力检查，不能只凭模板已验证就跳过主机门禁。
- Do not send selected files to any additional network service or include them in public artifacts.
  A file explicitly provided through the host remains subject to the user's host account,
  organization, and retention policies; do not claim the Skill can override those policies.
- Before inspecting medical data or reference images, require the user to confirm that the material
  follows their institution's rules, is deidentified, and has been checked for burned-in text.
- Treat `panel-plan` as a deidentification-aware layout and evidence gate, not an OCR, PHI detector,
  medical image editor, or merged editable Origin project. Preserve every verified subproject.

## Apply the publication-informed contract

- Make every chart defend one explicit conclusion or evidence role.
- Use a white background, Arial, restrained color families, clear hierarchy, and no rainbow palette,
  decorative 3D, or unjustified grid.
- Derive physical Origin dimensions from chart type, data density, series count, and label length.
  Keep fixed size only for a profile that explicitly requires it, such as legacy fixed C 1s.
- Convert documented point, line-width, and page-size units correctly. Never copy small journal-page
  font values directly into Origin API fields; read back the resulting axis and text objects.
- Keep each condition's color consistent across related panels. Freeze palette IDs and exact HEX
  values, allowed modes, safe category count, and accessibility constraints into the plan.
- Let an explicit user style request outrank a style token inferred from a reference image. Color,
  line-width, transparency, page/aspect, and legend requests are still capability-gated and must be
  classified as applied, retained default, or rejected before rendering.
- Do not let a reference image or unverified cosmetic preference silently redefine semantic color
  mappings for XPS components, signed effects, heatmaps, diagnostic lines, confusion matrices, or
  similar evidence. An explicit replacement is allowed only through that route's independently
  verified override with exact series mapping and readback.
- Give every medical panel one distinct evidence role. Freeze a shared condition-to-color map before
  composing quantitative panels; require explicit semantic confirmation for a shared legend.
- Prefer editable labels and Origin objects. A Python preview or embedded bitmap is not an Origin
  deliverable.
- Call the result “publication-informed,” never “Nature compliant” or journal-approved.

## Report the result in plain language

Return the recognized data shape and roles, selected chart and alternatives, confidence and confirmed
transformations, source-adjacent output folder, copied plan, OPJU/PNG/PDF/TIF paths,
validation/readback paths, and any remaining human check. For a beginner, translate internal
identifiers into natural language, summarize environment state in one to three sentences, and put
technical paths after the concise outcome.

## Load detailed references only as needed

- `references/runtime.md`: launcher, setup, Python discovery, CLI commands, and artifacts.
- `references/chart-selection.md`: chart families, ranking rules, and support levels.
- `references/not-covered.md`（豆包工作版新增）：本 skill **没有**绘图路线的 17 种图表。
  用户点名要其中任何一种时，先看这份，直接说清楚，不要硬试。
- `selector/selector.py`（豆包工作版新增）：图表选择器。用户说不清要画什么图时用它。
  它把页面挂在 `http://127.0.0.1:<端口>/` 上，默认不弹系统浏览器——地址交给宿主的内置浏览器打开。
- `references/data-contracts.md`: accepted layouts, column semantics, and repair guidance.
- `references/semantic-understanding.md`: per-column use, element checklist, derived-data lineage,
  and the hash-bound confirmation gate.
- `references/reference-figures.md`: safe reference grammar, bindings, adaptation limits, and
  separate confirmation.
- `references/figure-contract.md`: evidence logic, visual hierarchy, typography, and color rules.
- `references/origin-safety.md`: local Automation and verified-API guardrails.
- `references/verification.md`: mandatory artifacts, readback, and visual QA.
- `references/showcase.md`: neutral demonstration data and gallery policy.
- `references/palettes.md`: Chinese palette selector, compatibility, and accessibility limits.
