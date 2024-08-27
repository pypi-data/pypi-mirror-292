import datetime
from math import ceil
import os
import csv as csvmod
import time
from typing import Literal
import click
import random
from pdfminer.high_level import extract_text
from talc.utils.cli.io import print_single_case, get_failures_and_warnings, Web

from talc.synthetic import QuestionGenerationConfig, Document
from talc.evals import (
    EvalsClient,
    TestCaseWithRubric,
)
from talc.grading import (
    GradingSet,
    TestCaseResponse,
    ScoringRule,
    GradingPipeline,
)
from talc.utils.grading.defaults import DEFAULT_GRADER_CONFIG
from talc.utils.synthetic.defaults import (
    DEFAULT_HALLUCINATION_ARGS,
    DEFAULT_SIMPLE_ARGS,
    DEFAULT_MID_SIMPLE_ARGS,
)


talc_api_key: str | None = os.getenv("TALC_API_KEY", None)
talc_base_url: str = os.getenv(
    "TALC_BASE_URL", "http://evals-webserver-webapp.azurewebsites.net"
)


def poll_results(
    client: EvalsClient,
    print_passed: bool,
    out_file: str | None,
    scoring_rules: list[ScoringRule],
):
    while True:
        run_info = client.get_results()
        print(f"Progress: {run_info.completion_progress * 100}%")
        if run_info.completion_progress >= 1:
            print("\n============================================================")
            print("Grading complete.")
            for key in run_info.grades.keys():
                print(f"{key}: {run_info.grades[key] * 100}%")

            print("============================================================\n")

            assert run_info.test_cases is not None

            failures, warnings = get_failures_and_warnings(
                run_info.test_cases, scoring_rules
            )

            passed = [
                case
                for case in run_info.test_cases
                if case not in failures and case not in warnings
            ]

            if out_file is not None:
                with open(out_file, "w", newline="") as csvfile:
                    writer = csvmod.writer(csvfile)
                    writer.writerow(
                        [
                            "id",
                            "question",
                            "expected_answer",
                            "result",
                            "failure",
                            "warning",
                            "grades",
                        ]
                    )
                    for case in run_info.test_cases:
                        writer.writerow(
                            [
                                case.id,
                                case.question,
                                case.expected_response,
                                case.response,
                                True if case in failures else False,
                                True if case in warnings else False,
                                case.grades,
                            ]
                        )

            if print_passed and len(passed) > 0:
                print("=================PASSED=================")
                for case in passed:
                    print_single_case(case, "green")
            if len(warnings) > 0:
                print("=================WARNINGS=================")
                for warning in warnings:
                    print_single_case(warning, "yellow")
            if len(failures) > 0:
                print("=================FAILURES=================")
                for failure in failures:
                    print_single_case(failure, "red")
            if len(failures) > 0:
                return 1
            else:
                return 0

        time.sleep(2)


