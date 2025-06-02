// Configurações globais
let serverUrl = "http://192.168.0.2:11434/api/generate";
let modelName = "drbycrr-model:latest";
let isConnected = true;

// Elementos DOM
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const settingsButton = document.getElementById('settingsButton');
const settingsPanel = document.getElementById('settingsPanel');
const closeSettings = document.getElementById('closeSettings');
const serverUrlInput = document.getElementById('serverUrl');
const modelNameInput = document.getElementById('modelName');
const saveSettingsBtn = document.getElementById('saveSettings');
const testConnectionBtn = document.getElementById('testConnection');
const statusIndicator = document.getElementById('statusIndicator');

// Função para verificar o status do servidor
async function checkServerStatus() {
    try {
        const response = await fetch('/status');
        if (response.ok) {
            const data = await response.json();
            serverUrl = data.ollama_url;
            modelName = data.ollama_model;
            isConnected = data.ollama_connected; // Já está correto, usando ollama_connected
            
            // Atualizar os campos de configuração
            serverUrlInput.value = serverUrl;
            modelNameInput.value = modelName;
            
            // Atualizar o indicador de status
            updateStatusIndicator(isConnected);
            
            // Adicionar mensagem de sistema com informações de conexão
            const statusMessage = isConnected 
                ? `Conectado ao servidor Ollama em ${serverUrl} usando o modelo ${modelName}` 
                : `Não foi possível conectar ao servidor Ollama em ${serverUrl}. Verifique as configurações.`;
            
            addMessage('sistema', statusMessage);
            return data;
        } else {
            throw new Error('Falha ao verificar o status do servidor');
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        updateStatusIndicator(false);
        addMessage('sistema', 'Erro ao conectar com o servidor. Verifique se o servidor está em execução.', true);
        return null;
    }
}

// Função para atualizar o indicador de status
function updateStatusIndicator(isOnline) {
    if (isOnline) {
        statusIndicator.classList.remove('offline');
        statusIndicator.classList.add('online');
    } else {
        statusIndicator.classList.remove('online');
        statusIndicator.classList.add('offline');
    }
}

// Função para testar a conexão com o servidor Ollama
async function testConnection() {
    const url = serverUrlInput.value;
    addMessage('sistema', `Testando conexão com ${url}...`);
    
    try {
        const response = await fetch('/config/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ollama_url: url
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage('sistema', `Conexão bem-sucedida com ${url}`);
            updateStatusIndicator(true);
        } else {
            addMessage('sistema', `Falha na conexão com ${url}: ${data.error}`, true);
            updateStatusIndicator(false);
        }
    } catch (error) {
        console.error('Erro ao testar conexão:', error);
        addMessage('sistema', `Erro ao testar conexão: ${error.message}`, true);
        updateStatusIndicator(false);
    }
}

// Função para enviar mensagem
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Limpar o campo de entrada
    userInput.value = '';
    
    // Adicionar mensagem do usuário ao chat
    addMessage('user', message);
    
    // Mostrar indicador de digitação
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        // Remover indicador de digitação
        removeTypingIndicator();
        
        if (response.ok) {
            const data = await response.json();
            addMessage('bot', data.response);
        } else {
            const errorData = await response.json();
            addMessage('sistema', `Erro: ${errorData.error}`, true);
            console.error('Erro na resposta:', errorData);
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('sistema', 'Erro ao se comunicar com o servidor. Verifique sua conexão.', true);
        console.error('Erro ao enviar mensagem:', error);
    }
}

// Função para adicionar mensagem ao chat
function addMessage(sender, content, isError = false) {
    const messageDiv = document.createElement('div');
    
    if (sender === 'sistema') {
        messageDiv.className = isError ? 'system-message error' : 'system-message';
        messageDiv.textContent = content;
    } else {
        messageDiv.className = `message ${sender}`;
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.textContent = sender === 'user' ? 'Você' : 'Assistente';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Funções para indicador de digitação
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'dots';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dotsDiv.appendChild(dot);
    }
    
    typingDiv.appendChild(dotsDiv);
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Função para alternar a visibilidade do painel de configurações
function toggleSettings() {
    settingsPanel.classList.toggle('visible');
}

// Função para salvar configurações
async function saveSettings() {
    const newServerUrl = serverUrlInput.value.trim();
    const newModelName = modelNameInput.value.trim();
    
    if (!newServerUrl || !newModelName) {
        addMessage('sistema', 'Por favor, preencha todos os campos de configuração.', true);
        return;
    }
    
    try {
        const response = await fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ollama_url: newServerUrl,
                ollama_model: newModelName
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            serverUrl = newServerUrl;
            modelName = newModelName;
            
            addMessage('sistema', `Configurações atualizadas com sucesso! Usando ${modelName} em ${serverUrl}`);
            toggleSettings();
            
            // Verificar a conexão com as novas configurações
            await checkServerStatus();
        } else {
            const errorData = await response.json();
            addMessage('sistema', `Erro ao salvar configurações: ${errorData.error}`, true);
        }
    } catch (error) {
        console.error('Erro ao salvar configurações:', error);
        addMessage('sistema', 'Erro ao salvar configurações. Verifique sua conexão.', true);
    }
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

settingsButton.addEventListener('click', toggleSettings);
closeSettings.addEventListener('click', toggleSettings);
saveSettingsBtn.addEventListener('click', saveSettings);
testConnectionBtn.addEventListener('click', testConnection);

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar o status do servidor
    await checkServerStatus();
    
    // Adicionar mensagem de boas-vindas
    addMessage('bot', 'Olá! Sou o assistente virtual do Hospital Regional. Como posso ajudar você hoje?');
});