#!/bin/bash 
python ../qr/src/setup_test_environment.py -f dummy.txt -p simulation_data -o random.tsv -s 3 -r $1
python ../qr/src/smpc_fed_qr.py -M3 -I0 -k simulation_data/data/0/random.tsv -o simulation_data/results/0 -p output & \
python ../qr/src/smpc_fed_qr.py -M3 -I1 -k simulation_data/data/1/random.tsv -o simulation_data/results/1 -p output & \
python ../qr/src/smpc_fed_qr.py -M3 -I2 -k simulation_data/data/2/random.tsv -o simulation_data/results/2 -p output
python ../qr/src/verify_output.py -q output_Q.tsv -d simulation_data/ -s 3 -f data.tsv -r output_R.tsv
