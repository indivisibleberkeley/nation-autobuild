import csv
import argparse
from collections import defaultdict
from datetime import datetime

def item_to_tag(item):
    item = item.lower()
    if item.startswith("snacks for"):
        return "snacks"
    if item.startswith("deliver snacks"):
        return "snack-delivery"
    if item.startswith("simple lunch"):
        return "lunch"
    if item == "sign-in volunteer":
        return "signin"
    raise Exception("Can't process item " + item)

def cli_main():
    parser = argparse.ArgumentParser("Process SignUpGenius CSV for NationBuilder import")
    parser.add_argument("infile", help="Input CSV")
    parser.add_argument("outfile", help="Output CSV")
    args = parser.parse_args()

    tags = defaultdict(list)

    with open(args.infile) as f:
        rdr = csv.reader(f)
        # Skip the first two lines
        next(rdr)
        next(rdr)

        labels = next(rdr)
        item_idx = labels.index("Item")
        email_idx = labels.index("Email")
        start_idx = labels.index("Start Date/Time (mm/dd/yyyy)")

        for row in rdr:
            item = row[item_idx]
            email = row[email_idx]
            date = datetime.strptime("%m/%d/%Y")

            tags[email].append(item_to_tag(item))

    with open(args.outfile, "w") as f:
        wtr = csv.writer(f)
        datestr = datetime.now().strftime("%Y/%m/%d")
        prefix = "event/elections/phonebank/" + datestr + "/"

        for email in tags:
            taglist = [prefix + tag for tag in tags[email]]
            wtr.writerow([email, ",".join(taglist)])

if __name__ == "__main__":
    cli_main()
