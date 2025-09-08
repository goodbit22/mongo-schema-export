import sys
import re
import pymongo
import argparse


def get_collections(client, databases):
 # Get the list of collections in the database
    try:
        db = client[databases]
        return db.list_collection_names()
    except Exception as e:
        print(f"Error fetching collections: {e}")
        sys.exit(1)
    

def create_file_collections(client, databases, pattern, filename="collections.txt"):
    collections = get_collections(client, databases)
    matching_collections = [coll for coll in collections if re.match(f"^{pattern}", coll)]
    try:
        with open(filename, 'w') as f:
            for coll in matching_collections:
                f.write(f"{coll}\n")
        print(f"Collections matching the pattern '{pattern}' have been written to '{filename}'.")
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description="Export a collections name for a mongodb database"
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
        "--databases",
        metavar="db",
        type=str,
        help="Databases separated by a comma, eg: db_1,db_2,db_n",
    )
    parser.add_argument(
        "--filename",
        metavar="file",
        type=str,
        help="filename",
    )
    parser.add_argument(
        "--pattern",
        metavar="pattern",
        type=str,
        help="pattern",
    )
    args = parser.parse_args(argv[1:])

    if args.uri:
        _client = pymongo.MongoClient(args.uri)
    else:
        client_args = {}
        for i in "host", "port", "username", "password", "authSource":
            if hasattr(args, i):
                client_args[i] = getattr(args, i)        
        _client = pymongo.MongoClient(**client_args)
    if args.filename:
        filename = args.filename
    if args.pattern and  args.databases:
        pattern = args.pattern
        databases = args.databases
        create_file_collections(_client, databases, pattern, filename)
    else:
        print("pattern and database not specified")

if __name__ == "__main__":
    sys.exit(main() or 0)