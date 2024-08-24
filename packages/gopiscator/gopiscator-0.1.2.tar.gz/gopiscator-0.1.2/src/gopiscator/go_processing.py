"""Gene Ontology processing module."""

import functools
import os
import pathlib
import shutil
from typing import Dict, List

import pandas as pd
import requests
from tqdm.auto import tqdm


def download_go_obo_file() -> pathlib.Path:
    """Download go-basic.obo file."""
    url = "http://purl.obolibrary.org/obo/go/go-basic.obo"
    filename = pathlib.Path(os.getcwd(), "go-basic.obo")

    if not filename.exists():
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()  # Raise error for bad responses

        file_size = int(response.headers.get("Content-Length", 0))
        filename.parent.mkdir(parents=True, exist_ok=True)

        desc = "(Unknown total file size)" if file_size == 0 else ""
        response.raw.read = functools.partial(response.raw.read, decode_content=True)  # Decompress if needed

        print(f"Downloading {url} to {filename}...")
        with tqdm.wrapattr(response.raw, "read", total=file_size, desc=desc) as r_raw:
            with filename.open("wb") as f:
                shutil.copyfileobj(r_raw, f)
        print("Download completed.")
    else:
        print(f"File {filename} already exists.")

    return filename


def create_alt_id_dict(go_dag: Dict) -> Dict[str, str]:
    """Create a dictionary to map alt_id to primary id."""
    alt_id_dict = {
        alt_id: term_id
        for term_id, term in go_dag.items()
        if term.alt_ids and term_id not in term.alt_ids
        for alt_id in term.alt_ids
    }
    return alt_id_dict


def create_obsolete_term_dict(obodag: Dict) -> Dict[str, str]:
    """Create a dictionary to map obsolete terms to their replacement terms."""
    obsolete_term_dict = {
        term_id: term.replaced_by for term_id, term in obodag.items() if term.is_obsolete and term.replaced_by
    }
    return obsolete_term_dict


def replace_alt_ids(go_terms: List[str], alt_id_map: Dict[str, str]) -> List[str]:
    """Replace all alt_id terms with their primary id."""
    return [alt_id_map.get(term, term) for term in go_terms]


def replace_obsolete_terms(df: pd.DataFrame, obodag: Dict) -> pd.DataFrame:
    """Replace obsolete GO terms with their replacement terms."""
    obsolete_term_dict = create_obsolete_term_dict(obodag)
    df["GOID"] = df["GOID"].apply(lambda term: obsolete_term_dict.get(term, term))
    return df.dropna(subset=["GOID"])


def add_go_term_details(df: pd.DataFrame, obodag: Dict) -> pd.DataFrame:
    """Add GO term details like name and definition to the DataFrame."""
    df["GO_term_name"] = df["GOID"].apply(lambda x: obodag[x].name if x in obodag else None)
    df["Definition"] = df["GOID"].apply(lambda x: obodag[x].defn if x in obodag else "No definition available")
    df["Definition"] = df["Definition"].str.replace('"', "")
    return df


def process_go_annotations(go_df: pd.DataFrame, obodag: Dict) -> pd.DataFrame:
    """Process GO annotations, replace alt_ids and reduce redundancy."""
    go_df["GOID"] = go_df["GOID"].astype(str).str.split(",")
    go_df = go_df.explode("GOID").reset_index(drop=True)

    alt_id_dict = create_alt_id_dict(obodag)
    go_df["GOID"] = replace_alt_ids(go_df["GOID"], alt_id_dict)
    go_df = replace_obsolete_terms(go_df, obodag)

    return go_df
