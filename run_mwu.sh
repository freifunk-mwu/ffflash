#!/bin/bash

CDIR=$(cd "$(dirname "$0")"; pwd)
FLASH="$CDIR/ffflash.py"

function run()
{
    local WWWDIR="$1"
    local APIFILE="$2"
    local NODELIST="$3"
    local SITE="$4"

    $FLASH \
        "$WWWDIR/$APIFILE" \
        "--nodelist" "$NODELIST" \
        "--rankfile" "$WWWDIR/score.json" \
        "--sidecars" \
            "$WWWDIR/inc/contact.yaml" \
            "$WWWDIR/inc/services.yaml" \
            "$WWWDIR/inc/support.club.yaml" \
            "$WWWDIR/inc/support.donations.campaigns.yaml" \
            "$WWWDIR/inc/timeline.yaml" \
        "-st" "$SITE" \
        "-v"

    if [ $? -ne 0 ]; then echo "# error processing $APIFILE"; fi
}

run "/var/www/freifunk.net/api.wiesbaden" "ffapi_wi.json" "https://map.freifunk-mwu.de/data/nodes.json" "ffwi"
run "/var/www/freifunk-mainz.de/api" "ffapi_mz.json" "https://map.freifunk-mwu.de/data/nodes.json" "ffmz"
