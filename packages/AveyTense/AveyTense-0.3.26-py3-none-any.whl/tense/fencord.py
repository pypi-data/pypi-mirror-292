"""
**TensePy Fencord** \n
\\@since 0.3.24 \\
\\@modified 0.3.25 \\
\\@author Aveyzan
```ts \\
module tense.fencord
```
Since 0.3.25 this module is called `tense.fencord` instead of `tense.core`. \\
Import this module only, if:
- you have Python 3.8 or above
- you have discord.py via `pip install discord`

This TensePy module features `Fencord` class.
"""
import sys

if sys.version_info < (3, 9):
    err, s = (RuntimeError, "Not allowed to import this module when having Python version least than 3.9.")
    raise err(s)

import subprocess as sb

try:
    import discord as dc
except (NameError, ModuleNotFoundError, ImportError):
    sb.run([sys.executable, "-m", "pip", "install", "discord"])

import tense.tcs as tcs, re, warnings as wa, inspect as ins, collections as ct
from tense import *
import discord as dc


    
# between @since and @author there is unnecessarily long line spacing
# hence this warning is being thrown; it is being disabled.
wa.filterwarnings("ignore", category = SyntaxWarning)

_var = tcs.TypeVar
_spec = tcs.SpecVar

_T = _var("_T")
# _P = _spec("_P")

_T_coroutine = _var("_T_coroutine", bound = tcs.Callable[..., tcs.Coroutine[tcs.Any, tcs.Any, list[dc.app_commands.AppCommand]]])

_DiscordHandler = tcs.Union[dc.Interaction[dc.Client], dc.Message] # since 0.3.24
_SupportsSlashCommandServers = tcs.Union[_T, list[_T], tuple[_T, ...], set[_T], frozenset[_T], ct.deque[_T], None] # since 0.3.25

