import json
import logging
import os
import time
from string import Template

import click
import coloredlogs
import markdown

from promptarchitect.engineered_prompt import EngineeredPrompt
from promptarchitect.log_error import LogError, Severity
from promptarchitect.prompt_file import PromptFile
from promptarchitect.prompt_validation import PromptValidation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")


class ValidateEngineeredPrompts:
    """
    Class to validate
    """

    def _html_markup(self, prompt: str, remove_double_line_breaks=False) -> str:
        """
        Format the prompt text for HTML display.

        Args:
            prompt (str): The prompt text.
            remove_double_line_breaks (bool): Whether to remove double line breaks.

        Returns:
            str: The formatted prompt text.
        """
        # Escape HTML comments so they are not interpreted as comments
        prompt = prompt.replace("<!--", "<-- ")

        # Change all lines starting with a # to a heading 3
        prompt = "\n".join(
            f"<h3>{line[1:]}</h3>" if line.startswith("#") else line
            for line in prompt.split("\n")
        )

        # Change all newlines to <br> tags
        prompt = prompt.replace("\n", "<br>").strip()

        if remove_double_line_breaks:
            prompt = prompt.replace("</h3><br>", "</h3>")

        prompt = markdown.markdown(prompt)

        # # The regular expression pattern to find text between double asterisks
        # # Explanation of pattern:
        # # \*\*: Matches literal **
        # # (.*?): Non-greedy match for any characters (captured for later use)
        # # \*\*: Matches literal **
        # pattern = r"\*\*(.*?)\*\*"

        # # Substitute the pattern in the text with <strong> tags wrapping
        # # the captured group
        # prompt = re.sub(pattern, r"<strong>\1</strong>", prompt)

        return prompt.strip()

    def _get_template(self, template_name: str) -> str:
        """
        Get the content of a template file.

        Args:
            template_name (str): The name of the template file.

        Returns:
            str: The content of the template file.
        """
        template_path = os.path.join(self.html_templates_location, template_name)
        try:
            with open(template_path, "r") as f:
                return Template(f.read())
        except FileNotFoundError:
            logger.error(
                f"Template file '{template_name}' not found at location {template_path}."  # noqa: E501
            )
            return ""

    def __init__(
        self,
        prompts_location: str,
        completions_output: str,
        html_templates_location: str = "src/templates/reports",
        reports_location: str = "dashboard",
    ) -> None:
        self.prompts_location = prompts_location
        self.completions_output = completions_output
        self.html_pages = []
        self.prompt_files = self._load_prompt_files()
        self.total_passed = 0
        self.total_failed = 0
        self.prompt_completions = {}
        self.validation_results = {}
        self.passed_tests_count = {}
        self.failed_tests_count = {}
        self.html_templates_location = html_templates_location

        self.report_template = self._get_template("report.html")
        self.report_details_template = self._get_template(
            "report_test_results_details.html"
        )
        self.report_table_template = self._get_template("report_test_results.html")
        self.dashboard_template = self._get_template("dashboard.html")
        self.dashboard_template_with_tests = self._get_template(
            "prompt_files_with_tests.html"
        )
        self.dashboard_template_without_tests = self._get_template(
            "prompt_files_without_tests.html"
        )
        self.errors = LogError()  # Initialize an empty list to store error messages
        # Create the reports directory if it does not exist
        self.report_location = reports_location
        os.makedirs(self.report_location, exist_ok=True)

    def run_tests(self):
        """Run tests for each engineered prompt based on its associated test cases."""

        logger.info("Running tests for each engineered prompt.")

        self.validation_results = {}
        self.passed_tests_count = {}
        self.failed_tests_count = {}

        for prompt_id, engineered_prompts in self.prompt_completions.items():
            self._run_tests_for_prompt(prompt_id, engineered_prompts)

        logger.info("All tests have been executed and stored.")

    def _run_tests_for_prompt(self, prompt_id, engineered_prompts):
        test_results = {}
        count_passed = 0
        count_failed = 0

        for ep in engineered_prompts.values():
            for test_id, test_prompt in ep.prompt_file.tests.items():
                if test_id not in test_results:
                    test_results[test_id] = {}

                test_passed = self.execute_or_load_test(ep, test_id, test_prompt)
                if test_passed is not None:
                    count_passed, count_failed = self._update_counts(
                        test_passed, count_passed, count_failed
                    )
                    test_results[test_id][ep.input_file] = {
                        "result": test_passed,
                        "validation_object": self.current_prompt_validation,
                    }

        self.validation_results[prompt_id] = test_results
        self.passed_tests_count[prompt_id] = count_passed
        self.failed_tests_count[prompt_id] = count_failed

    def execute_or_load_test(self, ep, test_id, test_prompt):
        test_completion_input = ep.completion.response_message

        # TODO: Implement caching of test results. Something is of with the completion type
        # stored_data_file = os.path.join(ep.output_path, f"{test_id}.json")

        # if os.path.exists(stored_data_file):
        #     return self._load_test_from_cache(stored_data_file, ep.prompt_file.filename)
        # else:
        #     return self.execute_test(test_id, test_prompt, test_completion_input, ep)

        return self.execute_test(test_id, test_prompt, test_completion_input, ep)

    def _load_test_from_cache(self, file_path, prompt_filename):
        try:
            with open(file_path, "r") as f:
                stored_data = json.load(f)
            self.current_prompt_validation = PromptValidation.from_dict(stored_data)
            return self.current_prompt_validation.passed
        except Exception as e:
            self.errors.log_error(
                name=prompt_filename,
                message=f"Error reading from cache: {e}. Skipping test",
                severity=Severity.ERROR,
            )
        return None

    def execute_test(self, test_id, test_prompt, test_completion_input, ep):
        try:
            prompt_validation = PromptValidation(
                test_id=test_id,
                test_prompt=test_prompt,
                test_completion_input=test_completion_input,
                engineered_prompt=ep,
            )
            test_passed = prompt_validation.run_test()
            self.current_prompt_validation = prompt_validation
            return test_passed
        except Exception as e:
            self.errors.log_error(
                name=ep.prompt_file.filename,
                message=f"Error creating PromptValidation object: {e}. Skipping test.",
                severity=Severity.ERROR,
            )
        return None

    def _update_counts(self, test_passed, count_passed, count_failed) -> tuple:
        if test_passed:
            count_passed += 1
        else:
            count_failed += 1

        return count_passed, count_failed

    def _fill_errors_warnings(self, name: str = None) -> tuple:
        """
        Get the errors and warnings from the LogError object and
        fill the HTML templates.

        Args:
            name (str): Filter errors and warnings by the associated name (optional).
        Returns:
            tuple: A tuple containing the errors and warnings summary and details.
        """
        # Initialize the results container
        errors_warnings = [
            error
            for error in self.errors.errors
            if name is None or name in error["name"]
        ]
        if not errors_warnings:
            return "No errors or warnings found.", ""

        # Count errors and warnings from the filtered results
        n_errors = sum(1 for error in errors_warnings if error["severity"] == "ERROR")
        n_warnings = sum(
            1 for error in errors_warnings if error["severity"] == "WARNING"
        )

        # Format the summary string
        s_errors_warnings = f"{n_errors} error{'s' if n_errors != 1 else ''} and {n_warnings} warning{'s' if n_warnings != 1 else ''} found."  # noqa: E501

        # Prepare the details for the report and dashboard
        d_errors_warnings = ""
        for error in errors_warnings:
            d_errors_warnings += self._get_template(
                "errors-warnings-details.html"
            ).substitute(
                name=error["name"],
                message=error["message"],
                severity=error["severity"].capitalize(),
            )

        # Insert the details into the table template
        d_errors_warnings = self._get_template(
            "errors-warnings-table.html"
        ).safe_substitute(errors_warnings=d_errors_warnings)

        return s_errors_warnings, d_errors_warnings

    def format_test_details(self, idx, detail, file_path, prompt_file_name):
        """Format HTML for individual test details."""

        if not file_path:
            input_file = ""
            test_path = ""
        else:
            test_path = os.path.dirname(file_path)
            input_file = os.path.basename(file_path)

        cost = detail["validation_object"].completion.cost
        duration = detail["validation_object"].completion.duration
        unique_id = f"{detail['validation_object'].test_id}_{idx}".replace(" ", "_")
        return {
            "cost": cost,
            "duration": duration,
            "test_path": test_path,
            "html": self.report_details_template.safe_substitute(
                status="Passed" if detail["result"] else "Failed",
                # input_file=os.path.basename(os.path.dirname(detail)),
                input_file=input_file,
                description=self._html_markup(
                    detail["validation_object"].completion.response_message
                ),
                duration=f"{duration:.1f}s",
                cost=f"${cost:.2f}",
                last_run=detail["validation_object"].last_run,
                errors=self.errors.count_errors(prompt_file_name),
                warnings=self.errors.count_warnings(prompt_file_name),
                unique_id=unique_id,
                completion=markdown.markdown(
                    detail[
                        "validation_object"
                    ].engineered_prompt.completion.response_message
                ),
            ),
        }

    def generate_html_report(self, test_results, prompt_file_name) -> str:
        total_cost = 0
        total_duration = 0
        test_tables = ""
        formatted_detail = None

        for test_id, tests in test_results.items():
            test_results_html = ""
            details_metadata = None

            for idx, (file_path, detail) in enumerate(tests.items()):
                # Format the test details
                formatted_detail = self.format_test_details(
                    idx, detail, file_path, prompt_file_name
                )
                test_results_html += formatted_detail["html"]
                total_cost += formatted_detail["cost"]
                total_duration += formatted_detail["duration"]

                if not details_metadata:
                    details_metadata = detail  # Store first detail for later use

            # Use the first detail to get metadata for headers
            if details_metadata:
                test_prompt = details_metadata["validation_object"].test_prompt
                model = details_metadata[
                    "validation_object"
                ].engineered_prompt.prompt_file.metadata["model"]
                test_system_role = details_metadata[
                    "validation_object"
                ].completion.system_role
                system_role = details_metadata[
                    "validation_object"
                ].engineered_prompt.completion.system_role

                test_tables += self.report_table_template.safe_substitute(
                    test_id=test_id,
                    test_prompt=test_prompt,
                    model=model,
                    system_role=test_system_role,
                    test_results_details=test_results_html,
                )
            else:
                system_role = "No system role found."

        original_prompt = (
            details_metadata["validation_object"].engineered_prompt.prompt_file.text
            if details_metadata
            else ""
        )

        s_errors_warnings, d_errors_warnings = self._fill_errors_warnings(
            prompt_file_name
        )

        return self.report_template.safe_substitute(
            prompt_file=os.path.basename(prompt_file_name),
            total_cost=f"$ {total_cost:.2f}",
            total_duration=f"{total_duration:.1f}s",
            test_results=test_tables,
            test_path=formatted_detail["test_path"] if formatted_detail else "",
            prompt=self._html_markup(original_prompt, remove_double_line_breaks=True),
            system_role=self._html_markup(system_role, remove_double_line_breaks=True),
            creation_date=time.strftime("%Y-%m-%d %H:%M:%S"),
            errors_warnings=s_errors_warnings,
            errors=self.errors.count_errors(prompt_file_name),
            warnings=self.errors.count_warnings(prompt_file_name),
            errors_warnings_details=d_errors_warnings,
        )

    def create_reports(self) -> None:
        """
        Create reports for the test results in HTML files.
        """
        output_path = self.report_location

        logger.info(f"Creating reports for the test results in {output_path}")

        for file in self.prompt_files:
            # Create a prompt file
            try:
                prompt_file = PromptFile(os.path.join(self.prompts_location, file))
            except Exception:
                pass

            # Check if there are tests in the prompt file
            if not prompt_file.tests:
                continue

        ## Loop through each prompt file that had tests
        for prompt_file_name, test_results in self.validation_results.items():
            # Get the base name of the prompt file
            # without the extension and path
            # add the HTML extension
            html_file_name = (
                f"{os.path.splitext(os.path.basename(prompt_file_name))[0]}.html"
            )
            self.html_pages.append(html_file_name)
            # Generate the HTML report for the current prompt file
            report_html = self.generate_html_report(test_results, prompt_file_name)
            report_file_path = os.path.join(output_path, html_file_name)
            with open(report_file_path, "w") as f:
                f.write(report_html.strip())

        logger.info("Reports created successfully.")

    def _split_prompt_files(self, prompt_files: list) -> tuple:
        """
        Split the prompt files into two lists based on the presence of tests.

        Args:
            prompt_files (list): A list of prompt file names.

        Returns:
            tuple: A tuple of two lists, one with prompt files with tests
            and one without.
        """
        prompt_files_with_tests = []
        prompt_files_without_tests = []

        for file in prompt_files:
            # Create a prompt file
            # In some cases meta data is missing; keep going
            try:
                prompt_file = PromptFile(os.path.join(self.prompts_location, file))
            except Exception:
                pass

            # Check if there are tests in the prompt file and there's a test path
            # in the metadata
            if prompt_file.tests and "test_path" in prompt_file.metadata:
                prompt_files_with_tests.append(file)
            else:
                prompt_files_without_tests.append(file)

        return prompt_files_with_tests, prompt_files_without_tests

    def _calculate_test_cost_and_duration(self, test_results: dict) -> tuple:
        """
        Calculate the total cost and duration for the test completions.

        Args:
            test_results (dict): A dictionary of test completions.

        Returns:
            tuple: A tuple containing the total cost and duration.
        """
        total_cost = 0.0
        total_duration = 0.0

        for test in test_results.values():
            for ep in test.values():
                total_cost += ep["validation_object"].completion.cost
                total_duration += ep["validation_object"].completion.duration
        return total_cost, total_duration

    def _calculate_cost_and_duration(self, prompt_completions: dict) -> tuple:
        """
        Calculate the total cost and duration for the prompt completions.

        Args:
            prompt_completions (dict): A dictionary of prompt completions.

        Returns:
            tuple: A tuple containing the total cost and duration.
        """
        total_cost = 0.0
        total_duration = 0.0

        for ep in prompt_completions.values():
            total_cost += ep.cost
            total_duration += ep.duration
        return total_cost, total_duration

    def _calculate_outdated_tests(
        self, test_results: dict, last_modified: float
    ) -> int:
        """
        Calculate the number of outdated tests based on the last modified date
        of the prompt file.

        Args:
            test_results (dict): A dictionary of test completions.
            last_modified (float): The last modified date of the prompt file.

        Returns:
            int: The number of outdated tests.
        """
        outdated_tests = 0

        for test in test_results.values():
            for ep in test.values():
                # Check if the last run date is older than the last modified date
                # of the prompt file
                # First convert the string last_run date.
                # It's in "%Y-%m-%d %H:%M:%S" format

                last_run = time.mktime(
                    time.strptime(ep["validation_object"].last_run, "%Y-%m-%d %H:%M:%S")
                )
                if last_run < last_modified:
                    outdated_tests += 1
        return outdated_tests

    def _total_tests_count(self, test_results: dict) -> int:
        """
        Calculate the total number of tests in the test results.

        Args:
            test_results (dict): A dictionary of test completions.

        Returns:
            int: The total number of tests.
        """
        total_tests = 0

        for test in test_results.values():
            for test_completion in test.values():
                total_tests += 1
        return total_tests

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration from seconds to 'X hr Y min Z sec', 'Y min Z sec', or 'Z sec'.

        Args:
            seconds (float): The duration in seconds.

        Returns:
            str: The formatted duration string
        """

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours}h{minutes}m{remaining_seconds}s"
        elif minutes > 0:
            return f"{minutes}m{remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"

    def create_dashboard(self) -> None:
        """
        Create a dashboard of the test results in an HTML file.
        """
        output_path = self.report_location
        logger.info(f"Creating dashboard for the test results in {output_path}")

        # Split the prompt files into with and without tests
        prompt_files_with_tests, prompt_files_without_tests = self._split_prompt_files(
            self.prompt_files
        )

        # Get statistics for the dashboard
        total_prompt_files = len(self.prompt_files)
        total_prompt_files_with_tests = len(prompt_files_with_tests)
        total_completion_cost = 0.0
        total_completion_duration = 0.0
        total_test_cost = 0.0
        total_test_duration = 0.0
        total_tests_outdated = 0

        # Create the dashboard table for the prompt files with tests
        test_table = ""
        tests_outdated = 0
        prompt_files_with_tests.sort()

        for prompt_file in prompt_files_with_tests:
            # Get the last modified date of the prompt file
            last_modified = os.path.getmtime(
                os.path.join(self.prompts_location, prompt_file)
            )

            completion_cost = 0.0
            completion_duration = 0.0
            tests_outdated = 0

            # Total number of tests for the prompt file
            base_file_name = os.path.splitext(prompt_file)[0]

            # If there are no reports for the prompt file, skip it
            # The error that caused the missing report is already logged
            # And will be displayed in the dashboard
            if self.prompt_completions.get(base_file_name) is None:
                continue

            # Get the cost and average duration for the prompt file completion
            completion_cost, completion_duration = self._calculate_cost_and_duration(
                self.prompt_completions[base_file_name]
            )

            avg_duration = completion_duration / len(
                self.prompt_completions[base_file_name]
            )

            total_test_cost, total_test_duration = (
                self._calculate_test_cost_and_duration(
                    self.validation_results[base_file_name]
                )
            )

            # Check if the modification date of the prompt file is newer
            # than one of the completion dates of the tests
            # If so, the test is outdated
            tests_outdated += self._calculate_outdated_tests(
                self.validation_results[base_file_name], last_modified
            )
            cost = completion_cost + total_test_cost
            duration = completion_duration + total_test_duration
            # Total test are the sum of the length of the validation objects
            # for each test. The validation object contains the test results
            total_tests = self._total_tests_count(
                self.validation_results[base_file_name]
            )
            # total_tests = len(self.validation_results[base_file_name])
            passed = self.passed_tests_count[base_file_name]
            perc_passed = passed / total_tests * 100 if total_tests > 0 else 0
            # Get the link to the report file from the hml_pages list
            report_file = f"{os.path.splitext(os.path.basename(prompt_file))[0]}.html"

            if perc_passed < 50:
                severity_class = "error"
            elif perc_passed < 75:
                severity_class = "warning"
            else:
                severity_class = "success"

            # Create a table row for the dashboard based on the template
            test_table += self.dashboard_template_with_tests.safe_substitute(
                percentage_passed=f"{perc_passed:.1f}%",
                severity_class=severity_class,
                severity=severity_class.capitalize(),
                report_link=report_file,
                prompt_file=prompt_file,
                cost=f"$ {cost:.2f}",
                duration=f"{avg_duration:.1f} sec",
                outdated_tests=tests_outdated,
                number_of_tests=len(self.validation_results[base_file_name]),
            )

            total_completion_cost += cost
            total_completion_duration += duration
            total_tests_outdated += tests_outdated

        without_test_table = ""
        # Create the dashboard for the prompt files without tests
        prompt_files_without_tests.sort()
        for prompt_file in prompt_files_without_tests:
            without_test_table += self.dashboard_template_without_tests.substitute(
                prompt_file=prompt_file
            )
        s_errors_warnings, d_errors_warnings = self._fill_errors_warnings()
        # Avoid division by zero
        percentage_with_tests = (
            (total_prompt_files_with_tests / total_prompt_files * 100)
            if total_prompt_files
            else 0
        )

        # Create the dashboard with the template
        dashboard_html = self.dashboard_template.substitute(
            prompt_files_with_tests=test_table,
            prompt_files_without_tests=without_test_table,
            total_errors_warnings=self.errors.count_errors()
            + self.errors.count_warnings(),
            total_prompt_files=total_prompt_files,
            percentage_with_tests=f"{percentage_with_tests:.0f}%",
            outdated_tests=total_tests_outdated,
            total_cost=f"$ {total_completion_cost:.2f}",
            duration=self._format_duration(total_completion_duration),
            errors_warnings=s_errors_warnings,
            errors_warnings_details=d_errors_warnings,
        )

        # Write the dashboard to a file
        dashboard_file_path = os.path.join(output_path, "dashboard.html")
        with open(dashboard_file_path, "w") as f:
            f.write(dashboard_html)

        logger.info("Dashboard created successfully.")

    def get_errors_and_warnings(self) -> tuple:
        """
        Count the number of errors and warnings in the validation results.

        Args:
            None

        Returns:
            tuple: A tuple containing the number of errors and warnings.
        """
        return self.errors.count_errors(), self.errors.count_warnings()

    def _load_prompt_files(self):
        """Load and return list of prompt files."""

        return [
            file
            for file in os.listdir(self.prompts_location)
            if file.endswith(".prompt")
        ]

    def _validate_prompt_file(self, file):
        """Validate and load the prompt file, handling errors."""
        try:
            prompt_file = PromptFile(os.path.join(self.prompts_location, file))
            if not prompt_file.tests:
                return None
            if "system_role" in prompt_file.metadata and not os.path.exists(
                prompt_file.metadata["system_role"]
            ):
                raise FileNotFoundError("Specified system role file does not exist.")
            if "test_path" not in prompt_file.metadata:
                raise ValueError("Test path not specified in metadata.")
            if not os.path.exists(prompt_file.metadata["test_path"]):
                raise FileNotFoundError("Specified test path does not exist.")
            return prompt_file
        except Exception as e:
            self.errors.log_error(
                name=file,
                message=f"Error loading prompt file {file}: {e}.",
                severity=Severity.ERROR,
            )
        return None

    def run_completions(self):
        """Process completions for each prompt file that passes validation."""

        logger.info("Running completions all prompt files.")
        for file in self.prompt_files:
            prompt_file = self._validate_prompt_file(file)
            if not prompt_file:
                continue

            known_input_files = self._get_known_input_files(prompt_file)
            if not known_input_files:
                self.errors.log_error(
                    name=file,
                    message=f"No input files found for tests in {file}.",
                    severity=Severity.ERROR,
                )
                continue

            self._process_completions(file, prompt_file, known_input_files)

    def _get_known_input_files(self, prompt_file):
        """Retrieve and return the known test input files from the prompt
        file's metadata."""
        test_path = prompt_file.metadata["test_path"]
        return [f for f in os.listdir(test_path) if not f.startswith(".")]

    def _process_completions(self, file, prompt_file, known_input_files):
        """Process each known input file for completions."""
        base_file_name = os.path.splitext(file)[0]
        results_from_known_inputs = {}
        for input_file in known_input_files:
            completion_output_path = os.path.join(
                self.completions_output, base_file_name, os.path.splitext(input_file)[0]
            )
            os.makedirs(completion_output_path, exist_ok=True)
            ep = EngineeredPrompt(
                prompt_file_path=os.path.join(self.prompts_location, file),
                output_path=completion_output_path,
            )
            if self._execute_prompt(ep, input_file, prompt_file):
                self.total_passed += 1
            else:
                self.total_failed += 1
            results_from_known_inputs[input_file] = ep
        self.prompt_completions[base_file_name] = results_from_known_inputs

    def _execute_prompt(self, ep, input_file, prompt_file):
        """Execute the prompt and handle caching, logging any errors that occur."""
        try:
            result = ep.execute(
                cached=True,
                input_file=os.path.join(prompt_file.metadata["test_path"], input_file),
            )
            if ep.errors.count_errors() + ep.errors.count_warnings() > 0:
                for error in ep.errors.errors:
                    self.errors.log_error(
                        name=error["name"],
                        message=error["message"],
                        severity=(
                            Severity.ERROR
                            if error["severity"] == "ERROR"
                            else Severity.WARNING
                        ),
                        verbose=False,
                    )
            return result
        except Exception as e:
            self.errors.log_error(
                name=prompt_file.filename,
                message=f"Failed to execute completion: {e}",
                severity=Severity.ERROR,
            )
            return False

    def clear_all_test_completions(self, completions_output):
        """
        Remove all .json files in the completions_output directory and subdirectories.
        """

        # First ask for confirmation
        if not click.confirm("Are you sure you want to remove all test completions?"):
            return

        for root, dirs, files in os.walk(completions_output):
            for file in files:
                if file.endswith(".json"):
                    os.remove(os.path.join(root, file))

    def clear_all_completions(self, completions_output):
        """
        Remove all files in the completions_output directory and subdirectories.
        """

        # First ask for confirmation
        if not click.confirm("Are you sure you want to remove all completions?"):
            return

        for root, dirs, files in os.walk(completions_output):
            for file in files:
                os.remove(os.path.join(root, file))

    def run(self):
        """Run the validation process."""
        self.run_completions()
        self.run_tests()
        self.create_reports()
        self.create_dashboard()
