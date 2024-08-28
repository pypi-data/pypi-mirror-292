"""
**TensePy Types & Constants**

\\@since 0.3.26b3 \\
\\@author Aveyzan \\
https://aveyzan.glitch.me/tense/py/module.tcs.html
```ts \\
module tense.tcs
```
Types and constants package for TensePy. It also contains ABCs (Abstract Base Classes).

Despite Python e.g. in version 3.10 provides union type expression with bar (`|`), in version 3.12 - preceding `type` keyword notations \\
still it is recommended to write the code in accordance to older Python versions.

If downloading `typing_extensions` module went unsuccessfully, try to manually run `pip install typing_extensions`.
"""

import sys

if sys.version_info < (3, 9):
    err, s = (RuntimeError, "Use 'tense_eight' module for Python versions below 3.9.")
    raise err(s)

import os, tkinter as tk, typing as tp, types as ty, io, math as ma, collections as ct, warnings as wa, functools as fn, abc, collections.abc as abc2, asyncio as aio, subprocess as sb, enum, inspect as ins
import zipfile as zi, urllib as url
from mmap import mmap
from array import array
from copy import copy

try:
    import typing_extensions as tpe
except (ModuleNotFoundError, ImportError, NameError):
    sb.run([sys.executable, "-m", "pip", "install", "typing_extensions"])

import typing_extensions as tpe

#################################### VERSION COMPONENTS (0.3.26b3) ####################################
# Consider NOT changing the version values, as it may be
# mistaken, and possibly you may not be up-to-date.

_a = "alpha"
"""An alpha release; this kind of version is not stable and may not offer some functions"""
_b = "beta"
"""A beta release; this kind of version may have some errors, although may offer all functions"""
_c = "candidate"
"""A candidate release; this kind of version can be released as ultimate, unless there won't be errors on the way"""
_rc = "final"
"""Same as `c`, but it is considered newer release"""
_p = "post-release"
"""A post release; this kind of version is uploaded after factual upload of ultimate version"""
_d = "developer"
"""A dev release; shouldn't be used"""

VERSION = "0.3.26c2"
"""Returns currently used version of Tense"""
VERSION_TUPLE = (0, 3, 26, _c, 2)
"""Returns currently used version of Tense as a tuple"""

VERSION_LIST = (
    "0.2.1", "0.2.2", "0.2.3", "0.2.4", "0.2.5", "0.2.6", "0.2.7", "0.2.8", "0.2.9", "0.2.10", "0.2.11", "0.2.12", "0.2.13", "0.2.14", "0.2.15", "0.2.16",
    "0.3.0", "0.3.1", "0.3.2", "0.3.3", "0.3.4", "0.3.5", "0.3.6", "0.3.7", "0.3.8", "0.3.9", "0.3.10", "0.3.11", "0.3.12", "0.3.13", "0.3.14", "0.3.15",
    "0.3.16", "0.3.17", "0.3.18", "0.3.19", "0.3.20", "0.3.21", "0.3.22", "0.3.23", "0.3.24", "0.3.25", "0.3.26a1", "0.3.26a2", "0.3.26a3", "0.3.26b1",
    "0.3.26a4", "0.3.26b2", "0.3.26b3", "0.3.26c1", VERSION
)
"""Returns list (not `list`) of Tense versions in ascending order"""

VERSION_ID = 50
"""Determined by size of constant `VERSION_LIST` minus one"""

#################################### MATH CONSTANTS (0.3.26b3) ####################################

NAN = ma.nan
INF = ma.inf
E = 2.718281828459045235360287471352
PI = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461
TAU = 6.283185307179586476925287
SQRT2 = 1.4142135623730950488016887242097
THOUSAND           = 1000 # 1e+3
MILLION            = 1000000 # 1e+6
BILLION            = 1000000000 # 1e+9
TRILLION           = 1000000000000 # 1e+12
QUADRILLION        = 1000000000000000 # 1e+15
QUINTILLION        = 1000000000000000000 # 1e+18
SEXTILLION         = 1000000000000000000000 # 1e+21
SEPTILLION         = 1000000000000000000000000 # 1e+24
OCTILLION          = 1000000000000000000000000000 # 1e+27
NONILLION          = 1000000000000000000000000000000 # 1e+30
DECILLION          = 1000000000000000000000000000000000 # 1e+33
UNDECILLION        = 1000000000000000000000000000000000000 # 1e+36
DUODECILLION       = 1000000000000000000000000000000000000000 # 1e+39
TREDECILLION       = 1000000000000000000000000000000000000000000 # 1e+42
QUATTUOR_DECILLION = 1000000000000000000000000000000000000000000000 # 1e+45
QUINDECILLION      = 1000000000000000000000000000000000000000000000000 # 1e+48
SEXDECILLION       = 1000000000000000000000000000000000000000000000000000 # 1e+51
SEPTEN_DECILLION   = 1000000000000000000000000000000000000000000000000000000 # 1e+54
OCTODECILLION      = 1000000000000000000000000000000000000000000000000000000000 # 1e+57
NOVEMDECILLION     = 1000000000000000000000000000000000000000000000000000000000000 # 1e+60
VIGINTILLION       = 1000000000000000000000000000000000000000000000000000000000000000 # 1e+63
GOOGOL             = 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 # 1e+100
CENTILLION         = 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 # 1e+303


#################################### OTHER CONSTANTS ####################################

JS_MIN_SAFE_INTEGER = -9007199254740991
"""
\\@since 0.3.26b3

`-(2^53 - 1)` - the smallest safe integer in JavaScript
"""
JS_MAX_SAFE_INTEGER = 9007199254740991
"""
\\@since 0.3.26b3

`2^53 - 1` - the biggest safe integer in JavaScript
"""
JS_MIN_VALUE = 4.940656458412465441765687928682213723650598026143247644255856825006755072702087518652998363616359923797965646954457177309266567103559397963987747960107818781263007131903114045278458171678489821036887186360569987307230500063874091535649843873124733972731696151400317153853980741262385655911710266585566867681870395603106249319452715914924553293054565444011274801297099995419319894090804165633245247571478690147267801593552386115501348035264934720193790268107107491703332226844753335720832431936092382893458368060106011506169809753078342277318329247904982524730776375927247874656084778203734469699533647017972677717585125660551199131504891101451037862738167250955837389733598993664809941164205702637090279242767544565229087538682506419718265533447265625e-324
"""
\\@since 0.3.26b3

`2^-1074` - the smallest possible number in JavaScript \\
Precision per digit
"""
JS_MAX_VALUE = 17976931348623139118889956560692130772452639421037405052830403761197852555077671941151929042600095771540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368
"""
\\@since 0.3.26b3

`2^1024 - 2^971` - the biggest possible number in JavaScript \\
Precision per digit
"""

SMASH_HIT_CHECKPOINTS = 12
"""
\\@since 0.3.26b3

Amount of checkpoints in Smash Hit (11 normal + 1 endless)
"""
MC_ENCHANTS = 42
"""
\\@since 0.3.26b3

Amount of enchantments in Minecraft
"""
MC_DURABILITY = {
    "helmet_turtleShell": 275,
    "helmet_leather": 55,
    "helmet_golden": 77,
    "helmet_chainmail": 165,
    "helmet_iron": 165,
    "helmet_diamond": 363,
    "helmet_netherite": 407,
    "chestplate_leather": 80,
    "chestplate_golden": 112,
    "chestplate_chainmail": 240,
    "chestplate_iron": 240,
    "chestplate_diamond": 528,
    "chestplate_netherite": 592,
    "leggings_leather": 75,
    "leggings_golden": 105,
    "leggings_chainmail": 225,
    "leggings_iron": 225,
    "leggings_diamond": 495,
    "leggings_netherite": 555,
    "boots_leather": 65,
    "boots_golden": 91,
    "boots_chainmail": 195,
    "boots_iron": 195,
    "boots_diamond": 429,
    "boots_netherite": 481,
    "bow": 384,
    "shield": 336,
    "trident": 250,
    "elytra": 432,
    "crossbow_java": 465,
    "crossbow_bedrock": 464,
    "brush": 64,
    "fishingRod_java": 64,
    "fishingRod_bedrock": 384,
    "flintAndSteel": 64,
    "carrotOnStick": 25,
    "warpedFungusOnStick": 100,
    "sparkler_bedrock": 100,
    "glowStick_bedrock": 100,
    "tool_gold": 32,
    "tool_wood": 65,
    "tool_stone": 131,
    "tool_iron": 250,
    "tool_diamond": 1561,
    "tool_netherite": 2031
}

NULL = None # 0.3.26b3


###### TYPES ######

_var = tp.TypeVar
_uni = tp.Union
_opt = tp.Optional
_cal = tp.Callable
_gen = tp.Generic

_T = _var("_T")

if sys.version_info >= (3, 5, 2):
    _nam = tp.NamedTuple # 0.3.26c1
    _new = tp.NewType # 0.3.26c1
else:
    _nam = tpe.NamedTuple # 0.3.26c1
    _new = tpe.NewType # 0.3.26c1

if sys.version_info >= (3, 5, 3):
    _cla = tp.ClassVar[_T] # 0.3.26b3
else:
    _cla = tpe.ClassVar[_T] # 0.3.26b3

if sys.version_info >= (3, 6, 2):
    _nor = tp.NoReturn # 0.3.26b3
