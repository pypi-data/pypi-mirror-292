"""Main data processing module."""

import sys
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from goatools.obo_parser import GODag
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import fdrcorrection
from tabulate import tabulate

from gopiscator.go_processing import add_go_term_details, process_go_annotations


def read_data(
    go_file: str, genes_file: str, obo_file: str, background_file: str = None
) -> Tuple[pd.DataFrame, pd.DataFrame, GODag]:
    """Read GO and genes data from files."""
    obodag = GODag(obo_file, optional_attrs=["def", "replaced_by"], load_obsolete=True, prt=None)
    go_df = pd.read_csv(go_file, sep="\t", names=["Geneid", "GOID"])
    genes_list = pd.read_csv(genes_file, sep="\t", names=["gene"])

    # Read the background gene list if provided
    if background_file:
        background_genes = pd.read_csv(background_file, sep="\t", names=["gene"])
        go_df = go_df[go_df["Geneid"].isin(background_genes["gene"])]

    return go_df, genes_list, obodag


def get_ontologies(go_df: pd.DataFrame, obodag: GODag) -> Dict[str, pd.DataFrame]:
    """Assign ontologies to GO terms and separate into different categories."""
    go_df["Ontology"] = go_df["GOID"].apply(lambda x: obodag[x].namespace if x in obodag else None)
    filtered_df = go_df.dropna(subset=["Ontology"])
    ontologies = {
        "BP": filtered_df[filtered_df["Ontology"] == "biological_process"].reset_index(drop=True),
        "MF": filtered_df[filtered_df["Ontology"] == "molecular_function"].reset_index(drop=True),
        "CC": filtered_df[filtered_df["Ontology"] == "cellular_component"].reset_index(drop=True),
    }
    return ontologies


