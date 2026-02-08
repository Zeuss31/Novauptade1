/**
 * Nova Artifact Renderer
 * * Bu script, web sayfasında kod ve önizleme artifact'leri oluşturur ve yönetir.
 * - Kodları renklendirir (Highlight.js gerekir).
 * - Kopyalama, indirme ve çalıştırma (simüle) işlevleri sunar.
 * - Kod ve Önizleme sekmeleri arasında geçiş yapar.
 */
class NovaArtifactRenderer {
    constructor() {
        this.feed = document.getElementById('artifact-feed');
    }

    /**
     * Güvenlik için HTML metinlerini temizler.
     * @param {string} text - Temizlenecek metin.
     * @returns {string} Temizlenmiş HTML.
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Yeni bir artifact oluşturur ve sayfaya ekler.
     * @param {object} data - Artifact verileri (id, type, title, language, content vb.).
     */
    createArtifact(data) {
        if (!this.feed) {
            console.error('Artifact feed container (#artifact-feed) not found.');
            return;
        }

        const artifactId = `artifact-${data.id || Date.now()}`;
        const container = document.createElement('div');
        container.className = 'artifact-container';
        container.id = artifactId;

        const icon = data.type === 'code' ? '💻' : '🌐';
        const hasPreview = data.type === 'html';

        container.innerHTML = `
            <div class="artifact-header">
                <div class="artifact-title">
                    <span>${icon}</span>
                    <span>${this.escapeHtml(data.title)}</span>
                    <span class="artifact-badge">${this.escapeHtml(data.language)}</span>
                </div>
                <div class="artifact-actions">
                    <button class="btn" data-action="copy">Kopyala</button>
                    <button class="btn" data-action="download">İndir</button>
                    ${data.language === 'python' ? '<button class="btn" data-action="run">Çalıştır</button>' : ''}
                </div>
            </div>
            
            ${hasPreview ? `
                <div class="artifact-tabs">
                    <button class="tab active" data-tab="code">Kod</button>
                    <button class="tab" data-tab="preview">Önizleme</button>
                </div>
            ` : ''}
            
            <div class="artifact-content-wrapper">
                </div>
        `;

        this.feed.appendChild(container);
        this.renderContent(container, data, 'code'); // Başlangıçta kodu göster
        this.attachEventListeners(container, data);
    }

    /**
     * Artifact içeriğini (kod veya önizleme) render eder.
     * @param {HTMLElement} container - Artifact ana kapsayıcısı.
     * @param {object} data - Artifact verileri.
     * @param {string} tab - Gösterilecek sekme ('code' veya 'preview').
     */
    renderContent(container, data, tab) {
        const contentWrapper = container.querySelector('.artifact-content-wrapper');
        contentWrapper.innerHTML = ''; // Önceki içeriği temizle

        if (tab === 'code') {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.className = `language-${data.language}`;
            code.textContent = data.content;
            pre.appendChild(code);
            contentWrapper.appendChild(pre);

            // Kod renklendirme (Highlight.js kütüphanesi sayfada olmalı)
            if (window.hljs) {
                hljs.highlightElement(code);
            }
        } else if (tab === 'preview') {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'artifact-preview';
            const iframe = document.createElement('iframe');
            iframe.sandbox = 'allow-scripts'; // Güvenlik için
            previewDiv.appendChild(iframe);
            contentWrapper.appendChild(previewDiv);
            
            // iframe içeriğini güvenli bir şekilde yaz
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            iframeDoc.open();
            iframeDoc.write(data.content);
            iframeDoc.close();
        }
    }

