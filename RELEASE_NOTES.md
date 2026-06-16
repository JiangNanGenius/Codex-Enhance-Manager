# Release Notes

## v2.2.28 - 2026-06-17

- Switched the packaged and desktop EXE filename to `CodexEnhancedManager.exe`; desktop copy cleanup now removes the old filename when possible.
- Improved Codex process detection with a Windows CIM path-based fallback for current `OpenAI.Codex` desktop processes.
- Automatically refreshes stale Codex launch paths in settings when a WindowsApps package version changes or a CLI/runtime shim was saved as the launch target.
- Removed third-party tool attribution from visible quota, provider, README, and frontend strings.
- Renamed the frontend local-cache setting ids and labels while keeping the existing config key compatible.
- Verified with targeted process/config/build/updater/frontend checks, Python compile checks, JavaScript syntax checks, local config refresh, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `71.34 MB`; SHA256: `990c54c759b41d6e897c4025591e94755aac82da6ae7502678c2f90ab7cf50da`.

## v2.2.27 - 2026-06-17

- Added a required user confirmation before the app closes an already-running Codex process during launch or injection setup.
- The backend now returns a confirmation-required payload instead of silently killing Codex when `/api/codex/start` is called without confirmation.
- The main Web UI, provider launch flows, sync launch flow, tray menu, floating monitor entry, and existing-instance launch action now share the same confirmation-and-retry behavior.
- Confirmed launches send an explicit one-shot confirmation token before Codex is closed and restarted.
- Verified with targeted Codex start API tests, desktop launch confirmation tests, Python compile checks, and JavaScript syntax checks. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `71.34 MB`; SHA256: `456d5c5ab10fe3b2e6305e67e115aad92f503715cffde4a2ff4c7f68a26352f6`.

## v2.2.26 - 2026-06-17

- Renamed the desktop app display name, window title, tray identity, shortcuts, startup defaults, and Codex provider label to `Codex Enhanced Manager`.
- Added automatic migration from the old documents data directory to `Documents/Codex Enhanced Manager` while preserving the old directory for compatibility and rollback.
- Migrates app-storage paths in `config.json` so providers, request logs, diagnostics, temp files, exports, and backups point to the new data directory.
- Migrates old startup task and shortcut names to `CodexEnhancedManager` / `CodexEnhancedManager.cmd`.
- Verified with targeted path/config/startup/shortcut/Codex config tests, Python compile checks, JavaScript syntax checks, local config migration, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `71.34 MB`; SHA256: `cb34d2a4915f06308e992f06f16d5c8c933c8086f28148793c55806e1362992f`.

## v2.2.25 - 2026-06-17

- Fixed stale Smart Routing data causing `No candidate supports required capabilities` when Codex requests custom tools or native Responses capabilities.
- Rebuilds the default AMR group from the current provider store when the proxy sees stale or empty default candidates, then retries the route once.
- Includes native text+image Responses models in AMR image candidates so image-capable native proxy requests can route correctly.
- Increased the Codex launch wait window when CDP injection is enabled and improved timeout diagnostics for renderer connection stalls.
- Hardened one-file EXE startup by writing a concrete PyInstaller extraction directory instead of an unexpanded environment-variable path.
- Verified with targeted AMR/proxy tests, targeted Codex start/injection API tests, real-data isolated AMR route simulations, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `71.33 MB`; SHA256: `47f206fa59dd217368a62caafd73a11e93d282d38013fd784296431f8e16ed22`.

## v2.2.24 - 2026-06-17

- Fixed the injected Usage Panel getting stuck on `Loading...` when the local bridge was stale or unavailable.
- Added a bridge timeout and HTTP fallback so route, token, cost, context, and Fast Route Switch data can recover through the active desktop backend.
- Re-registered the renderer bridge from the listener session and made bridge requests prefer the desktop backend state before falling back to default local ports.
- Verified with targeted injection unit tests, generated injection JavaScript syntax check, stale-backend bridge simulation, local quick-settings API call, and local route-resolution check. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.

