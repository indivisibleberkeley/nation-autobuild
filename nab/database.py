import plyvel
import uuid
import io
import csv
import json
import re
from datetime import datetime
from collections import defaultdict, namedtuple

SignupEntry = namedtuple("SignupEntry", ["email", "tag_list"])

def get_connection():
    from nab import app
    return NationAutoBuildDatabase(app.config)

def date_from_string(datestr):
    parts = datestr.split(" ")
    notz_str = " ".join(parts[:-1])
    return datetime.strptime(notz_str, "%m/%d/%Y %I:%M %p")

UUID_RE = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

def parse_uuid(uuidstr):
    if not UUID_RE.match(uuidstr):
        return None
    return uuid.UUID(uuidstr)

class NationAutoBuildDatabase(object):
    def __init__(self, config):
        self.db = plyvel.DB(config["LEVELDB_NAME"], create_if_missing=True)
        self.encoding = config.get("LEVELDB_ENCODING", "utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def store_signup_file(self, csvfile):
        oid = uuid.uuid1()
        prefix = b"signups/" + oid.bytes

        rdr = csv.reader(io.StringIO(csvfile.read().decode("utf-8")))
        # Skip the first two lines
        next(rdr)
        next(rdr)

        with self.db.write_batch() as wb:
            # Store the headers
            headers = next(rdr)
            headerdata = bytes("\n".join(headers), self.encoding)
            wb.put(prefix + b"/headers", headerdata)

            columns = [[] for _ in range(0, len(headers))]

            # Store the columns separately
            for row in rdr:
                for i, val in enumerate(row):
                    columns[i].append(val)

            for i, col in enumerate(columns):
                key = prefix + b"/columns/" + bytes(str(i), self.encoding)
                value = bytes("\n".join(col), self.encoding)
                wb.put(key, value)

        return oid

    def get_column_names(self, uuidstr):
        oid = parse_uuid(uuidstr)
        if not oid:
            return None
        headerdata = self.db.get(b"signups/" + oid.bytes + b"/headers")
        if not headerdata:
            return []
        headers = headerdata.decode(self.encoding).split("\n")
        return headers

    def get_signup_column(self, oid, colid):
        key = b"signups/" + oid.bytes + b"/columns/" + bytes(colid, self.encoding)
        coldata = self.db.get(key)
        if not coldata:
            return []
        return coldata.decode(self.encoding).split("\n")

    def get_unique_roles(self, uuidstr, role_col):
        oid = parse_uuid(uuidstr)
        if not oid:
            return None
        rolelist = self.get_signup_column(oid, role_col)
        return set([role.lower() for role in rolelist])

    def generate_csv(self, uuidstr, date_col, email_col, role_col, rolemap):
        oid = parse_uuid(uuidstr)
        if not oid:
            return None

        dates = self.get_signup_column(oid, date_col)
        emails = self.get_signup_column(oid, email_col)
        roles = self.get_signup_column(oid, role_col)

        tag_template = "event/elections/phonebank/monthly/%Y/%m/{}"
        member_map = defaultdict(set)

        for (date, email, role) in zip(dates, emails, roles):
            dateobj = date_from_string(date)
            category = rolemap.get(role.lower())
            if email and category:
                tag = dateobj.strftime(tag_template).format(category)
                member_map[email].add(tag)

        buf = io.StringIO()
        wtr = csv.writer(buf)

        for (email, tagset) in member_map.items():
            tagcol = ",".join(tagset)
            wtr.writerow([email, tagcol])

        self.db.put(
                b"signups/" + oid.bytes + b"/result",
                bytes(buf.getvalue(), self.encoding))

    def get_csv(self, uuidstr):
        oid = parse_uuid(uuidstr)
        if not oid:
            return None
        return self.db.get(b"signups/" + oid.bytes + b"/result")

    def get_csv_entries(self, uuidstr):
        csvdata = self.get_csv(uuidstr)
        if not csvdata:
            return None

        f = io.StringIO(csvdata.decode(self.encoding))
        rdr = csv.reader(f)

        for row in rdr:
            yield SignupEntry(row[0], row[1].split(","))