else:
    _nor = tpe.NoReturn # 0.3.26b3

if sys.version_info >= (3, 7, 4):
    _for = tp.ForwardRef # 0.3.26c1
else:
    _for = tpe.ForwardRef # 0.3.26c1

if sys.version_info >= (3, 8):
    _lit = tp.Literal # 0.3.26c1
    _fin = tp.Final # 0.3.26c1
    _pro = tp.Protocol # 0.3.26c1
else:
    _lit = tpe.Literal # 0.3.26c1
    _fin = tpe.Final # 0.3.26c1
    _pro = tpe.Protocol # 0.3.26c1

if sys.version_info >= (3, 9):
    _ann = tp.Annotated # 0.3.26c1
    _con2 = abc2.Container[_T] # 0.3.26b3
    _con3 = ct.Counter[_T] # 0.3.26c1
    _tpa = tpe.TypeAlias # 0.3.26c1
else:
    _ann = tpe.Annotated # 0.3.26c1
    _con2 = tp.Container[_T] # 0.3.26b3
    _con3 = tp.Counter[_T] # 0.3.26c1
    _tpa = tp.TypeAlias # 0.3.26c1

if sys.version_info >= (3, 10):
    _tpg = tp.TypeGuard[_T] # 0.3.26b3
    _par = tp.ParamSpec # 0.3.26b3
    _para = tp.ParamSpecArgs # 0.3.26b3
    _park = tp.ParamSpecKwargs # 0.3.26b3
    _con = tp.Concatenate # 0.3.26b3
    Ellipsis = ty.EllipsisType # 0.3.25
else:
    _tpg = tpe.TypeGuard[_T] # 0.3.26b3
    _par = tpe.ParamSpec # 0.3.26b3
    _para = tpe.ParamSpecArgs # 0.3.26b3
    _park = tpe.ParamSpecKwargs # 0.3.26b3
    _con = tpe.Concatenate # 0.3.26b3
    @tp.final
    class ellipsis: ...
    Ellipsis = ellipsis

if sys.version_info >= (3, 11):
    _ttv = tp.TypeVarTuple # 0.3.26b3
    _not = tp.NotRequired # 0.3.26b3
    _req = tp.Required # 0.3.26b3
    _unp = tp.Unpack # 0.3.26b3
    _nev = tp.Never # 0.3.26c1
    _any = tp.Any # 0.3.26c1
    _lis = tp.LiteralString # 0.3.26c1
    _sel = tp.Self # 0.3.26c1
    _ase = tp.assert_type # 0.3.26c1
    _asn = tp.assert_never # 0.3.26c1
    _rev = tp.reveal_type # 0.3.26c1
    _dat = tp.dataclass_transform # 0.3.26c1
    _get = tp.get_overloads # 0.3.26c1
    _cle = tp.clear_overloads # 0.3.26c1
else:
    _ttv = tpe.TypeVarTuple # 0.3.26b3
    _not = tpe.NotRequired # 0.3.26b3
    _req = tpe.Required # 0.3.26b3
    _unp = tpe.Unpack # 0.3.26b3
    _nev = tpe.Never # 0.3.26c1
    _any = tpe.Any # 0.3.26c1
    _lis = tpe.LiteralString # 0.3.26c1
    _sel = tpe.Self # 0.3.26c1
    _ase = tpe.assert_type # 0.3.26c1
    _asn = tpe.assert_never # 0.3.26c1
    _rev = tpe.reveal_type # 0.3.26c1
    _dat = tpe.dataclass_transform # 0.3.26c1
    _get = tpe.get_overloads # 0.3.26c1
    _cle = tpe.clear_overloads # 0.3.26c1

if sys.version_info >= (3, 12):
    _tat = tp.TypeAliasType # 0.3.26c1
    _buf = abc2.Buffer # 0.3.26c1
else:
    _tat = tpe.TypeAliasType # 0.3.26c1
    _buf = tpe.Buffer # 0.3.26c1

if sys.version_info >= (3, 13):
    _nod = tp.NoDefault # 0.3.26c1
    _tpi = tp.TypeIs[_T] # 0.3.26c1
else:
    _nod = tpe.NoDefault # 0.3.26c1
    _tpi = tpe.TypeIs[_T] # 0.3.26c1

_P = _par("_P")
_T_class = _var("_T_class", bound = type)
_T_func = _var("_T_func", bound = _cal[..., tp.Any])
_T_cov = _var("_T_cov", covariant = True)
_T_con = _var("_T_con", contravariant = True)
_KT = _var("_KT")
_KT_cov = _var("_KT_cov", covariant = True)
_KT_con = _var("_KT_con", contravariant = True)
_VT = _var("_VT")
_VT_cov = _var("_VT_cov", covariant = True)
_CoroutineLike = _cal[_P, tp.Generator[_any, _any, _T]]
# >>> _uni[_cal[_P, tp.Generator[_any, _any, _T]], _cal[..., _T]]
_DecoratorLike = _cal[_P, _T]
# abroad types basing on parameter names
_V1 = _var("_V1")
_V2 = _var("_V2")
_M = _var("_M")

Annotated = _ann
"\\@since 0.3.26c1. Alias to `typing.NoReturn` (≥ 3.9) / `typing_extensions.NoReturn` (< 3.9)"
Any = _any
"\\@since 0.3.26c1. Alias to `typing.Any`"
Buffer = _buf
"\\@since 0.3.26c1. Alias to `collections.abc.Buffer` (≥ 3.12) / `typing_extensions.Buffer` (< 3.12)"
Callable = _cal
"\\@since 0.3.26c1. Alias to `typing.Callable`"
ClassVar = _cla[_T]
"\\@since 0.3.26b3. Alias to `typing.ClassVar` (≥ 3.5.3) / `typing_extensions.ClassVar` (< 3.5.3)"
Concatenate: type[_con[_T, _P]]
"\\@since 0.3.26c1. Alias to `typing.Concatenate` (≥ 3.6.2) / `typing_extensions.Concatenate` (< 3.6.2)"
Container = _con2[_T]
"\\@since 0.3.26b3. Alias to `collections.Container` (≥ 3.9) / `typing.Container` (< 3.9)"
Coroutine = abc2.Coroutine[_T, _T_con, _T_cov]
"\\@since 0.3.26c1. Alias to `collections.abc.Coroutine` (≥ 3.5). `_T` = yield, `_T_con` = send, `_T_cov` = return. Usually used as `Coroutine[Any, Any, _T]`"
Counter = _con3[_T]
"\\@since 0.3.26c1. Alias to `collections.Counter` (≥ 3.9) / `typing.NoReturn` (< 3.9)"
Final = _fin
"\\@since 0.3.26c1. Alias to `typing.Final` (≥ 3.8) / `typing_extensions.Final` (< 3.8)"
Generic = _gen
"\\@since 0.3.26c1. Alias to `typing.Generic`"
Literal = _lit
"\\@since 0.3.26c1. Alias to `typing.Literal` (≥ 3.8) / `typing_extensions.Literal` (< 3.8)"
LiteralString = _lis
"\\@since 0.3.26c1. Alias to `typing.LiteralString` (≥ 3.11) / `typing_extensions.LiteralString` (< 3.11)"
NamedTuple = _nam
"\\@since 0.3.26c1. Alias to `typing.NamedTuple` (≥ 3.5.2) / `typing_extensions.NamedTuple` (< 3.5.2)"
Never = _nev
"\\@since 0.3.26c1. Alias to `typing.Never` (≥ 3.11) / `typing_extensions.Never` (< 3.11)"
NewType = _new
"\\@since 0.3.26c1. Alias to `typing.NewType` (≥ 3.5.2) / `typing_extensions.NewType` (< 3.5.2)"
NoDefault = _nod
"\\@since 0.3.26c1. Alias to `typing.NoDefault` (≥ 3.13) / `typing_extensions.NoDefault` (< 3.13)"
NoReturn = _nor
"\\@since 0.3.26c1. Alias to `typing.NoReturn` (≥ 3.6.2) / `typing_extensions.NoReturn` (< 3.6.2)"
NotRequired = _not
"\\@since 0.3.26b3. Alias to `typing.NotRequired` (≥ 3.11) / `typing_extensions.NotRequired` (< 3.11)"
Optional = _opt
"\\@since 0.3.26b3. Alias to `typing.Optional`"
Pack = _con
"\\@since 0.3.26b3. Alias to `typing.Concatenate` (≥ 3.10) / `typing_extensions.Concatenate` (< 3.10)"
Protocol = _pro
"\\@since 0.3.26c1. Alias to `typing.Protocol` (≥ 3.8) / `typing_extensions.Protocol` (< 3.8)"
Required = _req
"\\@since 0.3.26c1. Alias to `typing.Required` (≥ 3.11) / `typing_extensions.Required` (< 3.11)"
Self = _sel
"\\@since 0.3.26c1. Alias to `typing.Self` (≥ 3.11) / `typing_extensions.Self` (< 3.11)"
SpecVar = _par
"\\@since 0.3.26c1. Alias to `typing.ParamSpec` (≥ 3.10) / `typing_extensions.ParamSpec` (< 3.10)"
SpecVarArgs = _para
"\\@since 0.3.26c1. Alias to `typing.ParamSpecArgs` (≥ 3.10) / `typing_extensions.ParamSpecArgs` (< 3.10)"
SpecVarKwargs = _park
"\\@since 0.3.26c1. Alias to `typing.ParamSpecKwargs` (≥ 3.10) / `typing_extensions.ParamSpecKwargs` (< 3.10)"
TypeAlias = _tpa
"\\@since 0.3.26c1. Alias to `typing_extensions.TypeAlias` (≥ 3.9) / `typing.TypeAlias` (< 3.9) -- Reason: deprecated"
TypeAliasType = _tat
"\\@since 0.3.26c1. Alias to `typing.TypeAliasType` (≥ 3.12) / `typing_extensions.TypeAliasType` (< 3.12)"
TypeGuard = _tpg[_T]
"\\@since 0.3.26c1. Alias to `typing.TypeGuard` (≥ 3.10) / `typing_extensions.TypeGuard` (< 3.10)"
TypeTupleVar = _ttv
"\\@since 0.3.26c1. Alias to `typing.TypeVarTuple` (≥ 3.11) / `typing_extensions.TypeVarTuple` (< 3.11)"
TypeIs = _tpi[_T]
"\\@since 0.3.26c1. Alias to `typing.TypeIs` (≥ 3.13) / `typing_extensions.TypeIs` (< 3.13)"
Union = _uni
"\\@since 0.3.26c1. Alias to `typing.Union`"
Unpack = _unp
"\\@since 0.3.26b3. Alias to `typing.Unpack` (≥ 3.11) / `typing_extensions.Unpack` (< 3.11) -- Experimental"