## v2.2.23 - 2026-06-16

- Fixed the native Token Monitor so it can still read local token/context data when the desktop HTTP URL is unavailable or stale.
- Added an in-process fallback for the monitor's `/api/token/current` snapshot; this does not depend on Codex page injection.
- Improved monitor rendering so stable token totals show `0 tok/min` instead of staying blank, and zero context-used values display as `0 / window`.
- Verified with targeted native monitor unit tests, real local `/api/token/current` snapshot via Flask test client, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `74.25 MB`; SHA256: `73965249b5212256622938a0dfea930cc471340136781da69a8fe5b6c08c792f`.

## v2.2.22 - 2026-06-16

- Added a built-in Simplified Chinese Codex UI enhancement that translates common buttons, menus, labels, and input placeholders through the existing injection layer.
- Kept the translation guard narrow: chat content, code blocks, message bodies, and editable content are skipped, and disabling the feature restores translated UI nodes where possible.
- Added a quick-panel and settings-page toggle for the Chinese UI enhancement; it stays independent from Plugin Unlock and remains available in official-login mode.
- Updated the official usage-alert hider to recognize newer Chinese rate-limit reset wording.
- Cleaned user-facing quota notes and launch comments.
- Verified with targeted Python/unit checks, generated injection JavaScript syntax check, README reference check, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `74.25 MB`; SHA256: `9aeec8fc00150b126deb86b33b2965cf2acc512d527500cb987b794bb9fb7e65`.

## v2.2.21 - 2026-06-14

- Fixed official-direct mode detection so an older third-party provider focus no longer makes the injected panel or floating monitor treat the active Codex session as third-party/proxy usage.
- Kept official-login injection useful while Plugin Unlock stays forced off: the Usage Panel now refreshes quick settings while open and keeps the last safe runtime state if a transient backend status poll fails.
- Improved the injected Usage Panel's official quota display so official subscription/quota snapshots are shown directly instead of being hidden behind the generic official-login message.
- Verified with targeted Python/unit checks and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `74.25 MB`; SHA256: `dfda7d1c1d3379167ca67bb077116b10291daff33fcc51b4ca727b50cb720f83`.

## v2.2.20 - 2026-06-13

- Clarified the AMR image-routing contract: direct image requests only use AMR `image_candidates` for AMR group model IDs, while `provider/model` image requests stay on that provider's native image endpoint and native Responses image-generation tools are forwarded as Responses.
- Added a provider connectivity compatibility check so root API URLs probe `/v1/models` first, making relay/base-url diagnostics match common OpenAI-compatible deployments.
- Refined the built-in Codex usage-alert hider with stricter quota-banner and usage-card detection, without adding a generic script/plugin marketplace.
- Reconfirmed the built-in Codex plugin unlock path: marketplace filtering, plugin entry access, and install-button unlock remain available only through our own injection layer, with official OAuth login forcing the feature off.
- Hardened one-file packaging so the optional top-level charset-normalizer `_mypyc` extension is excluded from the archive, avoiding the Windows bootloader extraction failure shown by the previous build.
- Verified with targeted Python/unit checks and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `74.25 MB`; SHA256: `2f72f234074cb9f631695c51643923ffa52800adb30f57dc3c807f1381306351`.

## v2.2.19 - 2026-06-12

- Fixed Codex history migration so launches only skip when the exact previous provider/model sync is trustworthy; removed the official/third-party family shortcut that could leave history on the wrong backend.
- Hardened local proxy request logging: running proxy instances now receive updated request-log configuration, failed domestic Responses requests are logged, and debug events report skipped, written, or failed request-log writes.
- Changed domestic partial Responses handling to block unsupported tool/content combinations instead of silently sanitizing and forwarding altered requests.
- Fixed native Responses forwarding to strip internal `_cem_*` fields before upstream calls, and fixed chat-to-Responses conversion after the adapter signature changed.
- Improved Codex injection bridge handling so renderer requests use the injected backend URL and unwrap `{ success, data }` responses correctly.
- Verified with static checks, real local-proxy HTTP smoke tests using the user's provider/AMR configuration, and packaged EXE smoke test. Full pytest was intentionally skipped because this environment has Codex-disruptive tests.
- EXE: `74.25 MB`; SHA256: `70f3f8a675b3d37587ac3695c7a674d8e852342d3bd541dcefb8c125e4706a66`.

