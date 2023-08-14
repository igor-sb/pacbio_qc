"""Code for aligning all exons to each of the reads."""

import tempfile

import fire
import pandas as pd
from Bio import SeqIO

from gencdna.alignment_output import UsearchOutputParser
from gencdna.config.alignment_output import USEARCH_COLUMN_NAMES
from gencdna.external_calls import BinaryExecutable


def align_exons_vs_single_read(
    exons_fasta_file: str,
    read_fasta_file: str,
    config: str = 'config/usearch.yml',
) -> pd.DataFrame:
    align = BinaryExecutable('usearch', config)
    align_output = align.run(
        '-usearch_local',
        exons_fasta_file,
        '-db',
        read_fasta_file,
    )
    return (
        UsearchOutputParser(USEARCH_COLUMN_NAMES, align_output)
        .output_as_dataframe()
        .sort_values(by=['subject_id', 'query_id'])
    )


def align_exons_vs_reads(
    exons_fasta_file: str,
    reads_fasta_file: str,
    config: str = 'config/usearch.yml',
) -> pd.DataFrame:
    alignment_outputs: list[pd.DataFrame] = []
    for read in SeqIO.parse(reads_fasta_file, 'fasta'):
        with tempfile.NamedTemporaryFile() as single_read_fasta:
            SeqIO.write(read, single_read_fasta.name, 'fasta')
            alignment_outputs.append(
                align_exons_vs_single_read(
                    exons_fasta_file=exons_fasta_file,
                    read_fasta_file=single_read_fasta.name,
                    config=config,
                ),
            )
    return pd.concat(alignment_outputs)


def main(
    input_exons_fasta: str,
    input_reads_fasta: str,
    output_blast: str,
    config: str = 'config/usearch.yml',
) -> None:
    alignment_output_df = align_exons_vs_reads(
        exons_fasta_file=input_exons_fasta,
        reads_fasta_file=input_reads_fasta,
        config=config,
    )
    alignment_output_df.to_csv(output_blast, sep='\t', index=False)


if __name__ == '__main__':
    fire.Fire(main)
