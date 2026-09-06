<div align="center">
  <h1>DoubaoPlot</h1>
  <p><strong>在豆包工作里，把科研数据画成能继续编辑的 Origin 图</strong></p>
  <p>基于 <a href="https://github.com/hang-jin/editaplot">hang-jin/editaplot</a> 的二次创作 · Apache-2.0</p>
  <p>
    <img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-4c6ef5">
    <img alt="Platform: Windows 10/11 x64 only" src="https://img.shields.io/badge/platform-Windows%2010%2F11%20x64%20only-0078d4">
    <img alt="Python 3.10–3.12" src="https://img.shields.io/badge/Python-3.10%E2%80%933.12-3776ab">
    <img alt="Doubao Work Skill" src="https://img.shields.io/badge/Doubao%20Work-Skill-7c3aed">
    <img alt="Origin 2021–2026b compatibility target" src="https://img.shields.io/badge/Origin-2021%E2%80%932026b%20target-2563eb">
    <img alt="Fully verified with Origin 2024b" src="https://img.shields.io/badge/fully%20verified-2024b-0f766e">
    <a href="https://github.com/hang-jin/editaplot"><img alt="上游 EditaPlot 的 GitHub Stars" src="https://img.shields.io/github/stars/hang-jin/editaplot?style=social"></a>
  </p>
  <p><a href="README.en.md">English</a> · 中文为主要说明语言</p>
</div>

## 这是什么

你把实验数据（CSV、TXT、XLS、XLSX）交给豆包工作，它读懂每一列、推荐画哪种图、请你确认，然后调用你电脑上装好的 Origin 把图画出来。

**交付的不是一张图片，是一个能继续编辑的 Origin 工程文件（`.opju`）**，外加 PNG、PDF、TIF。双击打开，颜色、坐标轴、图例、文字全都能接着改。

它不是「把模板里的数字换掉」，也不会拿 Python 预览图冒充 Origin 成图。哪一列看不准，它会停下来问你，不会自己补列、拟合或者替你下结论。

三件事先说清楚：

- **只能在 Windows 10/11 x64 实体电脑上用。** Origin 本身就是 Windows 软件，Mac、Linux、WSL、虚拟机都跑不了整条链路。
- **Origin 得你自己装好。** 它只调用你电脑上已经有的 Origin 或 OriginPro，不会替你安装或修改。
- **它不替你算数据。** 不平滑、不拟合、不删离群值、不做检验。这些你算好了给它，它才画。

> 只想知道怎么用，不看这么长 → [豆包工作使用说明.md](豆包工作使用说明.md)

## 它画出来的图长什么样

<div align="center">
  <img src="assets/gallery/xps-fit.png" alt="XPS 峰拟合" width="31%">
  <img src="assets/gallery/medical-grouped-box.png" alt="医学分组箱线图" width="31%">
  <img src="assets/gallery/uv-vis-tauc.png" alt="UV–Vis 与 Tauc 插图" width="31%">
  <img src="assets/gallery/percent-composition.png" alt="百分比堆叠组成图" width="31%">
  <img src="assets/gallery/medical-shap.png" alt="复合 SHAP 特征贡献图" width="31%">
  <img src="assets/gallery/circular-network.png" alt="多阶段环形有向加权网络" width="31%">
</div>

这些都是在装了 Origin 2024b 的真机上跑出来、人工看过一遍的，用的是合成教学数据，不代表任何真实测量。

➡️ [45 张示例图和各自的用途](docs/gallery.md)

## 它能画什么

一共 40 条绘图路线：

| 方向 | 图形 |
|---|---|
| 材料与光谱 | XPS 扫描/拟合、XPS 多谱线对比、XRD、GSAS/GSAS-II XRD Rietveld、XAS、FTIR/IR、NMR、DSC、PL/TRPL、UV–Vis/Tauc、EIS、CV、LSV、三维多条件 Nyquist |
| 通用统计 | 柱状/条形、误差棒、堆叠/百分比堆叠、饼图、桑基、多阶段环形有向加权网络、折线、趋势、散点、气泡、雷达、热力图（高密度矩阵会自动调整版式） |
| 分布与效应 | 原始点汇总、箱线、小提琴、Raincloud、直方图、森林效应图、三维双密度曲线 |
| 医学与机器学习 | ROC、PR、校准曲线、DCA、混淆矩阵、Bland–Altman、配对纵向轨迹、分组箱线、复合预计算 SHAP |

