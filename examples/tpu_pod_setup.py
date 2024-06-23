"""
This script demonstrates how to install software and conda evnironment on a TPU
pod. You can run this setup with the following tpc command:

tpc launch tpu_pod_setup.py

The envrionment dependencies specified here is token from the
(mintext project)[https://github.com/young-geng/mintext].
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
    - pytorch
    - conda-forge
dependencies:
    - python=3.10
    - pip
    - numpy<2
    - scipy
    - matplotlib
    - seaborn
    - jupyter
    - tqdm
    - pytorch=2.3.0
    - cpuonly
    - pip:
        - -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
        - jax[tpu]==0.4.28
        - scalax>=0.2.1
        - flax==0.8.3
        - optax==0.2.2
        - transformers==4.41.0
        - torch==2.3.0
        - orbax-checkpoint==0.5.14
        - tensorflow-cpu==2.16.1
        - sentencepiece
        - datasets
        - tpu_pod_commander>=0.1.1
        - mlxu>=0.2.0
        - einops
        - gcsfs
EndOfFile


# install dependencies
source ~/miniforge3/bin/activate
conda env create -f $HOME/tpu_environment.yml
conda activate mintext
conda clean -a -y
"""


# Specify all the parameters to TPC via the configure_tpc function
# Change these acchording to your project and zone and TPU pod name
configure_tpc( # type: ignore
    project='my-gcp-project',
    zone='europe-west4-b',
    name='my-tpu-pod',
    launch_script=launch_script,
)