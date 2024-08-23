from dataclasses import dataclass

@dataclass
class MessagesHandlers:
    TEXT: bool = False
    CAPTION : bool = False
    DOCUMENT: bool = False
    AUDIO: bool = False
    VIDEO: bool = False
    VOICE: bool = False
    STICKER: bool = False
    CONTACT: bool = False
    LOCATION: bool = False
    REPLY : bool = False
    POLL: bool = False
    NEW_CHAT_MEMBERS: bool = False
    LEFT_CHAT_MEMBER: bool = False
    NEW_CHAT_TITLE: bool = False
    NEW_CHAT_PHOTO: bool = False
    MESSAGE_AUTO_DELETE_TIMER_CHANGED : bool = False
    PINNED_MESSAGE : bool = False
    ALLSTATUS : bool = False


@dataclass
class HANDLERS:
    commands : dict = None
    messages : MessagesHandlers = None
    callback : str = None
    inline : str = None
    join_request : str = None
    reaction : str = None
    error : str = None


