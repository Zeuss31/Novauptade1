/**
 * ARTIFACT MANAGER - Frontend
 * Artifact'ları render eder ve yönetir
 */

class ArtifactRenderer {
    constructor() {
        this.artifacts = new Map();
        this.currentTab = new Map();
    }

    async createArtifact(artifactData, messageElement) {
        const artifactId = artifactData.id;
        this.artifacts.set(artifactId, artifactData);

        const container = this.createArtifactContainer(artifactData);
        messageElement.appendChild(container);

        await this.renderContent(artifactId, artifactData);
    }

    createArtifactContainer(data) {
        const container = document.createElement('div');
        container.className = 'artifact-container';
        container.id = `artifact-${data.id}`;

        const icon = this.getIcon(data.type);

        container.innerHTML = `
            <div class="artifact-header">
                <div class="artifact-title">
                    ${icon}
                    <span>${this.escapeHtml(data.title)}</span>
                    <span class="artifact-badge">${data.language || data.type}</span>
                </div>
                <div class="artifact-actions">
                    ${this.getActionButtons(data)}
                </div>
            </div>
            
            ${this.getTabs(data)}
            
            <div class="artifact-content" id="content-${data.id}">
                <div class="artifact-loading">
                    <div class="artifact-spinner"></div>
                </div>
            </div>
            
            <div class="artifact-footer">
                <div class="artifact-version-info">
                    <span>v${data.version || 1}</span>
                    <span>${new Date(data.created_at || Date.now()).toLocaleString('tr-TR')}</span>
                </div>
            </div>
        `;

        this.attachEventListeners(container, data);
        return container;
    }

    getIcon(type) {
        const icons = {
            'code': '💻',
            'html': '🌐',
            'react': '⚛️',
            'svg': '🎨',
            'markdown': '📝'
        };
        return icons[type] || '📄';
    }

    getActionButtons(data) {
        let buttons = `
            <button class="artifact-btn" data-action="copy">
                📋 Kopyala
            </button>
            <button class="artifact-btn" data-action="download">
                ⬇️ İndir
            </button>
        `;

        if (data.language === 'python') {
            buttons += `
                <button class="artifact-btn" data-action="run">
                    ▶️ Çalıştır
                </button>
            `;
        }

        return buttons;
    }

    getTabs(data) {
        if (['html', 'react'].includes(data.type)) {
            return `
                <div class="artifact-tabs">
                    <button class="artifact-tab active" data-tab="code">
                        Kod
                    </button>
                    <button class="artifact-tab" data-tab="preview">
                        Önizleme
                    </button>
                </div>
            `;
        }
        return '';
    }

    async renderContent(artifactId, data) {
        const contentEl = document.getElementById(`content-${artifactId}`);
        const currentTab = this.currentTab.get(artifactId) || 'code';

        if (currentTab === 'code') {
            contentEl.innerHTML = `
                <pre class="artifact-code"><code class="language-${data.language || 'text'}">${this.escapeHtml(data.content)}</code></pre>
            `;

            if (window.hljs) {
                contentEl.querySelectorAll('code').forEach(block => {
                    hljs.highlightElement(block);
                });
            }
        } else if (currentTab === 'preview') {
            contentEl.innerHTML = `
                <div class="artifact-preview">
                    <iframe id="preview-${artifactId}" sandbox="allow-scripts"></iframe>
                </div>
            `;

            const iframe = document.getElementById(`preview-${artifactId}`);
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            iframeDoc.open();
            iframeDoc.write(data.content);
            iframeDoc.close();
        }
    }

    attachEventListeners(container, data) {
        const artifactId = data.id;

        container.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const action = e.target.dataset.action;

                switch (action) {
                    case 'copy':
                        await this.copyToClipboard(data.content);
                        this.showToast('Kopyalandı! ✓');
                        break;

                    case 'download':
                        this.downloadArtifact(data);
                        break;

                    case 'run':
                        await this.runPythonCode(artifactId, data.content);
                        break;
                }
            });
        });

        container.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', async (e) => {
                const tabName = e.target.dataset.tab;

                container.querySelectorAll('.artifact-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');

                this.currentTab.set(artifactId, tabName);
                await this.renderContent(artifactId, data);
            });
        });
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    downloadArtifact(data) {
        const extensions = {
            'python': 'py',
            'javascript': 'js',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'markdown': 'md'
        };

        const ext = extensions[data.language] || 'txt';
        const filename = `${data.title.replace(/\s+/g, '_')}.${ext}`;

        const blob = new Blob([data.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
    }

    async runPythonCode(artifactId, code) {
        const contentEl = document.getElementById(`content-${artifactId}`);

        const resultDiv = document.createElement('div');
        resultDiv.className = 'artifact-execution-result';
        resultDiv.innerHTML = '<div class="artifact-loading"><div class="artifact-spinner"></div></div>';
        contentEl.appendChild(resultDiv);

        try {
            const response = await fetch('/api/code/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });

            const result = await response.json();

            resultDiv.className = `artifact-execution-result ${result.success ? 'success' : 'error'}`;
            resultDiv.innerHTML = `
                <strong>${result.success ? '✓ Çalıştırıldı' : '✗ Hata'}</strong>
                ${result.execution_time ? ` (${result.execution_time.toFixed(3)}s)` : ''}
                <pre>${this.escapeHtml(result.output || result.error || 'Çıktı yok')}</pre>
            `;
        } catch (error) {
            resultDiv.className = 'artifact-execution-result error';
            resultDiv.innerHTML = `<strong>✗ Hata</strong><pre>${this.escapeHtml(error.message)}</pre>`;
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
window.artifactRenderer = new ArtifactRenderer();