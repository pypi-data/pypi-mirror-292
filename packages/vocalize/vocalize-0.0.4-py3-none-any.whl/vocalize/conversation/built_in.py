from vocalize.conversation.message import Message
from vocalize.conversation.role import Role
from .conversation import CustomConversation, MessageMetadataType

def llama_3_formatter(messages: list[Message[MessageMetadataType]], assistant_role: Role):
    text = ''
    text += '<|begin_of_text|>'
    for message in messages:
        text += f"<|start_header_id|>{str(message.role)}<|end_header_id|>\n\n{message.content}<|eot_id|>"
    text += f"<|start_header_id|>{str(assistant_role)}<|end_header_id|>\n\n"
    return text

class Llama3Conversation(CustomConversation[MessageMetadataType]):

    def format(self):
        """
            random
        """
        text = llama_3_formatter(self.messages, self.roles.assistant)
        return text
        # text = ''
        # text += '<|begin_of_text|>'
        # for message in self.messages:
        #     text += f"<|start_header_id|>{str(message.role)}<|end_header_id|>\n\n{message.content}<|eot_id|>"
        # text += f"<|start_header_id|>{str(self.roles.assistant)}<|end_header_id|>\n\n"
        # return text