class Auto(enum.auto):
    "\\@since 0.3.26c1. Instances are replaced with an appropriate value in Enum class suites"
    ...

class Verify(enum.verify):
    "\\@since 0.3.26c2. Check an enumeration for various constraints"
    ...

class IntegerFlag(enum.IntFlag):
    "\\@since 0.3.26c1. Support for integer-based flags"
    ...

class IntegerEnum(enum.IntEnum):
    "\\@since 0.3.26c1. Enum where members are also (and must be) integers"
    ...

class Enum(enum.Enum):
    "\\@since 0.3.26c1. Create a collection of name/value pairs"
    ...

EnumCheck = enum.EnumCheck
"\\@since 0.3.26c1. Various conditions to check an enumeration for"

class EnumMeta(enum.EnumMeta):
    "\\@since 0.3.26c2"
    ...

class StringEnum(enum.StrEnum):
    "\\@since 0.3.26c1. Enum where members are also (and must be) strings"
    ...

if sys.version_info >= (3, 11):
    ReprEnum = enum.ReprEnum
    "\\@since 0.3.26c1"
    FlagBoundary = enum.FlagBoundary
    "\\@since 0.3.26c1"

class Flag(enum.Flag):
    "\\@since 0.3.26c1. Support for flags"
    ...

class IntegerVar(tk.IntVar):
    "\\@since 0.3.26c1. Value holder for integer variables"
    ...

class StringVar(tk.StringVar):
    "\\@since 0.3.26c1. Value holder for string variables"
    ...

class BooleanVar(tk.BooleanVar):
    "\\@since 0.3.26c1. Value holder for boolean variables"
    ...

class Variable(tk.Variable):
    "\\@since 0.3.26c1"
    ...

class FloatVar(tk.DoubleVar):
    "\\@since 0.3.26c1. Value holder for float variables"
    ...

class ZipFile(zi.ZipFile):
    "\\@since 0.3.26c2. Class with methods to open, read, write, close, list zip files"
    ...

class ZipExtFile(zi.ZipExtFile):
    "\\@since 0.3.26c2. File-like object for reading an archive member. Returned by `ZipFile.open()`"
    ...

class LargeZipFile(zi.LargeZipFile):
    "\\@since 0.3.26c2. Raised when writing a zipfile, the zipfile requires ZIP64 extensions and those extensions are disabled"
    ...

class ZipPath(zi.Path):
    "\\@since 0.3.26c2. A pathlib-compatible interface for zip files"
    ...

BufferFlags = ins.BufferFlags
"\\@since 0.3.26c2"

class Signature(ins.Signature):
    """
    \\@since 0.3.26c2
    
    A Signature object represents the overall signature of a function. It stores a Parameter object for each \\
    parameter accepted by the function, as well as information specific to the function itself.
    """
    ...

def overload(f: _T_func): # 0.3.26c1
    """
    \\@since 0.3.26c1

    A decorator for overloaded functions and methods
    """
    if sys.version_info >= (3, 11):
        return tp.overload(f)
    else:
        return tpe.overload(f)
        
def override(m: _T_func): # 0.3.26c1
    """
    \\@since 0.3.26c1

    A decorator for creating methods to override by subclasses \\
    of their class parents. This decorator should be used only \\
    in subclasses, which will override specific method(s) from \\
    base class, using the same method name(s). Details in PEP 698
    """
    try:
        m.__override__ = True
    except (AttributeError, TypeError):
        # Skip the attribute silently if it is not writable.
        # AttributeError happens if the object has __slots__ or a
        # read-only property, TypeError if it's a builtin class.
        pass
    return m

class argumental:
    """
    \\@since 0.3.26c1

    Alias to function `typing.get_args()`
    """
    def __new__(cls, t):
        if sys.version_info >= (3, 8):
            return tp.get_args(t)
        else:
            return tpe.get_args(t)

def runtime(c: _T_class): # 0.3.26c1
    """
    \\@since 0.3.26c1

    A decorator which formalizes protocol class to a protocol runtime. \\
    Protocol class injected with this decorator can be used in `isinstance()` \\
    and `issubclass()` type checking functions.

    In practice equivalent to `runtime_checkable` decorator from `typing`
    """
    # according to source code of typing_extensions
    if sys.version_info >= (3, 13):
        return tp.runtime_checkable(c)
    else:
        return tpe.runtime_checkable(c)
    
def coroutine(f: _CoroutineLike[_P, _T]):
    """
    \\@since 0.3.26c1

    This function converts regular generator function to a coroutine.
    """
    return ty.coroutine(f)
        
def final(f: _T):
    """
    \\@since 0.3.26b3

    A decorator for final methods and classes. Classes preceded by this \\
    decorator cannot be subclassed. Final methods cannot be overriden by the \\
    subclass. Better use this decorator instead of class `tense.tcs.FinalClass`.

    Examples::
    
        @final
        class FinalClass: ... # ok
        class SubclassOfFinalClass(FinalClass): ... # error
        class ClassWithFinalMethod:
            @final
            def example(self): ... # ok
        class SubclassOfClassWithFinalMethod(ClassWithFinalMethod):
            def example(self): ... # error
    """
    try:
        f.__final__ = True
    except (AttributeError, TypeError):
        pass
    return f
    
def abstract(f: _T):
    """
    \\@since 0.3.26b3

    A decorator for abstract methods and properties

    Example:
    ```py \\
    class Example:
    @abstract
    def test1(): ... # method

    @abstract
    @property
    def test2(): ... # property
    ```
    """
    f.__isabstractmethod__ = True
    return f

class abstractproperty(property):
    """
    \\@since 0.3.26c1

    A decorator class for abstract properties.

    Equivalent invoking decorators `tense.tcs.abstract` and in-built `property`.
    """
    __isabstractmethod__ = True

class abstractstaticmethod(staticmethod):
    """
    \\@since 0.3.26c1

    A decorator class for abstract static methods.

    Equivalent invoking decorators `tense.tcs.abstract` and in-built `staticmethod`.
    """
    __isabstractmethod__ = True
    def __init__(self, f: _cal[_P, _T_cov]):
        f.__isabstractmethod__ = True
        super().__init__(f)

class abstractclassmethod(classmethod):
    """
    \\@since 0.3.26c1

    A decorator class for abstract class methods.

    Equivalent invoking decorators `tense.tcs.abstract` and in-built `classmethod`.
    """
    __isabstractmethod__ = True
    def __init__(self, f: _cal[_con[type[_T], _P], _T_cov]):
        f.__isabstractmethod__ = True
        super().__init__(f)

def noTypeCheck(f: _T_func): # 0.3.26c1
    "\\@since 0.3.26c1"
    return tp.no_type_check(f)
def noTypeCheckDecorator(d: _DecoratorLike[_P, _T]): # 0.3.26c1
    "\\@since 0.3.26c1"
    return tp.no_type_check_decorator(d)

class MissingValueError(Exception):
    """
    \\@since 0.3.19 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs // to 0.3.26b3 in module tense.primary
    ```
    Missing value (empty parameter)
    """
    ...
class IncorrectValueError(Exception):
    """
    \\@since 0.3.19 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs // to 0.3.26b3 in module tense.primary
    ```
    Incorrect value of a parameter, having correct type
    """
    ...
class NotInitializedError(Exception):
    """
    \\@since 0.3.25 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs // to 0.3.26b3 in module tense.primary
    ```
    Class was not instantiated
    """
    ...
class InitializedError(Exception):
    """
    \\@since 0.3.26b3 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs
    ```
    Class was instantiated
    """
    ...
class NotReassignableError(Exception):
    """
    \\@since 0.3.26b3 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs
    ```
    Attempt to re-assign a value
    """
    ...
