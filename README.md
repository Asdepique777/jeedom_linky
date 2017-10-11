# Exporter les données Linky de consomation personnelle en format JSON

## Il s'agit d'un fork du code de Asdepique777/jeedom_linky -- Septembre 2017

Le code à été modifié pour permettre le téléchargement des données des relevés Linky via le site web d'erdf/enedis aprés la mise à jour du site. Les modifications ont été proposées pour intégration au repo d'origine dont le code ne fonctionne plus.

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
In "gen_json.sh" script, set up environment variables containing your Enedis email and password.

	export LINKY_USERNAME="prenom.nom@mail.com"
	export LINKY_PASSWORD="password"

As the script was initially build for Jeedom environment, the defaut path targets the SCRIPT directory. For other purposes, it is possible to modify this path.

	BASE_DIR="/var/www/html/plugins/script/core/ressources/linky"

Then, just run "gen_json.sh" script to generate the JSON files.
