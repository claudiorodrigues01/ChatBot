# Assistente Hospitalar - Chatbot

## Descrição
Este projeto implementa um chatbot para assistência hospitalar utilizando o modelo de linguagem Ollama. O sistema consiste em uma interface web simples que se comunica com um servidor Ollama para processar perguntas e fornecer respostas relevantes ao contexto hospitalar.

## Funcionalidades
- Interface de chat amigável e responsiva
- Configuração flexível do servidor Ollama
- Indicador de status de conexão
- Persistência de configurações
- Suporte a diferentes modelos do Ollama

## Requisitos
- Python 3.6+
- Flask
- Servidor Ollama rodando (localmente ou em rede)
- Navegador web moderno

## Instalação

1. Clone este repositório:
```
git clone https://github.com/seu-usuario/assistente-hospitalar.git
cd assistente-hospitalar
```

2. Instale as dependências:
```
pip install flask requests
```

3. Certifique-se de ter o Ollama instalado e rodando com o modelo desejado.

## Uso

1. Inicie o servidor Flask:
```
python app.py
```

2. Acesse a interface web através do navegador:
```
http://localhost:5000
```

3. Para acessar de outros dispositivos na mesma rede, use o endereço IP do servidor:
```
http://[IP-DO-SERVIDOR]:5000
```

## Configuração

### Configuração do Servidor Ollama
Por padrão, o sistema tenta se conectar ao servidor Ollama na rede local. Você pode alterar a URL do servidor e o modelo através da interface de configurações no canto superior direito da tela.

### Acesso em Rede
Para permitir acesso de outros dispositivos na rede:
1. Verifique se o Firewall está permitindo conexões na porta 5000
2. Adicione uma regra de entrada para permitir conexões TCP na porta 5000

## Estrutura do Projeto
- `app.py`: Servidor Flask e lógica de backend
- `index.html`: Interface principal do chatbot
- `script.js`: Lógica de frontend e comunicação com o backend
- `style.css`: Estilos da interface
- `config.json`: Arquivo de configuração persistente (gerado automaticamente)

## Solução de Problemas

### O chatbot não está acessível de outros dispositivos na rede
- Verifique se o servidor está rodando com `host='0.0.0.0'`
- Confirme que o firewall permite conexões na porta 5000
- Verifique se está usando o endereço IP correto do servidor

### Não consegue conectar ao servidor Ollama
- Verifique se o servidor Ollama está em execução
- Confirme que a URL do servidor Ollama está correta
- Verifique se o modelo especificado está disponível no servidor Ollama

## Segurança
Este projeto é destinado para uso em redes locais confiáveis. Para implantação em ambientes de produção, considere:
- Implementar autenticação de usuários
- Utilizar HTTPS
- Configurar um proxy reverso (como Nginx ou Apache)
- Implementar limitação de taxa de requisições

## Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.