### 这 17 种画不了

Origin 本身画得出来，但这个 Skill 没有对应的绘图路线。你点名要下面任何一种，它会直接告诉你没有，不会硬试着画一遍再失败：

| 分类 | 画不了的图 |
|---|---|
| 基础统计 | 面积图、ECDF 图（经验累积分布）、Q-Q 图 |
| 专业谱图 | 三元相图（Ternary）、**生存曲线（Kaplan-Meier）** |
| 多维关系 | 断轴图、极坐标 / 风向玫瑰图、成对关系图、平行坐标图、矩阵散点图 |
| 三维 | 等高线图、3D 曲面图、3D 条形图、3D 体绘图、3D 切片图、3D 矢量场图、3D 等值面图 |

最容易被问到的是**生存曲线**：医学那组做了 ROC、PR、DCA、校准曲线、混淆矩阵、Bland–Altman，唯独没有 KM。

**PCA / t-SNE / UMAP 不在这张表里**，能画。但降维坐标要你自己先算好，它只负责把算好的坐标画成分组散点，不替你降维。

### 配色

![中文科研配色](assets/palettes/palette-selector-public.zh-CN.png)

10 组科研配色，首屏 8 组、进阶 2 组。选图的时候它会按你选中的图型自动推荐，色盲风险高的排在后面。XPS 组分、正负值、热力图、诊断参考线这些颜色有科学含义，它不会为了好看乱改。

配色是重新设计和抽象出来的，不复制期刊封面、水印或版式，也不是任何期刊的官方模板。

## 装

**在豆包工作里说这一句：**

```text
帮我安装 GitHub 上 chuspeeism 的 doubaoplot Skill
```

用 Codex、Claude Code 的话，把同一句话说给它。

装完之后重开一个任务就能用了。**Origin 记得自己先装好。**

**它会先把要做的事讲给你听。** 第一次画图前，它先报一遍这条链路的四件事——装 Skill、取绘图引擎、装 10 个依赖库、有没有一个能用的 Python——并点名说清楚哪几件你这台机器上已经现成、直接跳过。缺的那几件它自己补，只有"要不要装 Python"这一件会停下来问你。你不用猜它在等什么。

<details>
<summary><b>如果它说找不到绘图引擎（engine_not_found）</b></summary>

绘图引擎不在 Skill 里，在完整仓库的 `runtime/` 目录下。有些宿主只会把 Skill 那个子目录装进来，拿不到引擎。

**它会自己去取，不用你动手。** Skill 里已经写明：缺引擎时 Agent 直接联网把完整仓库拿下来跑 `setup`，不为这一步问你，也不许把下载推回给你。只有一种情况它会先问你一句——你电脑上没有 64 位 Python 3.10–3.12、需要装一个 Python，那是系统级变更。

要自己动手也可以，下载完整仓库，在里面跑一次 `setup`：

```powershell
git clone https://github.com/chuspeeism/doubaoplot.git
Set-Location doubaoplot
.\editaplot.cmd setup
```

不会用 git 就在 GitHub 页面上下载 Source ZIP，**完整解压**之后在那个目录里跑同一条 `setup`。

`setup` 做三件事：找一个电脑上已有的 64 位 Python 3.10–3.12，建一个只属于本项目的 Python 环境，把 Skill 装到它探测到的宿主目录并**打印实际装到了哪**。电脑上没有合适的 Python 时，它会先用中文告诉你这是一项系统变更、等你同意，才去装 Python 3.12。它不会安装或修改 Origin。

</details>

<details>
<summary><b>如果装完之后 Agent 里看不到这个 Skill</b></summary>

多半是装到别的目录去了。它按这个顺序找地方装：

1. 你设了 `EDITAPLOT_SKILL_DIR` 环境变量，就装那儿
2. 本机已经存在的宿主目录。豆包工作在 Windows 上是 `%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills`，另外还会试 `~/.doubao/skills`、`~/.doubao-work/skills`、`~/.codex/skills`
3. 都没找到，回落到 `~/.codex/skills/doubaoplot`

