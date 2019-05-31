# -*- coding: utf-8 -*-

# Import modules
import argparse
import re
from Bio import SeqIO


# Setting parameters
parser = argparse.ArgumentParser(description='Protein Explorer: A pipeline used to explore and to generate reports of proteins of interest')
parser.add_argument("f", nargs="?",
                    type=argparse.FileType('r'),
                    help="Fasta file.")
parser.add_argument("e", nargs='?',
                    type=argparse.FileType('r'),
                    help="Expression file (RSEM output)")
parser.add_argument("id", nargs='?',
                    action="store",
                    help="Sample name.")
parser.add_argument("n", nargs='?',
                    action="store",
                    help="Species")
parser.add_argument("t", nargs='?',
                    action="store",
                    help="Seq type (n (nucleotide) or a (amino acids)).")                     
args = parser.parse_args()

# Open multifasta
multifasta = SeqIO.parse(args.f, 'fasta')
expression = args.e.readlines()
infos_to_store = {}


if args.t.lower() == "n":
    type_seq = "nucleotide"
elif args.t.lower() == "a":
    type_seq = "aminoacids"
else:
    print("Error: Type sequence unknow (Set n or a )")


    
for fasta in multifasta:
    header, sequence = fasta.id, str(fasta.seq)
    seq_size = len(sequence)

    for line in expression:
        all_fields = line.split("\t")
        transcript_id = all_fields[0]
        tpm = all_fields[5]
        fpkm = all_fields[6]

        if (header == transcript_id) and tpm != "0.00":
            infos_to_store[header] = [args.id,args.n,type_seq,seq_size,sequence,tpm,fpkm]

for k,v in infos_to_store.items():
    print("{}\n{}\n".format(k,v))