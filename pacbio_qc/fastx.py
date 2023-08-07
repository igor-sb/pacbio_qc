"""FASTQ/FASTA manipulation functions."""

import gzip
from contextlib import nullcontext
from typing import IO, Union


def open_fastx_or_fastxgz(filename: str) -> Union[IO, nullcontext]:
    if filename.lower().endswith(('.gz', '.gzip')):
        return gzip.open(filename, 'rt')
    return nullcontext(filename)
