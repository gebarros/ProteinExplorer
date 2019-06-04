# -*- coding: utf-8 -*-

# Import modules
import argparse
import re
import pymongo
from Bio import SeqIO
from pymongo import MongoClient


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
            #infos_to_store[header] = [args.id,args.n,type_seq,seq_size,sequence,tpm,fpkm]
            infos_to_store[header] = {"code":args.id,
                              "species": args.n,
                              "type_seq": type_seq,
                              "seq_size": seq_size,
                              "id": header,
                              "sequence": sequence,
                              "tpm": float(tpm),
                              "fpkm": float(fpkm)}
# Creating Mongo connection and DB
conn = pymongo.MongoClient('localhost', 27017)
db = conn.sequencesdb
collections = db.list_collection_names()

# Checking if the collection exists
if 'proteins' in collections:
    db.proteins.drop()
else:
    db.create_collection("proteins")

for v in infos_to_store.values():
    db.proteins.insert_one(v)

print("{} itens inserted".format(db.proteins.count_documents({})))