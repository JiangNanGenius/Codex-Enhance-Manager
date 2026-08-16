/** Local-only renderer extensions. */

async function extensionRequest(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok || data.success === false) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

async function loadExtensionsPage() {
    try {
        const [scripts, themes, pets] = await Promise.all([
            extensionRequest('/api/extensions/scripts'),
            extensionRequest('/api/extensions/themes'),
            extensionRequest('/api/extensions/pets'),
        ]);
        renderExtensionList('scripts', scripts.scripts || []);
        renderExtensionList('themes', themes.themes || []);
        renderExtensionList('pets', pets.pets || []);
    } catch (error) {
        showToast(`扩展加载失败：${error.message}`, 'error');
    }
}

function renderExtensionList(kind, records) {
    const target = document.getElementById(`extension-${kind}-list`);
    if (!target) return;
    if (!records.length) {
        target.innerHTML = '<div class="text-xs text-dark-500 py-3">尚未导入</div>';
        return;
    }
    target.innerHTML = records.map(record => `
        <div class="rounded-lg border border-dark-700 bg-dark-900/60 p-3">
            <div class="flex items-start justify-between gap-2">
                <div class="min-w-0"><div class="text-sm text-white truncate">${escapeHtml(record.name || record.id)}</div><div class="text-[11px] text-dark-500 font-mono truncate">${escapeHtml(record.sha256 || '')}</div></div>
                <label class="text-xs text-dark-300 flex items-center gap-1"><input type="checkbox" ${record.enabled ? 'checked' : ''} onchange="setExtensionEnabled('${kind}','${escapeAttr(record.id)}',this.checked)">启用</label>
            </div>
            <div class="mt-2 flex items-center justify-between text-xs text-dark-400"><span>${escapeHtml(record.version || 'local')}</span><button class="text-red-300 hover:text-red-200" onclick="deleteExtension('${kind}','${escapeAttr(record.id)}')">删除</button></div>
        </div>
    `).join('');
}

async function importLocalScript() {
    const file = document.getElementById('extension-script-file')?.files?.[0];
    if (!file) return showToast('请选择本地 .js 文件', 'error');
    const form = new FormData();
    form.append('file', file);
    form.append('name', document.getElementById('extension-script-name')?.value || '');
    form.append('version', document.getElementById('extension-script-version')?.value || '');
    try {
        await extensionRequest('/api/extensions/scripts/import', { method: 'POST', body: form });
        showToast('脚本已导入，默认保持停用', 'success');
        loadExtensionsPage();
    } catch (error) { showToast(error.message, 'error'); }
}

async function importAssetPack(kind) {
    const inputId = kind === 'themes' ? 'extension-theme-file' : 'extension-pet-file';
    const file = document.getElementById(inputId)?.files?.[0];
    if (!file) return showToast('请选择本地 ZIP 文件', 'error');
    const form = new FormData();
    form.append('file', file);
    try {
        await extensionRequest(`/api/extensions/${kind}/import`, { method: 'POST', body: form });
        showToast('资源包已导入，默认保持停用', 'success');
        loadExtensionsPage();
    } catch (error) { showToast(error.message, 'error'); }
}

async function setExtensionEnabled(kind, id, enabled) {
    const base = kind === 'scripts' ? `/api/extensions/scripts/${encodeURIComponent(id)}` : `/api/extensions/${kind}/${encodeURIComponent(id)}`;
    try {
        await extensionRequest(`${base}/enabled`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ enabled }) });
        showToast('扩展状态已更新；重新注入或重启 Codex 后完全生效', 'success');
        loadExtensionsPage();
    } catch (error) { showToast(error.message, 'error'); loadExtensionsPage(); }
}

async function deleteExtension(kind, id) {
    if (!window.confirm('删除该本地扩展？此操作会移除管理器保存的副本。')) return;
    const base = kind === 'scripts' ? `/api/extensions/scripts/${encodeURIComponent(id)}` : `/api/extensions/${kind}/${encodeURIComponent(id)}`;
    try {
        await extensionRequest(base, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ confirmation: 'DELETE_LOCAL_EXTENSION' }) });
        showToast('扩展已删除', 'success');
        loadExtensionsPage();
    } catch (error) { showToast(error.message, 'error'); }
}
