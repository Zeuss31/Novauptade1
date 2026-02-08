/**
 * RASTGELE TEMA DEĞİŞTİRİCİ
 * Her tıkta tamamen farklı tasarım
 */

const themes = [
    {
        name: "Modern Dark",
        styles: {
            body: "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
            chatContainer: "background: rgba(255,255,255,0.95); border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);",
            userMessage: "background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 18px 18px 5px 18px; box-shadow: 0 4px 15px rgba(102,126,234,0.4);",
            aiMessage: "background: #f8f9fa; color: #333; border-radius: 18px 18px 18px 5px; border-left: 4px solid #667eea;",
            input: "border: 2px solid #667eea; border-radius: 25px; padding: 15px 20px; font-size: 16px;",
            button: "background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 25px; padding: 12px 30px; font-weight: bold; box-shadow: 0 4px 15px rgba(102,126,234,0.4);",
            header: "background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 20px 20px 0 0;"
        }
    },
    {
        name: "Neon Cyberpunk",
        styles: {
            body: "background: #0a0e27; background-image: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,0,255,0.05) 2px, rgba(255,0,255,0.05) 4px);",
            chatContainer: "background: rgba(10,14,39,0.9); border: 2px solid #ff00ff; border-radius: 0; box-shadow: 0 0 50px rgba(255,0,255,0.5), inset 0 0 50px rgba(0,255,255,0.1);",
            userMessage: "background: rgba(255,0,255,0.2); color: #ff00ff; border: 1px solid #ff00ff; border-radius: 0; box-shadow: 0 0 20px rgba(255,0,255,0.5); font-family: 'Courier New', monospace;",
            aiMessage: "background: rgba(0,255,255,0.2); color: #00ffff; border: 1px solid #00ffff; border-radius: 0; box-shadow: 0 0 20px rgba(0,255,255,0.5); font-family: 'Courier New', monospace;",
            input: "background: rgba(0,0,0,0.5); border: 2px solid #ff00ff; color: #ff00ff; border-radius: 0; padding: 15px; font-family: 'Courier New', monospace;",
            button: "background: transparent; color: #00ffff; border: 2px solid #00ffff; border-radius: 0; padding: 12px 30px; font-family: 'Courier New', monospace; box-shadow: 0 0 20px rgba(0,255,255,0.5);",
            header: "background: rgba(0,0,0,0.8); color: #ff00ff; padding: 20px; border: 2px solid #ff00ff; border-bottom: none; font-family: 'Courier New', monospace; text-shadow: 0 0 10px #ff00ff;"
        }
    },
    {
        name: "Soft Pastel",
        styles: {
            body: "background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);",
            chatContainer: "background: white; border-radius: 30px; box-shadow: 0 10px 40px rgba(252,182,159,0.3);",
            userMessage: "background: linear-gradient(135deg, #ff9a9e, #fecfef); color: white; border-radius: 25px 25px 5px 25px; box-shadow: 0 3px 10px rgba(255,154,158,0.3);",
            aiMessage: "background: linear-gradient(135deg, #a1c4fd, #c2e9fb); color: #333; border-radius: 25px 25px 25px 5px; box-shadow: 0 3px 10px rgba(161,196,253,0.3);",
            input: "border: 2px solid #ff9a9e; border-radius: 30px; padding: 15px 25px; background: rgba(255,255,255,0.8);",
            button: "background: linear-gradient(135deg, #ff9a9e, #fecfef); color: white; border-radius: 30px; padding: 12px 35px; font-weight: 600;",
            header: "background: linear-gradient(135deg, #ff9a9e, #fecfef); color: white; padding: 25px; border-radius: 30px 30px 0 0;"
        }
    },
    {
        name: "Terminal Hacker",
        styles: {
            body: "background: #000000;",
            chatContainer: "background: #0c0c0c; border: 1px solid #00ff00; border-radius: 0; box-shadow: 0 0 20px rgba(0,255,0,0.3);",
            userMessage: "background: transparent; color: #00ff00; border-left: 3px solid #00ff00; border-radius: 0; padding-left: 15px; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff00;",
            aiMessage: "background: transparent; color: #00ff00; border-left: 3px solid #00ff00; border-radius: 0; padding-left: 15px; font-family: 'Courier New', monospace; opacity: 0.8;",
            input: "background: #000; border: 1px solid #00ff00; color: #00ff00; border-radius: 0; padding: 15px; font-family: 'Courier New', monospace;",
            button: "background: transparent; color: #00ff00; border: 2px solid #00ff00; border-radius: 0; padding: 12px 30px; font-family: 'Courier New', monospace; text-transform: uppercase;",
            header: "background: #000; color: #00ff00; padding: 20px; border-bottom: 1px solid #00ff00; font-family: 'Courier New', monospace; text-transform: uppercase;"
        }
    },
    {
        name: "Glassmorphism",
        styles: {
            body: "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
            chatContainer: "background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);",
            userMessage: "background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);",
            aiMessage: "background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); color: white; border: 1px solid rgba(255,255,255,0.25); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);",
            input: "background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); color: white; border-radius: 15px; padding: 15px;",
            button: "background: rgba(255,255,255,0.25); backdrop-filter: blur(10px); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 15px; padding: 12px 30px; font-weight: 600;",
            header: "background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); color: white; padding: 20px; border-radius: 20px 20px 0 0; border-bottom: 1px solid rgba(255,255,255,0.2);"
        }
    },
    {
        name: "Retro 80s",
        styles: {
            body: "background: linear-gradient(180deg, #ff6ec4 0%, #7873f5 100%); background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255,255,255,0.1) 50px, rgba(255,255,255,0.1) 51px);",
            chatContainer: "background: #2d2d44; border: 5px solid #ff6ec4; border-radius: 10px; box-shadow: 10px 10px 0 #7873f5;",
            userMessage: "background: #ff6ec4; color: #2d2d44; border-radius: 0; padding: 15px; font-family: 'Arial Black', sans-serif; box-shadow: 5px 5px 0 #7873f5;",
            aiMessage: "background: #7873f5; color: white; border-radius: 0; padding: 15px; font-family: 'Arial Black', sans-serif; box-shadow: 5px 5px 0 #ff6ec4;",
            input: "background: #2d2d44; border: 3px solid #ff6ec4; color: #ff6ec4; border-radius: 0; padding: 15px; font-family: 'Arial Black', sans-serif;",
            button: "background: #ff6ec4; color: #2d2d44; border: 3px solid #7873f5; border-radius: 0; padding: 15px 30px; font-family: 'Arial Black', sans-serif; box-shadow: 5px 5px 0 #7873f5; text-transform: uppercase;",
            header: "background: #2d2d44; color: #ff6ec4; padding: 20px; border-bottom: 5px solid #ff6ec4; font-family: 'Arial Black', sans-serif; text-transform: uppercase;"
        }
    }
];

