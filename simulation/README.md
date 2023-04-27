# Simulation of additive SMPC based QR orthonormalisation using MPyC
## Reproduce the contents of this folder


### Install the relevant packages

We chose Conda for dependency management. Assuming you have conda installed on your computer  initialize the conda environment using

(In the parent folder)
```
conda env create -f environment.yml
```

### Create and navigate into the directory
```
mkdir simulation
cd simulation
```

### Generate some sample data
This script allows you to generate sample data. Unless you specify a valid filename, the script will generate a random gaussian data matrix. If you specify a valid file, this file will instead be split into the number of specified shards.
```
python ../qr/src/setup_test_environment.py -f dummy.txt -p simulation_data -o random.tsv -s 3
python ../qr/src/setup_test_environment.py -f ../data/diabetes/diabetes.tsv -p simulation_diabetes -o diabetes.tsv -s 3
```

