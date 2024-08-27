import pytest
import os

from vocalize.conversation import Conversation
from vocalize.conversation.role import Roles, Role
from vocalize.stt.deepgram import Deepgram, DeepgramConfig
import asyncio
import time

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_deepgram_latency():
    from dotenv import load_dotenv
    load_dotenv()
    roles = Roles(user=Role(name='user'), assistant=Role(name='assistant'), system=Role(name='system'))
    conversation = Conversation(roles=roles)
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    config = DeepgramConfig(
        encoding=None,
        sample_rate=None,
        endpointing=10,
        speech_final=True,
        model='nova-phonecall'
        )
    deepgram = Deepgram(
        api_key=os.environ['DEEPGRAM_API_KEY'], is_call_connected=False,
        config=config, conversation=conversation
        )
    deepgram.input_queue = input_queue
    deepgram.output_queue = output_queue
    websocket = await deepgram.connect()
    data = None
    with open('vocalize/tests/sample_data/audio.wav', 'rb') as f:
        data = f.read()
    first_half = data[: int(len(data) // 2)]
    second_half = data[int(len(data) // 2):]
    start_send_time = time.perf_counter()
    await websocket.send(first_half)
    await websocket.send(second_half)
    after_send_time = time.perf_counter()
    response = await websocket.recv()
    received_time = time.perf_counter()
    print(f"Time taken from starting send to receiving the transcription response: {received_time - start_send_time}")
    response_time = received_time - start_send_time
    await websocket.close()
    assert response_time < 0.8
