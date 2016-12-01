#!/usr/bin/python
"""Commands for bot."""
import conduit

ECHO_CMD = "echo"
HELP_CMD = "help"
CHAT_CMD = "chat"
DEBUG_CMD = "debug"
ALIVE_CMD = "alive"
DEBUG_CMDS = [ECHO_CMD, CHAT_CMD, DEBUG_CMD]
ALL_CMDS = [HELP_CMD, ALIVE_CMD]


class Context(object):
    """Context for executing commands."""

    CONPH = "conph"
    ROOM_PHID = "room_phid"
    BOT_USER_PHID = "bot_user_phid"
    BOT_USER = "bot_user"
    LAST_TRANS = "last_transactions."
    CHATBOT = "chatbot"
    DEBUG = "debug"
    FACTORY = "factory"

    def __init__(self, factory):
        """init instance."""
        self.cache = {}
        self.cache[Context.DEBUG] = False
        self.cache[Context.FACTORY] = factory
        self.factory_obj(Context.CONPH, conduit.Conpherence)

    def get(self, key):
        """get a value."""
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def set(self, key, val):
        """set a value."""
        self.cache[key] = val

    def factory_obj(ctx, key, obj_type):
        """Get (or create -> get) a factory-backed object."""
        obj = ctx.get(key)
        if obj is None:
            obj = ctx.get(Context.FACTORY).create(obj_type)
            ctx.set(key, obj)
        return obj


def _updatethread(ctx, room_id, msg):
    """Update a conpherence thread."""
    ctx.get(Context.CONPH).updatethread(room_id, msg)


def _create_chatbot():
    """Create a chatbot."""
    from chatterbot import ChatBot
    chat = ChatBot("chatbot",
                   trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
    chat.train("chatterbot.corpus.english")
    return chat


def execute(command, parameters, room_id, ctx, debugging):
    """Execute a command."""
    try:
        cmd = command
        debug = ctx.get(Context.DEBUG)
        if not debug and command in DEBUG_CMDS:
            cmd = HELP_CMD
        if cmd == ECHO_CMD:
            _updatethread(ctx, room_id, " ".join(parameters))
        elif cmd == CHAT_CMD:
            chatty = ctx.get(Context.CHATBOT)
            if chatty is None:
                chatty = _create_chatbot()
                ctx.set(Context.CHATBOT, chatty)
            if len(parameters) == 0:
                resp = "/silence"
            else:
                resp = chatty.get_response(" ".join(parameters))
            _updatethread(ctx, room_id, str(resp))
        elif command == DEBUG_CMD and debugging:
            ctx.set(Context.DEBUG, not debug)
            _updatethread(ctx, room_id, "debug mode toggled")
        elif cmd == ALIVE_CMD:
            _updatethread(ctx, room_id, "yes")
        else:
            use_cmds = ALL_CMDS
            if debug:
                use_cmds += DEBUG_CMDS
            _updatethread(ctx,
                          room_id,
                          "available: " + ",".join(sorted(use_cmds)))
    except Exception as e:
        _updatethread(ctx, room_id, str(e))