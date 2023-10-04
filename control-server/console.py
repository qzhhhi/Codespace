import csv
import ast
import json
import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser(
    prog="console",
    description="Console of codespace server.",
    epilog="(C)Copyright: NJUST.Alliance - All rights reserved"
)

parser.add_argument("--host", default="127.0.0.1", help="Hostname of MongoDB server.")
parser.add_argument("--port", default=27017, type=int, help="Port of MongoDB server.")

subparsers = parser.add_subparsers(dest="function", required=True)

whitelist_parser = subparsers.add_parser("whitelist")
whitelist_parser.add_argument("--ls", action="store_true", help="List all items.")
whitelist_parser.add_argument("--find", metavar="FILTER", help="List all items found by filter.")
whitelist_parser.add_argument("--rm", metavar="FILTER", help="Remove items found by filter.")
whitelist_parser.add_argument("--insert", metavar="DATA", help="Insert JSON format data.")
whitelist_parser.add_argument("--insert-csv", metavar="PATH", help="Insert multiline csv file.")
whitelist_parser.add_argument("--enable", metavar="PATH", help="Enable items found by filter.")
whitelist_parser.add_argument("--disable", metavar="PATH", help="Disable items found by filter.")

account_parser = subparsers.add_parser("account")
account_parser.add_argument("--ls", action="store_true", help="List all items.")
account_parser.add_argument("--find", metavar="FILTER", help="List all items found by filter.")
account_parser.add_argument("--rm", metavar="FILTER", help="Remove items found by filter.")
account_parser.add_argument("--insert", metavar="DATA", help="Insert JSON format data.")

args = parser.parse_args()
print(args)

mongo = MongoClient(f"mongodb://root:password@{args.host}:{args.port}")
# whitelist = mongo["user"]["whitelist"]
# accounts = mongo["user"]["account"]

titles = set(["_id", "name", "tel", "qq", "batch", "enabled"])

def to_filter(str):
    try:
        int(str)
        return {"_id": str}
    except:
        return json.loads(str)

target_collection = mongo["user"][args.function]

if args.ls:
    for data in target_collection.find({}):
        print(json.dumps(data, ensure_ascii=False))
    print(f"Found data count: {target_collection.count_documents({})}.")
elif args.find:
    filter = to_filter(args.find)
    for data in target_collection.find(filter):
        print(json.dumps(data, ensure_ascii=False))
    print(f"Found data count: {target_collection.count_documents(filter)}.")
elif args.rm:
    filter = to_filter(args.rm)
    data_list = target_collection.find(filter)
    for data in data_list:
        print(json.dumps(data, ensure_ascii=False))
    confirmation = input(f"A total of {target_collection.count_documents(filter)} pieces of data will be removed, are you sure? y/n: ")
    if confirmation.lower() == "y":
        target_collection.delete_many(filter)
elif args.insert:
    data = json.loads(args.insert)
    if titles == set(data.keys()):
        target_collection.insert_one(data)
        print(f"Successfully inserted following data:\n{data}")
    else:
        print(f"Inserted data MUST satisfy: key equals to {titles}")
elif args.insert_csv:
    with open(args.insert_csv) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        csv_title = None
        data_list = []
        for row in csv_reader:
            if csv_title is None:
                csv_title = row
                if titles != set(csv_title):
                    print(f"Inserted data title MUST satisfy: {titles}")
                    break
            else:
                data = dict(zip(csv_title, row))
                data["batch"] = int(data["batch"])
                data["enabled"] = False if data["enabled"] == "0" else True
                print(json.dumps(data, ensure_ascii=False))
                data_list.append(data)
        confirmation = input(f"A total of {len(data_list)} pieces of data will be inserted, are you sure? y/n: ")
        if confirmation.lower() == "y":
            target_collection.insert_many(data_list)
            print(f"Successfully inserted data.")
elif args.enable:
    filter = to_filter(args.enable)
    data_list = target_collection.find(filter)
    for data in data_list:
        print(json.dumps(data, ensure_ascii=False))
    confirmation = input(f"A total of {target_collection.count_documents(filter)} pieces of data will be enabled, are you sure? y/n: ")
    if confirmation.lower() == "y":
        target_collection.update_many(filter, {"$set": {"enabled": True}})
elif args.disable:
    filter = to_filter(args.disable)
    data_list = target_collection.find(filter)
    for data in data_list:
        print(json.dumps(data, ensure_ascii=False))
    confirmation = input(f"A total of {target_collection.count_documents(filter)} pieces of data will be disabled, are you sure? y/n: ")
    if confirmation.lower() == "y":
        target_collection.update_many(filter, {"$set": {"enabled": False}})