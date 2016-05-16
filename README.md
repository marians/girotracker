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

As a result, you get two CSV files with per rider, per stage classification data.

## Source data

For each stage, these files can be available (`<num>` is replaced by the two digity, zero-padded stage number):

- `cls_rosa_<num>.xml`: General classification
- `cls_tp_<num>.xml`: Stage results for each rider
- `rit_tp_<num>.xml`: Riders who retired during or after this stage. May be an empty list.

(to be continued)
