from typing import Protocol, runtime_checkable


@runtime_checkable
class Stringable(Protocol):
    """An object that can be converted to a string,
    i.e., one that defines a `__str__` method.
    """
    def __str__(self) -> str:
        ...


ElementContent = Stringable

ElementContentInput = (
    ElementContent
    | list[ElementContent]
    | tuple[ElementContent]
    | dict[str | int, ElementContent]
    | None
)

ElementAttributes = dict[str, Stringable | bool] | None

TableCellContent = ElementContent | tuple[ElementContent, ElementAttributes]
TableRowContent = list[TableCellContent]
TableRowsContent = list[TableRowContent | tuple[TableRowContent, ElementAttributes]]

ElementContentContainer = dict[str | int, ElementContent]


def process_element_content_input(content: ElementContentInput) -> ElementContentContainer:
    if not content:
        return {}
    if isinstance(content, dict):
        return content
    if isinstance(content, (list, tuple)):
        return {idx: elem for idx, elem in enumerate(content)}
    return {0: content}
