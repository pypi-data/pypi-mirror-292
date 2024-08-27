# pitchbase

[![PyPI version](https://badge.fury.io/py/pitchbase.svg)](https://badge.fury.io/py/pitchbase)
[![Build Status](https://secure.travis-ci.org/toyama0919/pitchbase.png?branch=master)](http://travis-ci.org/toyama0919/pitchbase)

Command Line utility for pitchbase.

Support python3 only.

## Settings

### config file($HOME/.pitchbase)

```yaml
default:
  host: stg-ap.pitchbase.jp
  organization_code: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  username: hiroshi.toyama
  password: xxxxxxxxxx
  grant_type: xxxxxxxxxx
```

### environment variables

```sh
export PITCHBASE_HOST=stg-ap.pitchbase.jp
export PITCHBASE_ORGANIZATION_CODE=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export PITCHBASE_USERNAME=hiroshi.toyama
export PITCHBASE_PASSWORD=xxxxxxxxxx
export PITCHBASE_GRANT_TYPE=xxxxxxxxxx
```

## Examples

#### get pitch-data by command line

```bash
$ pitchbase pitch-data --filter="game_id eq '2021051427'" | jq .
{
  "results": [
    {
      "1b_code": "2019007",
      "2b_code": "2020065",
      "3b_code": "2021049",
      "__c": 1620982019374,
      "__u": 1621089404671,
      "_id": "17bb26ebcb7c07aa1caedef7f4e1342a_2021051427_011010101",
      ...

```

#### get movie-angle by command line

```bash
$ pitchbase movie-angle --filter="game_id eq '2021080527'" | jq .
{
  "results": [
    {
      "__c": 1628685058185,
      "__u": 1628688147039,
      "_id": "6113c3021bf476531525d8b5",
      ...
```

#### get game-schedule by command line

```bash
pitchbase game-schedule --filter="game_id eq '2021080527'" | jq .
{
  "results": [
    {
      "__c": 1628160045124,
      "__u": 1628259411117,
      ...
```

#### get trackman record by command line

```bash
pitchbase trackman-record --filter="game_id eq '2021051427'" | jq .
{
  "results": [
    {
      "__c": 1628160045124,
      "__u": 1628259411117,
      ...
```

#### get player-master by command line

```bash
pitchbase player-master --filter="team.code eq 2012001" | jq .
{
  "results": [
    {
      "__c": 1610950983947,
      "__u": 1615180733457,
      "affiliation_history": null,
      "batting": "R",
      "birthday": 20010703,
      "birthplace": null,
      "blood_type": "AB",
      "disabled": false,
      "draft_year": "2019",
      "ebis_code": null,
      "face_file": "https://stg-www.pitchbase.jp/img/profile/2021/2012001/2020002.jpg",
      "fixed": true,
      "height": null,
      "is_latest": true,
      "join_date": null,
      "join_scene": null,
      "join_year": null,
      "last_game_date": null,
      "leave_date": null,
      "note": null,
      "order": null,
      "organization_code": null,
      "pitching": "R",
      "player_code": "2020002",
      "player_name": "東妻　純平",
      "player_name_en": "Jumpei Azuma",
      "player_no": "57",
      "player_short_name": "東　妻",
      "player_short_name_en": null,
      "player_type": null,
      "runner_rank": null,
      "season": 2021,
      "simple_player_code": "2",
      "team": {
        "code": "2012001",
        "sub_id": "12",
        "name": "横浜ＤｅＮＡベイスターズ"
      },
      "throwing_style": null,
      "weight": null
    },
    ...
```

#### get team-master by command line

```bash
$ pitchbase team-master --filter="season eq 2021" | jq .
{
  "results": [
    {
      "__c": 1610951278169,
      "__u": 1610951278169,
      "bis_team_code": "1992001",
      "classification": null,
      "disabled": false,
      "division": null,
      "fixed": true,
      "home_stadium_code": null,
      "is_latest": true,
      "league": "P",
      "order": null,
      "organization_code": null,
      "parent_team_code": null,
      "season": 2021,
      "team_code": "1992001",
      "team_formal_name": "千葉ロッテマリーンズ",
      "team_formal_name_en": null,
      "team_initial": "ロ",
      "team_name": "マリーンズ",
      "team_name_e": "Marines",
      "team_name_es": "M",
      "team_name_s": "ロッテ",
      "team_name_tm": [
        "CHI_MAR",
        "MIN_MAR"
      ]
    },
    ...
```


## Python API

```py
from boto3.session import Session
from pitchbase.auth import Auth
from pitchbase import Pitchbase
import json


client = Session().client("secretsmanager")
response = client.get_secret_value(
    SecretId='stg_pitchbase_auth_info'
)
data = json.loads(response.get("SecretString"))

auth = Auth(
    endpoint=data.get("endpoint"),
    organization_code=data.get("organization_code"),
    username=data.get("username"),
    password=data.get("password"),
    grant_type=data.get("grant_type"),
)
pitchbase = Pitchbase(auth=auth)
team_master = pitchbase.get_team_master(filter="season eq 2021")
print(team_master)
```


## Installation

```sh
$ pip install git+https://${YDB_GITHUB_TOKEN}:x-oauth-basic@github.dena.jp/AI/pitchbase@vX.X.X
```

or

```
$ pip install git+ssh://git@github.dena.jp/AI/pitchbase@vX.X.X
```

## CI

### install test package

```
$ ./scripts/ci.sh install
```

### test

```
$ ./scripts/ci.sh run-test
```

flake8 and black and pytest.

### release pypi

```
$ ./scripts/ci.sh release
```

git tag and pypi release.
