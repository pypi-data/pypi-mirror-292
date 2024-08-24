from .core.file import has_hidden_attribute
from .core.timely_property import timely_property, timely_cls_property
from .core.bit_operation import xor_encrypt
from .core.string import is_fstring, extract_fstring_keys
from .core.dicts import flatten_nested_dict, parse_dotted_dict
from .core.cls_property import classProperty

from .struct.does_nothing import NothingInstance
from .struct.frozen_dict import FrozenDict
from .struct.folder_watcher import FolderWatcher
# from .struct.file_property import FileProperty
from .struct.simple_io_dict import SimpleIODict, SimpleIOLooseDict