## v2.2.18 - 2026-06-11

- Added official Codex OAuth quota reading and exposed quota snapshots in the floating monitor, quick panel, and settings flow.
- Added balance/quota probes for DeepSeek, KimiCode, Zhipu, MiniMax Coding Plan, SiliconFlow, StepFun, OpenRouter, and Novita.
- Locked Plugin Unlock off while an official Codex login is detected; Enhancement Injection remains available and defaults on.
- Added visible version labels in the main sidebar and injected Codex quick panel.
- Fixed injected quick panel backend fallback, quick toggles, and official-login lock state rendering.
- Hardened settings serialization so missing or mocked Codex auth mode cannot break `/api/settings`.
- Updated packaging to disable UPX and keep the release manifest with packaged smoke-test proof.
- EXE: `74.33 MB`; SHA256: `6f680ee54988cdb24849de4594cb6cda25ac872677f18156d91a7e2e728c36a1`.
- Verified with `python -m pytest -q` and `python build_exe.py --smoke-test --write-release-manifest`.

## v2.2.12 - 2026-06-09

### 中文

- 重做供应商页的信息架构：模型上下文窗口、接口覆盖、是否显示给 Codex、模型级文本/视觉/工具/图片/视频能力全部放到供应商编辑器的“模型明细”区。
- 保留高级批量模型清单，方便粘贴和迁移；保存、预览和测试优先读取新的可视化模型明细表。
- “模型轮换”正式改名为“智能路由”，用户可见的导航、说明、官方模式提示和 README 已统一改名。
- Codex 集成页新增三张连接模式卡：官方直连、保留登录 + 本地代理、第三方/本地代理；切回官方的入口现在直接可见并可一键启动。
- 设置向导增加当前步骤卡和进度条，步骤状态、说明和完成度会随切换同步，整体更接近真正的设置向导。
- 本次 EXE 大小 `73.22 MB`，SHA256 `896b034d5a81807c16bdf7ba555eba846b7266435f8d694170c36ffebd9d22e3`。
- 已通过 `python -m pytest -q`、前端 JS 静态检查、`python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest`。

### English

- Reworked Provider information architecture: model context window, interface override, Codex visibility, and model-level text, vision, tools, image, and video capabilities now live in the Provider editor’s Model Details section.
- Kept the advanced bulk model list for paste/migration workflows; save, preview, and test flows now prefer the visual Model Details table.
- Renamed user-facing “Model Rotation” to “Smart Routing” across navigation, copy, official-mode warnings, and README.
- Added three obvious connection-mode cards on Codex Integration: Official Direct, Keep Login + Local Proxy, and Third-party / Local Proxy, so switching back to official is discoverable and launchable.
- Improved the Settings Wizard with a current-step card and progress bar that sync title, detail, status, and completion as the user moves through steps.
- This EXE is `73.22 MB` with SHA256 `896b034d5a81807c16bdf7ba555eba846b7266435f8d694170c36ffebd9d22e3`.
- Verified with `python -m pytest -q`, frontend JS static checks, and `python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest`.

## v2.2.11 - 2026-06-09

### 中文

