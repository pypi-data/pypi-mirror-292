from vocalize.conversation.role import Roles, Role
from vocalize.llm import LocalLLM
from vocalize.conversation import Conversation
import pytest
import asyncio
import time
from functools import wraps


def timer(function, repeat: int = 100, *args, **kwargs):
    from statistics import mean
    @wraps(function)
    def wrapper(*args, **kwargs):
        durations = []
        for _ in range(repeat):
            time_start = time.perf_counter()
            result = function(*args, **kwargs)
            time_end = time.perf_counter()
            durations.append(time_end - time_start)

        print(f"{function.__name__} took an average of {mean(durations) * 1000} milliseconds")
        result = function(*args, **kwargs)
        return result

    return wrapper


@timer
def benchmark():
    roles = Roles(system=Role(name='system'), assistant=Role(name='assistant'), user=Role(name='user'))
    conversation = Conversation(roles=roles)
    llm = LocalLLM(
        is_call_connected=asyncio.Event(),
        host='192.168.1.14',
        port=8000,
        debug=True,
        protocol='http',
        slug='/llm',
        conversation=conversation
        )
    completion = 'Hello my name isHello my name isHello my name isHello my name isHello my name isHello my name is'
    stopping_tokens = ['USER', 'my']
    stopping_index = llm.find_first_stopping_token_index(stopping_tokens=stopping_tokens, completion=completion)


def test_find_stopping_index():
    print(f"name: {__name__}")
    benchmark()
    assert 1 == 1

def test_crop_completion():
    roles = Roles(system=Role(name='system'), assistant=Role(name='assistant'), user=Role(name='user'))
    conversation = Conversation(roles=roles)
    llm = LocalLLM(
        is_call_connected=asyncio.Event(),
        host='192.168.1.14',
        port=8000,
        debug=True,
        protocol='http',
        slug='/llm',
        conversation=conversation
        )
    cases = [{'completion': 'Hello my name is', 'result': 'Hello my name'}, 
             {'completion': 'Hey', 'result': 'Hey'}, {'completion': ' Hey', 'result': ' Hey'}, 
             {'completion': ' Hello my name is', 'result': ' Hello my name'}, 
             {'completion': '   ', 'result': '   '}, 
             {'completion': '  Hey how ', 'result': '  Hey'}]
    for case in cases:
        completion = case['completion']
        result = case['result']
        assert llm.crop_completion_if_spaces(completion=completion) == result

if __name__ == '__main__':
    test_crop_completion()
