The flow should have a debug mode that keeps track of execution and response time for each step. For example: it should log how long it takes to the LLM text completion and get an audio response from TTS provider. This will better track latency bottlenecks and the user will be able to choose better providers.


Needed Documentation:
1. Interrupter.cancellable usage and coroutines
2. Roadmap and upcoming features
3. Where things happen in flow EX: user message is added in STT