- 修复官方登录态识别：当 `auth.json` 为 ChatGPT/OAuth 登录且 `config.toml` 只配置模型时，界面会锁定显示官方 `openai` 登录态和当前模型（例如 `gpt-5.5`），不再误判为普通供应商缺失。
- 官方登录态改为只做可切换的直连状态，不进入本地代理、AMR 或模型轮换；安全的 Codex 页面增强注入仍可启用。
- 本地代理默认使用高熵 bearer token，设置页只显示指纹；Codex provider 写入会使用真实 token，并且代理端口被占用时会自动退避到后续可用端口。
- 启动 Codex 改为带进度的后台任务，完整历史同步会显示阶段进度；同步默认不再每次做完整备份，并新增备份清理入口。
- 新增一键修复 Codex 配置到模板态、首次切回官方登录的风险重置流程、Goal mode 总设置、官方用量统计读取和悬浮窗 token 消耗速度。
- 本次 EXE 大小 `73.21 MB`，SHA256 `da20b3222acd814a2bb9e0524cb9fda5f30ee91220b0d4d77fba365d10a84d09`。
- 已通过 `python -m pytest -q`、前端 JS 静态检查、`python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest`。

### English

- Fixed official-login detection: when `auth.json` contains ChatGPT/OAuth auth and `config.toml` only sets a model, the UI now locks to the official `openai` login state and current model such as `gpt-5.5` instead of treating the provider as missing.
- Official login is now a switch-only direct state and is excluded from the local proxy, AMR, and model rotation; safe Codex page enhancement injection can still run.
- The local proxy now uses a high-entropy bearer token by default, settings only show its fingerprint, Codex provider config writes the real token, and occupied proxy ports automatically back off to the next available port.
- Codex launch now runs as a progress-reporting background task; full history sync shows progress, full backup is no longer the default on every sync, and backups can be pruned from the UI.
- Added one-click Codex config template repair, a risk-confirmed official-login reset flow, a global Goal mode setting, official usage reading, and token consumption speed in the floating monitor.
- This EXE is `73.21 MB` with SHA256 `da20b3222acd814a2bb9e0524cb9fda5f30ee91220b0d4d77fba365d10a84d09`.
- Verified with `python -m pytest -q`, frontend JS static checks, and `python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest`.

## v2.2.10 - 2026-06-08

### 中文

- 修复点击设置页/进入设置向导时弹出 CMD 窗口的问题。
- 设置页会读取 Windows 开机启动状态，后端需要调用 `schtasks.exe /Query`；现在该调用统一带 `CREATE_NO_WINDOW`，查询、创建和删除任务都不会闪出控制台窗口。
- 补充测试，确保启动管理器默认命令 runner 永远传入隐藏控制台参数。
- 优化启动体感：后端平台识别不再触发 Windows WMI，总览页和设置页先渲染首屏，再后台刷新供应商、清理、启动状态和更新检查。
- 后端初始化实测从 500ms 级别降到约 `27ms`；本次 EXE 大小 `73.15 MB`，SHA256 `e9d7cebb3dc18b3ac2b5f41829a4ee658065051792787343ec58f5b86e80d544`；已验证打包版启动后 `/api/startup/status` 正常返回。

### English

- Fixed a CMD window flashing when opening Settings or the Settings Wizard.
- Settings reads Windows startup status through `schtasks.exe /Query`; the startup command runner now always uses `CREATE_NO_WINDOW`, so query/create/delete task operations do not flash a console window.
- Added coverage to ensure the startup manager default runner always passes the hidden-console flag.
- Improved perceived startup speed: backend platform detection no longer touches Windows WMI, and Overview/Settings render their first screen before provider, cleanup, startup-status, and update checks finish in the background.
- Backend initialization dropped from the 500ms range to about `27ms`; this EXE is `73.15 MB` with SHA256 `e9d7cebb3dc18b3ac2b5f41829a4ee658065051792787343ec58f5b86e80d544`; packaged startup plus `/api/startup/status` was verified.

## v2.2.9 - 2026-06-08

### 中文