`setup` 会把最终选中的路径打出来。如果你的 Agent 读的不是那个目录，指定一下再装一次：

```powershell
$env:EDITAPLOT_SKILL_DIR = "<你的 Agent 的 skills 目录>\doubaoplot"
.\editaplot.cmd setup
```

</details>

<details>
<summary><b>如果装依赖库特别慢，或者报 dependency_install_timeout</b></summary>

那 10 个依赖库要下大约 45 MB，是整个安装里最花时间的一步（取仓库才 7.7 MB）。默认从官方 PyPI 下载，国内直连常见几十到几百 KB/s，容易拖到超时（这一步的上限是 900 秒）。

**它会自己换成国内镜像重试**，用清华 TUNA，连不上再换阿里云，换完会告诉你换了哪个。你也可以先手动设好再让它装：

```powershell
$env:PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

换源换的只是"从哪儿下载"，装的仍然是锁文件里钉死的那些版本，一个都不会变。

</details>

<details>
<summary><b>如果安装报错，提到 editaplot，或者说「写不进去」</b></summary>

先更新到最新版再装。2026-09-06 之前的版本有一个必现的坑：安装脚本在把 Skill 落盘前会做一次身份校验，而那段校验只认上游的名字 `editaplot`，本项目的 SKILL.md 写的是 `doubaoplot` —— 于是**每一次安装都会失败**。失败信息有两种样子，哪一种都不是你的目录权限有问题：

- 第一次装：身份校验没过，旧版本会把它伪装成「写不进去，请给写权限」
- 再装一次：`skill_destination_not_editaplot` ——「这个非空目录不是我认识的 Skill，拒绝覆盖」

看到这两种，不要去改文件夹权限，也不要用管理员权限重跑。拉最新代码再跑一次 `setup` 即可。

**另外，别用手工复制代替 `setup`。** 把 `skill/doubaoplot` 直接拷进 skills 目录，Skill 是进去了，但绘图引擎和项目专属的 Python 环境都没跟过来，要等第一次画图才发现。

</details>

## 两种用法

### 用法一：你有参考图，照着复刻

看到一张顺眼的图，想用自己的数据画成那个样子。把**参考图**和**你的数据文件**一起发过去，然后说：

```text
帮我在 Origin 中，用我的数据复刻这张参考图的绘图风格
```

它会先分析参考图的版式、配色和绘图细节，再用你的数据画。

**参考图只影响样式，不制造数据。** 你数据里没有的东西，它不会编出来凑成参考图的样子。

### 用法二：你不知道该画什么图，点着选

这是更常见的情况：数据有了，但不知道该画箱线图还是小提琴图，更不知道该怎么跟 AI 描述才能一次到位。

直接调用这个 Skill，说：

```text
我不知道该画什么图，帮我看看
```

它会在**豆包工作自己的内置浏览器里**打开**图表选择器**：45 张真机跑出来的示例图铺开，按方向分好类（材料表征、电化学、医学与机器学习、通用统计、分布形态……）。

选择器是一个只监听本机的小页面（`http://127.0.0.1:17864/`），不会另外弹一个 Chrome 窗口来打断你。只有当你的 Agent 完全没有内置浏览器时，它才会去调系统默认浏览器。

点中一张，右侧立刻显示：

- **这张图需要你的数据里有哪几列** ← 最有用的一条
- 这条路线的边界，哪些东西它不会替你算
- 推荐配色、出图尺寸、误差标注、显著性星号这些细节

选完点「发送给豆包」就回去了；点「复制」也行，粘回对话框一样。页面**永远先把内容放进你的剪贴板**再去试自动发送，所以自动发送没成也不会卡住，你只是多粘贴一下。

选择器说的「需要哪几列」是提示不是结论。你的数据到底有没有这些列，它画之前还会再逐列核对一遍，缺了照样告诉你缺什么。

### 第一次用，可以直接发这段

把文件拖进去，然后发：