@click.group()
def evals():
    pass


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option("--dataset", prompt="Dataset ID", help="The ID of the dataset to load.")
@click.option(
    "--out_file",
    help="Path to CSV file to save results to.",
)
def get_dataset(dataset: str, api_key: str | None, out_file: str) -> None:
    """Download or pretty print a test dataset from the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)
    data = client.get_dataset(dataset)

    random.shuffle(data)

    with open(out_file, "w", newline="") as csvfile:
        writer = csvmod.writer(csvfile)
        writer.writerow(["id", "question", "expected_answer", "sources"])
        for case in data:
            writer.writerow(
                [
                    case.id,
                    case.question,
                    case.expected_response,
                    case.scenario_data.get("source_document_titles", []),
                ]
            )


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option(
    "--in_file",
    prompt="Results CSV path",
    help="Path to CSV file to load results from. Columns should be 'id', 'result'. Header row is required and case sensitive.",
)
@click.option("--print_passed", is_flag=True, help="Print the passed test cases.")
@click.option("--out_file", default=None, help="Optionally save output as CSV.")
@click.option(
    "--config",
    default="all_passed",
    help="The name of the grader configuration to use.",
)
def eval(
    api_key: str | None,
    in_file: str,
    print_passed: bool,
    out_file: str,
    config: str,
):
    """Grade a test run from a CSV. Columns 'id' and 'result' are required, other columns will be ignored. CSV should have a header row."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(in_file, newline="") as csvfile:
        reader = csvmod.DictReader(csvfile)

        results = [
            TestCaseResponse(id=row["id"], response=row["result"]) for row in reader
        ]

    if config.endswith(".json"):
        loaded_config = GradingPipeline.parse_file(config)
    else:
        loaded_config = DEFAULT_GRADER_CONFIG

    grading_set = GradingSet(
        responses=results,
        pipeline=loaded_config,  # type: ignore
    )
    print("Grading " + str(len(results)) + " test cases.")
    run_info = client.start_run()
    client.submit_responses(grading_set)
    print("Submitted results. Beginning grading for run ID: " + run_info.id)

    res = poll_results(client, print_passed, out_file, loaded_config.scoring_rules)
    exit(res)


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option("--run_id", prompt="Run ID", help="The ID of the run to get results for.")
@click.option("--print_passed", is_flag=True, help="Print the passed test cases.")
def get_results(api_key: str | None, run_id: str, print_passed: bool):
    """Get the grades for a test run."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url, run_id)

    res = poll_results(client, print_passed, None, DEFAULT_GRADER_CONFIG.scoring_rules)

    exit(res)


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option(
    "--csv",
    prompt="CSV path",
    help="Path to CSV file to upload. Column headers should be 'question' and 'expected_answer'. An optional source_text column can be included as well.",
)
@click.option("--name", prompt="Dataset name", help="The name of the dataset.")
def upload_manual_testset(api_key: str | None, csv: str, name: str):
    """Add a new dataset to the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.DictReader(csvfile)

        try:
            dataset = [
                TestCaseWithRubric(
                    question=row["question"],
                    expected_response=row["expected_answer"],
                    scenario_data={},
                    id=None,
                    source_content=(
                        [row["source_text"]] if "source_text" in row else []
                    ),
                )
                for row in reader
            ]
        except KeyError:
            raise click.UsageError(
                "CSV file must have columns 'question' and 'expected_answer'. A header is required. An optional source_text column can be included."
            )

    dataset_id = client.upload_dataset(name, dataset)
    print(f"Dataset created with ID: {dataset_id}")


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option(
    "--in_file",
    prompt="Input CSV path",
    help="Path to CSV file to upload. Columns should be 'question', 'expected_answer' and 'user_answer'. An optional source_text column can be included as well.",
)
@click.option(
    "--name",
    help="The name of the dataset.",
    default="Temp Dataset",
    required=False,
)
@click.option(
    "--out_file",
    help="Name of the output file",
    required=False,
)
@click.option("--print_passed", is_flag=True, help="Print the passed test cases.")
def upload_and_grade(
    api_key: str | None,
    in_file: str,
    name: str,
    out_file: str | None,
    print_passed: bool,
):
    """Upload a CSV with questions, reference answers, and user answers. Grade the user answers and return the grade. Column names must be 'question', 'expected_answer', and 'user_answer'."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(in_file, newline="") as csvfile:
        reader = csvmod.DictReader(csvfile)

        rows = [row for row in reader]

        assert "question" in rows[0]
        assert "expected_answer" in rows[0]
        assert "user_answer" in rows[0]

    dataset = [
        TestCaseWithRubric(
            question=row["question"],
            expected_response=row["expected_answer"],
            scenario_data={},
            id=None,
            source_content=([row["source_text"]] if "source_text" in row else []),
        )
        for row in rows
    ]

    dataset = client.upload_dataset(name, dataset)

    # Download the dataset to get the IDs
    data = client.get_dataset(dataset.id)

    # Map the IDs to the actual responses using the questions as a key

    id_map = {case.question: case.id for case in data}

    results = [
        TestCaseResponse(
            id=id_map[row["question"]],
            response=row["user_answer"] if "user_answer" in row else "",
        )
        for row in rows
    ]

    # Create a run and submit the results
    run_info = client.start_run()

    # MAX TODO: Expose this config to the user
    grading_set = GradingSet(
        responses=results,
        pipeline=DEFAULT_GRADER_CONFIG,
    )
    client.submit_responses(grading_set)
    print("Submitted results. Beginning grading for run ID: " + run_info.id)

    res = poll_results(
        client, print_passed, out_file, DEFAULT_GRADER_CONFIG.scoring_rules
    )

    exit(res)


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option("--out_file", default=None, help="Path to save the output to.")
@click.option(
    "--config",
    help="Path to a JSON config file.",
    default=None,
)
@click.option(
    "--question_limit",
    default=10,
    type=click.INT,
    help="The number of questions to generate. If set in the config file, this will be ignored.",
)
@click.option(
    "--source",
    help="Input folder, single file path, or URL. Multiple allowed.",
    multiple=True,
    default=[],
)
def generate(
    api_key: str | None,
    config: str | None,
    out_file: str | None,
    question_limit: int,
    source: list[str],
):
    """Generate a dataset from a set of documents."""
    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    if out_file is None:
        out_file = (
            "questions_"
            + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            + ".csv"
        )

    client = EvalsClient(api_key, talc_base_url)

    kb_override_id = None

    if len(source) > 0:

        documents = parse_documents(source)
        knowledge_base = client.upload_knowledge_base_asbytes(
            documents,
            "questions_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
        )

        print(f"Knowledge Base created with ID: {knowledge_base.id}")

        kb_override_id = knowledge_base.id

    if config is None:
        generation_configs = []

        s1 = DEFAULT_SIMPLE_ARGS.copy()
        s1.question_limit = ceil(question_limit / 3)
        generation_configs.append(s1)
        s2 = DEFAULT_MID_SIMPLE_ARGS.copy()
        s2.question_limit = ceil(question_limit / 3)
        generation_configs.append(s2)
        s3 = DEFAULT_HALLUCINATION_ARGS.copy()
        s3.question_limit = ceil(question_limit / 3)
        generation_configs.append(s3)

        if kb_override_id is None:
            raise click.UsageError(
                "No source documents provided. Please use the --source option or provide a config file."
            )

        generation_args = QuestionGenerationConfig(
            knowledge_bases=[kb_override_id],
            question_configs=generation_configs,
            name="questions_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
        )
    else:
        try:
            generation_args = QuestionGenerationConfig.parse_file(config)
        except Exception as e:
            raise click.UsageError(f"Error parsing config file: {e}")
        if kb_override_id is not None:
            generation_args.knowledge_bases = [kb_override_id]
        elif len(generation_args.knowledge_bases) == 0:
            raise click.UsageError("No knowledge bases found in the config file.")
        if len(generation_args.question_configs) == 0:
            raise click.UsageError(
                "No question configurations found in the config file."
            )

    dataset_job = client.start_generate_dataset(
        config=generation_args,
    )

    while True:
        dataset_job = client.get_dataset_creation_job(dataset_job.id)
        print("Status: " + dataset_job.status)
        if dataset_job.status == "COMPLETE":
            break
        if dataset_job.status == "ERROR":
            print("Generation failed.")
            print(dataset_job.error)
            exit(1)
        time.sleep(2)

    dataset = client.get_dataset(dataset_job.dataset_id)

    with open(out_file, "w", newline="") as csvfile:
        writer = csvmod.writer(csvfile)
        writer.writerow(["id", "question", "expected_answer", "sources"])
        for case in dataset:
            writer.writerow(
                [
                    case.id,
                    case.question,
                    case.expected_response,
                    case.scenario_data.get("source_document_titles", []),
                ]
            )

    print(f"Dataset created with ID: {dataset_job.dataset_id}")
    print(f"Dataset written to {out_file}")


def parse_documents(input_path: list[str]) -> list[Document]:
    documents: list[Document] = []
    web = Web()
    # Figure out what kind of document each file is, and load it into a list of Document objects
    for f in input_path:
        # If it's a URL, load it locally and scrape
        if f.startswith("http") or f.startswith("https"):
            scraped = web.scrape(f)
            if len(scraped) > 0:
                for doc in scraped:
                    documents.append(doc)
        elif os.path.isdir(f):
            for root, _, files in os.walk(f):
                for path in files:
                    document = read_document(os.path.join(root, path))
                    if document is not None:
                        documents.append(document)
                    else:
                        # TODO: [Resolve handling] Current behavior is to gracefully skip if unsupported file within directory, but we throw error if unsupported file is provided directly as only input.
                        print(
                            f"Skipping file with unknown extension {path} in directory {root}."
                        )
        elif os.path.isfile(f):
            document = read_document(f)
            if document is not None:
                documents.append(document)
            else:
                raise click.UsageError(
                    "Unsupported file type. Only .md and .pdf files are supported."
                )
        else:
            raise click.UsageError(
                "Unsupported file type. Only URLs starting with http, and .md files and .pdf files are currently supported."
            )
    return documents


def read_document(fp: str) -> Document | None:
    """
    Read a document from a file path as either text or bytes.
    Currently supported extensions: [.pdf, .md, .txt]
    """
    if fp.endswith(".md") or fp.endswith(".txt"):
        with open(fp, "r") as f:
            return Document(
                content=f.read().encode(encoding="utf-8", errors="ignore"),
                title=f.name,
                filepath=os.path.basename(fp),
                content_type="text/markdown",
            )
    if fp.endswith(".txt"):
        with open(fp, "r") as f:
            return Document(
                content=f.read().encode(encoding="utf-8", errors="ignore"),
                title=f.name,
                filepath=os.path.basename(fp),
                content_type="text/plain",
            )
    elif fp.endswith(".pdf"):
        print(f"Reading pdf: {fp}")
        with open(fp, "rb") as f:
            return Document(
                content=f.read(),
                title=os.path.basename(fp),
                filepath=fp,
                content_type="application/pdf",
            )
    else:
        return None


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
@click.option(
    "--source",
    help="Input folder, single file path, or URL. Multiple allowed.",
    multiple=True,
    default=[],
)
@click.option(
    "--source_list",
    default=None,
    help="A list of sources to upload. Accepts a newline separated txt file of files, filepaths, or URLs to upload.",
)
@click.option(
    "--friendly_name",
    default=None,
    help="Brief text description of this knowledge base.",
)
def upload_kb(
    api_key: str | None,
    source: list[str],
    friendly_name: str | None,
    source_list: str | None,
):
    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    # if knowledge_base_name is None:
    #    knowledge_base_name = f"kb_" + datetime.datetime.now().strftime(
    #        "%Y_%m_%d_%H_%M_%S"
    #    )
    if friendly_name is None:
        raise click.UsageError(
            "No friendly name  provided. Please use the --friendly_name option to provide a brief description string"
        )

    if source_list is not None:
        with open(source_list, "r") as f:
            source = f.read().split("\n")
            source = [x for x in source if x != ""]

    client = EvalsClient(api_key, talc_base_url)
    documents = parse_documents(source)
    # TODO: If friendly name already exists, reject and ask again
    knowledge_base = client.upload_knowledge_base_asbytes(documents, friendly_name)
    print(f"Knowledge Base created with ID: {knowledge_base.id}")


@evals.command()
@click.option(
    "--api_key",
    default=talc_api_key,
    help="Talc API key. Can also be specified with the TALC_API_KEY environment variable.",
)
def list_kbs(
    api_key: str | None,
):
    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )
    client = EvalsClient(api_key, talc_base_url)
    kbs = client.list_kbs()
    print("Kbs:")
    for kb in kbs:
        print(f"  {kb.friendly_name} ({kb.id})")


def main():
    evals()
