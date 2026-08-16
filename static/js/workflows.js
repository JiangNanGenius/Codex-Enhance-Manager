/** Explicit local worktree and project record workflows. */

function worktreePayload() {
    return {
        repository: document.getElementById('worktree-repository')?.value || '',
        target: document.getElementById('worktree-target')?.value || '',
        remote: document.getElementById('worktree-remote')?.value || 'upstream',
        base_branch: document.getElementById('worktree-base')?.value || 'main',
        branch: document.getElementById('worktree-branch')?.value || '',
    };
}

async function loadWorkflowsPage() {
    try {
        const [caps, projects] = await Promise.all([api('/api/platform/capabilities'), api('/api/workflows/projects')]);
        const target = document.getElementById('workflow-capabilities');
        if (target) target.textContent = `${caps.platform} ${caps.architecture} · worktree ${caps.worktrees ? 'supported' : 'unsupported'} · online market disabled · remote control disabled`;
        renderWorkflowProjects(projects.projects || []);
    } catch (error) { showToast(`工作流加载失败：${error.message}`, 'error'); }
}

async function previewWorktree() {
    try {
        const result = await api('/api/workflows/worktrees/preview', { method: 'POST', body: JSON.stringify(worktreePayload()) });
        document.getElementById('worktree-preview').textContent = JSON.stringify(result, null, 2);
    } catch (error) { showToast(error.message, 'error'); }
}

async function createWorktree() {
    if (!window.confirm('将执行预览中的 git fetch 与 git worktree add，是否继续？')) return;
    try {
        const result = await api('/api/workflows/worktrees', { method: 'POST', body: JSON.stringify({ ...worktreePayload(), confirmation: 'CREATE_UPSTREAM_WORKTREE' }) });
        document.getElementById('worktree-preview').textContent = JSON.stringify(result, null, 2);
        showToast('Worktree 已创建', 'success');
        loadWorkflowsPage();
    } catch (error) { showToast(error.message, 'error'); }
}

async function recordWorkflowProject() {
    const payload = {
        kind: document.getElementById('workflow-project-kind')?.value || 'local',
        host: document.getElementById('workflow-project-host')?.value || '',
        name: document.getElementById('workflow-project-name')?.value || '',
        path: document.getElementById('workflow-project-path')?.value || '',
    };
    try {
        await api('/api/workflows/projects', { method: 'POST', body: JSON.stringify(payload) });
        showToast('项目记录已保存', 'success');
        loadWorkflowsPage();
    } catch (error) { showToast(error.message, 'error'); }
}

function renderWorkflowProjects(projects) {
    const target = document.getElementById('workflow-project-list');
    if (!target) return;
    target.innerHTML = projects.length ? projects.map(project => `
        <div class="rounded-lg border border-dark-700 bg-dark-900/60 p-3 flex items-start justify-between gap-3">
            <div class="min-w-0"><div class="text-sm text-white truncate">${escapeHtml(project.name || project.path)}</div><div class="text-xs text-dark-500 font-mono truncate">${escapeHtml(project.host ? `${project.host}:${project.path}` : project.path)}</div></div>
            <button class="text-xs text-red-300" onclick="deleteWorkflowProject('${escapeAttr(project.id)}')">删除记录</button>
        </div>`).join('') : '<div class="text-xs text-dark-500 py-3">尚无项目记录</div>';
}

async function deleteWorkflowProject(id) {
    try {
        await api(`/api/workflows/projects/${encodeURIComponent(id)}`, { method: 'DELETE' });
        loadWorkflowsPage();
    } catch (error) { showToast(error.message, 'error'); }
}
