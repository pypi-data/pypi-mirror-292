from typing import Literal as _Literal

from markitup import html as _html, doc as _doc


class ReporterException(Exception):
    """Base exception class with HTML reporting capabilities."""

    def __init__(
        self,
        message: str,
        description: str | None = None,
        message_html: str | _html.Element | None = None,
        description_html: str | _html.Element | None = None,
        report_heading: str = "Error Report",
    ):
        message_html = message_html or message
        description_html = description_html or description

        super().__init__(message + (f"\n{description}" if description else ""))
        self.message = message
        self.description = description
        self.message_html = message_html
        self.description_html = description_html
        self._html_head = _html.elem.head(
            [
                _html.elem.title(report_heading),
                _html.elem.style(
                    """
code {
    background-color: #f5f5f5; /* Light gray background */
    border: 1px solid #ddd;    /* Light gray border */
    padding: 2px 4px;          /* Small padding around the text */
    border-radius: 4px;        /* Rounded corners */
    font-family: monospace;    /* Monospace font for code */
    font-size: 90%;            /* Slightly smaller font size */
    color: #c7254e;            /* Text color */
    background-color: #f9f2f4; /* Background color */
}
.highlight-line {
    background-color: yellow;
}
.highlight-char {
    background-color: lightblue;
}
"""
                )
            ]
        )
        self._report_heading = report_heading
        return

    def report(self, mode: _Literal["full", "short"] = "full", md: bool = False) -> _doc.Document:
        """Generate a report for the exception."""
        detail_section_content = self._report_content(mode, md)
        summary = self.message_html + (f" {self.description_html}" if self.description_html else "")
        report = _doc.from_contents(
            heading=self._report_heading,
            content={"summary": _html.elem.p(summary, align="justify")},
            head=self._html_head if not md else None,
            section=_doc.from_contents(
                heading="Error Details",
                content=detail_section_content,
            ) if detail_section_content else None,
        )
        if not md:
            report.add_highlight(style="monokai-sublime", languages=["yaml", "json", "toml"])
        return report

    def _report_content(self, mode: _Literal["full", "short"], md: bool) -> list[str | _html.Element] | str | _html.Element | None:
        return