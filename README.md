# 🎙️ Leitor de Voz (Edge-TTS)

Uma ferramenta leve, elegante e produtiva para Windows que transforma qualquer texto selecionado em áudio realista usando as vozes neurais do Microsoft Edge.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-v6.6+-green.svg)

## ✨ Funcionalidades

- **Seleção Instantânea**: Pressione um atalho e ouça o texto selecionado em qualquer programa (Navegador, PDF, Word, etc).
- **Vozes Neurais Realistas**: Utiliza a tecnologia `edge-tts` para vozes em português brasileiro com entonação natural.
- **Interface Flutuante (Overlay)**: Painel minimalista que aparece apenas durante a leitura com controles de:
    - Play/Pause.
    - Ajuste de velocidade em tempo real (0.5x até 2.0x).
    - Barra de progresso e cronômetro regressivo.
- **Leitura de Clipboard**: Atalho dedicado para ler o que estiver na sua área de transferência.
- **Exportação de Áudio**: Salve a leitura atual em um arquivo `.mp3` com um clique.
- **Início Automático**: Opção para iniciar junto com o Windows em segundo plano (System Tray).
- **Limpeza Inteligente**: Remove automaticamente links, sintaxe Markdown e caracteres especiais antes da leitura para uma experiência fluida.

## ⌨️ Atalhos de Teclado

| Ação | Atalho |
| :--- | :--- |
| **Ler Texto Selecionado** | `Ctrl` + `Alt` + `\` |
| **Ler Área de Transferência** | `Ctrl` + `Alt` + `Z` |

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior instalado.
- Windows 10/11.

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/qualquer-texto-para-voz.git
   cd qualquer-texto-para-voz
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```powershell
   python main.py
   ```
   *Para rodar em segundo plano sem janela de terminal:*
   ```powershell
   .\venv\Scripts\pythonw.exe main.py
   ```

## 🛠️ Tecnologias Utilizadas

- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)**: Interface gráfica moderna e responsiva.
- **[edge-tts](https://github.com/rany2/edge-tts)**: Interface Python para o serviço TTS do Microsoft Edge.
- **[keyboard](https://github.com/boppreh/keyboard)**: Captura de atalhos globais no sistema.
- **[pyperclip](https://github.com/asweigart/pyperclip)**: Manipulação da área de transferência.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido para facilitar a leitura e aumentar a produtividade. 🚀
