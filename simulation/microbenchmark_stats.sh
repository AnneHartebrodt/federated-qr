#!/bin/bash 
mkdir -p logs
start_time=$(date +%s)
for seed in 1 2 3 4 5 6 7 8 9 10
do
touch logs/log_$seed.txt
python ../qr/src/setup_test_environment.py -f dummy.txt -p simulation_data -o random.tsv -s 3 -r $seed
python ../qr/src/smpc_fed_qr.py -M3 -I0 -k simulation_data/data/0/random.tsv -o simulation_data/results/0 -p output & \
python ../qr/src/smpc_fed_qr.py -M3 -I1 -k simulation_data/data/1/random.tsv -o simulation_data/results/1 -p output & \
python ../qr/src/smpc_fed_qr.py -M3 -I2 -k simulation_data/data/2/random.tsv -o simulation_data/results/2 -p output >> logs/log_$seed.txt
python ../qr/src/verify_output.py -q output_Q.tsv -d simulation_data/ -s 3 -f data.tsv -r output_R.tsv >> logs/log_$seed.txt
done
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
echo "Elapsed time: $elapsed"
python extract_results.py

