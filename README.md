# girotracker

Track the stage by stage development of the general classification at the Giro d'Italia 2016

## Usage

### Install dependencies:

```nohighlight
virtualenv venv
source venv/bin/activate
pip install requests lxml
```

### Run the script:

To fetch latest stage data first, remove the `cache` directory.

```nohighlight
python track.py
```

As a result, you get some CSV and JSON files with per rider, per stage classification data.

## Output data

### `rider_results.json` and `rider_results.min.json`

This is an object with one key per rider, where the key is the rider's unique identifier. Each value is an object like this:

```json
{
  "accumulated_times": [710, 17421, 33246, ...], 
  "country": "ITA", 
  "name": "POZZOVIVO Domenico", 
  "stage_ranks": [97, 88, 56, ...], 
  "team_id": "ALM", 
  "team_name": "AG2R LA MONDIALE"
}
```

The attributes:

- `accumulated_times`: Array with total time ridden by this rider after each stage, in seconds
- `country`: Country of the rider
- `name`: Last name and first name of the rider
- `stage_ranks`: Array with the rider's rank after each stage
- `team_id`: Unique identifier of the rider's team
- `team_name`: Name of the rider's team

## Source data

For each stage, these files can be available (`<num>` is replaced by the two digity, zero-padded stage number):

- `cls_rosa_<num>.xml`: General classification
- `cls_tp_<num>.xml`: Stage results for each rider
- `rit_tp_<num>.xml`: Riders who retired during or after this stage. May be an empty list.

(to be continued)