```text
请帮我画这份数据。不要修改原文件；先告诉我识别到哪些列、最推荐哪种图，
再逐列说明哪些要画、哪些只作辅助或验证、哪些保留但不画，并列出最终图形元素和不会自动进行的
计算。若有不确定列，请先问我，不要猜。若需要安装 Python，请先征得我同意；不要安装或修改 Origin。
等我确认科学目的和元素清单后再绘图，完成后请检查可编辑项目和 PNG、PDF、TIF。
我不需要提前打开 Origin。Doctor 只做只读发现；请在绘图前运行真实 smoke，
自动启动专用 Origin 实例并按当前版本和模板能力继续。
不要让我复制 PowerShell、使用管理员权限或修改 DCOM/注册表。
```

如果还给了参考图，接着说：

```text
请把参考图只当作视觉简报：总结它的图形元素、布局、数据编码和可安全采用的风格，
不要复制图中的数据、文字、拟合结果、物相、Logo 或水印，也不要把参考图嵌入成图。
请另外询问并记录我明确选择的系列颜色、线宽、填充透明度、画幅比例和图例显示/无框/位置；
我的明确选择优先于参考图。请分别列出「采用、保留模板默认、拒绝、仍需确认」的内容，
只有当前模板已经验证并能反读的样式才算采用，等我确认后再适配到我的数据。
```

## 你最后拿到什么

**不是一张图片，是一个文件夹**，建在你数据文件旁边，叫 `<数据文件名>_EditaPlot_<时间戳>`。

| 文件 | 是什么 |
|---|---|
| **`result.opju`** | **Origin 工程文件，核心是它。** 双击打开，颜色、坐标轴、图例、文字全都能接着改 |
| `result.png` | 插 Word、发群里 |
| `result.pdf` | 矢量，投稿常要 |
| `result.tif` | 期刊最常点名要的格式 |
| `origin_verify_report.json` | 画完之后回头去 Origin 里把坐标轴、字体、图层重新读一遍的核对报告 |

最后那份核对报告是它跟「导出个 PNG 就算完事」的区别：画完还要回到 Origin 里把对象重新读一遍，对不上就算失败。

画完 Origin 窗口默认不关，图就摆在那儿，可以直接上手改。它不会覆盖你的原始数据，只有你明确指定别的位置时才会改输出目录。

**想在 Origin 里改，得你自己双击 `result.opju`。** Agent 给你看的是 `result.png` —— 它的截图通道看不到自己启动的那个 Origin 窗口，这一步只能真人来。

## 多久算正常，卡住了怎么办

环境配好、数据量正常、该确认的都确认了，从识别到导出验证在 4–5 分钟内是合理范围，其中连接 Origin 和正式绘图各十几秒。第一次装依赖、大 Excel、复杂图层、慢硬盘或者 Windows 安全扫描都会多花点时间。

**没在等你确认、也没有新进度，卡了 30 分钟以上就不正常了。** 先让它报告停在哪个阶段，再对着下面这张表看：

| 现象 | 多半是 |
|---|---|
| 装完在 Agent 里看不到这个 Skill | 装到别的目录去了，见上面「装」那节的第二个折叠块 |
| 报 `engine_not_found` | 没拿到绘图引擎，见「装」那节的第一个折叠块 |
| 卡在 setup 或者下载依赖 | 网络、代理或者 Python 包源的问题，不是 Origin 的问题 |
| 卡在理解数据 | 多半在等你回复，或者在等你批权限 |
| 卡在启动 Origin | 先跑 `editaplot.cmd doctor`，它会告诉你卡在哪一阶段。再看 Origin 是不是弹了对话框、输出文件夹能不能写、有没有被网盘同步锁住 |
| 选择器弹不出来 | 让它把打印出来的 `http://127.0.0.1:…` 地址在内置浏览器里打开；`17864 / 17865 / 17866` 三个端口都被占时它会改给本地文件路径，自己双击打开，点「复制」再粘回来 |
| 点了「发送给豆包」没反应 | 内容已经在剪贴板里了，直接粘贴 |
| 画出来不是想要的样子 | 在 Origin 里直接改，这就是给你 OPJU 的意义 |

同一台电脑同一时间只跑一个 Origin 绘图任务，其余的排队等，看到排队提示别重复发起。正式绘图本身不用联网，网络只在第一次下载、更新和装依赖时用到。

