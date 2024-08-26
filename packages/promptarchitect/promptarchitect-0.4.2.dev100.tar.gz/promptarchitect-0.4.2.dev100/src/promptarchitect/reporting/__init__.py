from os import PathLike
from promptarchitect.reporting.html import HtmlTestReporter
from promptarchitect.reporting.json import JsonTestReporter


def create_test_reporter(report_format: str, report_path: PathLike) -> None:
    """
    Create a test reporter based on the report format.

    Parameters
    ----------
    report_format : str
        The format of the report.
    report_path : PathLike
        The path to the report.

    Returns
    -------
    TestReporter
        The test reporter.
    """
    if report_format == "html":
        return HtmlTestReporter(report_path)
    elif report_format == "json":
        return JsonTestReporter(report_path)
    else:
        raise ValueError(f"Unsupported report format: {report_format}")
