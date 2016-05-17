import requests
from lxml import etree
from pprint import pprint
import os
import csv
import json


base_uri = "http://xml2.temporeale.gazzettaobjects.it"
stage_path = "/Giroditalia/2016/classifiche/xml/arrivo/"
stage_menu_urimask = "menu_{stagenum:02d}.xml"
stage_cache_path = "cache/stages"

num_stages = 21

def get_stages():
    """
    Read all available XML data per stage. Data files are cached in a local
    folder for further reference.
    """
    stages = []
    for stagenum in range(1, num_stages+1):
        stage = {}
        uri = base_uri + stage_path + stage_menu_urimask.format(stagenum=stagenum)
        r = requests.get(uri)
        if r.status_code > 400:
            break
        root = etree.fromstring(r.content)
        for el in root:
            key = str(el.tag)
            if key in ["tappa"]:
                stage[key] = int(el.get("numero"))
            elif key in ["tipo_tappa"]:
                stage[key] = int(el.text)
            elif key in ("classifiche_tappa", "classifiche_generali"):
                stage[key] = {}
                for file in el.findall(".//file"):
                    stage[key][file.get("codice").lower()] = file.text
        stages.append(stage)

    for stage in stages:
        stagepath = "%s/%02d" % (stage_cache_path, stage["tappa"])
        if not os.path.exists(stagepath):
            os.makedirs(stagepath)
        for cat in ("classifiche_generali", "classifiche_tappa"):
            for key in stage[cat].keys():
                uri = base_uri + stage_path + stage[cat][key]
                r = requests.get(uri)
                with open("%s/%s" % (stagepath, stage[cat][key]), "wb+") as f:
                    f.write(r.text)


def timestring_to_seconds(s):
    parts = s.split(":")
    # from right: seconds, minutes, hours
    seconds = int(parts[-1])
    minutes = int(parts[-2])
    if len(parts) == 3:
        hours = int(parts[-3])
        return seconds + (minutes*60) + (hours*60*60)
    else:
        return seconds + (minutes*60)

def process_gc():
    """
    Reformats the general classification data from the cache
    into simple JSON, where the structure returnes is a list
    stage by stage, with a list rider by rider.
    """
    classification = []
    for stagenum in range(1, num_stages+1):
        filepath = "%s/%02d/cls_rosa_%02d.xml" % (
            stage_cache_path, stagenum, stagenum)
        if not os.path.exists(filepath):
            break
        stage = []
        with open(filepath, "rb") as f:
            xml = f.read()
            root = etree.fromstring(xml)
            for feed in root.iter("feed"):
                for classifica in feed.iter("classifica"):
                    for item in classifica.iter("item"):
                        bonus = 0
                        if item.find("abbuono").text is not None:
                            bonus = int(item.find("abbuono").text)
                        time_seconds = 0
                        if item.find("tempo").text is not None:
                            time_seconds = timestring_to_seconds(item.find("tempo").text)
                        time_difference = 0
                        if item.find("distacco").text is not None:
                            time_difference = timestring_to_seconds(item.find("distacco").text)
                        pos = {
                            "rank": int(item.find("pos").text),
                            "rider_id": int(item.find("nome").get("numero")),
                            "rider_name": item.find("nome").text,
                            "country": item.find("nazione").text,
                            "team_id": item.find("squadra").get("id"),
                            "team_name": item.find("squadra").text,
                            "bonus": bonus,
                            "time": time_seconds,
                            "time_difference": time_difference,
                        }
                        stage.append(pos)
        classification.append(stage)
    return classification


def export_development_by_rider(classification):
    # collect riders and order by ID
    riders = {}
    for item in classification[0]:  # using stage 1 to fetch all riders
        riders[str(item["rider_id"])] = {
            "name": item["rider_name"],
            "team_id": item["team_id"],
            "team_name": item["team_name"],
            "country": item["country"],
            "stage_ranks": [],
            "accumulated_times": []
        }
    # collect results
    for stage_results in classification:
        for rider_results in stage_results:
            idstr = str(rider_results["rider_id"])
            riders[idstr]["stage_ranks"].append(rider_results["rank"])
            riders[idstr]["accumulated_times"].append(rider_results["time"])
    num_stages_ridden = len(classification)
    
    # create CSV output
    headers = [
        "rider_id",
        "rider_name",
        "team_id",
        "team_name",
        "country"
    ]
    headers = headers + [("stage_" + str(n)) for n in range(1, num_stages_ridden+1)]

    rider_keys = sorted(riders.keys(), key=int)
    with open("rider_ranks.csv", "wb") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for rider_id in rider_keys:
            row = [
                rider_id,
                riders[rider_id]["name"],
                riders[rider_id]["team_id"],
                riders[rider_id]["team_name"],
                riders[rider_id]["country"],
            ] + riders[rider_id]["stage_ranks"]
            writer.writerow(row)


    with open("rider_times.csv", "wb") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for rider_id in rider_keys:
            row = [
                rider_id,
                riders[rider_id]["name"],
                riders[rider_id]["team_id"],
                riders[rider_id]["team_name"],
                riders[rider_id]["country"],
            ] + riders[rider_id]["accumulated_times"]
            writer.writerow(row)

    with open("rider_results.json", "wb") as jsonfile:
        jsonfile.write(json.dumps(riders, indent=2, sort_keys=True))

    with open("rider_results.min.json", "wb") as jsonfile:
        jsonfile.write(json.dumps(riders, sort_keys=True, separators=(',', ':')))


if __name__ == "__main__":
    if not os.path.exists(stage_cache_path):
        get_stages()
    gc = process_gc()
    export_development_by_rider(gc)
    #pprint(gc)