## 命令行（可选）

熟悉命令行之后也可以直接跑：

```powershell
.\editaplot.cmd doctor
.\editaplot.cmd inspect <data.csv>
.\editaplot.cmd recommend <data.csv> --intent "比较模型并展示误差"
.\editaplot.cmd understand <data.csv> --template-id xrd --output data-understanding.json
.\editaplot.cmd palettes --template-id trend
.\editaplot.cmd plan <data.csv> --template-id bar --claim "模型 A 指标更高" --evidence-role comparison --palette-id ocean_coral --semantic-confirmation-json semantic-confirmation.json --output render-plan.json
$smokeDir = Join-Path $env:TEMP ("EditaPlot-origin-smoke-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
.\editaplot.cmd origin-smoke --output-dir $smokeDir
.\editaplot.cmd render render-plan.json
.\editaplot.cmd verify <Origin-output-directory>
```

`palettes --template-id` 只列这个图型能用的配色。`origin-smoke` 会先启动一个隔离的 Origin 实例跑完最小导出闭环，通过了才进正式 render。日常用可以忽略 `--engine-home`；普通绘图别给 `render` 传 `--output-dir`，正式结果会自动存到源数据旁边的新文件夹。

Skill 目录里没有 `editaplot.cmd` 的时候（宿主只装了 Skill 子目录就是这样），把上面所有 `.\editaplot.cmd` 换成 `python "<Skill 目录>\scripts\bootstrap_editaplot.py"`，后面参数完全一样。

## 它需要你给什么权限

按下面的最小范围批准就够了，不需要把整台电脑交出去：

| 允许的范围 | 用途 |
|---|---|
| 读取完整仓库、你的数据文件和可选的参考图 | 安装 Skill、理解列含义、制定绘图计划 |
| 写入本仓库和当前用户的 skill 目录 | 创建项目隔离环境并安装/更新 Skill |
| 写入原始数据所在的文件夹 | 在源文件旁边新建时间戳交付文件夹，不覆盖原文件 |
| 运行本地 `editaplot.cmd`、PowerShell、Python，并在当前 Windows 会话启动 Origin | 环境检查、连接测试、绘图、导出和反读 |
| 第一次安装或更新时访问 GitHub 与 Python 包源 | 下载公开源码和锁定依赖 |

普通使用**不需要**管理员权限、鼠标控制、整个 C 盘的写权限，也不需要改 DCOM、注册表、防火墙或者 Origin 安装。如果 Windows「受控文件夹访问」、单位策略、网盘同步或只读目录挡住了写入，只放行当前仓库和当前数据文件夹，或者明确指定另一个能写的输出目录。别拿全局提权当修复手段。

有些宿主的普通命令是由隔离账户跑的，这种进程不一定有权限用你当前登录的身份启动 Origin。所以它读的是当前进程真实的 Windows 安全令牌，而不是环境变量。检测到隔离环境时，它会在调用 Origin 之前停下来，只针对那一条精确的命令申请受限的本地执行权限，批了才重跑。你不需要把命令复制到自己的 PowerShell，也不需要管理员权限或者改注册表。

它自带的 Python 运行时和 Origin 自动化**不会主动把你的数据上传到网络**；但你主动交给 Agent 的文件，仍然受你所用账号和组织的数据策略约束。医学数据或参考图在交出去之前，必须按你所在机构的要求去标识化，并检查图像里有没有烧录身份信息 —— 它**不承诺自动发现 PHI**。

## 它不会替你做的事

这是一条明确的边界，建议你别绕：

- 只读你的原始文件。绘图用的辅助列只存在内存里或者可编辑的 Origin 工作簿里
- 每一列画之前都先说明用途。看不准的数值列不会自动变成一条新曲线
- 缺哪一列就直接告诉你缺什么，**不会编一列出来凑数**
- 不替你平滑数据、删离群值、补峰、算误差、拟合曲线、做显著性检验
- 不替你识别物相、算带隙、算寿命、训练模型。这些结果你明确提供了，它才画进图里
- 参考图只能影响你已确认的数据支撑得住的图形语法和安全样式，不能新增证据也不能藏掉必需元素。你明确指定的样式优先，并且逐项记录为采用、保留默认还是拒绝
- 只在第三根轴有真实实验含义的时候才用 3D，不做装饰性 3D
- 图例可以在 OPJU 里手动挪，但坐标轴缺失、字体不一致、色条重叠或者文字被裁掉，仍然判为失败