let currentThemeIndex = 0;

function applyTheme(theme) {
    // Body
    document.body.setAttribute('style', theme.styles.body);
    
    // Chat container
    const chatContainer = document.querySelector('.chat-container, .container, #chatContainer');
    if (chatContainer) chatContainer.setAttribute('style', theme.styles.chatContainer);
    
    // User messages
    document.querySelectorAll('.user-message, .message-user').forEach(el => {
        el.setAttribute('style', theme.styles.userMessage);
    });
    
    // AI messages
    document.querySelectorAll('.ai-message, .message-ai, .assistant-message').forEach(el => {
        el.setAttribute('style', theme.styles.aiMessage);
    });
    
    // Input
    const input = document.querySelector('input[type="text"], textarea, #messageInput');
    if (input) input.setAttribute('style', theme.styles.input);
    
    // Buttons
    document.querySelectorAll('button').forEach(btn => {
        btn.setAttribute('style', theme.styles.button);
    });
    
    // Header
    const header = document.querySelector('header, .header, #header');
    if (header) header.setAttribute('style', theme.styles.header);
    
    // Toast notification
    showThemeToast(theme.name);
}

function showThemeToast(themeName) {
    // Remove old toast
    const oldToast = document.getElementById('themeToast');
    if (oldToast) oldToast.remove();
    
    // Create toast
    const toast = document.createElement('div');
    toast.id = 'themeToast';
    toast.innerHTML = `Tema: ${themeName}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

function randomTheme() {
    currentThemeIndex = Math.floor(Math.random() * themes.length);
    applyTheme(themes[currentThemeIndex]);
}

function nextTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    applyTheme(themes[currentThemeIndex]);
}

// CSS animations
const style = document.createElement('style');
style.innerHTML = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    
    button:hover {
        transform: translateY(-2px);
        transition: all 0.3s;
    }
`;
document.head.appendChild(style);

// Sayfa yüklendiğinde tema değiştirme butonunu ekle
window.addEventListener('DOMContentLoaded', () => {
    const themeButton = document.createElement('button');
    themeButton.innerHTML = '🎨 Rastgele Tema';
    themeButton.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9998;
        cursor: pointer;
    `;
    themeButton.onclick = randomTheme;
    document.body.appendChild(themeButton);
    
    console.log('🎨 Tema değiştirici hazır! Butona tıkla veya randomTheme() çağır.');
});