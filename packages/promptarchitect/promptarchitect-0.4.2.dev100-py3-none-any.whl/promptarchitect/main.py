from pathlib import Path
from typing import Annotated

import typer

from promptarchitect.validate_engineered_prompts import (
    ValidateEngineeredPrompts,  # noqa: E402
)

app = typer.Typer(rich_markup_mode=True)


@app.command()
def main(
    prompts: Annotated[str, typer.Option()] = "examples/prompts",
    completions: Annotated[str, typer.Option()] = "examples/completions",
    templates: Annotated[str, typer.Option()] = None,
    report: Annotated[str, typer.Option()] = "dashboard",
):
    """
    Create engineered prompts for higher quality LLM completions.
    """

    if templates is None:
        templates = (
            Path(__file__).parent / "templates/reports/themes/github-pajamas-theme"
        )  # noqa: E501

    validation = ValidateEngineeredPrompts(
        prompts_location=prompts,
        html_templates_location=templates,
        completions_output=completions,
        reports_location=report,
    )

    # validation.clear_all_test_completions(completions_output=completions_output)
    validation.run()

    errors, warnings = validation.get_errors_and_warnings()

    if errors + warnings > 0:
        print(
            f"\033[91mErrors: {errors}\033[0m, \033[93mWarnings: {warnings}\033[0m, "  # noqa: E501
        )
        if validation.errors.duplicates > 0:
            print(
                f"\033[93mRemoved duplicate errors/warnings: {validation.errors.duplicates}\033[0m, please check the dashboard for more information."  # noqa: E501
            )


if __name__ == "__main__":
    app()
