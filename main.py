import sys
import os
import asyncio
import keyboard
import pyperclip
import logging
import shutil
import time
import re
import winshell
from win32com.client import Dispatch
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from qasync import QEventLoop, asyncSlot

# Robust path handling for relative components
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Logging Setup
LOG_FILE = os.path.join(BASE_PATH, "app.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Redirect standard output and error to the log file for background execution
# Doing this as early as possible to capture import errors
try:
    # Use 'a' for append, and ensure it's written immediately (buffering=1)
    log_stream = open(LOG_FILE, 'a', encoding='utf-8', buffering=1)
    sys.stdout = log_stream
    sys.stderr = log_stream
    logging.info("Redirecionamento de output configurado.")
except Exception as e:
    logging.error(f"Erro ao configurar redirecionamento: {e}")

from tts_engine import TTSEngine
from audio_player import AudioPlayer
from ui_overlay import UIOverlay

class ShortcutSignals(QObject):
    """Signals to bridge between keyboard thread and main UI thread."""
    trigger_selection = pyqtSignal()
    trigger_clipboard = pyqtSignal()

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.tts = TTSEngine()
        self.player = AudioPlayer()
        self.overlay = UIOverlay()
        
        # Paths based on script location
        self.base_path = BASE_PATH
        
        self.temp_audio = os.path.join(self.base_path, "temp_speech.mp3")
        self.last_text = ""
        self.current_tts_task = None

        # Thread-safe signals
        self.shortcut_signals = ShortcutSignals()
        self.shortcut_signals.trigger_selection.connect(self._handle_selection_shortcut)
        self.shortcut_signals.trigger_clipboard.connect(self.process_clipboard_and_read)

        self.setup_tray()
        self.setup_shortcuts()
        self.connect_signals()
        
        logging.info("Aplicativo iniciado.")

    def setup_tray(self):
        from PyQt6.QtWidgets import QStyle
        # Use a standard system icon instead of a theme icon which may not exist
        icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_DriveCDIcon)
        self.tray_icon = QSystemTrayIcon(icon, self.app)
        self.tray_icon.setToolTip("Leitor de Voz (Edge-TTS)\nCtrl+Alt+\\: Ler Seleção\nCtrl+Alt+Z: Ler Clipboard")
        
        menu = QMenu()
        
        # Action to show shortcuts legend
        help_action = QAction("Teclas de Atalho (Legenda)", menu)
        help_action.triggered.connect(self.show_help)
        menu.addAction(help_action)
        
        # Action for startup
        self.startup_action = QAction("Iniciar com o Windows", menu, checkable=True)
        self.startup_action.setChecked(self.is_startup_enabled())
        self.startup_action.triggered.connect(self.toggle_startup)
        menu.addAction(self.startup_action)
        
        # Action to open logs
        log_action = QAction("Ver Logs", menu)
        log_action.triggered.connect(self.open_logs)
        menu.addAction(log_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Sair", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Show initial notification
        self.tray_icon.showMessage(
            "Leitor de Voz Ativo",
            "Atalhos:\nCtrl+Alt+\\ (Selecionado)\nCtrl+Alt+Z (Clipboard)",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )

    def setup_shortcuts(self):
        # Register global shortcuts using 'keyboard'
        # Emitting a signal is thread-safe and will be queued for the main thread
        try:
            keyboard.add_hotkey('ctrl+alt+\\', self.shortcut_signals.trigger_selection.emit, suppress=True)
            keyboard.add_hotkey('ctrl+alt+z', self.shortcut_signals.trigger_clipboard.emit, suppress=True)
            logging.info("Atalhos registrados com sucesso (suprimidos).")
        except Exception as e:
            logging.error(f"Erro ao registrar atalhos: {e}")

    def connect_signals(self):
        self.overlay.play_clicked.connect(self.player.play)
        self.overlay.pause_clicked.connect(self.player.pause)
        self.overlay.rate_changed.connect(self.player.set_rate)
        self.overlay.save_btn.clicked.connect(self.save_audio)
        self.overlay.close_clicked.connect(self.stop_and_hide)
        self.overlay.seek_requested.connect(self.player.set_position)

        self.player.position_changed.connect(self._handle_player_update)
        self.player.duration_changed.connect(self._handle_player_update)
        self.player.state_changed.connect(self.on_player_state_changed)

    def _handle_player_update(self, param=None):
        pos = self.player.player.position()
        dur = self.player.player.duration()
        if dur > 0:
            self.overlay.update_progress(pos, dur)
        else:
            # If duration is not yet available, keep it at least showing position
            self.overlay.slider.setValue(pos)

    def on_player_state_changed(self, state):
        import PyQt6.QtMultimedia as QtMultimedia
        is_playing = state == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState
        self.overlay.set_playing(is_playing)

    def show_help(self):
        QMessageBox.information(
            None, 
            "Legenda de Atalhos", 
            "Ctrl + Alt + \\: Captura o texto selecionado (via Ctrl+C) e inicia a leitura.\n\n"
            "Ctrl + Alt + Z: Lê o conteúdo atual da Área de Transferência (Clipboard).\n\n"
            "Durante a leitura, use o painel flutuante para controlar a velocidade e salvar o áudio."
        )

    def open_logs(self):
        if os.path.exists(LOG_FILE):
            os.startfile(LOG_FILE)

    def save_audio(self):
        if os.path.exists(self.temp_audio):
            # Para garantir que o arquivo não está sendo usado pelo player
            self.player.stop()
            # Pequeno delay para o OS liberar o arquivo
            time.sleep(0.1)
            
            file_name, _ = QFileDialog.getSaveFileName(
                None, "Salvar Áudio", f"leitura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3", "Audio Files (*.mp3)"
            )
            if file_name:
                try:
                    shutil.copy2(self.temp_audio, file_name)
                    logging.info(f"Áudio salvo com sucesso em: {file_name}")
                    QMessageBox.information(None, "Sucesso", f"Áudio salvo em:\n{file_name}")
                except Exception as e:
                    logging.error(f"Erro ao salvar áudio: {e}")
                    QMessageBox.critical(None, "Erro", f"Não foi possível salvar o arquivo:\n{e}")

    def stop_and_hide(self):
        self.player.stop()
        self.overlay.hide()
        logging.info("Reprodução parada pelo usuário.")

    def _handle_selection_shortcut(self):
        logging.info("Atalho de seleção detectado. Aguardando liberação de teclas...")
        # Pequeno delay para garantir que Ctrl+Alt+\ foram soltos pelo usuário 
        # antes de enviarmos o Ctrl+C, evitando conflitos de 'AltGr'
        time.sleep(0.1)
        
        logging.info("Simulando Ctrl+C...")
        keyboard.press_and_release('ctrl+c')
        
        # Pequeno delay para o clipboard atualizar antes de processar
        QTimer.singleShot(400, self.process_clipboard_and_read)

    def process_clipboard_and_read(self):
        text = pyperclip.paste()
        if text:
            cleaned_text = self.clean_text(text)
            logging.info(f"Processando texto capturado ({len(text)} caracteres, limpo para {len(cleaned_text)}).")
            
            # Cancelar tarefa anterior se houver
            if self.current_tts_task and not self.current_tts_task.done():
                logging.info("Cancelando leitura anterior...")
                self.current_tts_task.cancel()
            
            # Forçar parada do áudio
            self.player.stop()
            
            # Iniciar nova leitura
            self.current_tts_task = asyncio.ensure_future(self.generate_and_play(cleaned_text))
        else:
            logging.warning("Área de transferência vazia.")

    def clean_text(self, text):
        """Removes Markdown and special formatting characters."""
        # Remover URLs
        text = re.sub(r'http\S+', '', text)
        # Remover headers Markdown (#)
        text = re.sub(r'#+\s*', '', text)
        # Remover negrito/itálico (**, *, __, _)
        text = re.sub(r'(\*\*|\*|__|_) (.*?)\1', r'\2', text)
        # Remover blocos de código
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remover links markdown [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        # Remover checklists [x] [ ]
        text = re.sub(r'\[[ xX]?\]\s*', '', text)
        # Remover caracteres residuais comuns de formatação
        text = re.sub(r'[`~>]', '', text)
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def generate_and_play(self, text):
        logging.info("Iniciando etapa de geração TTS...")
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()
        self.overlay.title_label.setText("Gerando áudio...")
        self.app.processEvents()
        
        success = await self.tts.generate_audio(text, self.temp_audio)
        
        if success:
            logging.info("Geração concluída. Carregando player...")
            self.overlay.title_label.setText("Lendo...")
            self.overlay.reset_progress()
            self.player.load(self.temp_audio)
            self.player.play()
            logging.info("Reprodução iniciada.")
        else:
            self.overlay.title_label.setText("Erro ao gerar áudio.")
            logging.error("Falha na geração do áudio pelo Edge-TTS.")

    def is_startup_enabled(self):
        startup_path = winshell.startup()
        shortcut_path = os.path.join(startup_path, "LeitorDeVoz.lnk")
        return os.path.exists(shortcut_path)

    def toggle_startup(self, enabled):
        startup_path = winshell.startup()
        shortcut_path = os.path.join(startup_path, "LeitorDeVoz.lnk")
        
        if enabled:
            try:
                # Usando pythonw.exe para execução silenciosa em segundo plano
                pythonw_path = os.path.join(self.base_path, "venv", "Scripts", "pythonw.exe")
                script_path = os.path.join(self.base_path, "main.py")
                
                logging.info(f"Tentando ativar inicialização silenciosa. Python: {pythonw_path}, Script: {script_path}")
                
                if not os.path.exists(pythonw_path):
                    logging.error(f"Erro: pythonw.exe não encontrado em {pythonw_path}")
                    self.startup_action.setChecked(False)
                    return

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = pythonw_path
                shortcut.Arguments = f'"{script_path}"'
                shortcut.WorkingDirectory = self.base_path
                shortcut.IconLocation = pythonw_path
                shortcut.save()
                logging.info(f"Inicialização com Windows em segundo plano ativada em: {shortcut_path}")
            except Exception as e:
                logging.error(f"Erro ao ativar inicialização: {e}")
                self.startup_action.setChecked(False)
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                logging.info("Inicialização com Windows desativada.")

    def quit_app(self):
        logging.info("Encerrando aplicativo.")
        self.tray_icon.hide()
        self.app.quit()
        sys.exit()

    def run(self):
        loop = QEventLoop(self.app)
        asyncio.set_event_loop(loop)
        with loop:
            loop.run_forever()

if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()
