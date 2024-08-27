from typing import Iterable

from openai.types.chat import ChatCompletionMessageParam

from maitai_gen.chat import ChatCompletionMessage, ChatMessage


def openai_messages_to_proto(messages: Iterable[ChatCompletionMessageParam]):
    proto_messages: [ChatMessage] = []
    for message in messages:
        if isinstance(message, ChatMessage):
            proto_messages.append(message)
        elif isinstance(message, ChatCompletionMessage):
            proto_messages.append(ChatMessage().from_pydict(message.to_pydict()))
        else:
            proto_messages.append(
                ChatMessage().from_pydict(message)
            )
    return proto_messages