@tcs.final
class Fencord:
    """
    Fencord
    +++++++
    \\@since 0.3.24 (before 0.3.25 as `DC`) \\
    \\@author Aveyzan
    ```ts \\
    in module tense.fencord
    ```
    Providing methods to help integrating with Discord.

    This class is not yet prepared to become subclassed
    """
    import tense.tcs as __tcs, discord.abc as __abc, discord.app_commands as __app, discord as __dc
    __commandtree = None
    __client = None
    __intents = None
    __synccorountine = None
    @property
    def user(self):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "property" in class Fencord
        ```
        Returns user of this client
        """
        return self.__client.user
    @property
    def servers(self):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "property" in class Fencord
        ```
        Returns servers/guilds tuple in which client is
        """
        return self.__client.guilds
    @property
    def getClient(self):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "property" in class Fencord
        ```
        Returns reference to `Client` instance inside the class.
        """
        return self.__client
    @property
    def getTree(self):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "property" in class Fencord
        ```
        Returns reference to `CommandTree` instance inside the class.

        This might be needed to invoke decorator `CommandTree.command()` \\
        for slash/application commands, since projected method for this class \\
        (`Fencord.slashCommand()`) leads to errors.
        """
        return self.__commandtree
    def __init__(self, intents: __dc.Intents = ..., messageContent: bool = True):
        """
        Fencord
        +++++++
        \\@since 0.3.24 (before 0.3.25 as `DC`) \\
        \\@author Aveyzan
        ```ts \\
        in module tense.fencord
        ```
        Providing methods to help integrating with Discord.
        Parameters:
        - `intents` - Instance of `discord.Intents`.
        - `messageContent` - When `True`, `client.message_content` setting is set to `True`, \\
        `False` otherwise. Defaults to `True`.
        """
        if not isinstance(intents, (self.__dc.Intents, self.__tcs.Ellipsis)):
            err = TypeError
            s = f"Parameter 'intends' must have instance of class 'discord.Intents' or an ellipsis, instead received: '{type(intents).__name__}'"
            raise err(s)
        if not isinstance(messageContent, bool):
            err = TypeError
            s = f"Parameter 'messageContent' must have boolean value, instead received: '{type(intents).__name__}'"
            raise err(s)
        if isinstance(intents, self.__tcs.Ellipsis): self.__intents = self.__dc.Intents.default()
        else: self.__intents = intents
        if messageContent: self.__intents.message_content = True
        self.__client = self.__dc.Client(intents = self.__intents)
        self.__commandtree = self.__app.CommandTree(self.__client)
        e = Tense.fencordFormat()
        print(f"\33[1;90m{e}\33[1;36m INITIALIZATION\33[0m Class '{__class__.__name__}' was successfully initalized. Line {ins.currentframe().f_back.f_lineno}")
    @staticmethod
    def returnName(handler: _DiscordHandler, /, target: __tcs.Optional[__dc.Member] = None, mention: __tcs.Optional[bool] = None, name: __tcs.Optional[bool] = None):
        """
        \\@since 0.3.24 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        Shorthand method for faciliating returning name: display name, mention or just username
        """
        from discord import Member, Interaction
        m = ""
        if isinstance(target, Member):
            if mention is True:
                m = target.mention
            else:
                if name is True: m = target.name
                else: m = target.display_name
        else:
            if isinstance(handler, Interaction):
                if mention is True:
                    m = handler.user.mention
                else:
                    if name is True: m = handler.user.name
                    else: m = handler.user.display_name
            else:
                if mention is True:
                    m = handler.author.mention
                else:
                    if name is True: m = handler.author.name
                    else: m = handler.author.display_name
        return m
    @staticmethod
    def initClient():
        """
        \\@since 0.3.24 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        Shortcut to the following lines of code: 
        ```py \\
        intends = discord.Intends.default()
        intends.message_content = True
        client = discord.Client(intends = intends)
        ```
        Returned is new instance of `Client` class. \\
        It does not apply to variables inside this class.
        """
        from discord import Intents, Client
        intends = Intents.default()
        intends.message_content = True
        return Client(intents = intends)
    @staticmethod
    def commandInvoked(name: str, author: __tcs.Union[__dc.Interaction, __dc.Message], /, parameters: __tcs.Optional[dict[str, str]] = None, error: __tcs.Optional[str] = None):
        """
        \\@since 0.3.24 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        Prints `INVOCATION` to the console. If `error` is a string, it is returned as `INVOCATION ERROR`
        """
        from discord import Message
        e = Tense.fencordFormat()
        if error is None:
            if isinstance(author, Message): t = f"\33[1;90m{e}\33[1;38;5;99m INVOCATION\33[0m Invoked message command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
            else: t = f"\33[1;90m{e}\33[1;38;5;99m INVOCATION\33[0m Invoked slash command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
        else:
            if isinstance(author, Message): t = f"\33[1;90m{e}\33[1;38;5;9m INVOCATION ERROR\33[0m Attempt to invoke message command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
            else: t = f"\33[1;90m{e}\33[1;38;5;9m INVOCATION ERROR\33[0m Attempt to invoke slash command '{name.lower()}' by '{Fencord.returnName(author, name = True)}'"
        if parameters is not None:
            t += " with parameter values: "
            for e in parameters:
                t += f"'{e}' -> {parameters[e]}, "
            t = re.sub(r", $", "", t)
        if error is not None: t += f"; \33[4m{error}\33[0m"
        return t
    @staticmethod
    def commandEquals(message: __dc.Message, *words: str):
        """
        \\@since 0.3.24 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        In reality just string comparison operation; an auxiliary \\
        method for message commands. Case is insensitive
        """
        for string in words:
            if message.content.lower() == string: return True
        return False
    
    def slashCommand(
        self,
        name: __tcs.Optional[__tcs.Union[str, __app.translator.locale_str]] = None,
        desc: __tcs.Optional[__tcs.Union[str, __app.translator.locale_str]] = None,
        nsfw: bool = False,
        servers: _SupportsSlashCommandServers[__abc.Snowflake] = None,
        autoLocaleStrings: bool = True,
        extras: dict[__tcs.Any, __tcs.Any] = {},
        override: bool = False
        ):
        """
        \\@since 0.3.25 (experimental to 0.3.26c2) \\
        \\@author Aveyzan
        ```ts \\
        "method" in class Fencord
        ```
        A decorator for slash/application commands. Typically a slight remake of `command()` decorator, but in reality \\
        it invokes method `add_command()`.

        Parameters (all are optional):
        - `name` - The name of the command. If none provided, command name will be name of the callback, fully lowercased. \\
        If `name` was provided, method will convert the string to lowercase, if there is necessity. Defaults to `None`.
        - `desc` - Description of the command. This shows up in the UI to describe the command. If not given, it defaults to the \\
        first line of the docstring of the callback shortened to 100 characters. Defaults to `None`.
        - `nsfw` - Indicate, whether this command is NSFW (Not Safe For Work) or not. Defaults to `False`.
        - `servers` - List/tuple/set/frozenset/deque of servers/guilds (there instances of `discord.Object`). If `None` given, command \\
        becomes global. This parameter can be also single instance of `discord.Object`. Defaults to `None`.
        - `autoLocaleString` - When it is `True`, then all translatable strings will implicitly be wrapped into `locale_str` \\
        rather than `str`. This could avoid some repetition and be more ergonomic for certain defaults such as default \\
        command names, command descriptions, and parameter names. Defaults to `True`.
        - `extras` - A dictionary that can be used to store extraneous data. The library will not touch any values or keys within this \\
        dictionary. Defaults to `None`.
        - `override` - If set to `True`, no exception is raised and command may be simply overwritten. Defaults to `False`.
        """
        if self.__commandtree is None:
            err, s = (self.__tcs.IncorrectValueError, f"Since 0.3.25 the '{__class__.__name__}' class must be concretized and needs to take '{self.__dc.Client.__name__}' class argument.")
            raise err(s)
        else:
            from discord.app_commands import Group
            from discord.app_commands.commands import CommandCallback
            from discord.abc import MISSING
            _servers = tuple([servers]) if isinstance(servers, self.__abc.Snowflake) else tuple(servers) if not Tense.isNone(servers) else None
            # suprisingly unexpected error: pylance said that we need 3 type parameters instead of 1
            # but compiler says we need only 1 instead of 3 (typing module TYPE_CHECKING value = true)
            def _decorator(f: CommandCallback[Group]): # type: ignore
                nonlocal name, desc, nsfw, autoLocaleStrings, extras
                if not ins.iscoroutinefunction(f):
                    err, s = (TypeError, "Expected command function to be a coroutine")
                    raise err(s)
                cmd = self.__app.Command(
                    name = name.lower() if Tense.isString(name) and reckon(name) > 0 else name if name is not None else f.__name__,
                    description = desc if desc is not None else "..." if f.__doc__ is None else f.__doc__[:100],
                    callback = f,
                    nsfw = nsfw,
                    parent = None,
                    auto_locale_strings = autoLocaleStrings,
                    extras = extras
                )
                self.__commandtree.add_command(
                    cmd,
                    # silly rapptz! I know we cannot mix guild and guilds parameters, but this error
                    # occurs only whether... I pass Any instead of MISSING
                    guild = _servers[0] if _servers is not None and reckon(_servers) == 1 else None,
                    guilds = _servers if _servers is not None and reckon(_servers) > 1 else MISSING,
                    override = override
                )
                return cmd
            return _decorator

    def sync(self, server: __tcs.Optional[__abc.Snowflake] = None):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "method" in class Fencord
        ```
        Sync all slash/application commands, display them on Discord, and translate all strings to `locale_str`. \\
        Used for `on_ready()` event as `await fencord.sync(server?)`. If class wasn't initialized, thrown is error \\
        `tense.tcs.NotInitializedError`.

        Parameters\\:
        - `server` (Optional) - The server/guild to sync the commands to. If `None` then it syncs all global commands \\
        instead.
        """
        if self.__commandtree is None:
            err, s  = (self.__tcs.NotInitializedError, f"Since 0.3.25 the '{__class__.__name__}' class must be concretized.")
            raise err(s)
        else:
            self.__synccorountine = self.__commandtree.sync(guild = server)
            return self.__synccorountine
    
    def event(self, f: _T_coroutine, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "method" in class Fencord
        ```
        A decorator which defines an event for client to listen to.

        Function injected with this decorator must have valid name,
        those can be for example: `on_message()`, `on_ready()`
        """
        if self.__client is None:
            err, s = (self.__tcs.NotInitializedError, f"Since 0.3.25 the '{__class__.__name__}' class must be concretized.")
            raise err(s)
        elif not ins.iscoroutinefunction(f):
            err, s = (TypeError, "Expected 'coroutine' parameter to be a coroutine.")
            raise err(s)
        else:
            return self.__client.event(f)
        
    @staticmethod
    def bold(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text bold
        """
        return f"**{text}**"
    @staticmethod
    def italic(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text italic
        """
        return f"*{text}*"
    @staticmethod
    def underline(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text underlined
        """
        return f"__{text}__"
    @staticmethod
    def code(text: str, language: tcs.Optional[str] = None, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: coded text
        """
        if language is None:
            return f"`{text}`"
        else:
            return f"```{language}\n{text}\n```"
    @staticmethod
    def big(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text big
        """
        return f"# {text}"
    @staticmethod
    def medium(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text medium
        """
        return f"## {text}"
    @staticmethod
    def small(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text small
        """
        return f"### {text}"
    @staticmethod
    def smaller(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text smaller
        """
        return f"-# {text}"
    @staticmethod
    def quote(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: transform text to quote
        """
        return f"> {text}"
    @staticmethod
    def spoiler(text: str, /):
        """
        \\@since 0.3.25 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text spoiled
        """
        return f"||{text}||"
    @staticmethod
    def textUrl(text: str, url: str, hideEmbed = True):
        """
        \\@since 0.3.26a2 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        On Discord: make text become hyperlink, leading to specified URL
        """
        return f"[{text}](<{url}>)" if hideEmbed else f"[{text}]({url})"
    @staticmethod
    def silent(text: str):
        """
        \\@since 0.3.26a3 \\
        \\@author Aveyzan
        ```ts \\
        "static method" in class Fencord
        ```
        Make a message silent. Usable for Direct Messages. \\
        As a tip, refer `@silent` as `> ` (quote), and message \\
        MUST be prefixed with `@silent`.
        """
        return f"@silent {text}"
    __all__ = [n for n in locals() if n[:1] != "_"]
    "\\@since 0.3.26c2"
    __dir__ = __all__
    "\\@since 0.3.26c2"

if __name__ == "__main__":
    err = RuntimeError
    s = "This file is not for compiling, consider importing it instead."
    raise err(s)

del wa, tcs, ct, dc # not for export

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__dir__ = __all__