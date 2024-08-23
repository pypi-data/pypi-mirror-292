import sys
import csv
import json
import pickle
import typing

from configparser import ConfigParser

from _io import FileIO

from systempath import *

from typing import *

if typing.TYPE_CHECKING:
    from configparser import Interpolation

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = TypeVar('TypeAlias')

try:
    import yaml
except ModuleNotFoundError:
    yaml = None
else:
    YamlLoader: TypeAlias = Union[
        Type[yaml.BaseLoader],
        Type[yaml.Loader],
        Type[yaml.FullLoader],
        Type[yaml.SafeLoader],
        Type[yaml.UnsafeLoader]
    ]
    YamlDumper: TypeAlias = Union[
        Type[yaml.BaseDumper],
        Type[yaml.Dumper],
        Type[yaml.SafeDumper]
    ]

import exceptionx as ex

ConvertersMap:       TypeAlias = Dict[str, Callable[[str], Any]]
CSVDialectLike:      TypeAlias = Union[str, csv.Dialect, Type[csv.Dialect]]
JsonObjectHook:      TypeAlias = Callable[[Dict[Any, Any]], Any]
JsonObjectParse:     TypeAlias = Callable[[str], Any]
JsonObjectPairsHook: TypeAlias = Callable[[List[Tuple[Any, Any]]], Any]
FileNewline:         TypeAlias = Literal['', '\n', '\r', '\r\n']
YamlDumpStyle:       TypeAlias = Literal['|', '>', '|+', '>+']


class CSVReader(Iterator[List[str]]):
    line_num: int

    @property
    def dialect(self) -> csv.Dialect:
        ...

    def __next__(self) -> List[str]:
        ...


class CSVWriter:

    @property
    def dialect(self) -> csv.Dialect:
        ...

    def writerow(self, row: Iterable[Any]) -> Any:
        ...

    def writerows(self, rows: Iterable[Iterable[Any]]) -> None:
        ...


class File2(File):

    @property
    def ini(self):
        return INI(self)

    @property
    def csv(self):
        return CSV(self)

    @property
    def json(self):
        return JSON(self)

    @property
    def yaml(self):
        return YAML(self)


class INI:
    """Class to read and parse INI file."""

    def __init__(self, file: File, /):
        self.file = file

    def read(
            self,
            encoding:                Optional[str]               = None,
            *,
            defaults:                Optional[Mapping[str, str]] = None,
            dict_type:               Type[Mapping[str, str]]     = dict,
            allow_no_value:          bool                        = False,
            delimiters:              Sequence[str]               = ('=', ':'),
            comment_prefixes:        Sequence[str]               = ('#', ';'),
            inline_comment_prefixes: Optional[Sequence[str]]     = None,
            strict:                  bool                        = True,
            empty_lines_in_values:   bool                        = True,
            default_section:         str                         = 'DEFAULT',
            interpolation:           Optional['Interpolation']   = None,
            converters:              Optional[ConvertersMap]     = None
    ) -> ConfigParser:
        """
        Read and parse the INI file.

        @param encoding
            The encoding used to read files is usually specified as "UTF-8". The
            default encoding is platform-based, and
            `locale.getpreferredencoding(False)` is called to obtain the current
            locale encoding. For a list of supported encodings, please refer to
            the `codecs` module.

        @param defaults
            A dictionary containing default key-value pairs to use if some
            options are missing in the parsed configuration file.

        @param dict_type
            The type used to represent the returned dictionary. The default is
            `dict`, which means that sections and options in the configuration
            will be preserved in the order they appear in the file.

        @param allow_no_value
            A boolean specifying whether options without values are allowed. If
            set to True, lines like `key=` will be accepted and the value of key
            will be set to None.

        @param delimiters
            A sequence of characters used to separate keys and values. The
            default is `("=", ":")`, which means both "=" and ":" can be used as
            delimiters.

        @param comment_prefixes
            A sequence of prefixes used to identify comment lines. The default
            is `("#", ";")`, which means lines starting with "#" or ";" will be
            considered comments.

        @param inline_comment_prefixes
            A sequence of prefixes used to identify inline comments. The default
            is None, which means inline comments are not supported.

        @param strict
            A boolean specifying whether to parse strictly. If set to True, the
            parser will report syntax errors, such as missing sections or
            incorrect delimiters.

        @param empty_lines_in_values
            A boolean specifying whether empty lines within values are allowed.
            If set to True, values can span multiple lines, and empty lines will
            be preserved.

        @param default_section
            The name of the default section in the configuration file. If
            specified, any options not belonging to any section during parsing
            will be added to this default section.

        @param interpolation
            Specifies the interpolation type. Interpolation is a substitution
            mechanism that allows values in the configuration file to reference
            other values. Supports `configparser.BasicInterpolation` and
            `configparser.ExtendedInterpolation`.

        @param converters
            A dictionary containing custom conversion functions used to convert
            string values from the configuration file to other types. The keys
            are the names of the conversion functions, and the values are the
            corresponding conversion functions.
        """
        kw = {}
        if interpolation is not None:
            kw['interpolation'] = interpolation
        if converters is not None:
            kw['converters'] = converters
        config = ConfigParser(
            defaults               =defaults,
            dict_type              =dict_type,
            allow_no_value         =allow_no_value,
            delimiters             =delimiters,
            comment_prefixes       =comment_prefixes,
            inline_comment_prefixes=inline_comment_prefixes,
            strict                 =strict,
            empty_lines_in_values  =empty_lines_in_values,
            default_section        =default_section,
            **kw
        )
        config.read(self.file, encoding=encoding)
        return config


