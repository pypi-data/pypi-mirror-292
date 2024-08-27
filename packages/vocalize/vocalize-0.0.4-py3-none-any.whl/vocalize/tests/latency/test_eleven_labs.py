import pytest
import asyncio
from vocalize.tts import ElevenLabs, ElevenLabsConfig, ElevenVoices
from vocalize.tests.fixtures import load_env, initialize_skeleton
from vocalize.flow.events import Events
from vocalize.interrupter.interrupter import Interrupter
import os


# @pytest.mark.asyncio
# async def test_eleven_labs_latency(initialize_skeleton):
#     print("api key", os.environ["TTS_API_KEY"])
#     conversation, events, input_queue, output_queue, interrupter = initialize_skeleton
#     config = ElevenLabsConfig(
#         optimize_streaming_latency=3,
#         model="eleven_monolingual_v1",
#         output_format="ulaw_8000",
#         similarity_boost=0.7,
#         stability=0.7,
#         style=0,
#         use_speaker_boost=True,
#         voice_id=ElevenVoices.Grace.value,
#         chunk_length_schedule=[50, 150, 250, 350],
#     )

#     tts = ElevenLabs(
#         api_key=os.environ["TTS_API_KEY"],
#         is_call_connected=events.is_call_connected,
#         debug=True,
#         config=config,
#         events=events,
#         input_queue=input_queue,
#         output_queue=output_queue,
#         interrupter=interrupter,
#     )
#     await input_queue.put("this is a test message")
#     await input_queue.put(None)
#     start_task = asyncio.create_task(tts.start())
#     await asyncio.sleep(10)
#     tts.stop()
#     start_task.cancel()
#     raise NotImplementedError(
#         "This test has not been finished yet. We still need to get latency from Eleven Labs"
#     )


# asyncio.run(test_eleven_labs_latency(initialize_skeleton()))