## 这个项目是怎么来的

**DoubaoPlot 是 [hang-jin](https://github.com/hang-jin) 的 [EditaPlot](https://github.com/hang-jin/editaplot) 的二次创作，基于上游提交 `4aa986f`，沿用 Apache-2.0。**

上面这一整页写的能力，几乎全部是 hang-jin 做的。让 AI 读懂科研数据、推荐图形、调用本机 Origin 画出能继续编辑的图 —— 这个想法和它的全部实现都出自 EditaPlot：40 条绘图路线、每一次画完都回 Origin 反读核对的验证机制、45 张真机示例图、10 组科研配色。这些我们一样没换。

我们加的是外面那一层，让它在豆包工作里能装、能用、能说清楚要什么图：

| 加了什么 | 为什么 |
|---|---|
| Skill 装得进豆包工作 | 上游写死装到 `~/.codex/skills`，豆包工作读不到那个目录，装完会表面成功、实际白装。现在会探测宿主目录并打印实际路径；宿主只装了 Skill 子目录、找不到启动器的时候也给出等效入口 |
| 图表选择器 | 用户常常不知道该画哪种图，也说不准需求。让他**看着选**比让他**描述**准得多。它只负责把需求问清楚，不改任何绘图行为，也不跳过任何确认环节 |
| 那 17 种画不了的图列成清单 | 之前会硬试一遍再失败，白等几分钟，还让人以为是自己数据的问题 |
| 报错直接给出可选项 | 列角色填错、配色和图型不兼容的时候，之前只说「不对」，得去翻源码猜。为此改了一处报错文案和一次配色查询，**渲染逻辑没动** |
| 面向用户的文档和提示词 | 上游文档是以 Codex 为宿主写的 |

**绘图行为、数据契约、验证门禁一处没动。** 逐条改动声明见 [NOTICE](NOTICE)。

名字 DoubaoPlot 只属于这个二次创作版本，不代表 hang-jin 的背书或参与。

**如果这套东西帮到了你，请去给 [hang-jin/editaplot](https://github.com/hang-jin/editaplot) 点一个 Star。** 真正让它画出顶刊质感科研图的是那个项目，我们只是把它搬进了豆包工作。

<div align="center">
  <a href="https://github.com/hang-jin/editaplot"><img src="https://raw.githubusercontent.com/hang-jin/editaplot/metrics/assets/star-trend/stars.svg" width="760" alt="EditaPlot GitHub Star 趋势"></a>
</div>

<p align="center"><sub>上游 EditaPlot 的 Star 趋势，由上游仓库自己生成。只统计仓库的 Star 总数，不涉及任何用户名单、用户名或加星时间。</sub></p>

**换别的 Agent 也能用。** 这是标准的 SKILL.md 技能，Codex、Claude Code 这些能读 SKILL.md 的 Agent 都能装能用，绘图能力完全一样。只是安装目录探测、文档语气、提示词和选择器的交互都是照着豆包工作的用户做的，用别的 Agent 这些优化用不上。上文写「豆包工作」的地方，换成你在用的 Agent 就行。

## 与 OriginLab 的关系

本项目只调用你电脑上已经装好的 Origin 或 OriginPro，默认启动一个由它独占的本机实例，不要求你事先打开窗口。它不捆绑、不安装、不修改这个软件，也不通过网络或云端开放它的 Automation Server。本项目与 OriginLab Corporation 没有隶属、赞助或背书关系；Origin 和 OriginPro 是 OriginLab 的商标，这里只用来说明兼容性。

## 许可

[Apache License 2.0](LICENSE)，与上游一致。相对上游的改动逐条声明在 [NOTICE](NOTICE)。

顶部徽章和 Star 趋势图只使用 GitHub 提供的仓库聚合数量，不请求、不保存、不展示 Star 用户名单、用户名、账号 ID 或者个人加星时间。
