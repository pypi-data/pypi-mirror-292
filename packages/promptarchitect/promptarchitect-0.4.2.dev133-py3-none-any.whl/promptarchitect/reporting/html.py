from promptarchitect.reporting.core import TestReporter


class HtmlTestReporter(TestReporter):
    """Reports test results in HTML format."""

    def __init__(self, report_path):
        """
        Initialize the HTML test reporter.

        Parameters
        ----------
        report_path : str
            The path to the report
        """
        super().__init__(report_path)
