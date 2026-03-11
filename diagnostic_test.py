import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from qasync import QEventLoop
import logging

# Configuração básica de log para o teste
logging.basicConfig(level=logging.INFO)

async def test_logic():
    print("Iniciando teste de diagnóstico de loop e linha de comando...")
    
    # 1. Simular o que acontece no atalho
    print("Passo 1: Simulando disparo de atalho via QTimer (Main Thread)...")
    
    def simulate_shortcut_trigger():
        print("Atalho disparado! Agendando processamento no loop...")
        # Simula o redirecionamento que fiz no código (on_read_clipboard -> singleShot)
        asyncio.ensure_future(delayed_work())

    async def delayed_work():
        print("Trabalho assíncrono iniciado com sucesso no loop principal!")
        print("Teste concluído com sucesso. O loop está respondendo corretamente.")
        QApplication.quit()

    QTimer.singleShot(500, simulate_shortcut_trigger)
    print("Aguardando disparo do Timer...")

def run_diagnostic():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        loop.create_task(test_logic())
        loop.run_forever()

if __name__ == "__main__":
    run_diagnostic()
