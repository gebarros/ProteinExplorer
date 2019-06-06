# -*- coding: utf-8 -*-
'''
This code needs as input a fasta file and their quantification result obtained from RSEM bioinformatics software.
After to process and select the fields of interests, the data are stored into the chosen database (Mongo or SQLite3).

Example: python feed_database.py [File.fasta] [File.expression.isoforms.results] [Sample_name] [Species name] [n] [s]
'''

# Import modules
import argparse
import re
import os
import sqlite3
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
parser.add_argument("db", nargs='?',
                    action="store",
                    help="Database to store the data (s (sql) or m (mongo)).")               
args = parser.parse_args()

# Open multifasta
multifasta = SeqIO.parse(args.f, 'fasta')
expression = args.e.readlines()
infos_to_store_mongo = {}
infos_to_store_sql = {}


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
            infos_to_store_mongo[header] = {"code":args.id,
                              "species": args.n,
                              "type_seq": type_seq,
                              "seq_size": seq_size,
                              "id": header,
                              "sequence": sequence,
                              "tpm": float(tpm),
                              "fpkm": float(fpkm)}
            infos_to_store_sql[header] = [args.id,args.n,type_seq,seq_size,header,sequence,tpm,fpkm]

if args.db.lower() == "m":
    # Creating Mongo connection and DB
    conn = pymongo.MongoClient('localhost', 27017)
    db = conn.sequencesdb
    collections = db.list_collection_names()

    # Checking if the collection exists
    if 'proteins' in collections:
        db.proteins.drop()
    else:
        db.create_collection("proteins")

    for v in infos_to_store_mongo.values():
        db.proteins.insert_one(v)

    print("{} itens inserted into MongoDB".format(db.proteins.count_documents({})))

elif args.db.lower() == "s":
    # Remove db if already exists
    if os.path.exists("biosequences.db"):
        os.remove("biosequences.db") 
    
    #If database does not exists, it is created at this moment
    con = sqlite3.connect('biosequences.db')
    #Create a cursor allows to access all the records in dataset
    cur = con.cursor()
    #Create a table
    sql_create = 'create table proteins\
                (id integer primary key,\
                code varchar(15),\
                species varchar(15),\
                type_seq varchar(20),\
                seq_size integer,\
                annotation varchar(200),\
                sequence text,\
                tpm real,\
                fpkm real)'
    cur.execute(sql_create)
    # Null allow add primary key
    sql_insert = 'insert into proteins values (NULL,?,?,?,?,?,?,?,?)'

    for rec in infos_to_store_sql.values():
        cur.execute(sql_insert, rec)
    con.commit()
    print("Itens inserted into SQL database")
    con.close()

else:
    print("Error: Select a valid database (Set s or m )")