def create_summary_tables(go_df: pd.DataFrame, genes_list: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create summary tables for GO terms and genes."""
    go_df_no = go_df.groupby("GOID").nunique().reset_index()
    go_df_no["population_total"] = go_df["Geneid"].nunique()
    go_df_no = go_df_no.rename(columns={"Geneid": "population_hits"})

    list_genes = (
        pd.merge(genes_list, go_df, left_on="gene", right_on="Geneid", how="right").dropna().reset_index(drop=True)
    )
    list_genes_no = (
        list_genes.groupby("GOID")
        .nunique()
        .reset_index()
        .drop(columns=["gene"])
        .rename(columns={"Geneid": "list_hits"})
    )

    all_go = pd.merge(list_genes_no, go_df_no, on="GOID", how="left")
    all_go["list_total"] = list_genes["gene"].nunique()
    return all_go, list_genes


def create_contingency_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create a contingency table for Fisher's exact test."""
    df["genes_in_list"] = df["list_hits"] - 1
    df["genes_in_set"] = df["population_hits"] - df["list_hits"] + 1
    df["genes_in_list_not_in_set"] = df["list_total"] - df["list_hits"]
    df["genes_not_in_list_not_in_set"] = (
        df["population_total"] - df["list_total"] - (df["population_hits"] - df["list_hits"])
    )

    columns_order = [
        "GOID",
        "genes_in_list",
        "genes_in_set",
        "genes_in_list_not_in_set",
        "genes_not_in_list_not_in_set",
        "list_total",
        "population_total",
        "population_hits",
        "list_hits",
    ]
    return df[columns_order]


def calculate_p_value(row: pd.Series, gene_count: int) -> float:
    """Calculate the P-value using Fisher's exact test."""
    if pd.notnull(row["genes_in_set"]) and row["list_hits"] >= gene_count:
        return fisher_exact(
            [
                [row["genes_in_list"], row["genes_in_set"]],
                [row["genes_in_list_not_in_set"], row["genes_not_in_list_not_in_set"]],
            ],
            alternative="greater",
        )[1]
    return 1.0


def adjust_p_values(df: pd.DataFrame) -> pd.DataFrame:
    """Adjust p-values using the Benjamini-Hochberg FDR correction."""
    p_values = df["P-value"].values
    _, adjusted_p_values = fdrcorrection(p_values)
    df["FDR"] = adjusted_p_values
    return df


def run_fishers_test(df: pd.DataFrame, threshold: float, gene_count: int) -> pd.DataFrame:
    """Perform the gene set enrichment analysis using Fisher's exact test and adjust p-values."""
    df_copy = df.copy()
    df_copy["P-value"] = df_copy.apply(lambda row: calculate_p_value(row, gene_count), axis=1)
    df_copy = adjust_p_values(df_copy)
    filtered_df = df_copy[df_copy["P-value"] <= threshold].sort_values(by="P-value")

    return filtered_df


def add_enrichment_score(df: pd.DataFrame) -> pd.DataFrame:
    """Add an enrichment score to the DataFrame."""
    df["Enrichment_score"] = -df["P-value"].apply(np.log10)
    return df


def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Add GeneRatio and BgRatio columns to the DataFrame."""
    df["GeneRatio"] = df["list_hits"].astype(str) + "[" + df["list_total"].astype(str) + "]"
    df["BgRatio"] = df["population_hits"].astype(str) + "[" + df["population_total"].astype(str) + "]"
    df["Count"] = df["list_hits"]
    return df


def add_rich_factor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Rich factor, the ratio of the number of differentially expressed genes
    annotated in a pathway to the number of all genes annotated in this pathway, to the DataFrame.
    """
    df["Rich_factor"] = df["list_hits"] / df["population_hits"]
    return df


def add_fold_enrichment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Fold enrichment, the enrichment of the term in the gene list
    compared to the background population of genes, to the DataFrame.
    """
    df["Fold_enrichment"] = (df["list_hits"] / df["list_total"]) / (df["population_hits"] / df["population_total"])
    return df


def save_results(input_df: pd.DataFrame, output_file_path: str) -> None:
    """Save the final results to a file."""
    input_df.to_csv(output_file_path, sep="\t", index=False)


def print_results(input_df: pd.DataFrame) -> None:
    """Print the final results in terminal."""
    final_output_reduced = input_df[["GOID", "Ontology", "GO_term_name", "P-value", "Enrichment_score", "Rich_factor"]]

    final_output_reduced.loc[:, "Rich_factor"] = final_output_reduced["Rich_factor"].round(1)
    final_output_reduced.loc[:, "Enrichment_score"] = final_output_reduced["Enrichment_score"].round(2)
    final_output_reduced.loc[:, "P-value"] = final_output_reduced["P-value"].round(3)

    headers = final_output_reduced.columns.tolist()
    table = tabulate(final_output_reduced, headers=headers, tablefmt="fancy_grid")
    print(f"\n{table}")


def calculate_fisher(
    go_file: str, genes_file: str, obo_file: str, threshold: float, gene_count: int, background_file: str = None
) -> pd.DataFrame:
    """Calculate Fisher's exact test for GO terms."""
    go_df, genes_list, obodag = read_data(go_file, genes_file, obo_file, background_file)
    go_df = process_go_annotations(go_df, obodag)
    ontologies = get_ontologies(go_df, obodag)

    enriched_terms_list = []

    def concat_function(x):
        """Concatenate genes from a term using a comma as a separator."""
        return ",".join(map(str, x.sort_values().unique()))

    for ontology, df in ontologies.items():
        all_go, list_genes = create_summary_tables(df, genes_list)
        cont_tab = create_contingency_table(all_go)
        enriched_terms = run_fishers_test(cont_tab, threshold, gene_count)

        if not enriched_terms.empty:
            enriched_terms = add_go_term_details(enriched_terms, obodag)
            enriched_terms = add_enrichment_score(enriched_terms)
            enriched_terms = add_fold_enrichment(enriched_terms)
            enriched_terms = add_rich_factor(enriched_terms)
            enriched_terms = add_ratios(enriched_terms)

            enriched_terms = pd.merge(enriched_terms, list_genes, on="GOID")
            enriched_terms["Genes"] = enriched_terms.groupby(["GOID"])["gene"].transform(concat_function)

            enriched_terms_list.append(enriched_terms)

    # Concatenate all enriched_terms DataFrames
    if enriched_terms_list:
        df = pd.concat(enriched_terms_list, ignore_index=True)
        final_output = (
            df[
                [
                    "GOID",
                    "Ontology",
                    "GO_term_name",
                    "Definition",
                    "P-value",
                    "FDR",
                    "Enrichment_score",
                    "Fold_enrichment",
                    "Rich_factor",
                    "GeneRatio",
                    "BgRatio",
                    "Count",
                    "Genes",
                ]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        return final_output
    else:
        sys.exit("No enriched terms found.")