class CSV:
    """A class to handle CSV file reading and writing operations."""

    def __init__(self, file: File, /):
        self.file = file

    def reader(
            self,
            dialect:          CSVDialectLike = 'excel',
            *,
            delimiter:        str            = ',',
            quotechar:        Optional[str]  = '"',
            escapechar:       Optional[str]  = None,
            doublequote:      bool           = True,
            skipinitialspace: bool           = False,
            lineterminator:   str            = '\r\n',
            quoting:          int            = 0,
            strict:           bool           = False
    ) -> CSVReader:
        """
        Create a CSV reader object.

        @param dialect:
            The dialect to use for the CSV file format. A dialect is a set of
            specific parameters that define the format of a CSV file, such as
            the delimiter, quote character, etc. "excel" is a commonly used
            default dialect that uses a comma as the delimiter and a double
            quote as the quote character.

        @param delimiter:
            The character used to separate fields. The default in the "excel"
            dialect is a comma.

        @param quotechar:
            The character used to quote fields. The default in the "excel"
            dialect is a double quote.

        @param escapechar:
            The character used to escape field content, default is None. If a
            field contains the delimiter or quote character, the escape
            character can be used to avoid ambiguity.

        @param doublequote:
            If True (the default), quote characters in fields will be doubled.
            For example, "Hello, World" will be written as \"""Hello, World\""".

        @param skipinitialspace:
            If True, whitespace immediately following the delimiter is ignored.
            The default is False.

        @param lineterminator:
            The string used to terminate lines. The default is "\r\n", i.e.,
            carriage return plus line feed.

        @param quoting:
            Controls when quotes should be generated by the writer and
            recognized by the reader. It can be any of the following values:
                0: Indicates that quotes should only be used when necessary
                   (for example, when the field contains the delimiter or quote
                   character);
                1: Indicates that quotes should always be used;
                2: Indicates that quotes should never be used;
                3: Indicates that double quotes should always be used.

        @param strict:
            If True, raise errors for CSV format anomalies (such as extra quote
            characters). The default is False, which does not raise errors.
        """
        return csv.reader(
            Open(self.file).r(newline=''), dialect,
            delimiter       =delimiter,
            quotechar       =quotechar,
            escapechar      =escapechar,
            doublequote     =doublequote,
            skipinitialspace=skipinitialspace,
            lineterminator  =lineterminator,
            quoting         =quoting,
            strict          =strict
        )

    def writer(
            self,
            /,
            dialect:          CSVDialectLike    = 'excel',
            *,
            mode:             Literal['w', 'a'] = 'w',
            encoding:         Optional[str]     = None,
            delimiter:        str               = ',',
            quotechar:        Optional[str]     = '"',
            escapechar:       Optional[str]     = None,
            doublequote:      bool              = True,
            skipinitialspace: bool              = False,
            lineterminator:   str               = '\r\n',
            quoting:          int               = 0,
            strict:           bool              = False
    ) -> CSVWriter:
        """
        Create a CSV writer object.

        @param dialect:
            The dialect to use for the CSV file format. A dialect is a set of
            specific parameters that define the format of a CSV file, such as
            the delimiter, quote character, etc. "excel" is a commonly used
            default dialect that uses a comma as the delimiter and a double
            quote as the quote character.

        @param mode
            The mode to open the file, only "w" or "a" are supported.

        @param encoding
            Specify the output encoding, usually specified as "UTF-8". The
            default encoding is based on the platform, call
            `locale.getpreferredencoding(False)` to get the current locale
            encoding. See the `codecs` module for a list of supported encodings.

        @param delimiter:
            The character used to separate fields. The default in the "excel"
            dialect is a comma.

        @param quotechar:
            The character used to quote fields. The default in the "excel"
            dialect is a double quote.

        @param escapechar:
            The character used to escape field content, default is None. If a
            field contains the delimiter or quote character, the escape
            character can be used to avoid ambiguity.

        @param doublequote:
            If True (the default), quote characters in fields will be doubled.
            For example, "Hello, World" will be written as \"""Hello, World\""".

        @param skipinitialspace:
            If True, whitespace immediately following the delimiter is ignored.
            The default is False.

        @param lineterminator:
            The string used to terminate lines. The default is "\r\n", i.e.,
            carriage return plus line feed.

        @param quoting:
            Controls when quotes should be generated by the writer and
            recognized by the reader. It can be any of the following values:
                0: Indicates that quotes should only be used when necessary
                   (for example, when the field contains the delimiter or quote
                   character);
                1: Indicates that quotes should always be used;
                2: Indicates that quotes should never be used;
                3: Indicates that double quotes should always be used.

        @param strict:
            If True, raise errors for CSV format anomalies (such as extra quote
            characters). The default is False, which does not raise errors.
        """
        if mode not in ('w', 'a'):
            raise ex.ParameterError(
                f'parameter "mode" must be "w" or "a", not {mode!r}.'
            )
        return csv.writer(
            getattr(Open(self.file), mode)(encoding=encoding, newline=''),
            dialect,
            delimiter       =delimiter,
            quotechar       =quotechar,
            escapechar      =escapechar,
            doublequote     =doublequote,
            skipinitialspace=skipinitialspace,
            lineterminator  =lineterminator,
            quoting         =quoting,
            strict          =strict
        )


