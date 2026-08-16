# Third-party references and implementation boundary

Codex Enhanced Manager remains an Apache-2.0 project. The following sources were consulted for behavior, interoperability, and packaging research; their source code and artwork are not incorporated into this repository.

- OpenAI Codex documentation and public source behavior: configuration location, Responses transport, model catalog, Goals, plugins, service tiers, and desktop integration compatibility.
- PyWebView documentation: macOS apps are packaged with py2app and the Cocoa event loop stays on the main thread.
- pystray documentation: macOS integrates the tray with an existing GUI loop through `run_detached()`.
- GitHub Actions documentation: the `macos-14` standard runner is Apple Silicon arm64.
- BigPizzaV3/CodexPlusPlus and BigPizzaV3/CodexPlusPlusScriptMarket: user-visible enhancement categories, CDP injection patterns, local script/theme workflows, and compatibility behavior were studied independently. Both projects remain governed by their own licenses; no AGPL implementation or bundled media was copied.

Excluded by design: mobile/remote control, relay services, WeChat bridging, hosted extension marketplaces, and reference-project artwork.

Security boundary: locally imported JavaScript is user-supplied executable code and is disabled by default. Theme and pet packages are data-only and accept CSS, JSON, and supported image formats; executable JavaScript must be imported separately as a user script.