    /**
     * Butonlara ve sekmelere olay dinleyicileri ekler.
     * @param {HTMLElement} container - Artifact ana kapsayıcısı.
     * @param {object} data - Artifact verileri.
     */
    attachEventListeners(container, data) {
        // Aksiyon Butonları (Kopyala, İndir, Çalıştır)
        container.querySelector('.artifact-actions').addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                const action = e.target.dataset.action;
                switch (action) {
                    case 'copy':
                        navigator.clipboard.writeText(data.content).then(() => this.showToast('Kod panoya kopyalandı!'));
                        break;
                    case 'download':
                        this.downloadArtifact(data);
                        break;
                    case 'run':
                        this.runPythonCode(container, data.content);
                        break;
                }
            }
        });

        // Sekmeler (Kod, Önizleme)
        const tabsContainer = container.querySelector('.artifact-tabs');
        if (tabsContainer) {
            tabsContainer.addEventListener('click', (e) => {
                if (e.target.tagName === 'BUTTON') {
                    tabsContainer.querySelector('.active').classList.remove('active');
                    e.target.classList.add('active');
                    this.renderContent(container, data, e.target.dataset.tab);
                }
            });
        }
    }

    /**
     * Artifact'i dosya olarak indirir.
     * @param {object} data - Artifact verileri.
     */
    downloadArtifact(data) {
        const extensions = { 'python': 'py', 'javascript': 'js', 'html': 'html', 'css': 'css' };
        const ext = extensions[data.language] || 'txt';
        const filename = `${data.title.replace(/\s+/g, '_')}.${ext}`;
        
        const blob = new Blob([data.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Python kodunu çalıştırmayı SİMÜLE eder.
     * @param {HTMLElement} container - Sonucun gösterileceği artifact kapsayıcısı.
     * @param {string} code - Çalıştırılacak kod.
     */
    async runPythonCode(container, code) {
        let resultDiv = container.querySelector('.execution-result');
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.className = 'execution-result';
            container.appendChild(resultDiv);
        }

        resultDiv.innerHTML = '<div class="loading-spinner"></div>';

        // API çağrısını simüle etmek için 1.5 saniye bekle
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Simülasyon sonucu (rastgele başarılı veya hatalı döner)
        const isSuccess = Math.random() > 0.3; 
        if (isSuccess) {
            resultDiv.className = 'execution-result success';
            resultDiv.innerHTML = `
                <strong>Çalıştırma Başarılı (Simülasyon)</strong>
                <pre>Merhaba, Nova!\nBu, simüle edilmiş bir Python çıktısıdır.\nHesaplama sonucu: ${Math.floor(Math.random() * 100)}</pre>
            `;
        } else {
            resultDiv.className = 'execution-result error';
            resultDiv.innerHTML = `
                <strong>Hata Oluştu (Simülasyon)</strong>
                <pre>Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nNameError: name 'bilinmeyen_degisken' is not defined</pre>
            `;
        }
    }

    /**
     * Ekranda kısa süreli bir bildirim gösterir.
     * @param {string} message - Gösterilecek mesaj.
     */
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);

        // Toast'ı göster
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Toast'ı gizle ve kaldır
        setTimeout(() => {
            toast.classList.remove('show');
            toast.addEventListener('transitionend', () => toast.remove());
        }, 2500);
    }
}

// --- Sayfa Yüklendiğinde Çalışacak Kodlar ---

// Renderer sınıfından bir nesne oluştur
const novaRenderer = new NovaArtifactRenderer();

// Test Fonksiyonları (HTML'deki butonlar bunları çağırır)
function createPythonExample() {
    novaRenderer.createArtifact({
        id: 'py-' + Date.now(),
        type: 'code',
        title: 'Veri Analizi Scripti',
        language: 'python',
        content: `import pandas as pd

def analyze_data(source_url):
    """Verileri analiz eder ve bir özet döndürür."""
    print(f"Veriler şuradan çekiliyor: {source_url}")
    df = pd.read_csv(source_url)
    print("Veri özeti:")
    print(df.describe())
    return df

# Örnek kullanım
data_url = "https://example.com/data.csv"
analyzed_df = analyze_data(data_url)`
    });
}

function createHtmlExample() {
    novaRenderer.createArtifact({
        id: 'html-' + Date.now(),
        type: 'html',
        title: 'Basit Web Sayfası',
        language: 'html',
        content: `<!DOCTYPE html>
<html>
<head>
    <title>Önizleme</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; }
        h1 { color: #6a11cb; }
        button { background: #2575fc; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Merhaba, Nova!</h1>
    <p>Bu, iframe içinde çalışan bir önizlemedir.</p>
    <button onclick="alert('Tıkladın!')">Bana Tıkla</button>
</body>
</html>`
    });
}