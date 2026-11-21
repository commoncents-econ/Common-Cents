import csv, io, json, os, urllib.request, datetime as dt

URL = "https://www.rba.gov.au/statistics/tables/csv/f1.1-data.csv"
SERIES = "FIRMMCRT"  # cash rate target

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (econ-basics data updater)"})
raw = urllib.request.urlopen(req, timeout=60).read().decode("latin-1")
rows = list(csv.reader(io.StringIO(raw)))

hdr = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Series ID")
col = [c.strip() for c in rows[hdr]].index(SERIES)

def parse(s):
    for f in ("%d-%b-%Y", "%d/%m/%Y", "%d-%b-%y"):
        try:
            return dt.datetime.strptime(s.strip(), f)
        except ValueError:
            pass
    return None

obs = []
for r in rows[hdr + 1:]:
    if len(r) <= col or not r[col].strip():
        continue
    d = parse(r[0])
    if not d:
        continue
    try:
        obs.append((d, float(r[col])))
    except ValueError:
        pass

obs.sort()
monthly = {}
for d, v in obs:
    monthly[d.strftime("%Y-%m")] = v  # keeps last value in each month

points = [{"d": k, "v": v} for k, v in sorted(monthly.items()) if k >= "1990-01"]
os.makedirs("data", exist_ok=True)
with open("data/cash-rate.json", "w") as f:
    json.dump({"source": URL, "updated": dt.date.today().isoformat(), "points": points}, f)
print("Wrote", len(points), "points")
