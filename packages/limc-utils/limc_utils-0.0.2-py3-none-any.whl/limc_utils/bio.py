from Bio import SeqIO
import pandas as pd
from pathlib import Path


def read_seq(fasta_file):
    for record in SeqIO.parse(fasta_file, "fasta"):
        return str(record.seq)


def read_mutant(mutant_file, fasta_file=None, max_point=None, mutant_sep=":", offset=1, check=False):
    if Path(mutant_file).suffix == ".csv":
        df = pd.read_csv(mutant_file)
    elif Path(mutant_file).suffix == ".tsv":
        df = pd.read_csv(mutant_file, sep="\t")
    else:
        raise ValueError("File format not supported")

    df["point"] = [len(x.split(mutant_sep)) for x in df["mutant"]]
    if max_point is None:
        df = df[df["point"] <= max_point]

    if fasta_file is None:
        s0 = df["mutated_seqeunce"][0]
        m0 = df["mutant"][0]
        for sub in m0.split(mutant_sep):
            m0_wt, m0_pos, m0_mut = sub[0], int(sub[1:-1]) - offset, sub[-1]
            s0 = s0[: int(m0_pos)] + m0_wt + s0[int(m0_pos) + 1 :]
        wt_seq = s0
    else:
        wt_seq = read_seq(fasta_file)
        
    if check:
        for mutant in df["mutant"]:
            for sub in mutant.split(mutant_sep):
                wt, pos, mut = sub[0], int(sub[1:-1]) - offset, sub[-1]
                if wt_seq[pos] != wt:
                    raise ValueError(f"Wild type at position {pos} is {wt_seq[pos]}, not {wt}")

    return wt_seq, df
