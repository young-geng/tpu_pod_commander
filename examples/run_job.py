"""
This script demonstrates how to install software and conda evnironment on a TPU
pod. You can run this setup with the following tpc command:

tpc upload+launch run_job.py
"""


# Defines the bash script that will be executed on the TPU instance to set up
# the environment.
launch_script = r"""#! /bin/bash

source ~/miniforge3/bin/activate mintext
python /path/to/my/python/job.py

read # This will pause the script so tmux session will not close immediately
"""


# Specify all the parameters to TPC via the configure_tpc function
# Change these acchording to your project and zone and TPU pod name
configure_tpc( # type: ignore
    project='my-gcp-project',
    zone='europe-west4-b',
    name='my-tpu-pod',
    upload_path='/path/to/my/data:/path/to/remote/data',
    launch_script=launch_script,
)