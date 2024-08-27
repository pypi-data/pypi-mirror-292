"""The command-line interface."""

import sys

import click

from gopiscator.data_processing import calculate_fisher, print_results, save_results
from gopiscator.go_processing import download_go_obo_file
from gopiscator.utils import get_version

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], max_content_width=120)
VERSION = get_version("__init__.py")


@click.version_option(VERSION, "-v", "--version", is_flag=True)
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-i",
    "--gene-list",
    "gene_list",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Genes of interest list.",
)
@click.option(
    "-a",
    "--go-annotation",
    "annotation",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="GO annotation file.",
)
@click.option(
    "-o",
    "--output",
    "output",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    show_default="standard output",
    help="Write output to a file.",
)
@click.option(
    "-g",
    "--ontology",
    "ontology",
    default=lambda: download_go_obo_file(),
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    show_default="'go-basic.obo'; will be downloaded if absent",
    help="GO '.obo' file.",
)
@click.option(
    "-b",
    "--background-list",
    "background_list",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    show_default="All genes from 'go-annotation' file",
    help="Background gene list file.",
)
@click.option(
    "--threshold",
    "threshold",
    type=float,
    default=0.05,
    show_default=True,
    help="P-value threshold.",
)
@click.option(
    "--gene-count",
    "gene_count",
    type=int,
    default=2,
    show_default=True,
    help="Minimum No. of genes annotated to the specific GO term.",
)
def main(
    annotation: str,
    gene_list: str,
    ontology: str,
    output: str,
    threshold: float,
    gene_count: int,
    background_list: str = None,
) -> None:
    """
    GOpiscator (Tool for performing gene set enrichment analysis)
    """
    results = calculate_fisher(annotation, gene_list, ontology, threshold, gene_count, background_list)

    if output:
        save_results(results, output)
    else:
        print_results(results)


if __name__ == "__main__":
    sys.exit(main())
