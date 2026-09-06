# 给 Agent 的项目规则

## 这个仓库是什么

**DoubaoPlot**（`chuspeeism/doubaoplot`）——[hang-jin/editaplot](https://github.com/hang-jin/editaplot)
的二次创作，基于上游提交 `4aa986f`，Apache-2.0。

绘图能力全部来自上游：40 条 Origin 绘图路线、验证门禁、45 张实机示例图、10 组科研配色。
我们加的是安装目录适配、豆包语境文档、图表选择器。

## 第一条规则：优化改在这里，不要去改上游

发现的问题即使源自 editaplot 的代码，**也在本仓库内修复**。

- 不要 clone、修改或向 [hang-jin/editaplot](https://github.com/hang-jin/editaplot) 提交任何内容
- 不要建议「去上游提 PR」作为解决方案
- `git remote` 里的 `upstream` 只用于拉取历史，**只读**
- 本仓库的工作分支是 `main`，远端是 `origin`（`chuspeeism/doubaoplot`）

## 哪些是上游的代码

下面这些是 hang-jin 写的。**可以改**，但改之前先想清楚是不是必须改，改完必须按
Apache-2.0 第 4(b) 条在三份 `NOTICE` 里追加声明（`NOTICE`、`runtime/NOTICE`、
`skill/doubaoplot/NOTICE`，三份内容必须完全一致）。

| 路径 | 内容 |
|---|---|
| `runtime/src/origin_sciplot/` | 绘图引擎、Origin Automation、渲染器 |
| `runtime/templates/` | 42 个模板目录（40 条公开路线 + 2 个内部实现） |
| `assets/gallery/`、`assets/palettes/` | 47 张实机验证 PNG、10 组配色 |
| `tools/`、`tests/` | 构建工具与测试 |
| `docs/` | 上游文档 |

## 哪些是本项目新增或改写的

这些随便改，不需要 NOTICE 声明：

| 路径 | 内容 |
|---|---|
| `skill/doubaoplot/selector/` | 图表选择器：`chart-selector.html`（单文件，1.17 MB，45 张缩略图内嵌）+ `selector.py`（启动器与本地回传服务） |
| `skill/doubaoplot/references/not-covered.md` | 17 种没有绘图路线的图表清单 |
| `skill/doubaoplot/SKILL.md` 的「先决定走哪条路」章节 | 两种用法的入口路由 |
| `skill/doubaoplot/scripts/bootstrap_editaplot.py` 的 `resolve_skill_target()` 与 `SKILL_DIRECTORY_NAME` | 安装目录三级解析 |
| `README.md` 顶部声明与「开始使用」整章、`README.en.md` 顶部、`豆包工作使用说明.md` | 面向用户的文档 |
| `release/public-release-policy.json` 的 `max_file_bytes`、`max_total_bytes`、`secret_scan_exempt` | 发布策略的三处调整 |
| `tools/verify_public_release.py` 的 `secret_scan_exempt` 支持 | 按文件豁免密钥扫描 |

## 不要动的东西

1. **上游的安全与隐私声明原文**。`README.md` 里「不会主动把你的数据上传到网络」「不承诺自动发现
   PHI」这类句子有测试盯着（`tests/test_origin_safety_documentation.py`），改一个字就红。
   要改必须同步改测试，并想清楚为什么要改一条安全声明。
2. **技术标识符与错误码**。`origin_codex_sandbox_context` 这类 code 不要因为「读着像 Codex」就改，
   改了要连带改一堆调用点和测试。沙箱检测靠 Windows 账户名前缀判断，豆包下自然不触发。
3. **绘图行为、数据契约、验证门禁**。这三样是这个项目可信度的来源。

## 改完必须跑的三件事

在仓库根目录：

```bash
# 1. 改了 runtime/ 下任何文件，重建清单，否则门禁和测试都会红
python tools/build_runtime_manifest.py --runtime runtime

# 2. 测试。macOS 上的基线是 22 failed / 898 passed / 7 skipped
#    那 22 个失败全在 tests/test_editaplot.py，是 Windows 路径与 Origin 注册表相关，
#    在 macOS 上本来就失败。**只要不超过 22 个就是没弄坏东西。**
python -m pytest -p no:cacheprovider -q

# 3. 发布门禁必须 PASS。它要求改动先进 git 暂存区
git add -A && python tools/verify_public_release.py
```

依赖：`numpy pandas PyYAML jsonschema matplotlib openpyxl xlrd pillow pytest`。
`originpro` 与 `OriginExt` 是 Windows COM 封装，macOS 上装不了也不需要装。

## 平台限制

- **Origin 只在 Windows 上跑。** macOS 上能验证的是数据契约、绘图计划、意图路由、选择器前端，
  验证不了真机绘图、导出与对象反读。
- 涉及 Origin 渲染的改动，必须在装了 Origin 的 Windows 机器上实测才算完成。没实测就明说没实测，
  不要写成「已验证」。

## 选择器的两处特殊约定

1. `chart-selector.html` 是自解压包（Claude Design 导出），正文里有约 1 MB base64。
   **不要手改这个文件。** 它由一组构建脚本生成：解析上游 gallery 清单与模板契约得到卡片数据，
   再做字体子集化、缩略图压缩、缩略图位置烤入。这些构建脚本和原始素材体积较大，保留在本仓库之外
   的制作目录，未随公开仓库分发。需要改选择器内容时找维护者取构建目录，不要在这个文件上手改。
2. 页面与 `selector.py` 共用候选端口 `17864 / 17865 / 17866`，改一处必须同步改另一处。
   回传是「剪贴板兜底 + 本地端口优先」双通道，不要砍掉任何一条。

## 报告要求

改完说清楚：改了哪个文件、为什么改、动没动上游代码、三件验证各自的结果。
没验证的部分明说没验证，不要用「应该可以」代替实测。
