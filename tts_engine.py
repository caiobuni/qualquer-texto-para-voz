import edge_tts
import asyncio
import os

class TTSEngine:
    def __init__(self, voice="pt-BR-FranciscaNeural", rate="+10%", pitch="+5Hz"):
        self.voice = voice
        self.rate = rate  # Slightly faster for a more natural conversational flow
        self.pitch = pitch # Slightly higher pitch for a relaxed tone

    async def generate_audio(self, text: str, output_path: str):
        """
        Generates an audio file from the given text using edge-tts.
        """
        if not text.strip():
            return False

        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Error generating TTS audio: {e}")
            return False

if __name__ == "__main__":
    # Test execution
    async def test():
        engine = TTSEngine()
        text = "Olá! Este é um teste do sistema de leitura de voz. Espero que esteja funcionando perfeitamente."
        output_file = "test_audio.mp3"
        print(f"Gerando áudio em {output_file}...")
        success = await engine.generate_audio(text, output_file)
        if success:
            print(f"Áudio gerado com sucesso!")
        else:
            print(f"Falha na geração do áudio.")

    asyncio.run(test())
