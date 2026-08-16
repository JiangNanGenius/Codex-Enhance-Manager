<p align="center">
  <img src="icon.png" alt="Codex Enhanced Manager icon" width="96">
</p>

<h1 align="center">Codex Enhanced Manager</h1>

<p align="center">
  <strong>Keep Codex native. Add the control panel it should have had.</strong>
</p>

<p align="center">
  Official login switching · local proxy routing · smart routing · token telemetry · recovery tools
</p>

<p align="center">
  <a href="README.zh-CN.md">中文</a>
  ·
  <a href="https://github.com/JiangNanGenius/Codex-Enhance-Manager/releases">Download</a>
  ·
  <a href="RELEASE_NOTES.md">Release notes</a>
  ·
  <a href="LICENSE">License</a>
</p>

<p align="center">
  <img alt="Platform: Windows and Apple Silicon macOS" src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20arm64-2563eb.svg">
  <img alt="Local first" src="https://img.shields.io/badge/Local--first-by_default-0f766e.svg">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-334155.svg">
  <img alt="License: Apache-2.0" src="https://img.shields.io/badge/License-Apache--2.0-green.svg">
</p>

---

## Why This Exists

Codex feels best when it behaves like Codex: logged in, local, fast to launch, and not buried under provider plumbing. Codex Enhanced Manager keeps that native experience, then adds the parts power users keep reaching for: provider control, safe routing, readable usage, backup/repair tools, and a floating monitor that stays out of the way.

It is a Windows and Apple Silicon macOS desktop app backed by a local service. Your settings, providers, request metadata, diagnostics, backups, extensions, and exports stay on your machine by default.

## At A Glance

<table>
  <tr>
    <td width="50%">
      <strong>Official login stays official</strong><br>
      Detects ChatGPT/OAuth login, shows the effective OpenAI state, and keeps official direct mode out of local proxy routing and Smart Routing.
    </td>
    <td width="50%">
      <strong>Routing when you actually want it</strong><br>
      Starts a local proxy for routed modes, writes the real backoff port into Codex config, and protects the proxy with a high-entropy bearer token.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Model control without credential clutter</strong><br>
      Provider setup owns keys, base URLs, headers, capabilities, and media support. Model rotation owns new-session order, failover, and capability matching.
    </td>
    <td width="50%">
      <strong>Recovery for real failure modes</strong><br>
      Repair broken Codex config, reset risky official-login transitions with explicit warnings, prune backups, and inspect redacted diagnostics.
    </td>
  </tr>
</table>

## Connection Modes

| Mode | Use It When | What Happens |
| --- | --- | --- |
| Official direct | You want Codex to use the official account exactly as-is. | Keeps OAuth login intact, locks routing-changing provider behavior, and still allows safe UI enhancement injection. |
| Login plus proxy/API | You want the official login preserved while using local proxy/API routing. | Starts the local proxy, writes the active port and bearer token into Codex provider config, then syncs history with progress. |
| Third-party provider | You run Codex through custom vendors, proxy providers, or compatibility APIs. | Enables provider credentials, Responses/Chat selection, model mapping, media fallback, quotas, and Smart Routing. |

## How Codex Talks To Models

This project follows the current OpenAI Codex source behavior instead of guessing at the transport layer. Codex builds a Responses API request and sends `POST /responses` with SSE streaming. The official OpenAI agent-loop write-up documents the same endpoint choices for ChatGPT login, API-key auth, local providers, and cloud Responses providers.

What that means here:

- The Codex config we write uses `wire_api = "responses"` and points Codex at the local proxy `/v1` base URL.
- Providers marked as native Responses are forwarded to their upstream `/responses` endpoint with the Codex request shape preserved.
- Chat-only providers are adapted by the local proxy from Responses to Chat Completions.
- **Image routing is independent, but not global**:
  - Direct `POST /v1/images/generations` requests use AMR `image_candidates` only when the request model is an AMR group such as `auto`, `smart-routing`, `amr/<group>`, or `rotation/<group>`.
  - Direct image requests with a hard-routed `provider/model` value bypass AMR and are forwarded to that provider's image endpoint. This is the intended path for private pure-native proxy providers.
  - Native Responses requests that include OpenAI's built-in `image_generation` tool are forwarded to native upstreams as Responses requests; the proxy does not reinterpret that tool as AMR image routing.
  - Domestic compatibility providers can use the chat/tool fallback path when native Responses cannot safely carry the request. In that fallback, generated `generate_image` calls may use AMR `image_candidates` if the original model is an AMR group.

