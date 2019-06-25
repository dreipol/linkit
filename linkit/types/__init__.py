from linkit.types.file import FileType
from linkit.types.input import InputType
from linkit.types.manager import type_manager
from linkit.types.page import PageType

# Register default types we ship out of the box
type_manager.register(PageType)
type_manager.register(FileType)
type_manager.register(InputType)
