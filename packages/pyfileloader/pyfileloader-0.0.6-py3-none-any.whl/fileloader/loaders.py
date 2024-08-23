import csv
import gzip
import json
import sys


def detect_bom(file: str):
    # Open the file in binary mode to read raw bytes
    with open(file, "rb") as f:
        # Read the first 4 bytes of the file
        raw = f.read(4)

    # Check for the BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        return "UTF-8-SIG"
    elif raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
        return "UTF-32-SIG"
    elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "UTF-16-SIG"
    else:
        return "UTF-8"


def load_json(file: str):
    openfn = open
    needs_decode = False
    if file.endswith("gz"):
        openfn = gzip.open
        needs_decode = True

    with openfn(file, "r") as f:
        data = f.read()
    if needs_decode:
        data = data.decode("UTF-8")

    item = json.load(data)
    return item


def load_jsonl(file: str):
    lines = load_text(file)
    items = []
    for line in lines:
        items.append(json.loads(line))

    return items


def load_text(file: str):
    openfn = open
    needs_decode = False
    if file.endswith("gz"):
        openfn = gzip.open
        needs_decode = True

    items = []
    with openfn(file, "r") as f:
        for line in f:
            if needs_decode:
                line = line.decode("UTF-8")

            items.append(line.strip())

    return items


def load_csv(file: str, enc: str = ""):

    # if the encoding isn't explicit
    if enc = "":
        enc = detect_bom(file)

    # the resulting binary stream when opening with gzip.open needs to be handled
    # in a different manner than the other functions

    if file.endswith("gz"):
        print("Unsupported .gz extension. Manually gunzip first")
        sys.exit(1)

    items = []
    file_csv = csv.DictReader(open(file, mode="r", encoding=enc))
    for row in file_csv:
        items.append(row)

    return items


if __name__ == "__main__":

    # lines = load_text(sys.argv[1])
    lines = load_csv(sys.argv[1])

    print(lines)
