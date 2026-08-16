<p align="center">
  <img src="icon.png" alt="Codex Enhanced Manager 图标" width="96">
</p>

<h1 align="center">Codex Enhanced Manager</h1>

<p align="center">
  <strong>让 Codex 尽量保持原生，同时补上它本该有的控制台。</strong>
</p>

<p align="center">
  官方登录切换 · 本地代理路由 · 智能路由 · Token 监控 · 配置修复
</p>

<p align="center">
  <a href="README.md">English</a>
  ·
  <a href="https://github.com/JiangNanGenius/Codex-Enhance-Manager/releases">下载发布版</a>
  ·
  <a href="RELEASE_NOTES.md">更新日志</a>
  ·
  <a href="LICENSE">许可证</a>
</p>

<p align="center">
  <img alt="Platform: Windows and Apple Silicon macOS" src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20arm64-2563eb.svg">
  <img alt="Local first" src="https://img.shields.io/badge/Local--first-by_default-0f766e.svg">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-334155.svg">
  <img alt="License: Apache-2.0" src="https://img.shields.io/badge/License-Apache--2.0-green.svg">
</p>

---

## 为什么要做它

Codex 最舒服的状态应该是：官方登录态还在，启动像原生一样顺，历史记录能看，用量能看，供应商和模型可以换，但不会把配置文件搞成一团。

Codex Enhanced Manager 做的就是这件事：尽量不破坏 Codex 原生体验，把供应商、路由、智能路由、用量统计、备份恢复、配置修复和悬浮窗放进一个本地 Windows / Apple Silicon macOS 桌面工具里。

所有配置、供应商、请求元数据、诊断包、备份和导出默认都留在本机。

## 一眼看懂

<table>
  <tr>
    <td width="50%">
      <strong>官方登录态不乱动</strong><br>
      能识别 ChatGPT/OAuth 登录，显示真实的 OpenAI 官方状态和当前模型；官方直连只做切换，不进本地代理和智能路由。
    </td>
    <td width="50%">
      <strong>要路由时才路由</strong><br>
      需要代理/API 模式时才启动本地代理；端口被占用会自动退避，并把真实端口和强 bearer token 写进 Codex 配置。
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>供应商和轮换分清楚</strong><br>
      供应商页管密钥、地址、Header、模型能力和媒体能力；智能路由页只管新会话顺序、优先级、故障转移和能力匹配。
    </td>
    <td width="50%">
      <strong>真出问题也能修</strong><br>
      一键把 Codex 配置修回模板态；首次切回官方登录有风险提示和重置流程；备份可以清理，诊断会脱敏。
    </td>
  </tr>
</table>

## 三种连接模式

| 模式 | 适合谁 | 行为 |
| --- | --- | --- |
| 官方登录直连 | 想让 Codex 完全走官方账号的用户。 | 保留 OAuth 登录态，锁定会改变路由的供应商能力；安全的页面增强注入仍可开启。 |
| 保留登录并接入代理/API | 想保留官方登录，同时使用本地代理或 API 路由的用户。 | 启动本地代理，写入真实退避端口和强 token，再带进度同步历史记录。 |
| 第三方供应商 | 使用自定义供应商、代理商或兼容 API 的用户。 | 启用供应商密钥、Responses/Chat 协议选择、模型映射、媒体 fallback、额度脚本和智能路由。 |

## Codex 实际怎么请求模型

这里按 OpenAI Codex 当前源码设计来做，不猜传输层。Codex 会构造 Responses API 请求，并用 SSE 流式发送到 `POST /responses`。OpenAI 的 Codex agent-loop 文章也明确了同一套端点：ChatGPT 登录、API key、本地 provider 和云端 Responses provider 都围绕 `/responses`。

因此本工具的边界是：

- 写入 Codex 配置时只使用 `wire_api = "responses"`，并把 base URL 指向本地代理的 `/v1`。
- 原生 Responses 供应商会直通到上游 `/responses`，保留 Codex 的请求形态。
- 只有 Chat-only 供应商才由本地代理做 Responses 到 Chat Completions 的适配。
- **图像路由独立，但不是全局拦截**：
  - 直接 `POST /v1/images/generations` 请求只有在 `model` 是 `auto`、`smart-routing`、`amr/<group>`、`rotation/<group>` 这类 AMR 组时，才使用 AMR `image_candidates`。
  - 直接图像请求如果写成 `provider/model`，就是硬路由到该 provider 的图像端点，不经过 AMR。这是私有纯原生代理应走的路径。
  - 原生 Responses 请求里如果包含 OpenAI 内置 `image_generation` tool，会按原生 Responses 直通上游；代理层不会把这个 tool 重新解释成 AMR 图像路由。
  - 国内兼容 provider 在原生 Responses 不能安全承载时，可以退到 chat/tool fallback；这个 fallback 里出现的 `generate_image` 调用，只有原始 `model` 是 AMR 组时才会使用 AMR `image_candidates`。