class NotComparableError(Exception):
    """
    \\@since 0.3.26c1 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs
    ```
    Attempt to compare a value with another one
    """
    ...
class NotIterableError(Exception):
    """
    \\@since 0.3.26c1 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs
    ```
    Attempt to iterate
    """
    ...
class NotInvocableError(Exception):
    """
    \\@since 0.3.26c1 \\
    \\@author Aveyzan
    ```ts \\
    in module tense.tcs
    ```
    Attempt to call an object
    """
    ...

_internal_module = "tense.tcs"

def _e(code: int, *args: str):
    """
    \\@since 0.3.26c1
    ```ts \\
    in module tense.tcs
    ```
    Internal function for error handling

    - `100` - cannot modify a final variable (`any`)
    - `101` - cannot use comparison operators on type which doesn't support them + ...
    - `102` - cannot assign a new value or re-assign a value with any of augmented \\
    assignment operators on type which doesn't support them + ...
    - `103` - object is not iterable (`any`)
    - `104` - attempt to initialize an abstract class + ...
    - `105` - class (`any`) was not initialized
    - `106` - could not compare types - at least one of them does not support comparison \\
    operators
    - `107` - object cannot be called
    - `108` - object cannot use any of unary operators: '+', '-', '~', cannot be called nor be value \\
    of `abs()` in-built function
    - `109` - object cannot use unary +|- operator
    - `110` - object cannot use bitwise NOT operator '~'
    - `111` - this file is not for compiling, moreover, this file does not have a complete \\
    TensePy declarations collection. Consider importing module `tense` instead
    - any other - unknown error occured
    """
    _arg0 = "" if len(args) == 0 else args[0]
    if code == 100:
        err, s = (NotReassignableError, "cannot modify a final variable '{}'".format(_arg0) if _arg0 not in (None, "") else "cannot modify a final variable")
    elif code == 101:
        err, s = (NotComparableError, "cannot use comparison operators on type which doesn't support them" + _arg0)
    elif code == 102:
        err, s = (NotReassignableError, "cannot assign a new value or re-assign a value with any of augmented assignment operators on type which doesn't support them" + _arg0)
    elif code == 103:
        err, s = (NotIterableError, "object is not iterable ('{}')".format(_arg0) if _arg0 not in (None, "") else "cannot modify a final variable")
    elif code == 104:
        err, s = (InitializedError, "attempt to initialize an abstract class" + _arg0)
    elif code == 105:
        err, s = (NotInitializedError, "class '{}' was not initalized".format(_arg0))
    elif code == 106:
        err, s = (NotComparableError, "could not compare types - at least one of them does not support comparison operators")
    elif code == 107:
        err, s = (NotInvocableError, "object cannot be called" + _arg0)
    elif code == 108:
        err, s = (TypeError, "object cannot use any of unary operators: '+', '-', '~', cannot be called nor be value of abs() in-built function")
    elif code == 109:
        err, s = (TypeError, "object cannot use unary '{}' operator".format(_arg0))
    elif code == 110:
        err, s = (TypeError, "object cannot use bitwise NOT operator '~'")
    elif code == 111:
        err, s = (RuntimeError, "this file is not for compiling, moreover, this file does not have a complete TensePy declarations collection. Consider importing module 'tense' instead.")
    else:
        err, s = (RuntimeError, "unknown error occured")
    raise err(s)

@runtime
class NotReassignable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    This class does not support any form of re-assignment, those are augmented \\
    assignment operators: `+=`, `-=`, `*=`, `**=`, `/=`, `//=`, `%=`, `>>=`, `<<=`, \\
    `&=`, `|=`, `^=`. Setting new value also is prohibited.
    """
    __slots__ = ()
    __op = (
        "; used operator '+='", # 0
        "; used operator '-='", # 1
        "; used operator '*='", # 2
        "; used operator '/='", # 3
        "; used operator '//='", # 4
        "; used operator '**='", # 5
        "; used operator '<<='", # 6
        "; used operator '>>='", # 7
        "; used operator '%='", # 8
        "; used operator '&='", # 9
        "; used operator '|='", # 10
        "; used operator '^='", # 11
    )
    def __await_internal_sentinel(self, val = ""):
        return _e(102, val)
    def __set__(self, i: tp.Self, v: _T_con):
        # setting value not allowed...
        self.__await_internal_sentinel()
    def __iadd__(self, o: _T_con):
        i = 0
        self.__await_internal_sentinel(self.__op[i])
    def __isub__(self, o: _T_con):
        i = 1
        self.__await_internal_sentinel(self.__op[i])
    def __imul__(self, o: _T_con):
        i = 2
        self.__await_internal_sentinel(self.__op[i])
    def __ifloordiv__(self, o: _T_con):
        i = 4
        self.__await_internal_sentinel(self.__op[i])
    def __idiv__(self, o: _T_con):
        i = 3
        self.__await_internal_sentinel(self.__op[i])
    def __itruediv__(self, o: _T_con):
        i = 3
        self.__await_internal_sentinel(self.__op[i])
    def __imod__(self, o: _T_con):
        i = 8
        self.__await_internal_sentinel(self.__op[i])
    def __ipow__(self, o: _T_con):
        i = 5
        self.__await_internal_sentinel(self.__op[i])
    def __ilshift__(self, o: _T_con):
        i = 6
        self.__await_internal_sentinel(self.__op[i])
    def __irshift__(self, o: _T_con):
        i = 7
        self.__await_internal_sentinel(self.__op[i])
    def __iand__(self, o: _T_con):
        i = 9
        self.__await_internal_sentinel(self.__op[i])
    def __ior__(self, o: _T_con):
        i = 10
        self.__await_internal_sentinel(self.__op[i])
    def __ixor__(self, o: _T_con):
        i = 11
        self.__await_internal_sentinel(self.__op[i])

@runtime
class NotComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Cannot be compared with operators `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`
    """
    __slots__ = ()
    __op = (
        "; used operator '<'", # 0
        "; used operator '>'", # 1
        "; used operator '<='", # 2
        "; used operator '>='", # 3
        "; used operator '=='", # 4
        "; used operator '!='", # 5
        "; used operator 'in'", # 6
    )
    def __await_internal_sentinel(self, val = ""):
        return _e(101, val)
    def __lt__(self, other: _T_con):
        i = 0
        return self.__await_internal_sentinel(self.__op[i])
    def __gt__(self, other: _T_con):
        i = 1
        return self.__await_internal_sentinel(self.__op[i])
    def __le__(self, other: _T_con):
        i = 2
        return self.__await_internal_sentinel(self.__op[i])
    def __ge__(self, other: _T_con):
        i = 3
        return self.__await_internal_sentinel(self.__op[i])
    def __eq__(self, other: _T_con):
        i = 4
        return self.__await_internal_sentinel(self.__op[i])
    def __ne__(self, other: _T_con):
        i = 5
        return self.__await_internal_sentinel(self.__op[i])
    def __contains__(self, other: _T_con):
        i = 6
        return self.__await_internal_sentinel(self.__op[i])
    
@runtime
class Reversible(_pro[_T_cov]):
    """
    \\@since 0.3.26c2

    An ABC with one method `__reversed__`, which equals invoking `reversed(self)`. \\
    Returned type is addicted to covariant type parameter (iterator of type parameter).
    """
    def __reversed__(self) -> abc2.Iterator[_T_cov]: ...

ReversibleABC = abc2.Reversible[_T]
"\\@since 0.3.26c2"