References: [openai/codex `responses.rs`](https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/endpoint/responses.rs) and [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/).

## What You Get

- A setup flow for Codex paths, official login state, providers, model capabilities, routing, media fallback, startup, and save checks.
- Provider management with per-model upstream routing, aliases, context windows, compact thresholds, service tiers, Web Search/Responses Lite metadata, image policy, and media routing.
- Model rotation for next-session order, priority, fallback, and capability filtering without mixing it into provider credentials.
- Token, cost, and quota visibility from Codex usage, official login quota, cache totals, proxy metadata, local estimates, provider-reported fields, and preset balance scripts when available.
- A native floating monitor with tokens, cache, context, one-hour usage, token speed, balance burn rate, subscription quota percentage, opacity settings, tray actions, and quick switching.
- Local-only user scripts, validated CSS/image theme and pet packs, recoverable batch session deletion, multi-database discovery, and explicit worktree/Zed Remote records.
- Backup, restore, config-template repair, moved-session repair, redacted diagnostics, update checks, Windows EXE releases, and Apple Silicon DMG releases.

## Safety Model

- Local-first storage under `Documents/Codex Enhanced Manager/` on Windows and `~/Library/Application Support/Codex Enhanced Manager/` on macOS.
- API keys, bearer tokens, and sensitive headers are redacted in settings exports, diagnostics, and logs.
- The local proxy requires a generated bearer token; settings show only a fingerprint.
- Official direct mode is switch-only and does not enter local proxy routing or Smart Routing.
- Destructive Codex config/auth resets require explicit confirmation and warn that chat history may be lost.
- Imported JavaScript is disabled by default and clearly identified because enabled scripts execute inside the Codex renderer. Theme/pet packs reject executable JavaScript, unsafe paths, unsupported files, and oversized payloads.

## Provider Quota Notes

Known balance and Coding Plan quota methods are documented in [docs/provider-quota-and-billing.md](docs/provider-quota-and-billing.md), including built-in endpoints for KimiCode, Zhipu, MiniMax, SiliconFlow, StepFun, OpenRouter, Novita, DeepSeek, and official Codex OAuth quota.

## Install

### Windows EXE

Download the latest build from [Releases](https://github.com/JiangNanGenius/Codex-Enhance-Manager/releases), then run:

```text
CodexEnhancedManager.exe
```

### macOS arm64 DMG

Download `CodexEnhancedManager-v2.3.0-macos-arm64.dmg`, open it, and drag the app to Applications. This build supports Apple Silicon only and declares macOS 12.0 as the minimum version.

The DMG is ad-hoc signed and **not notarized**. On first launch, Control-click the app and choose **Open**. If Gatekeeper still blocks it, open **System Settings → Privacy & Security** and choose **Open Anyway** for this app. Only bypass Gatekeeper after verifying the release SHA-256.

### From Source

```bash
pip install -r requirements.txt
python main.py
```

The desktop app uses a local backend, usually:

```text
http://127.0.0.1:51234
```

If that port is occupied, the desktop launcher automatically moves to the next available port.

## Release Packaging

GitHub Actions builds the platform artifacts. The v2.3.0 release process intentionally performs no tests, lint, syntax checks, smoke tests, manual launches, or local package builds; CI only packages artifacts and records size/SHA-256 metadata.

Expected release assets:

```text
dist/CodexEnhancedManager.exe
dist/release-manifest.json
dist/CodexEnhancedManager-v2.3.0-macos-arm64.dmg
dist/macos-release-manifest.json
```

If either packaging job fails, the Release may temporarily contain source archives only. No runtime correctness claim is made from static review alone.

## Local Files

| Path | Purpose |
| --- | --- |
| `config.json` | Main app settings. |
| `providers/providers.json` | Local provider registry. |
| `logs/proxy_requests.jsonl` | Metadata-only proxy request log. |
| `backups/` | App and Codex config backups. |
| `diagnostics/` | Redacted diagnostic bundles. |
| `exports/` | User-requested exports. |
| `temp/` | Temporary app files. |
| `extensions/` | Imported scripts, themes, pets, hashes, and enable state. |
| `workflows/` | Explicitly recorded local/worktree/Zed Remote projects. |

## Independent Implementation

External projects were used to study user-visible behavior and protocol compatibility only. No AGPL source or bundled artwork is incorporated. See [THIRD_PARTY_REFERENCES.md](THIRD_PARTY_REFERENCES.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
