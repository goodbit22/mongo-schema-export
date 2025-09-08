#!/usr/bin/env python3
import sys
from collections import defaultdict
from datetime import datetime
import pymongo
from bson import json_util
import argparse
import logging
from typing import List
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
)


def log(verbose, *args):
    if verbose:
        print(*args)


def toInt(x):
    try:
        return int(x)
    except ValueError:
        return x
    
def read_file_collections(filename: str) -> List[str]:
    collections = []
    with open(filename) as file:
        for line in file:
            print(line.rstrip())
            collections.append(line.rstrip())
    return collections


def get_collections(client, databases):
 # Get the list of collections in the database
    try:
        db = client[databases]
        return db.list_collection_names()
    except Exception as e:
        print(f"Error fetching collections: {e}")
        sys.exit(1)
    

def pattern_collections(client, databases, pattern):
    collections = get_collections(client, databases)
    return [coll for coll in collections if re.match(f"^{pattern}", coll)]

def mongo_export(
    client: pymongo.MongoClient, fname: str, databases: str, verbose: bool
):
    """

    :param client:
    :param fname:
    :return:
    """
    out = defaultdict(dict)
    for dbname in databases.split(","):
        log(verbose, "Exporting database:", dbname)
        db = client[dbname]
        for cname in db.list_collection_names():
            coll = db[cname]
            log(verbose, "\tExporting collection", cname)
            opts = coll.options()
            autoIndexId = "autoIndexId"
            if autoIndexId in opts:
                del opts[autoIndexId]  # this is deprecated
            indexes = [dict(x) for x in coll.list_indexes()]
            out_indexes = []
            for i in indexes:
                i["keys"] = [[k, toInt(v)] for k, v in i["key"].items()]
                for f in "key", "ns", "v":
                    if f in i:
                        del i[f]
                out_indexes.append(i)

            out[dbname][cname] = {"indexes": out_indexes, "options": opts}
    with open(fname, "w") as out_file:
        out_str = json_util.dumps(
            {"databases": out, "exported": datetime.now().isoformat()}, indent=4
        )
        out_file.write(out_str)
    return out_str


def mongo_collections_export(
    client: pymongo.MongoClient, fname: str, databases: str, verbose: bool, collections
):
    """

    :param client:
    :param fname:
    :return:
    """
    out = defaultdict(dict)
    for dbname in databases.split(","):
        log(verbose, "Exporting database:", dbname)
        db = client[dbname]
        for cname in db.list_collection_names():
            if cname in collections:
                coll = db[cname]
                log(verbose, "\tExporting collection", cname)
                opts = coll.options()
                autoIndexId = "autoIndexId"
                if autoIndexId in opts:
                    del opts[autoIndexId]  # this is deprecated
                indexes = [dict(x) for x in coll.list_indexes()]
                out_indexes = []
                for i in indexes:
                    i["keys"] = [[k, toInt(v)] for k, v in i["key"].items()]
                    for f in "key", "ns", "v":
                        if f in i:
                            del i[f]
                    out_indexes.append(i)

            out[dbname][cname] = {"indexes": out_indexes, "options": opts}
    with open(fname, "w") as out_file:
        out_str = json_util.dumps(
            {"databases": out, "exported": datetime.now().isoformat()}, indent=4
        )
        out_file.write(out_str)
    return out_str


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description="Export a schema for a mongodb database"
    )
    parser.add_argument(
        "--uri",
        metavar="uri",
        type=str,
        help="Full uri, use in place of server/port/user/auth_db, eg: mongodb://user:pass@example.com:port/auth_db",
    )
    parser.add_argument(
        "--host", metavar="h", type=str, help="Server host", default="localhost"
    )
    parser.add_argument(
        "--port", metavar="p", type=int, help="Server port", default=27017
    )
    parser.add_argument(
        "--username", metavar="u", type=str, help="Username", default=""
    )
    parser.add_argument(
        "--password", metavar="pwd", type=str, help="Password", default=""
    )
    parser.add_argument(
        "--authSource",
        metavar="a",
        type=str,
        help="DB to auth against",
        default="admin",
    )
    parser.add_argument(
        "--file",
        metavar="f",
        type=str,
        help="Path to exported .json file",
        default="config.json",
    )
    parser.add_argument(
        "--databases",
        metavar="db",
        type=str,
        help="Databases separated by a comma, eg: db_1,db_2,db_n",
    )
    parser.add_argument(
        "--collection",
        metavar="col",
        type=str,
        help="Collection name"
    )

    parser.add_argument(
        "--filecollections",
        metavar="filecol",
        type=str,
        help="Filename file consist name collection"
    )

    parser.add_argument(
        "--pattern",
        metavar="pattern",
        type=str,
        help="Pattern to match collections"
    )

    parser.add_argument("--all", action="store_true", help="Export all databases")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    args = parser.parse_args(argv[1:])

    if args.uri:
        _client = pymongo.MongoClient(args.uri)
    else:
        client_args = {}
        for i in "host", "port", "username", "password", "authSource":
            if hasattr(args, i):
                client_args[i] = getattr(args, i)
        _client = pymongo.MongoClient(**client_args)
    if args.databases:
        databases = args.databases
    if args.collection:
        collections = args.collection
    elif args.filecollections:
        filename = args.filecollections
        collections =  read_file_collections(filename)
    elif args.pattern:
        pattern = args.pattern
        collections = pattern_collections(_client, databases, pattern)
    elif args.all:
        databases = ",".join(_client.database_names())
    else:
        exit("Please specify at least one database to export")

    if collections:
        s = mongo_collections_export(_client, args.file, databases, args.verbose, collections)
    else:
        s = mongo_export(_client, args.file, databases, args.verbose)

    if args.verbose:
        print(s)


if __name__ == "__main__":
    sys.exit(main() or 0)
