# -*- coding: utf-8 -*-

# Import modules
import argparse
import sqlite3
import re
from Bio import SeqIO


# Setting parameters
parser = argparse.ArgumentParser(description='Toxin Explorer: A pipeline used to explore and to generate a report of the predicted snake toxins')
parser.add_argument("f", nargs="?",
                    type=argparse.FileType('r'),
                    help="Fasta file of predicted toxins.")
parser.add_argument("e", nargs='?',
                    type=argparse.FileType('r'),
                    help="Expression file (RSEM output)")
parser.add_argument("id", nargs='?',
                    action="store",
                    help="Sample name.")
args = parser.parse_args()

# Open multifasta
multifasta = SeqIO.parse(args.f, 'fasta')
mydict = {}

for fasta in multifasta:
    name, sequence = fasta.id, str(fasta.seq)
    full_transcript_id, coord, toxin = name.split('|')
    transcript_id = full_transcript_id.split('.p')[0]
    toxin_family = toxin.split('_')[-1]
    seq_size = len(sequence)
    print(seq_size)

    with open(args.e, 'r') as line:
        

# for k,v in mydict.items():
#     result.write(">{}\n{}\n".format(k,v))
