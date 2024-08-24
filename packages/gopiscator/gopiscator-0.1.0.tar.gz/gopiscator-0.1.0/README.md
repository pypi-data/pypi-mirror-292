<p align="center">
  <img src="logo.png" alt="gopiscator Logo" height=200>
</p>
<hr>

`GOpiscator` is a command-line tool for performing gene set enrichment analysis using the Gene Ontology (GO) database.

[![PyPI version](https://badge.fury.io/py/gopiscator.svg)](https://badge.fury.io/py/gopiscator)
### Installation

```
pip install gopiscator
```

### Usage

```
Usage: gopiscator [OPTIONS]

  GOpiscator (Tool for performing gene set enrichment analysis)

Options:
  -i, --gene-list FILE      Genes of interest list.  [required]
  -a, --go-annotation FILE  GO annotation file.  [required]
  -o, --output FILE         Write output to a file.  [default: (standard output)]
  -g, --ontology FILE       GO '.obo' file.  [default: ('go-basic.obo'; will be downloaded if absent)]
  --threshold FLOAT         P-value threshold.  [default: 0.05]
  --gene-count INTEGER      Minimum No. of genes annotated to the specific GO term.  [default: 2]
  -v, --version             Show the version and exit.
  -h, --help                Show this message and exit.
```
> [!NOTE]
> `gene-list` should have your genes of interest, one gene per line:
> ||
>| --- |
>| Rv3861 |
>| Rv3862c |
>| Rv0083 |
>| Rv3371 |
>
> `go-annotation` should be tab-delimited with genes in the first column and GO terms in the second column (separated by comma):
> |||
>| --- | --- |
>| Rv0001 |	GO:0006172,GO:0006275,GO:0006270 |
>| Rv0002 |	GO:0046677,GO:0006260 |
>| Rv0003 |	GO:0009432,GO:0000731,GO:0006260 |
>| Rv0005 |	GO:0046677,GO:0006265,GO:0006261 |