参考：[openai/codex `responses.rs`](https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/endpoint/responses.rs) 和 [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)。

## 你会得到什么

- 设置向导：Codex 路径、官方登录态、供应商、模型能力、路由、媒体 fallback、开机启动和保存检查。
- 供应商管理：支持供应商内单模型路由、独立上下文、自动压缩阈值、服务档位、Web Search / Responses Lite 元数据、图片策略和媒体路由。
- 智能路由：管理下一个新会话的顺序、优先级、故障转移和能力筛选，不和密钥配置混在一起。
- 用量统计：读取 Codex Token、官方登录态额度、缓存、代理请求元数据、本地费用估算，以及可用时的供应商官方扣费信息。
- 悬浮窗：显示 Token、缓存、上下文、一小时用量、消耗速度、余额扣费速率、套餐额度百分比、透明度、托盘操作和快速切换。
- 本地导入：用户脚本、校验后的 CSS/图片主题与桌宠包；脚本默认停用，启用后会在 Codex 渲染进程执行。
- 会话与工作流：多数据库发现、分页批选、删除前备份和撤销恢复，以及只由用户显式触发的 worktree / Zed Remote 项目记录。
- 恢复工具：备份/恢复、配置模板修复、移动会话修复、脱敏诊断、更新检查、Windows EXE 和 Apple Silicon DMG 发布支持。

## 安全边界

- Windows 默认数据目录是 `Documents/Codex Enhanced Manager/`；macOS 是 `~/Library/Application Support/Codex Enhanced Manager/`。
- API Key、Bearer Token 和敏感 Header 会在设置导出、诊断和日志里脱敏。
- 本地代理默认生成高熵 bearer token；设置页只显示指纹。
- 官方直连是“只切换”的状态，不进入本地代理路由，也不参与智能路由。
- 删除/重置 Codex 配置和登录文件必须明确确认，并提示聊天记录有概率丢失。
- 主题/桌宠包拒绝可执行 JavaScript、路径穿越、未知类型与超限文件；JavaScript 只能以本地用户脚本单独导入。

## 供应商额度资料

已确认的余额和 Coding Plan 额度读取方法记录在 [docs/provider-quota-and-billing.md](docs/provider-quota-and-billing.md)，包括内置的 KimiCode、智谱、MiniMax、SiliconFlow、StepFun、OpenRouter、Novita、DeepSeek，以及官方 Codex OAuth 额度读取方式。

## 安装

### Windows EXE

从 [Releases](https://github.com/JiangNanGenius/Codex-Enhance-Manager/releases) 下载最新版，然后运行：

```text
CodexEnhancedManager.exe
```

### macOS arm64 DMG

下载 `CodexEnhancedManager-v2.3.0-macos-arm64.dmg`，打开后把应用拖入 Applications。仅支持 Apple Silicon，最低 macOS 12.0。

该版本仅做 ad-hoc 签名，**没有 Apple 公证**。首次启动请按住 Control 点按应用并选择“打开”；若仍被 Gatekeeper 阻止，请到“系统设置 → 隐私与安全性”中对本应用选择“仍要打开”。操作前请先核对 Release 中的 SHA-256。

### 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

桌面应用背后是本地后端，通常是：

```text
http://127.0.0.1:51234
```

如果端口被占用，桌面启动器会自动切到后续可用端口。

## 发布打包

GitHub Actions 负责构建平台资产。v2.3.0 按发布约定不执行测试、lint、语法检查、冒烟、手工启动或本地打包；CI 只构建并记录大小与 SHA-256。

预期发布资产：

```text
dist/CodexEnhancedManager.exe
dist/release-manifest.json
dist/CodexEnhancedManager-v2.3.0-macos-arm64.dmg
dist/macos-release-manifest.json
```

若任一打包任务失败，Release 可能暂时只有源码。静态逻辑审查不等于运行正确性验证。

## 本地文件

| 路径 | 用途 |
| --- | --- |
| `config.json` | 应用主设置。 |
| `providers/providers.json` | 本地供应商注册表。 |
| `logs/proxy_requests.jsonl` | 只记录元数据的代理请求日志。 |
| `backups/` | 应用和 Codex 配置备份。 |
| `diagnostics/` | 脱敏诊断包。 |
| `exports/` | 用户主动导出的文件。 |
| `temp/` | 临时文件。 |
| `extensions/` | 本地脚本、主题、桌宠、哈希与启用状态。 |
| `workflows/` | 显式记录的本地/worktree/Zed Remote 项目。 |

## 独立实现说明

外部项目只用于研究用户可见行为和协议兼容性；本项目未并入 AGPL 源码或参考项目素材。详见 [THIRD_PARTY_REFERENCES.md](THIRD_PARTY_REFERENCES.md)。

## 许可证

Apache License 2.0，详见 [LICENSE](LICENSE)。