class JSON:
    """A class for handling JSON operations with a file object. It provides
    methods for loading JSON data from a file and dumping Python objects into a
    file as JSON."""

    def __init__(self, file: File, /):
        self.file = file

    def load(
            self,
            *,
            cls:               Type[json.JSONDecoder]        = json.JSONDecoder,
            object_hook:       Optional[JsonObjectHook]      = None,
            parse_float:       Optional[JsonObjectParse]     = None,
            parse_int:         Optional[JsonObjectParse]     = None,
            parse_constant:    Optional[JsonObjectParse]     = None,
            object_pairs_hook: Optional[JsonObjectPairsHook] = None
    ) -> Any:
        """
        Load JSON data from the file.

        @param cls
            Specifies the class used for decoding JSON data. By default,
            `json.JSONDecoder` is used. You can customize the decoding process
            by inheriting from `json.JSONDecoder` and overriding its methods.

        @param object_hook
            This function will be used to decode dictionaries. It takes a
            dictionary as input, allows you to modify the dictionary or convert
            it to another type of object, and then returns it. This allows you
            to customize the data structure immediately after parsing JSON.

        @param parse_float
            This function will be used to decode floating-point numbers in JSON.
            By default, floating-point numbers are parsed into Python's float
            type. You can change this behavior by providing a custom function.

        @param parse_int
            This function will be used to decode integers in JSON. By default,
            integers are parsed into Python's int type. You can change this
            behavior by providing a custom function.

        @param parse_constant
            This function will be used to decode special constants in JSON (such
            as `Infinity`, `NaN`). By default, these constants are parsed into
            Python's `float("inf")` and `float("nan")`. You can change this
            behavior by providing a custom function.

        @param object_pairs_hook
            This function will be used to decode JSON objects. It takes a list
            of key-value pairs as input, allows you to convert these key-value
            pairs into another type of object, and then returns it. For example,
            you can use it to convert JSON objects to `gqylpy_dict.gdict`, which
            supports accessing and modifying key-value pairs in the dictionary
            using the dot operator.
        """
        return cls(
            object_hook      =object_hook,
            parse_float      =parse_float,
            parse_int        =parse_int,
            parse_constant   =parse_constant,
            object_pairs_hook=object_pairs_hook
        ).decode(self.file.content)

    def dump(
            self,
            obj:            Any,
            *,
            skipkeys:       bool                           = False,
            ensure_ascii:   bool                           = True,
            check_circular: bool                           = True,
            allow_nan:      bool                           = True,
            cls:            Type[json.JSONEncoder]         = json.JSONEncoder,
            indent:         Optional[Union[int, str]]      = None,
            separators:     Optional[Tuple[str, str]]      = None,
            default:        Optional[Callable[[Any], Any]] = None,
            sort_keys:      bool                           = False,
            **kw
    ) -> None:
        """
        Dump a Python object into the file as JSON.

        @param obj
            The Python object you want to convert to JSON format and write to
            the file.

        @param skipkeys
            If True (default is False), dictionary keys that are not of a basic
            type (str, int, float, bool, None) will be skipped during the
            encoding process.

        @param ensure_ascii
            If True (default), all non-ASCII characters in the output will be
            escaped. If False, these characters will be output as-is.

        @param check_circular
            If True (default), the function will check for circular references
            in the object and raise a `ValueError` if found. If False, no such
            check will be performed.

        @param allow_nan
            If True (default), `NaN`, `Infinity`, and `-Infinity` will be
            encoded as JSON. If False, these values will raise a `ValueError`.

        @param cls
            Specifies a custom encoder class, which should inherit from
            `json.JSONEncoder`. This class can be used to implement custom
            serialization methods.

        @param indent
            Specifies the number of spaces for indentation for prettier output.
            If None (default), the most compact representation will be used.

        @param separators
            A `(item_separator, key_separator)` tuple used to specify
            separators. The default separators are `(", ", ": ")`. If the
            `indent` parameter is specified, this parameter will be ignored.

        @param default
            A function that will be used to convert objects that cannot be
            serialized. This function should take an object as input and return
            a serializable version.

        @param sort_keys
            If True (default is False), the output of dictionaries will be
            sorted by key order.
        """
        return json.dump(
            obj, Open(self.file).w(),
            skipkeys      =skipkeys,
            ensure_ascii  =ensure_ascii,
            check_circular=check_circular,
            allow_nan     =allow_nan,
            cls           =cls,
            indent        =indent,
            separators    =separators,
            default       =default,
            sort_keys     =sort_keys,
            **kw
        )


