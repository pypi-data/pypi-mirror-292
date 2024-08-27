import base64
import asyncio


from vocalize.conversation import Role, Message
from vocalize.conversation.conversation import CustomConversation, Conversation, Roles
from vocalize.conversation.built_in import Llama3Conversation
from vocalize.llm.config import LLMConfig
from vocalize.llm.llm import LocalLLM
from vocalize.phone.call import TwilioCall
from vocalize.stt.deepgram import Deepgram, DeepgramConfig, DeepgramTranscription
import typing
from vocalize.flow import Flow
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from vocalize.tts.eleven_labs import ElevenLabsConfig, ElevenLabs
from pyinstrument import Profiler
from loguru import logger

load_dotenv()
app = FastAPI()

PROFILING = True  # Set this from a settings model


async def send_message_to_database(message: Message):
    await asyncio.sleep(1)
    logger.debug(f"Finished fake sending message to database: {message}")

async def add_continuation_to_previous_message_in_database(message: Message):
    await asyncio.sleep(1)
    logger.debug(f"Finished fake adding continuation to previous message in database: {message}")

class Llama3ConversationSqlAlchemy(Llama3Conversation):
    async def add_message(self, role: Role, content: str) -> None:
        if self.is_continuation(role):
            self.messages[-1].content += f" {content}"
            message_with_continuation = self.messages[-1]
            asyncio.create_task(add_continuation_to_previous_message_in_database(message_with_continuation))
            return None
        new_message = Message(role=role, content=content)
        asyncio.create_task(send_message_to_database(new_message))
        self.messages.append(new_message)



async def deepgram_exporter(transcription: DeepgramTranscription):
    logger.debug(f"Exporting transcription: {transcription}")

@app.websocket("/phone_call")
async def phone_call(websocket: WebSocket) -> None:
    await websocket.accept()

    is_call_connected = asyncio.Event()
    is_call_connected.set()

    user_role = Role(name="user", replace_with="user", metadata={'id': '1'})
    system_role = Role(name="system", replace_with="system")
    assistant_role = Role(name="assistant", replace_with="assistant", metadata={'id': '2'})
    roles = Roles(user=user_role, system=system_role, assistant=assistant_role)

    conversation = Llama3ConversationSqlAlchemy(roles=roles)
    await conversation.add_message(
        role=system_role, content="SYSTEM: Solar Sales Call. AGENT_INFORMATION: First Name: John Company Name: The Clean Energy Initiative Company Information: the company is called The Clean Energy Initiative the company is a non profit organization the company partners with local solar companies to help homeowners make the switch to solar with no upfront cost. Current Date: Sunday, 11/10/2024 PROSPECT_INFORMATION: First Name: Emily House Number: 146"
    )

    call = TwilioCall(websocket=websocket, debug=True, conversation=conversation)

    deepgram_config = DeepgramConfig(
       interim_results=True,
       endpointing=0
    )

    stt = Deepgram(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        is_call_connected=is_call_connected,
        debug=True,
        config=deepgram_config,
        user_role=user_role,
        conversation=conversation,
    )

    llm_config = LLMConfig(
        generation_max_tokens=20,
        stopping_tokens=["<|eot_id|>"],
        turn_max_tokens=400,
    )

    llm = LocalLLM(
        protocol="http",
        config=llm_config,
        slug=None,
        host="192.168.1.21",
        port=8000,
        is_call_connected=is_call_connected,
        debug=True,
        conversation=conversation,
    )

    tts_config = ElevenLabsConfig(
        optimize_streaming_latency=3,
        stability=0.7,
        voice_id="z9fAnlkpzviPz146aGWa",
        output_format="ulaw_8000",
        similarity_boost=0.75,
        use_speaker_boost=True,
        model="eleven_monolingual_v1",
        style=0,
        chunk_length_schedule=[50, 150, 250, 350],
    )

    tts = ElevenLabs(is_call_connected=is_call_connected, config=tts_config, api_key=os.environ["TTS_API_KEY"], debug=True)

    flow = Flow(
        input=call,
        stt=stt,
        llm=llm,
        tts=tts,
        output=call,
        roles=roles,
        debug=True,
        benchmarking=True,
    )

    print("starting flow")
    await flow.start()
    print("flow ended")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(host="127.0.0.1", port=8000, app="example:app", reload=False)
    print("after uvicorn")

 