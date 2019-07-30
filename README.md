# Script to export Linky consumption in JSON format !

## What is this?
This is a script based on Linkindle, created by Outadoc (https://github.com/outadoc/linkindle), allowing to get consumption from Enedis' website (https://espace-client-connexion.erdf.fr/auth/UI/Login?realm=particuliers), through API.
This generates JSON files ready to be plotted with Highcharts for example.

## Output
The script will generate 4 JSON files for :

- Half-hour power (kW)
- Daily consumption (kWh)
- Monthly consumption (kWh)
- Yearly consumption (kWh)

## Requirements
This script requires the use of Python 3 with the following dependencies:

- dateutil
- requests
- json

## Usage
Execute "config.sh" script and then change the "login" and the "pwd" (Enedis email and password)
Then, just run "gen_json.sh" script to generate the JSON files.
Fell free to add a cron to get ENEDIS data periodically.
