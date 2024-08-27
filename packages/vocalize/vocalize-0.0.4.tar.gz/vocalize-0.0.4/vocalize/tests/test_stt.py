from vocalize.stt.deepgram import DeepgramConfig, DeepgramTranscriber
import os
import pytest
from loguru import logger

@pytest.mark.asyncio
async def test_deepgram_transcriber():
    config = DeepgramConfig(encoding='linear16', sample_rate=16000)
    transcriber = DeepgramTranscriber(api_key=os.environ['STT_API_KEY'], config=config)
    await transcriber.connect()
    with open('vocalize/tests/sample_data/audio.wav', 'rb') as f:
        data = f.read()
        await transcriber.add_audio(data)
        transcription = await transcriber.get_transcription()
        logger.debug(f"{transcription=}")
        assert transcription.get_text() == "hi"
        await transcriber.close()
    