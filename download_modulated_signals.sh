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

# Load the access token stored in the file token.txt
TOKEN=$(cat token.txt)
# Get the file from https://gitlab.telecom-paris.fr/c2s/enseignement/smart-ics902/dpd-lab/-/raw/main/signals/LTE5_61p44Msps_PAR7p5dB.mat
curl --header "PRIVATE-TOKEN: $TOKEN" \
https://gitlab.telecom-paris.fr/c2s/enseignement/smart-ics902/dpd-lab/-/raw/main/signals/LTE5_61p44Msps_PAR7p5dB.mat \
-o signals/LTE5_61p44Msps_PAR7p5dB.mat