@runtime
class Awaitable(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__await__`, which equals invoking `yield self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __await__(self) -> abc2.Generator[_sel, _any, _T_cov]: ...

AwaitableABC = abc2.Awaitable[_T]
"\\@since 0.3.26c2"

@runtime
class Invocable(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__call__`, which equals invoking `self(...)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __call__(self, *args, **kwds) -> _T_cov: ...
    
@runtime
class Formattable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__format__`, which equals invoking `format(self)`.
    """
    def __format__(self, format_spec: str = "") -> str: ...

@runtime
class Containable(_pro[_T_con]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__contains__`, which equals invoking `value in self`. \\
    Type parameter there is contravariant, and equals type for `value` parameter.
    """
    def __contains__(self, value: _T_con) -> bool: ...

@runtime
class Iterable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with one method `__iter__`, which equals invoking `for x in self: ...`. \\
    Returned type is addicted to covariant type parameter. To 0.3.26b3 alias of `typing.Iterable`
    """
    def __iter__(self) -> _T_cov: ...

IterableABC = abc2.Iterable[_T]
"\\@since 0.3.26c2"

@runtime
class NotIterable(_pro):
    """
    \\@since 0.3.26b3

    Cannot be used with `for` loop
    """
    def __await_internal_sentinel(self):
        s = __class__.__qualname__
        return _e(102, s)
    def __iter__(self):
        return self.__await_internal_sentinel()

IteratorABC = abc2.Iterator[_T]
"\\@since 0.3.26b3"

@runtime
class Absolute(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__abs__`, which equals invoking `abs(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __abs__(self) -> _T_cov: ...

@runtime
class Truncable(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__trunc__`, which equals invoking `trunc(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __trunc__(self) -> _T_cov: ...

@runtime
class BooleanConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__bool__` which equals invoking `bool(self)`. \\
    To keep accordance with Python 2, there is also method `__nonzero__`, \\
    which you are encouraged to use the same way as `__bool__`. Preferred use::

        def __bool__(self): ... # some code
        def __nonzero__(self): return self.__bool__()
    """
    def __bool__(self) -> bool: ...
    def __nonzero__(self) -> bool: ...

@runtime
class IntegerConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__int__`, which equals invoking `int(self)`
    """
    def __int__(self) -> int: ...

@runtime
class FloatConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__float__`, which equals invoking `float(self)`
    """
    def __float__(self) -> float: ...

@runtime
class ComplexConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__complex__`, which equals invoking `complex(self)`
    """
    def __complex__(self) -> complex: ...

@runtime
class BytesConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__bytes__`, which equals invoking `bytes(self)`
    """
    def __bytes__(self) ->  bytes: ...

@runtime
class BinaryRepresentable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__bin__`, which equals invoking `bin(self)`.

    In reality there is no such magic method as `__bin__`, but I encourage \\
    Python working team to think about it.
    """
    def __bin__(self) -> str: ...

@runtime
class OctalRepresentable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__oct__`, which equals invoking `oct(self)`
    """
    def __oct__(self) -> str: ...

@runtime
class HexadecimalRepresentable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__hex__`, which equals invoking `hex(self)`
    """
    def __hex__(self) -> str: ...

@runtime
class StringConvertible(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__str__`, which equals invoking `str(self)`
    """
    def __str__(self) -> str: ...

@runtime
class Representable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__repr__`, which equals invoking `repr(self)`
    """
    def __repr__(self) -> str: ...

@runtime
class Indexable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__index__`. This allows to use self inside slice expressions, \\
    those are: `slice(self, ..., ...)` and `iterable[self:...:...]` (`self` can be \\
    placed anywhere)
    """
    def __index__(self) -> int: ...

@runtime
class Hashable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__hash__`, which equals invoking `hash(self)`.
    """
    def __hash__(self) -> int: ...

@runtime
class Positive(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__pos__`, which equals `+self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __pos__(self) -> _T_cov: ...

@runtime
class Negative(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__neg__`, which equals `-self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __neg__(self) -> _T_cov: ...

@runtime
class BufferOperable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__buffer__`.
    """
    def __buffer__(self, flags: ins.BufferFlags) -> memoryview: ...

@runtime
class NotInvocable(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    Cannot be called as a function (as `self()`)
    """
    def __call__(self, *args, **kwds):
        raise _e(107)

@runtime
class Invertible(_pro[_T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__invert__`, which equals `~self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __invert__(self) -> _T_cov: ...

@runtime
class NotInvertible(_pro):
    """
    \\@since 0.3.26c1

    Cannot be used with bitwise NOT operator `~` (as `~self`)
    """
    def __await_internal_sentinel(self, val = "~"):
        return _e(110)
    def __invert__(self):
        self.__await_internal_sentinel()

@runtime
class BitwiseAndOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__and__`, which equals `self & other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __and__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__or__`, which equals `self | other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __or__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__xor__`, which equals `self ^ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __xor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__lshift__`, which equals `self << other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__rshift__`, which equals `self >> other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseOperable(
    BitwiseAndOperable[_any, _any],
    BitwiseOrOperable[_any, _any],
    BitwiseXorOperable[_any, _any],
    BitwiseLeftOperable[_any, _any],
    BitwiseRightOperable[_any, _any]
):
    """
    \\@since 0.3.26c1

    Can be used with `&`, `|`, `^`, `<<` and `>>` operators
    """
    ...

@runtime
class BitwiseAndReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__iand__`, which equals `self &= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iand__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__ior__`, which equals `self |= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ior__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__ixor__`, which equals `self ^= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ixor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__ilshift__`, which equals `self <<= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ilshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1

    An ABC with one method `__irshift__`, which equals `self >>= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __irshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseReassignable(
    BitwiseAndOperable[_any, _any],
    BitwiseOrOperable[_any, _any],
    BitwiseXorOperable[_any, _any],
    BitwiseLeftReassignable[_any, _any],
    BitwiseRightReassignable[_any, _any]):
    """
    \\@since 0.3.26c1

    Can be used with `&=`, `|=`, `^=`, `<<=` and `>>=` operators
    """
    ...

class BitwiseCollection(
    BitwiseReassignable,
    BitwiseOperable):
    """
    \\@since 0.3.26c1

    Can be used with `&`, `|` and `^` operators, including their \\
    augmented forms: `&=`, `|=` and `^=`, with `~` use following::

        class Example(BitwiseCollection, Invertible[_T]): ...
    """
    ...

class UnaryOperable(Positive[_any], Negative[_any], Invertible[_any]):
    """
    \\@since 0.3.26c1

    Can be used with `+`, `-` and `~` operators preceding the type
    """
    ...

@runtime
class NotUnaryOperable(_pro):
    """
    \\@since 0.3.26c1

    Cannot be used with preceding operators `+`, `-` and `~`
    """
    ...
    def __await_internal_sentinel(self):
        return _e(108)
    def __pos__(self):
        return self.__await_internal_sentinel()
    def __neg__(self):
        return self.__await_internal_sentinel()
    def __invert__(self):
        return self.__await_internal_sentinel()
    

class InComparable(_pro[_T_con]):
    """
    \\@since 0.3.26c1

    Can be compared with `in` operator. \\
    Alias to `Containable`
    """
    def __contains__(self, value: _T_con) -> bool: ...

@runtime
class LeastComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `<`
    """
    def __lt__(self, other: _T_con) -> bool: ...

@runtime
class GreaterComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `>`
    """
    def __gt__(self, other: _T_con) -> bool: ...

@runtime
class LeastEqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `<=`
    """
    def __le__(self, other: _T_con) -> bool: ...

@runtime
class GreaterEqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26b3

    Can be compared with `>=`
    """
    def __ge__(self, other: _T_con) -> bool: ...

@runtime
class EqualComparable(_pro[_T_con]):
    """
    \\@since 0.3.26c1

    Can be compared with `==`
    """
    def __eq__(self, other: _T_con) -> bool: ...

@runtime
class InequalComparable(_pro[_T_con]):
    """
    \\@since 0.3.26c1

    Can be compared with `!=`
    """
    def __ne__(self, other: _T_con) -> bool: ...


class Comparable(
    LeastComparable[_any],
    GreaterComparable[_any],
    LeastEqualComparable[_any],
    GreaterEqualComparable[_any],
    EqualComparable[_any],
    InequalComparable[_any],
    InComparable[_any]
):
    """
    \\@since 0.3.26b3

    An ABC supporting any form of comparison with operators \\
    `>`, `<`, `>=`, `<=`, `==`, `!=`, `in` (last 3 missing before 0.3.26c1)
    """
    ...

@runtime
class ReckonOperable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__reckon__`. It must return an integer, preferably \\
    zero or above to accord type returned by `reckon()` function. Invoked as \\
    `reckon(self)`. This  also simultaneously supports `abroad()` function, \\
    every its variations and as well as `reckon()` function variations.

    Comparing to `__len__`, this isn't official magic method.
    """
    def __reckon__(self) -> int:
        """
        \\@since 0.3.26c1

        Return `reckon(self)`.
        """
        ...

# @runtime
# class AbroadOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26c2?

    An ABC with one method `__abroad__`.

    This magic method is used for `abroad()` function
    """
    # def __abroad__(self) -> _T_cov: ...

@runtime
class LenOperable(_pro):
    """
    \\@since 0.3.26c1

    An ABC with one method `__len__`, which equals invoking `len(self)`.
    """
    def __len__(self) -> int: ...

class Sequence(abc2.Sequence[_T_cov]):
    "\\@since 0.3.26c2"
    ...

class MutableSequence(abc2.MutableSequence[_T_cov]):
    "\\@since 0.3.26c2"
    ...

class Mapping(abc2.Mapping[_KT, _VT]):
    "\\@since 0.3.26c2"
    ...

class MutableMapping(abc2.MutableMapping[_KT, _VT]):
    "\\@since 0.3.26c2"
    ...

class Uniqual(abc2.Set[_T_cov]):
    "\\@since 0.3.26c2. Equals `collections.abc.Set`"
    ...

class MutableUniqual(abc2.MutableSet[_T_cov]):
    "\\@since 0.3.26c2. Equals `collections.abc.MutableSet`"
    ...


@final
class FinalVar(NotReassignable[_T], NotIterable, Comparable, UnaryOperable): # 0.3.26b3
    """
    \\@since 0.3.26b3

    Indicates a name should be final, and may not be re-assigned. In this case, names \\
    marked with `tense.tcs.FinalVar` are treated as *immutable*, as constants.
    ```py \\
    reassign_me = 96000 # ok
    reassign_me += 3 # ok; gets value 96003
    reassign_me = FinalVar(96000) # ok
    reassign_me += 3 # error
    ```
    To receive value, use one of following:
    ```py \\
    f = FinalVar(69)
    Tense.print(+f) # 69
    Tense.print(-f) # 69
    Tense.print(~f) # 69
    Tense.print(f()) # 69, deprecated since 0.3.26c1
    Tense.print(f[0]) # 69, deprecated since 0.3.26c1
    Tense.print(f | 0) # 69, deprecated since 0.3.26c1
    Tense.print(f & 0) # 69, deprecated since 0.3.26c1
    Tense.print(f ^ 0) # 69, deprecated since 0.3.26c1
    Tense.print(f + 0) # 69, deprecated since 0.3.26c1
    Tense.print(f - 0) # 69, deprecated since 0.3.26c1
    Tense.print(f ** 0) # 69, deprecated since 0.3.26c1
    Tense.print(f << 0) # 69, deprecated since 0.3.26c1
    Tense.print(f >> 0) # 69, deprecated since 0.3.26c1
    Tense.print(abs(f)) # 69, deprecated since 0.3.26c1
    Tense.print(math.trunc(f)) # 69, deprecated since 0.3.26c1
    ```
    This class itself is final and cannot be subclassed (since 0.3.26c1)
    """
    __var = None
    __slots__ = ()
    def __await_internal_sentinel(self, code = 1):
        if code == 1:
            return _e(105, __class__.__qualname__)
        elif code == 2:
            return _e(112)
        elif code == 3:
            return _e(106)
        else:
            return _e(100)

    def __init__(self, v: _T):
        self.__var = v
    def __instancecheck__(self, o: object) -> bool:
        return isinstance(o, FinalVar)
    def __get__(self, instance: tp.Self, owner: _T = None) -> _T:
        """
        \\@since 0.3.26b3

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        return self.__var
    def __pos__(self) -> _T:
        """
        \\@since 0.3.26b3

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        return self.__var
    def __neg__(self) -> _T:
        """
        \\@since 0.3.26b3

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        return self.__var
    def __invert__(self) -> _T:
        """
        \\@since 0.3.26b3

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            return self.__var
    def __call__(self) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable via calling the instance
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
    def __getitem__(self, index: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable via calling the instance
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if index != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __or__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable via calling the instance
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __xor__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable via calling the instance
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __and__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable via calling the instance
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __pow__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __add__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __sub__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __abs__(self) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            return self.__var
    def __trunc__(self) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            return self.__var
    def __lshift__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __rshift__(self, other: _lit[0]) -> _T:
        """
        \\@since 0.3.26b3 \\
        \\@deprecated 0.3.26c1

        Receive value of the final variable
        """
        if self.__var is None:
            self.__await_internal_sentinel(1)
        else:
            if other != 0:
                self.__await_internal_sentinel(2)
            return self.__var
    def __lt__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        tmp = True
        if self.__var is None:
            self.__await_internal_sentinel(1)
        try:
            tmp = bool(self.__var < other)
        except (SyntaxError, TypeError, ValueError):
            self.__await_internal_sentinel(3)
        return tmp
    def __gt__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        tmp = True
        if self.__var is None:
            self.__await_internal_sentinel(1)
        try:
            tmp = bool(self.__var > other)
        except (SyntaxError, TypeError, ValueError):
            self.__await_internal_sentinel(3)
        return tmp
    def __le__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        tmp = True
        if self.__var is None:
            self.__await_internal_sentinel(1)
        try:
            tmp = bool(self.__var <= other)
        except (SyntaxError, TypeError, ValueError):
            self.__await_internal_sentinel(3)
        return tmp
    def __ge__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        tmp = True
        if self.__var is None:
            self.__await_internal_sentinel(1)
        try:
            tmp = bool(self.__var >= other)
        except (SyntaxError, TypeError, ValueError):
            self.__await_internal_sentinel(3)
        return tmp
    def __eq__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        return self.__var == other
    def __ne__(self, other: _T):
        """
        \\@since 0.3.26b3

        Comparisons specification
        """
        return self.__var != other
    def __contains__(self, value: _T):
        """
        \\@since 0.3.26c1

        Determine, whether a value equals the one inside final variable. This manner is \\
        definite exception as in case of iterable objects, which by default use the `in` \\
        keyword.

        In contrast to `==`, expected parameter becomes left operand instead of right.
        """
        return self.__var == value

class Abstract:
    """
    \\@since 0.3.26b3

    Class for abstract classes. Classes extending this class cannot \\
    be instantiated.

    Usage:
    ```py \\
    class AbstractClass(Abstract): ... # ok
    abstract_instance = AbstractClass() # error
    ```
    """
    __slots__ = ()
    def __init__(self, /, *args, **kwds):
        return _e(104, f" {__class__.__qualname__}")

def classvar(v: _T, /):
    """
    \\@since 0.3.26b3 (experimental)

    Transform variable in a class to a class variable.

    This will be valid only whether this function is \\
    invoked inside a class.
    Use it as:
    ```py \\
    class Example:
        test = classvar(96000) # has value 96000
    ```
    """
    class _t:
        _v: ClassVar[_T] = v
    return _t._v

def finalvar(v: _T, /):
    """
    \\@since 0.3.26b3

    Use it as:
    ```py \\
    reassign_me = finalvar(96000) # has value 96000
    reassign_me += 3 # error
    ```
    """
    return FinalVar(v)

class FinalClass:
    """
    \\@since 0.3.26b3 (experimental)

    This class disallows class inheritance. For class members use `final` decorator, \\
    which can also operate on classes

    Usage:
    ```py \\
    class FinalClassExample(FinalClass): ...
    class SubclassOfFinalClass(FinalClassExample): ... # error
    ```
    """
    __slots__ = ('__weakref__',)
    __final__ = True
    def __init_subclass__(cls, /, *args, **kwds):
        try:
            if super().__final__ is True:
                err, s = (TypeError, "Cannot subclass a final class")
                raise err(s)
        except (AttributeError, TypeError):
            pass
        if 'predicate_sentinel' not in kwds or ('predicate_sentinel' in kwds and kwds is not True):
             err, s = (TypeError, "Cannot subclass a final class")
             raise err(s)

class Deprecated:
    """
    \\@since 0.3.26b3 (experimental)

    This class marks a class as deprecated. Every keyword parameter accord to \\
    the ones `warnings.warn()` method has. Instead of `skip_file_prefixes` you \\
    can also use `skipFilePrefixes` and instead of `stacklevel` - `stackLevel`. \\
    Excluded is only `category` parameter, which has value `DeprecationWarning`.

    Parameters: `message`, `stacklevel`, `source`, `skip_file_prefixes`, as in:
    ```py \\
    class IAmDeprecatedClass(Deprecated, message = ..., stacklevel = ..., ...)
    ```
    """
    def __init_subclass__(cls, /, *args, **kwds):
        wa.simplefilter("always", DeprecationWarning)
        wa.warn(
            str(kwds["message"]) if "message" in kwds else "Deprecated class.",
            DeprecationWarning,
            int(kwds["stacklevel"]) if "stacklevel" in kwds else 2,
            kwds["source"] if "source" in kwds else None,
            skip_file_prefixes = kwds["skipFilePrefixes"] if "skipFilePrefixes" in kwds else kwds["skip_file_prefixes"] if "skip_file_prefixes" in kwds else ()
        )
        wa.simplefilter("default", DeprecationWarning)
"""
@runtime
class SupportsAbs(_pro[_T_cov]): # 0.3.26b3
    def __abs__(self) -> _T_cov: ...

@runtime
class SupportsInt(_pro): # 0.3.26b3 - 0.3.26c1
    def __int__(self) -> int: ...

@runtime
class SupportsIndex(_pro): # 0.3.26b3 - 0.3.26c1
    def __index__(self) -> int: ...

@runtime
class SupportsFloat(_pro): # 0.3.26b3 - 0.3.26c1
    def __float__(self) -> float: ...

@runtime
class SupportsBytes(_pro): # 0.3.26b3 - 0.3.26c1
    def __bytes__(self) -> bytes: ...
"""
"""@runtime
class SupportsItems(_pro[_KT_cov, _VT_cov]): # 0.3.26b3
    def items(self) -> tp.AbstractSet[tuple[_KT_cov, _VT_cov]]: ...

@runtime
class SupportsKeysAndGetItem(_pro[_KT_cov, _VT_cov]): # 0.3.26b3
    def keys(self) -> tp.Iterable[_KT_cov]: ...
    def __getitem__(self, key: _KT, /) -> _VT_cov: ...

@runtime
class SupportsLenAndGetItem(_pro[_T_con]): # 0.3.26b3
    def __len__(self) -> int: ...
    def __getitem__(self, k: int, /) -> _T_con: ...

@runtime
class SupportsContainsAndGetItem(_pro[_KT_con, _VT_cov]): # 0.3.26b3
    def __contains__(self, x: tp.Any, /) -> bool: ...
    def __getitem__(self, key: _KT_con, /) -> _VT_cov: ...

@runtime
class SupportsItemAccess(_pro[_KT_con, _VT_cov]):
    def __contains__(self, x: tp.Any, /) -> bool: ...
    def __getitem__(self, key: _KT_con, /) -> _KT: ...
    def __setitem__(self, key: _KT_con, value: _VT, /) -> None: ...
    def __delitem__(self, key: _KT_con, /) -> None: ...

@runtime
class SupportsAdd(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __add__(self, x: _T_con, /) -> _T_cov: ...

@runtime
class SupportsAddReflected(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __radd__(self, x: _T_con, /) -> _T_cov: ...

@runtime
class SupportsSub(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __sub__(self, x: _T_con, /) -> _T_cov: ...

@runtime
class SupportsSubReflected(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __rsub__(self, x: _T_con, /) -> _T_cov: ...

@runtime
class SupportsDivMod(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __divmod__(self, other: _T_con, /) -> _T_cov: ...

@runtime
class SupportsDivModReflected(_pro[_T_con, _T_cov]): # 0.3.26b3
    def __rdivmod__(self, other: _T_con, /) -> _T_cov: ..."""

@runtime
class Indexed(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c2
    
    An ABC with one method `__getitem__`, which equals `self[key]`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `key` parameter.
    """
    def __getitem__(self, key: _T_con) -> _T_cov: ...

@runtime
class AsyncIterable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__aiter__`. Returned type is addicted to covariant type parameter.
    """
    def __aiter__(self) -> abc2.AsyncIterator[_T_cov]: ...

AsyncIterableABC = abc2.AsyncIterable[_T]
"\\@since 0.3.26c2"

@runtime
class AsyncNextOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__anext__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __anext__(self) -> abc2.Awaitable[_T_cov]: ...

@runtime
class AsyncExitOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__aexit__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aexit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[ty.TracebackType] = None) -> abc2.Awaitable[_T_cov]: ...

@runtime
class AsyncEnterOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__aenter__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aenter__(self) -> abc2.Awaitable[_T_cov]: ...

@runtime
class ExitOperable(_pro):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__exit__`. Returned type is addicted to covariant type parameter.
    """
    def __exit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[ty.TracebackType] = None) -> bool: ...

@runtime
class EnterOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__enter__`. Returned type is addicted to covariant type parameter.
    """
    def __enter__(self) -> _T_cov: ...

@runtime
class Ceilable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__ceil__`, which equals `ceil(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __ceil__(self) -> _T_cov: ...

@runtime
class Floorable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__floor__`, which equals `floor(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __floor__(self) -> _T_cov: ...

@runtime
class NextOperable(_pro[_T_cov]):
    """
    \\@since 0.3.26b3

    An ABC with magic method `__next__`, which equals `next(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __next__(self) -> _T_cov: ...

@runtime
class AdditionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__add__`, which equals `self + other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __add__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__sub__`, which equals `self - other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __sub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__mul__`, which equals `self * other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__matmul__`, which equals `self @ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __matmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__truediv__`, which equals `self / other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __truediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__floordiv__`, which equals `self // other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __floordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class DivmodOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__divmod__`, which equals `divmod(self, other)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter \\
    first is type for `other` parameter.
    """
    def __divmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__mod__`, which equals `self % other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__pow__`, which equals `self ** other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __pow__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedAdditionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__radd__`, which equals `other + self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __radd__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedSubtractionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rsub__`, which equals `other - self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rsub__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rmul__`, which equals `other * self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMatrixMultiplicationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rmatmul__`, which equals `other @ self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedTrueDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rtruediv__`, which equals `other / self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rtruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedFloorDivisionOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rfloordiv__`, which equals `other // self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rfloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedDivmodOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rdivmod__`, which equals `divmod(other, self)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter; \\
    first is type for `other` parameter.
    """
    def __rdivmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedModuloOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rmod__`, which equals `other % self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedExponentiationOperable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__rpow__`, which equals `other ** self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rpow__(self, other: _T_con) -> _T_cov: ...

@runtime
class AdditionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__iadd__`, which equals `self += other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iadd__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__isub__`, which equals `self -= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __isub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__imul__`, which equals `self *= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__imatmul__`, which equals `self @= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionReassingable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__itruediv__`, which equals `self /= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __itruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__ifloordiv__`, which equals `self //= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ifloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__imod__`, which equals `self %= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationReassignable(_pro[_T_con, _T_cov]):
    """
    \\@since 0.3.26c1
    
    An ABC with magic method `__ipow__`, which equals `self **= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ipow__(self, other: _T_con) -> _T_cov: ...

class ReflectedArithmeticOperable(
    ReflectedAdditionOperable[_any, _any],
    ReflectedSubtractionOperable[_any, _any],
    ReflectedMultiplicationOperable[_any, _any],
    ReflectedMatrixMultiplicationOperable[_any, _any],
    ReflectedTrueDivisionOperable[_any, _any],
    ReflectedFloorDivisionOperable[_any, _any],
    ReflectedDivmodOperable[_any, _any],
    ReflectedModuloOperable[_any, _any]
):
    """
    \\@since 0.3.26c1

    An ABC supporting every kind (except bitwise) of reflected arithmetic operations with following operators:
    ```py \\
        + - * @ / // % ** divmod
    ```
    where left operand is `other` and right is `self`
    """
    ...

class ArithmeticOperable(
    AdditionOperable[_any, _any],
    SubtractionOperable[_any, _any],
    MultiplicationOperable[_any, _any],
    MatrixMultiplicationOperable[_any, _any],
    TrueDivisionOperable[_any, _any],
    FloorDivisionOperable[_any, _any],
    DivmodOperable[_any, _any],
    ModuloOperable[_any, _any],
    ExponentiationOperable[_any, _any],
    ReflectedArithmeticOperable
):
    """
    \\@since 0.3.26c1

    An ABC supporting every kind (except bitwise) of arithmetic operations, including their \\
    reflected equivalents, with following operators:
    ```py \\
        + - * @ / // % ** divmod
    ```
    Both `self` and `other` can be either left or right operands.
    """
    ...

class ArithmeticReassignable(
    AdditionReassignable[_any, _any],
    SubtractionReassignable[_any, _any],
    MultiplicationReassignable[_any, _any],
    MatrixMultiplicationReassignable[_any, _any],
    TrueDivisionReassingable[_any, _any],
    FloorDivisionReassignable[_any, _any],
    ModuloReassignable[_any, _any],
    ExponentiationReassignable[_any, _any]
):
    """
    \\@since 0.3.26c1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned arithmetic operations \\
    with following operators:
    ```py \\
        += -= *= @= /= //= %= **=
    ```
    """
    ...

class ArithmeticCollection(
    ArithmeticOperable,
    ArithmeticReassignable
):
    """
    \\@since 0.3.26c1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned and normal arithmetic operations \\
    with following operators:
    ```py \\
        + - * @ / // % ** divmod += -= *= @= /= //= %= **=
    ```
    """
    ...

class OperatorCollection(
    ArithmeticCollection,
    BitwiseCollection,
    UnaryOperable,
    Comparable
):
    """
    \\@since 0.3.26c1

    An ABC supporting every kind of augmented/re-assigned, reflected and normal arithmetic operations \\
    with following operators:
    ```py \\
        + - * @ / // % ** divmod & | ^ += -= *= @= /= //= %= **= &= |= ^=
    ```
    unary assignment with `+`, `-` and `~`, and comparison with following operators:
    ```py \\
        > < >= <= == != in
    ```
    """
    ...

class LenGetItemOperable(
    LenOperable,
    Indexed[int, _T_cov]
):
    """
    \\@since 0.3.26c2
    
    An ABC with `__geitem__` and `__len__` methods. Those are typical in sequences.
    """
    ...

RichComparable = _uni[LeastComparable[tp.Any], GreaterComparable[tp.Any]]

EnchantedBookQuantity = _lit[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36] # 0.3.26b3
FileType = _uni[str, int, bytes, os.PathLike[str], os.PathLike[bytes]] # 0.3.26b3
FileMode = _lit[
    'r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw', 'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+',
    'x+t', '+xt', 'tx+', 't+x', '+tx', 'w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx', 'r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr', 'rb+', 'r+b', '+rb',
    'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx', 'rb', 'br', 'rbU', 'rUb', 'Urb',
    'brU', 'bUr', 'Ubr', 'wb', 'bw', 'ab', 'ba', 'xb', 'bx'
] # 0.3.26b3
FileOpener = _cal[[str, int], int] # 0.3.26b3
TicTacToeBoard = list[list[str]] # 0.3.26b3

ReckonType = _uni[
        dict[_T],
        list[_T],
        tuple[_T, ...],
        str,
        ct.deque[_T],
        set[_T],
        bytes,
        bytearray,
        memoryview,
        range,
        mmap,
        array[_T],
        enumerate[_T],
        frozenset[_T],
        ct.Counter[_T],
        ct.defaultdict[_T],
        io.TextIOWrapper,
        # since 0.3.24
        io.FileIO,
        io.BufferedWriter,
        io.BufferedRandom,
        io.BufferedReader,
        tp.IO[tp.Any],
        # since 0.3.25
        tp.TextIO,
        tp.BinaryIO,
        io.StringIO,
        io.BufferedRWPair,
        tp.Sequence[_T],
        tp.MutableSequence[_T],
        io.BytesIO,
        io.BufferedIOBase,
        tp.Mapping[_T, tp.Any],
        tp.MutableMapping[_T, tp.Any],
        tp.MutableSet[_T],
        tp.AbstractSet[_T],
        tp.Iterable[_T],
        ct.ChainMap[_T],
        ct.OrderedDict[_T],
        # 0.3.26b3
        tp.AsyncIterable[_T],
        # 0.3.26c1
        ReckonOperable,
        tk.StringVar
] # since 0.3.25
"""
\\@since 0.3.25 \\
\\@author Aveyzan
```ts \\
in module tense.tcs // to 0.3.26b3 in module tense.types
```
Package of types, which are considered countable and satisfy type requirement \\
for function `reckon()`. To 0.3.26b3 also known as `SupportsCountables`.
"""
ReckonNGT = _uni[
        dict,
        list,
        tuple,
        str,
        ct.deque,
        set,
        bytes,
        bytearray,
        memoryview,
        range,
        mmap,
        array,
        enumerate,
        frozenset,
        ct.Counter,
        ct.defaultdict,
        io.TextIOWrapper,
        # since 0.3.24
        io.FileIO,
        io.BufferedWriter,
        io.BufferedRandom,
        io.BufferedReader,
        tp.IO,
        # since 0.3.25
        tp.TextIO,
        tp.BinaryIO,
        io.StringIO,
        io.BufferedRWPair,
        tp.Sequence,
        tp.MutableSequence,
        io.BytesIO,
        io.BufferedIOBase,
        tp.Mapping,
        tp.MutableMapping,
        tp.MutableSet,
        tp.AbstractSet,
        tp.Iterable,
        ct.ChainMap,
        ct.OrderedDict,
        # 0.3.26c1
        tp.AsyncIterable,
        ReckonOperable,
        tk.StringVar
] # since 0.3.25, renamed from SupportsCountablesLackOfGeneric (0.3.26b3)


ColorType = _opt[_uni[_T, str, tuple[_T, _T, _T]]] # since 0.3.25, renamed from SupportsColor (0.3.26b3)
ColourType = ColorType[_T] # 0.3.26b3
AbroadValue1 = _uni[int, float, complex, ReckonType[_T]] # since 0.3.25, renamed from SupportsAbroadValue1 (0.3.26b3)
AbroadValue2 = _opt[_uni[int, float, bool, ReckonType[_T], Ellipsis]] # since 0.3.25, renamed from SupportsAbroadValue2 (0.3.26b3)
AbroadModifier = _opt[_uni[AbroadValue1[_T], Ellipsis]] # since 0.3.25, renamed from SupportsAbroadModifier (0.3.26b3)
ModernReplace = _uni[list[_T], tuple[_T, ...], _T] # since 0.3.25, expected string; renamed from SupportsModernReplace (0.3.26b3)
PickSequence = _uni[list[_T], tuple[_T, ...], set[_T], frozenset[_T], ct.deque[_T], tp.Sequence[_T], tp.MutableSequence[_T]] # since 0.3.25, added support for Sequence and MutableSequence, renamed from SupportsPick (0.3.26b3)
SanitizeMode = _lit[0, 1, 2, 3, 4, 5] # since 0.3.25, renamed from SupportsSanitizeMode (0.3.26b3)
TenseVersionType = tuple[_T, _T, _T] # since 0.3.25, renamed from SupportsTenseVersion (0.3.26b3)
AbroadPackType = _uni[list[_T], tuple[_T, ...], ct.deque[_T], set[_T], enumerate[_T], frozenset[_T]] # since 0.3.25, lose of dict and defaultdict support, added frozenset, renamed from SupportsAbroadPackValues (0.3.26b3)
AbroadConvectType = AbroadValue1[_T] # since 0.3.25, renamed from SupportsAbroadConvectValues (0.3.26b3)
AbroadLiveType = AbroadConvectType[_T] # since 0.3.25, renamed from SupportsAbroadLiveValues (0.3.26b3)
AbroadVividType = _uni[tuple[AbroadValue1[_V1]], tuple[AbroadValue1[_V1], AbroadValue2[_V2]], tuple[AbroadValue1[_V1], AbroadValue2[_V2], AbroadModifier[_M]]] # since 0.3.25, renamed from SupportsAbroadVividValues (0.3.26)
# SupportsAbroadDivisor = _uni[int, float] # for 0.3.25 - 0.3.26b3, use FloatOrInteger instead
AbroadInitializer = list[_T] # since 0.3.25
AbroadMultiInitializer = list[list[_T]] # since 0.3.25
FloatOrInteger = _uni[int, float] # since 0.3.25
ProbabilityType = _uni[_T, list[_opt[_T]], tuple[_T, _opt[_T]], dict[_T, _opt[_T]], ct.deque[_opt[_T]], set[_opt[_T]], frozenset[_opt[_T]]] # since 0.3.25, expected integer; renamed from SupportsProbabilityValuesAndFrequencies (0.3.26b3)
ShuffleType = _uni[str, list[_T], tp.MutableSequence[_T]] # since 0.3.26c1
TypeOrFinalVarType = _uni[_T, FinalVar[_T]] # since 0.3.26c1

_IntegerConvertible = _uni[str, Buffer, IntegerConvertible, Indexable, Truncable] # since 0.3.26c1
_FloatConvertible = _uni[str, Buffer, FloatConvertible, Indexable] # since 0.3.26c1
_ComplexConvertible = _uni[complex, FloatConvertible, Indexable] # since 0.3.26c1

class Integer:
    """
    \\@since 0.3.26b3
    
    Equivalent to `int`. Once instantiated, it returns \\
    integer of type `int`. (0.3.26c1)
    """
    def __new__(cls, x: _IntegerConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `int`. Once instantiated, it returns \\
        integer of type `int`. (0.3.26c1)
        """
        return int(x)
    def __instancecheck__(self, obj: object, /) -> TypeIs[int]:
        return isinstance(obj, int)

class Float:
    """
    \\@since 0.3.26b3
    
    Equivalent to `float`. Once instantiated, it returns \\
    number of type `float`. (0.3.26c1)
    """
    def __new__(cls, x: _FloatConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `float`. Once instantiated, it returns \\
        number of type `float`. (0.3.26c1)
        """
        return float(x)
    def __instancecheck__(self, obj: object, /) -> TypeIs[float]:
        return isinstance(obj, float)
    
class Complex:
    """
    \\@since 0.3.26b3
    
    Equivalent to `complex`. Once instantiated, it returns \\
    number of type `complex`. (0.3.26c1)
    """
    def __new__(cls, r: _uni[ComplexConvertible, _ComplexConvertible] = ..., i: _ComplexConvertible = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `complex`. Once instantiated, it returns \\
        number of type `complex`. (0.3.26c1)
        """
        return complex(r, i)
    def __instancecheck__(self, obj: object, /) -> TypeIs[complex]:
        return isinstance(obj, complex)
    
class String:
    """
    \\@since 0.3.26b3
    
    Equivalent to `str`. Once instantiated, it returns \\
    string of type `str`. (0.3.26c1)
    """
    def __new__(cls, x: object = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `str`. Once instantiated, it returns \\
        string of type `str`. (0.3.26c1)
        """
        return str(x)
    def __instancecheck__(self, obj: object, /) -> TypeIs[str]:
        return isinstance(obj, str)

class Boolean:
    """
    \\@since 0.3.26b3
    
    Equivalent to `bool`. Once instantiated, it returns \\
    boolean of type `bool`. (0.3.26c1)
    """
    def __new__(cls, x: object = ..., /):
        """
        \\@since 0.3.26b3
        
        Equivalent to `bool`. Once instantiated, it returns \\
        boolean of type `bool`. (0.3.26c1)
        """
        return bool(x)
    def __instancecheck__(self, obj: object, /) -> TypeIs[bool]:
        return obj is True or obj is False


List = list[_T] # 0.3.26b3
"\\@since 0.3.26b3"
Tuple = tuple[_T, ...] # 0.3.26b3
"\\@since 0.3.26b3"
Deque = ct.deque[_T] # 0.3.26b3
"\\@since 0.3.26b3"
Array = array[_T] # 0.3.26b3
"\\@since 0.3.26b3"
Dict = dict[_KT, _VT] # 0.3.26b3
"\\@since 0.3.26b3"
Bytes = bytes # 0.3.26b3
"\\@since 0.3.26b3"
ByteArray = bytearray # 0.3.26b3
"\\@since 0.3.26b3"
Filter = filter # 0.3.26b3
"\\@since 0.3.26b3"
Type = type # 0.3.26b3
"\\@since 0.3.26b3"
TypeVar = tp.TypeVar # 0.3.26b3
"\\@since 0.3.26b3"
Zip = zip # 0.3.26b3
"\\@since 0.3.26b3"
Slice = slice # 0.3.26c1
"\\@since 0.3.26c1"

assert_type = _ase # 0.3.26c1
"\\@since 0.3.26c1"
assert_never = _asn # 0.3.26c1
"\\@since 0.3.26c1"
reveal_type = _rev # 0.3.26c1
"\\@since 0.3.26c1"
dataclass_transform = _dat # 0.3.26c1
"\\@since 0.3.26c1"
get_overloads = _get # 0.3.26c1
"\\@since 0.3.26c1"
clear_overloads = _cle # 0.3.26c1
"\\@since 0.3.26c1"
Unzip = Unpack # 0.3.26b3
"\\@since 0.3.26b3"
Void = NoReturn # 0.3.26b3
"\\@since 0.3.26b3"
Enumerate = enumerate[_T] # 0.3.26b3
"\\@since 0.3.26b3"
classmember = classmethod
"\\@since 0.3.26b3"
staticmember = staticmethod
"\\@since 0.3.26b3"
abstractmember = abstract
"\\@since 0.3.26b3 (as alias to decorator function `abstract()`)"

if __name__ == "__main__":
    _e(111)

del os, ma, mmap, array, copy, tp, tpe, ty, ct, io, tk, wa, fn, abc, abc2, aio, sb, enum, ins, zi, url # Not for export

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__dir__ = __all__
