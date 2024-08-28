from __future__ import annotations

from markitup.dtype import (
    ElementContentInput as _ElementContentInput,
    ElementContentContainer as _ElementContentContainer,
    ElementAttributes as _ElementAttributes,
    process_element_content_input as _process_element_content_input,
)
from markitup import render as _render
from markitup.md import elem as _md_elem
from markitup.html import elem as _html_elem


class Document:
    def __init__(
        self,
        heading: _ElementContentContainer,
        content: _ElementContentContainer,
        section: dict[str | int, Document],
        head: _ElementContentContainer,
        footer: _ElementContentContainer,
        attrs_html: _ElementAttributes,
        attrs_head: _ElementAttributes,
        attrs_body: _ElementAttributes,
        attrs_footer: _ElementAttributes,
    ):
        self.heading = heading
        self.content = content
        self.section = section
        self.head = head
        self.footer = footer
        self.attrs_html = attrs_html
        self.attrs_head = attrs_head
        self.attrs_body = attrs_body
        self.attrs_footer = attrs_footer
        return

    def __str__(self):
        return f"{self.syntax()}\n"

    def syntax(self, title_level: int = 1, as_md: bool = False) -> str:
        return self.syntax_md(title_level) if as_md else self.syntax_html(title_level)

    def syntax_html(self, title_level: int = 1) -> str:
        html_content = []
        head = self.html_head
        if head:
            html_content.append(head)
        html_content.append(_html_elem.body(self.html_body_content(title_level), self.attrs_body))
        html = _html_elem.html(html_content, self.attrs_html)
        return str(html)

    def syntax_md(self, title_level: int = 1) -> str:
        content = [_md_elem.html_block(self.html_head)]
        if self.heading or self.section or title_level > 1:
            content.append(str(_md_elem.heading(level=min(6, max(1, title_level)), content=self.heading)))
        content.append(self._container_syntax(self.content, as_md=True))
        for subsection in self.section.values():
            subsection_str = str(subsection.syntax_md(title_level=title_level + 1))
            content.append(f"\n\n{subsection_str}\n\n" if subsection_str else "")
        content.append(self._container_syntax(self.footer, as_md=True))
        return "".join(str(c) for c in content)

    def display(self, ipython: bool = False, as_md: bool = False) -> None:
        """Display the element in an IPython notebook."""
        _render.display(str(self), ipython=ipython, as_md=as_md)
        return

    def add_highlight(
        self,
        version: str = "11.10.0",
        style: str = "default",
        languages: list[str] = None,
    ) -> None:
        """Use [highlight.js](https://highlightjs.org/) to highlight code blocks.

        This automatically adds the necessary CSS stylesheets and JavaScript scripts to the document.
        The stylesheet is added to the `<head>` element under the key `highlight_js_stylesheet`,
        and the scripts are added to the `<body>` element under the keys `highlight_js_script_languages`,
        `highlight_js_script_{language}` (for additional languages) and `highlight_js_script_load`.

        Parameters
        ----------
        version: string, default: "11.10.0"
            The version of highlight.js to use.

            See the [highlight.js GitHub repository](https://github.com/highlightjs/highlight.js)
            for available versions.
        style: string, default: "default"
            Name of the highlight.js stylesheet to use.

            This should be the filename (without the '.min.css' extension)
            of one of the available stylesheets in the specified version
            at [cdnjs](https://cdnjs.com/libraries/highlight.js).
            The full URL is constructed using `version` and `style` as follows:
            `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/styles/{style}.min.css`
        languages: list of strings, optional
            List of additional languages to load.

            These should be the filenames (without the '.min.js' extension)
            of the language scripts in the specified version
            at [cdnjs](https://cdnjs.com/libraries/highlight.js).
            The full URL is constructed using `version` and the language name as follows:
            `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/languages/{language}.min.js`

        Notes
        -----
        - highlight.js tries to automatically detect the language of each `<pre><code>` element.
          However, you can also specifically define the language of each element by adding a
          class named `language-{NAME}` to the `<code>` element,
          where `NAME` is an alias of one of the
          [supported languages by highlight.js](https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md).
          For example, to set the language of a code block to HTML:
          `<pre><code class="language-html">...</code></pre>`

        References
        ----------
        - [highlight.js Website](https://highlightjs.org/)
        - [highlight.js Documentation](https://highlightjs.readthedocs.io/en/stable/index.html)
        - [highlight.js cdnjs Repository](https://cdnjs.com/libraries/highlight.js)
        """
        base_url = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js"
        style_href = f"{base_url}/{version}/styles/{style}.min.css"
        self.head["highlight_js_stylesheet"] = _html_elem.link(rel="stylesheet", href=style_href)
        self.content["highlight_js_script_languages"] = _html_elem.script(
            src=f"{base_url}/{version}/highlight.min.js"
        )
        if languages:
            for language in languages:
                self.content[f"highlight_js_script_{language}"] = _html_elem.script(
                    src=f"{base_url}/{version}/languages/{language}.min.js"
                )
        self.content["highlight_js_script_load"] = _html_elem.script("hljs.highlightAll();")
        return

    @property
    def html_head(self) -> _html_elem.Head | None:
        return _html_elem.head(self.head, self.attrs_head) if self.head or self.attrs_head else None

    def html_body_content(self, title_level: int = 1) -> _html_elem.Article | _html_elem.Section:
        body_content = []
        if self.heading or self.section or title_level > 1:
            body_content.append(_html_elem.h(level=min(6, max(1, title_level)), content=self.heading))
        body_content.extend(list(self.content.values()))
        for subsection in self.section.values():
            body_content.append(subsection.html_body_content(title_level=title_level + 1))
        if self.footer:
            body_content.append(_html_elem.footer(self.footer, self.attrs_footer))
        if title_level > 1:
            return _html_elem.section(body_content)
        return _html_elem.article(body_content)

    @staticmethod
    def _container_syntax(container: _ElementContentContainer, as_md: bool):
        if not as_md:
            return "".join(str(elem) for elem in container.values())
        content = []
        curr_html_elements = []
        in_html = False
        for elem in container.values():
            if isinstance(elem, _html_elem.Element):
                curr_html_elements.append(elem)
                in_html = True
            else:
                if in_html:
                    content.append(str(_md_elem.HTMLBlock(content=curr_html_elements)))
                    curr_html_elements = []
                    in_html = False
                content.append(str(elem))
        if in_html:
            content.append(str(_md_elem.HTMLBlock(content=curr_html_elements)))
        content_str = "".join(content).strip()
        return f"\n\n{content_str}\n\n" if content_str else ""


SebsectionsInputType = (
    Document
    | list[Document]
    | tuple[Document]
    | dict[str | int, Document]
    | None
)


def from_contents(
    heading: _ElementContentInput = None,
    content: _ElementContentInput = None,
    section: SebsectionsInputType = None,
    head: _ElementContentInput = None,
    footer: _ElementContentInput | None = None,
    attrs_html: _ElementAttributes = None,
    attrs_head: _ElementAttributes = None,
    attrs_body: _ElementAttributes = None,
    attrs_footer: _ElementAttributes = None,
) -> Document:
    """Create a document from its components."""
    head = _process_element_content_input(head)
    content = _process_element_content_input(content)
    return Document(
        heading=_process_element_content_input(heading),
        content=content,
        section=_process_element_content_input(section),
        head=head,
        footer=_process_element_content_input(footer),
        attrs_html=attrs_html,
        attrs_head=attrs_head,
        attrs_body=attrs_body,
        attrs_footer=attrs_footer,
    )
