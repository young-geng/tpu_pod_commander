"""
This script demonstrates how to install software and conda evnironment on a TPU
pod. You can run this setup with the following tpc command:

tpc launch tpu_pod_setup.py
"""


# Defines the bash script that will be executed on the TPU instance to set up
# the environment.
launch_script = r"""#! /bin/bash

sudo apt-get update && sudo apt-get install -y \
    build-essential \
    python-is-python3 \
    tmux \
    htop \
    git \
    nodejs \
    bmon \
    p7zip-full \
    nfs-common

# install miniforge
rm -rf ~/Miniforge3-Linux-x86_64.sh
wget -P ~/ https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash ~/Miniforge3-Linux-x86_64.sh -b

cat > $HOME/tpu_environment.yml <<- EndOfFile
name: mintext
channels:
    - conda-forge
dependencies:
    - python=3.10
    - pip
    - numpy
    - scipy
    - matplotlib
    - seaborn
    - jupyter
    - tqdm
    - pip:
        - -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
        - jax[tpu]==0.4.28
        - flax==0.8.3
        - optax==0.2.2
        - transformers==4.41.0
        - orbax-checkpoint==0.5.14
        - sentencepiece
        - datasets
        - mlxu>=0.2.0
        - einops
        - gcsfs
EndOfFile

# install dependencies
source ~/miniconda3/bin/activate
conda init bash
conda env create -f $HOME/tpu_environment.yml
conda activate mintext
"""


# Specify all the parameters to TPC via the configure_tpc function
configure_tpc(
    project='my-gcp-project',
    zone='europe-west4-b',
    name='my-tpu-pod',
    launch_script=launch_script,
)