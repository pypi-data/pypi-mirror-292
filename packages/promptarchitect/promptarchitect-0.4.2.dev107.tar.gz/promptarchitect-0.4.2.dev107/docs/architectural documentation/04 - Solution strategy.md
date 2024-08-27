# 4 Solution strategy

## 4.1 Support for API usage and CLI usage

We want promptarchitect to be used in production and during development to make sure there are fewer differences between the two environments. We want to execute prompts in production and test them in development. 

To make this possible we provide an API to execute prompts in production, and a CLI tool to test prompts in development and during testing.

## 4.2 Flexible reporting structure

Prompt validation is important to business users as well because they seek reliable AI solutions. A report that matches the styling and layout of the business helps to increase the confidence level of business users. We therefore support building HTML reports using templating, so the testing reports can be formatted to match what the business users expect.

## 4.3 Support multiple forms of testing

It's important to understand that there's not one method to validate prompts. We need to look at multiple aspects of a 
prompt depending on the scenario we're using the prompt in. Therefore, we support multiple forms of testing:

- Format validation: Some prompts need to produce output in JSON, HTML or another format.
- Text property validation: In some cases we expect the prompt to produce a list of 5 items or similar.
- Semantic validation: In many cases we need to validate that the prompt follows semantic rules.
- Scoring: In cases where we're building RAG systems we need to score output for faithfulness and other metrics.

Promptarchitect supports these forms of tests through various types of test cases.

## 4.4 Prompt templating

We know that engineers build prompts that are structured with placeholders to insert pieces of information into a prompt. We support using placeholders in prompts to ensure that engineers are free to build prompts the way they want.
We use a well-known templating format [Mustache](https://mustache.github.io/) for this purpose.

## 4.5 Prompt file design

In section 4.1 we established that we're using a CLI and an API. For CLI usage, we introduce a concept called a prompt file. The prompt file defines the prompt with associated settings and tests. This file can be discussed with the business to establish what a prompt should do. It can also be provided to the CLI to validate the prompt. Finally, it can be used to load the prompt, so we can execute it in production. 

Please find the full specication for the prompt file in the [User documentation](../user/).
