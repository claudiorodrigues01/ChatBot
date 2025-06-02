from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import socket
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')

# Configuração do Ollama - URL padrão que pode ser alterada via interface
OLLAMA_URL = 'http://localhost:5000/api/generate'  # Alterado para localhost como padrão
# Modelo padrão
OLLAMA_MODEL = 'drbycrr-model:latest'

# Função para obter o endereço IP local da máquina
def get_local_ip():
    try:
        # Cria um socket para determinar qual interface de rede está sendo usada para conexão externa
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Não precisa ser um endereço alcançável
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"Erro ao obter IP local: {e}")
        return "127.0.0.1"  # Fallback para localhost

# Função para verificar se um host está acessível
def check_host_availability(host, port=11434, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/test')
def test_page():
    return send_from_directory('.', 'test.html')

@app.route('/status')
def status():
    # Retorna informações sobre o status do servidor e configurações atuais
    local_ip = get_local_ip()
    
    # Extrair o host do OLLAMA_URL
    ollama_host = OLLAMA_URL.split('://')[-1].split(':')[0]
    ollama_available = check_host_availability(ollama_host)
    
    return jsonify({
        'status': 'online',
        'server_ip': local_ip,
        'server_port': 5000,
        'ollama_url': OLLAMA_URL,
        'ollama_model': OLLAMA_MODEL,
        'ollama_connected': ollama_available  # Renomeado para corresponder ao que o frontend espera
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'response': 'Por favor, envie uma mensagem válida.'}), 400

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": user_message,
        "stream": False
    }

    try:
        # Aumentado o timeout para 60 segundos para lidar com redes mais lentas
        logger.info(f"Enviando requisição para Ollama: {OLLAMA_URL}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return jsonify({'response': data.get('response', 'Sem resposta do modelo.')})

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão com o Ollama: {e}")
        return jsonify({
            'response': f'Não foi possível conectar ao servidor Ollama em {OLLAMA_URL}. '
                      f'Verifique se o endereço está correto e se o servidor Ollama está em execução.'
        }), 503
    
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout na conexão com o Ollama: {e}")
        return jsonify({
            'response': 'O servidor Ollama demorou muito para responder. '
                      'Tente novamente mais tarde ou verifique a conexão de rede.'
        }), 504
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para o Ollama: {e}")
        return jsonify({
            'response': f'Erro ao comunicar com o servidor Ollama: {str(e)}. '
                      f'Verifique as configurações e tente novamente.'
        }), 500

# Rota para configurar a URL do Ollama remotamente
@app.route('/config', methods=['POST'])
def update_config():
    global OLLAMA_URL, OLLAMA_MODEL
    data = request.json
    
    # Aceitar tanto 'url' quanto 'ollama_url' para compatibilidade
    if 'ollama_url' in data:
        OLLAMA_URL = data['ollama_url']
    elif 'url' in data:
        OLLAMA_URL = data['url']
    
    # Aceitar tanto 'model' quanto 'ollama_model' para compatibilidade
    if 'ollama_model' in data:
        OLLAMA_MODEL = data['ollama_model']
    elif 'model' in data:
        OLLAMA_MODEL = data['model']
    
    # Salva as configurações em um arquivo para persistência
    try:
        with open('config.json', 'w') as f:
            json.dump({
                'ollama_url': OLLAMA_URL,
                'ollama_model': OLLAMA_MODEL
            }, f)
        logger.info(f"Configurações atualizadas: URL={OLLAMA_URL}, Modelo={OLLAMA_MODEL}")
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {e}")
    
    return jsonify({
        'status': 'success',
        'current_url': OLLAMA_URL,
        'current_model': OLLAMA_MODEL
    })

# Rota para testar a conexão com o servidor Ollama
@app.route('/config/test', methods=['POST'])
def test_connection():
    data = request.json
    test_url = data.get('ollama_url', OLLAMA_URL)
    
    # Extrair o host do URL de teste
    try:
        host = test_url.split('://')[-1].split(':')[0]
        is_available = check_host_availability(host)
        
        if is_available:
            return jsonify({
                'success': True,
                'message': f'Conexão bem-sucedida com {host}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Não foi possível conectar ao servidor em {host}'
            })
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao testar conexão: {str(e)}'
        })

# Carrega configurações salvas anteriormente, se existirem
def load_config():
    global OLLAMA_URL, OLLAMA_MODEL
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                OLLAMA_URL = config.get('ollama_url', OLLAMA_URL)
                OLLAMA_MODEL = config.get('ollama_model', OLLAMA_MODEL)
                logger.info(f"Configurações carregadas: URL={OLLAMA_URL}, Modelo={OLLAMA_MODEL}")
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")

# Função para verificar se a porta está aberta para conexões externas
def check_port_accessibility(port=5000):
    try:
        # Tenta criar um socket e vinculá-lo a todas as interfaces na porta especificada
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))
        s.close()
        # Se conseguir vincular, significa que a porta não está em uso
        return False
    except socket.error:
        # Se não conseguir vincular, a porta pode estar em uso (pelo nosso servidor)
        # ou bloqueada por outro processo
        return True

if __name__ == '__main__':
    # Carrega configurações salvas
    load_config()
    
    # Exibe informações úteis no console
    local_ip = get_local_ip()
    print(f"\n=== Assistente Hospitalar ===")
    print(f"Servidor web rodando em: http://{local_ip}:5000")
    print(f"Servidor também acessível em: http://0.0.0.0:5000")
    print(f"Servidor Ollama configurado em: {OLLAMA_URL}")
    print(f"Modelo atual: {OLLAMA_MODEL}")
    print(f"===========================")
    
    # Verificar se o servidor Ollama está acessível
    ollama_host = OLLAMA_URL.split('://')[-1].split(':')[0]
    if check_host_availability(ollama_host):
        print(f"Servidor Ollama está acessível em {ollama_host}")
    else:
        print(f"AVISO: Servidor Ollama não está acessível em {ollama_host}")
        print(f"Verifique se o servidor Ollama está em execução e se o endereço está correto.")
    
    print("")
    print("IMPORTANTE: Para acessar o chatbot de outras máquinas na rede:")
    print("1. Verifique se o Firewall do Windows está permitindo conexões na porta 5000")
    print("2. Para permitir conexões, abra o Firewall do Windows e adicione uma regra de entrada")
    print("   para permitir conexões TCP na porta 5000")
    print("3. Acesse o chatbot de outras máquinas usando: http://" + local_ip + ":5000")
    print("")
    
    # Permitir conexões de qualquer endereço na rede
    app.run(host='0.0.0.0', port=5000, debug=True)
