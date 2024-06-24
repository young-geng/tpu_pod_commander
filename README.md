# TPU Pod Commander
TPU Pod Commander is a package for setting up and launching jobs on Google Cloud TPU pods.

## Installation
To install TPU Pod Commander, you need to intall the gcloud cli first. Follow
[the instructions here](https://cloud.google.com/sdk/docs/install) to install it.
After installing the gcloud cli, you can install TPU Pod Commander by running the following command:
```bash
pip install tpu_pod_commander
```


## Usage
After installing TPU Pod Commander, the command `tpc` will be available in your
shell. TPC commands are all organized in the following format:
```bash
tpc <action> [config_file.py] [--flags=value ...]
```
where `<action>` is the action to perform, and paramters are specified jointly
by the optional config file and the flags. There is a one-to-one correspondence
between the flags and the parameters in the config file. When both are specified,
the flags will override the parameters in the config file.


### Actions
The following is a list of available actions:
- `list`: List all TPU pods in a given zone of a project.
- `create`: Create a TPU pod.
- `delete`: Delete a TPU pod.
- `queue`: Create a TPU pod via queued resources API.
- `ls_queue`: List all queued TPU pods.
- `cancel_queue`: Cancel a queued TPU pod.
- `describe`: Get the details of a TPU pod.
- `ips`: List the external IPs of all the hosts in a TPU pod.
- `upload`: Upload files to a TPU pod.
- `run`: Run a command on all the hosts of a TPU pod.
- `launch`: Launch a shell script job in a tmux session on all the hosts of a TPU pod.
- `check`: Check the status of a job running in the tmux session on a TPU pod.
- `stop`: Stop a job running in the tmux session on a TPU pod.
- `reboot`: Reboot all the hosts in a TPU pod.
- `unlock`: Remove the libtpu lock files on all hosts of a TPU pod.
- `stop+unlock`: Perform `stop` and `unlock` actions in sequence.
- `relaunch`: Perform `stop` and `launch` actions in sequence.
- `upload+launch`: Perform `upload` and `launch` actions in sequence.


### Config File and Flags
The optional config file is a Python file that contains the parameters for the
action. It should be in the following format:
```python
configure_tpc(
    key=value,
    ...
)
```
Note that no import statement is needed in the config file to use the
`configure_tpc` function. The paramters for `configure_tpc` has one-to-one
correspondence with the flags for the action, so for example specifying
`--zone=us-central1-a` in the command line flags is equivalent to specifying
`zone='us-central1-a'` in the config file. When both are specified for one
parameter, the flag will override the corresponding parameter in the config file.

The following is a list of available paramters:
- `zone`: The zone of the TPU pod.
- `project`: The GCP project of the TPU pod.
- `name`: The name of the TPU pod.
- `accelerator_type`: The type and size of the TPU pod, for example, `v4-256`.
- `runtime_version`: The runtime software version of the TPU pod.
- `reserved`: Whether the TPU pod should be created under reserved quota, default to `False`.
- `spot`: Whether the TPU pod should be created as a preemptible instance, default to `False`.
- `upload_path`: a comma-separated list of `<local path>:<remote path>` pairs to upload.
- `upload_remove_remote`: Whether to remove the remote files before uploading. Default to `True`.
- `command`: The command to run on the TPU pod.
- `launch_script_path`: The path to load the content of the launch script.
- `launch_script`: The content of the launch script. When both `launch_script_path`
  and `launch_script` are specified, the script content will be loaded from
  `launch_script_path` and override the `launch_script` parameter.
- `launch_script_remote_path`: The remote path on TPU pod to save the launch script,
  default to `~/tpc_launch_script.sh`.
- `tpu_user`: The username to use when connecting to the TPU pod. Default to current user.
- `tmux_session_name`: The name of the tmux session to create when launching a job.
  Default to `tpc`.
- `show_command`: Whether to show the gcloud command when excuting an action. Default to `True`.



Not all parameters are needed for all actions. The following is a list of required
parameters for each action:
- **`list`**: `zone`, `project`.
- **`create`**: `zone`, `project`, `name`, `accelerator_type`, `runtime_version`.
- **`delete`**: `zone`, `project`, `name`.
- **`queue`**: `zone`, `project`, `name`, `accelerator_type`, `runtime_version`.
- **`ls_queue`**: `zone`, `project`.
- **`cancel_queue`**: `zone`, `project`, `name`.
- **`describe`**: `zone`, `project`, `name`.
- **`ips`**: `zone`, `project`, `name`.
- **`upload`**: `zone`, `project`, `name`, `upload_path`.
- **`run`**: `zone`, `project`, `name`, `command`.
- **`launch`**: `zone`, `project`, `name`, `launch_script_path` or `launch_script`.
- **`check`**: `zone`, `project`, `name`.
- **`stop`**: `zone`, `project`, `name`.
- **`reboot`**: `zone`, `project`, `name`.
- **`unlock`**: `zone`, `project`, `name`.
- **`relaunch`**: `zone`, `project`, `name`, `launch_script_path` or `launch_script`.
- **`upload+launch`**: `zone`, `project`, `name`, `upload_path`, `launch_script_path` or `launch_script`.


## Examples
See the [examples](examples) directory for some example config files and
the corresponding commands.
