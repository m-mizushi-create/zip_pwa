import csv, json, sys
from collections import defaultdict

# python build_index_bundle.py KEN_ALL.CSV index_bundle.json
src = sys.argv[1]
dst = sys.argv[2]

def norm(s: str) -> str:
  return (s or "").replace("　","").replace(" ","").strip()

townIndex = defaultdict(set)  # "長野県須坂市塩川町" -> {"382-...."}
tmp_city_town = defaultdict(lambda: defaultdict(set))  # cityKey -> town -> set(zips)
cityNameIndex = defaultdict(set)  # "須坂市" -> {"長野県須坂市", ...}

with open(src, "r", encoding="cp932", newline="") as f:
  r = csv.reader(f)
  for row in r:
    zip7 = row[2]
    pref = norm(row[6])
    city = norm(row[7])
    town = norm(row[8])

    if not pref or not city:
      continue

    z = f"{zip7[:3]}-{zip7[3:]}"
    cityKey = pref + city
    townKey = cityKey + town

    townIndex[townKey].add(z)
    tmp_city_town[cityKey][town].add(z)
    cityNameIndex[city].add(cityKey)

# cityIndex 整形
cityIndex = {}
for cityKey, town_map in tmp_city_town.items():
  arr = []
  for town, zset in town_map.items():
    arr.append({"town": town, "zips": sorted(list(zset))})
  arr.sort(key=lambda x: x["town"])
  cityIndex[cityKey] = arr

bundle = {
  "townIndex": {k: sorted(list(v)) for k, v in townIndex.items()},
  "cityIndex": cityIndex,
  "cityNameIndex": {k: sorted(list(v)) for k, v in cityNameIndex.items()}
}

with open(dst, "w", encoding="utf-8") as f:
  json.dump(bundle, f, ensure_ascii=False)

print("wrote", dst, "townKeys", len(bundle["townIndex"]), "cities", len(bundle["cityIndex"]))