class YAML:
    """A class for handling YAML operations with a file object. It provides
    methods for loading YAML data from a file and dumping Python objects into a
    file as YAML."""

    def __init__(self, file: File, /):
        if yaml is None:
            raise ModuleNotFoundError(
                'dependency has not been installed, '
                'run `pip3 install systempath[pyyaml]`.'
            )
        self.file = file

    def load(self, loader: Optional['YamlLoader'] = None) -> Any:
        """
        Load YAML data from the file.

        @param loader
            Specify a loader class to control how the YAML stream is parsed.
            Defaults to `yaml.SafeLoader`. The YAML library provides different
            loaders, each with specific uses and security considerations.

            `yaml.FullLoader`:
                This is the default loader that can load the full range of YAML
                functionality, including arbitrary Python objects. However, due
                to its ability to load arbitrary Python objects, it may pose a
                security risk as it can load and execute arbitrary Python code.

            `yaml.SafeLoader`:
                This loader is safe, allowing only simple YAML tags to be
                loaded, preventing the execution of arbitrary Python code. It is
                suitable for loading untrusted or unknown YAML content.

            `yaml.Loader` & `yaml.UnsafeLoader`:
                These loaders are similar to `FullLoader` but provide fewer
                security guarantees. They allow loading of nearly all YAML tags,
                including some that may execute arbitrary code.

            Through this parameter, you can choose which loader to use to
            balance functionality and security. For example, if you are loading
            a fully trusted YAML file and need to use the full range of YAML
            functionality, you can choose `yaml.FullLoader`. If you are loading
            an unknown or not fully trusted YAML file, you should choose
            `yaml.SafeLoader` to avoid potential security risks.
        """
        return yaml.load(FileIO(self.file), loader or yaml.SafeLoader)

    def load_all(self, loader: Optional['YamlLoader'] = None) -> Iterator[Any]:
        """
        Load all YAML documents from the file.

        @param loader
            Specify a loader class to control how the YAML stream is parsed.
            Defaults to `yaml.SafeLoader`. The YAML library provides different
            loaders, each with specific uses and security considerations.

            `yaml.FullLoader`:
                This is the default loader that can load the full range of YAML
                functionality, including arbitrary Python objects. However, due
                to its ability to load arbitrary Python objects, it may pose a
                security risk as it can load and execute arbitrary Python code.

            `yaml.SafeLoader`:
                This loader is safe, allowing only simple YAML tags to be
                loaded, preventing the execution of arbitrary Python code. It is
                suitable for loading untrusted or unknown YAML content.

            `yaml.Loader` & `yaml.UnsafeLoader`:
                These loaders are similar to `FullLoader` but provide fewer
                security guarantees. They allow loading of nearly all YAML tags,
                including some that may execute arbitrary code.

            Through this parameter, you can choose which loader to use to
            balance functionality and security. For example, if you are loading
            a fully trusted YAML file and need to use the full range of YAML
            functionality, you can choose `yaml.FullLoader`. If you are loading
            an unknown or not fully trusted YAML file, you should choose
            `yaml.SafeLoader` to avoid potential security risks.
        """
        return yaml.load_all(FileIO(self.file), loader or yaml.SafeLoader)

    def dump(
            self,
            data: Any,
            /,
            dumper:             Optional['YamlDumper']      = None,
            *,
            default_style:      Optional[str]               = None,
            default_flow_style: bool                        = False,
            canonical:          Optional[bool]              = None,
            indent:             Optional[int]               = None,
            width:              Optional[int]               = None,
            allow_unicode:      Optional[bool]              = None,
            line_break:         Optional[str]               = None,
            encoding:           Optional[str]               = None,
            explicit_start:     Optional[bool]              = None,
            explicit_end:       Optional[bool]              = None,
            version:            Optional[Tuple[int, int]]   = None,
            tags:               Optional[Mapping[str, str]] = None,
            sort_keys:          bool                        = True
    ) -> None:
        """Dump Python object to the YAML file."""
        return yaml.dump_all(
            [data], Open(self.file).w(), dumper or yaml.Dumper,
            default_style     =default_style,
            default_flow_style=default_flow_style,
            canonical         =canonical,
            indent            =indent,
            width             =width,
            allow_unicode     =allow_unicode,
            line_break        =line_break,
            encoding          =encoding,
            explicit_start    =explicit_start,
            explicit_end      =explicit_end,
            version           =version,
            tags              =tags,
            sort_keys         =sort_keys
        )

    def dump_all(
            self,
            documents:          Iterable[Any],
            /,
            dumper:             Optional['YamlLoader']      = None,
            *,
            default_style:      Optional[YamlDumpStyle]     = None,
            default_flow_style: bool                        = False,
            canonical:          Optional[bool]              = None,
            indent:             Optional[int]               = None,
            width:              Optional[int]               = None,
            allow_unicode:      Optional[bool]              = None,
            line_break:         Optional[FileNewline]       = None,
            encoding:           Optional[str]               = None,
            explicit_start:     Optional[bool]              = None,
            explicit_end:       Optional[bool]              = None,
            version:            Optional[Tuple[int, int]]   = None,
            tags:               Optional[Mapping[str, str]] = None,
            sort_keys:          bool                        = True
    ) -> ...:
        """
        Dump all Python object to the YAML file.

        @param documents
            A list of Python objects to serialize as YAML. Each object will be
            serialized as a YAML document.

        @param dumper
            An instance of a Dumper class used to serialize documents. If not
            specified, the default `yaml.Dumper` class will be used.

        @param default_style
            Used to define the style for strings in the output, default is None.
            Options include ("|", ">", "|+", ">+"). Where "|" is used for
            literal style and ">" is used for folded style.

        @param default_flow_style
            A boolean value, default is False, specifying whether to use flow
            style by default. Flow style is a compact representation that does
            not use the traditional YAML block style for mappings and lists.

        @param canonical
            A boolean value specifying whether to output canonical YAML.
            Canonical YAML output is unique and does not depend on the Python
            object's representation.

        @param indent
            Used to specify the indentation level for block sequences and
            mappings. The default is 2.

        @param width
            Used to specify the width for folded styles. The default is 80.

        @param allow_unicode
            A boolean value specifying whether Unicode characters are allowed
            in the output.

        @param line_break
            Specifies the line break character used in block styles. Can be
            None, "\n", "\r", or "\r\n".

        @param encoding
            Specify the output encoding, usually specified as "UTF-8". The
            default encoding is based on the platform, call
            `locale.getpreferredencoding(False)` to get the current locale
            encoding. See the `codecs` module for a list of supported encodings.

        @param explicit_start
            A boolean value specifying whether to include a YAML directive
            (`%YAML`) in the output.

        @param explicit_end
            A boolean value specifying whether to include an explicit document
            end marker (...) in the output.

        @param version
            Used to specify the YAML version as a tuple. Can be, for example,
            `(1, 0)`, `(1, 1)`, or `(1, 2)`.

        @param tags
            A dictionary used to map Python types to YAML tags

        @param sort_keys
            A boolean value specifying whether to sort the keys of mappings in
            the output. The default is True.
        """
        return yaml.dump_all(
            documents, Open(self.file).w(), dumper or yaml.Dumper,
            default_style     =default_style,
            default_flow_style=default_flow_style,
            canonical         =canonical,
            indent            =indent,
            width             =width,
            allow_unicode     =allow_unicode,
            line_break        =line_break,
            encoding          =encoding,
            explicit_start    =explicit_start,
            explicit_end      =explicit_end,
            version           =version,
            tags              =tags,
            sort_keys         =sort_keys
        )


if __name__ == '__main__':
    ff = File2('tree/x.yaml')

    # x = ff.csv.reader()
    # print(list(x))

    data = [
        ['Name', 'Age', 'City'],
        ['Alice', '30', 'New York'],
        ['Bob', '25', 'Los Angeles'],
        ['Name', 'Age', 'City'],
        ['Alice', '30', 'New York'],
        ['Bob', '25', 'Los Angeles']
    ]

    x =ff.yaml.dump_all(data)
    print(x)

