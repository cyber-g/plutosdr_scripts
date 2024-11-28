#!/bin/bash

URL_BASE="https://github.com/analogdevicesinc/iio-oscilloscope/raw/refs/heads/main/waveforms/"

FILES="LTE10.mat \
        LTE5.mat \
        Tx_10MHz_61.44Msps_PeakScaling3.0dBFS_ETM1.1_PAR7.5dB_Offset0MHz_4Carrier.txt \
        Tx_20MHz_61.44Msps_PeakScaling3.0dBFS_ETM1.1_PAR7.5dB_Offset0MHz.txt"

# Test if signals directory exists
if [ ! -d signals ]; then
    mkdir signals
fi

for file in $FILES; do
    wget -c "$URL_BASE$file" -O signals/$file
done

### Get protected signals

# Test if token.txt exists
if [ ! -f token.txt ]; then
    echo "token.txt file not found. Fetching the files will fail."
    # Wait user input to continue
    read -p "Press enter to continue"
fi

# Load the access token stored in the file token.txt
TOKEN=$(cat token.txt)
# Project ID
PROJECT_ID=6463
URL_BASE="https://gitlab.telecom-paris.fr/api/v4/projects/$PROJECT_ID/repository/files/"
URL_POSTFIX="/raw?lfs=true&ref=main"
FILE_DIR="signals/"
FILES_PROTECTED="LTE5_61p44Msps_PAR7p5dB.mat \
                    LTE5_30p72Msps_PAR7p5dB.mat"

for file in $FILES_PROTECTED; do
    ENCODED_FILE_PATH=$(echo -n "$FILE_DIR$file" | jq -sRr @uri)
    echo curl --header "PRIVATE-TOKEN: $TOKEN" -o signals/$file "$URL_BASE$ENCODED_FILE_PATH$URL_POSTFIX"
    curl --header "PRIVATE-TOKEN: $TOKEN" -o signals/$file "$URL_BASE$ENCODED_FILE_PATH$URL_POSTFIX"
done
# Get the file https://gitlab.telecom-paris.fr/c2s/enseignement/smart-ics902/dpd-lab/-/raw/main/signals/LTE5_61p44Msps_PAR7p5dB.mat


# Get filters
URL_BASE_FTR="https://github.com/analogdevicesinc/iio-oscilloscope/raw/refs/heads/main/filters/"
FTRS="61_44_28MHz.ftr \
        LTE20_MHz.ftr"

mkdir -p filters
for file in $FTRS; do
    wget -c "$URL_BASE_FTR$file" -O filters/$file
done