- 修复双击应用后没有窗口的问题：如果 `51234` 被旧测试服务或普通 Flask 服务占用，启动器不再误判为“桌面应用已启动”，会自动切到 `51235` 之后的可用端口。
- 健康检查新增 `desktop_mode` 和 `desktop_port`，单实例逻辑只把真正的桌面实例当作已启动。
- 如果真实桌面实例已经在运行，再次启动会尝试把已有主窗口恢复到前台。
- 已补充入口测试，覆盖非桌面端口占用、真实桌面健康标记和动态端口 URL 更新。
- 本次 EXE 大小 `73.15 MB`，SHA256 `468bff7b618f9fa7c9f6e622422d40bb4d8acc0fd5a0c19afb257773b9f89e5a`；已验证源码桌面和打包 EXE 都能在端口冲突时启动到 `51235`。

### English

- Fixed the no-window launch failure: if `51234` is occupied by an old test server or a plain Flask server, the launcher no longer treats it as an already-running desktop app and automatically moves to the next available port after `51235`.
- Added `desktop_mode` and `desktop_port` to the health endpoint so single-instance checks only trust real desktop instances.
- When a real desktop instance is already running, launching again now tries to restore the existing main window.
- Added entrypoint tests for non-desktop port conflicts, desktop health markers, and dynamic backend URL updates.
- This EXE is `73.15 MB` with SHA256 `468bff7b618f9fa7c9f6e622422d40bb4d8acc0fd5a0c19afb257773b9f89e5a`; both source desktop startup and packaged EXE startup were verified to move to `51235` during a port conflict.

## v2.2.8 - 2026-06-08

### 中文

- 重写 README 中英文说明，把项目定位、连接模式、供应商和模型轮换边界、打包发布规则改成更清楚的用户语言。
- 设置向导、连接检查、审批规则测试、图片/视频能力检查、历史用量来源等文案继续去技术化，减少无意义的旧式检查说明。
- 自动审批默认提示词要求严格 JSON，包含 `decision`、`risk_level`、`reason`、`confidence`、`scope` 和 `reviewed_action_id`。
- Codex 连接页会自动检查将保存的连接信息，保存前使用同一套 `User-Agent` 和自定义 Header。
- 供应商页只负责连接、模型能力和媒体能力；模型轮换页负责新会话顺序、优先级和故障转移。
- 增强纯原生 Responses/Chat 代理的模型级区分，保留原生模式和 Codex 登录态下的配置锁定逻辑。
- 发布包必须包含 `CodexEnhancedManager.exe` 和 `release-manifest.json`；本次 EXE 大小 `73.14 MB`，SHA256 `2c549ecf3188d5bd5b88771583ccd1b8272d7468a5615a42cf3cdb1d80dd1edd`。
- 已通过 `python -m pytest -q`、JS/Python 静态检查、`python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest` 和独立 `CodexEnhancedManager.exe --smoke-test`。

### English

- Rewrote the English and Chinese README files with clearer user-facing positioning, connection modes, provider/routing boundaries, and release rules.
- Continued replacing technical or low-value check copy with connection checks, approval rule tests, media capability checks, and usage-source summaries.
- The default Auto Approval prompt now requires strict JSON with `decision`, `risk_level`, `reason`, `confidence`, `scope`, and `reviewed_action_id`.
- The Codex connection page now checks the connection that will be saved and uses the same `User-Agent` plus custom headers as real proxy requests.
- Provider setup is limited to connection and model/media capability details; Model Rotation owns new-session order, priority, and failover.
- Improved model-level separation for native Responses, compatible Responses, and Chat providers while preserving official-login and native-mode locks.
- Releases must include `CodexEnhancedManager.exe` and `release-manifest.json`; this EXE is `73.14 MB` with SHA256 `2c549ecf3188d5bd5b88771583ccd1b8272d7468a5615a42cf3cdb1d80dd1edd`.
- Verified with `python -m pytest -q`, JS/Python static checks, `python build_exe.py --no-desktop-copy --smoke-test --write-release-manifest`, and a separate `CodexEnhancedManager.exe --smoke-test` run.
