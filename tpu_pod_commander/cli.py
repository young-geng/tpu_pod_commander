import os
import subprocess
import re
import tempfile
import time
from absl.flags import argparse_flags
import mlxu


FLAGS, FLAGS_DEF = mlxu.define_flags_with_default(
    zone=str,
    project=str,
    name=str,
    accelerator_type=str,
    runtime_version=str,
    reserved=bool,
    spot=bool,
    upload_path=str,
    command=str,
    launch_script_path=str,
    launch_script=str,
    launch_script_remote_path=str,
    tpu_user=str,
    tmux_session_name=str,
    show_command=bool,
)


def configure_tpc(**kwargs):
    for key, value in kwargs.items():
        if key not in FLAGS_DEF:
            raise ValueError(f"Invalid config key: {key}")
        elif getattr(FLAGS, key) is None:
            # If we haven't overridden the config with a flag, use the config
            setattr(FLAGS, key, value)


def _assert_flags(**kwargs):
    for key in kwargs:
        assert getattr(FLAGS, key) is not None, f"Missing required flag: {key}"


def _execute_shell(cmd, print_output=True):
    """ Run a command in shell and print its output """
    if FLAGS.show_command:
        print(f'Running command: \n{cmd}\n')
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True,
        env=os.environ,
    )
    output_lines = []
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if print_output:
                print(output.strip())
            output_lines.append(output.strip())

    rc = process.poll()
    if rc != 0:
        raise ValueError(f"Command failed with return code {rc}")
    return rc, '\n'.join(output_lines)


def _subcommand_list():
    _assert_flags(
        zone=True,
        project=True,
    )
    _execute_shell(
        f'gcloud compute tpus tpu-vm list '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--quiet '
    )


def _subcommand_create():
    _assert_flags(
        zone=True,
        project=True,
        name=True,
        accelerator_type=True,
        runtime_version=True,
    )
    _execute_shell(
        f'gcloud alpha compute tpus tpu-vm create {FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--version={FLAGS.runtime_version} '
        f'--accelerator-type={FLAGS.accelerator_type} '
        f'--quiet '
    )


def _subcommand_queue():
    assert not FLAGS.reserved or not FLAGS.spot, "Cannot specify both reserved and spot"
    resource_type_flag = ''
    if FLAGS.reserved:
        resource_type_flag = '--reserved'
    elif FLAGS.spot:
        resource_type_flag = '--spot'

    _assert_flags(
        zone=True,
        project=True,
        name=True,
        accelerator_type=True,
        runtime_version=True,
    )
    _execute_shell(
        f'gcloud alpha compute tpus queued-resources create {FLAGS.name} '
        f'--node-id={FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--accelerator-type={FLAGS.accelerator_type} '
        f'--runtime-version={FLAGS.runtime_version} '
        f'--quiet '
        f'{resource_type_flag}'
    )


def _subcommand_ls_queue():
    _assert_flags(
        zone=True,
        project=True,
    )
    _execute_shell(
        f'gcloud alpha compute tpus queued-resources list '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--quiet '
    )


def _subcommand_del_queue():
    _assert_flags(
        name=True,
        zone=True,
        project=True,
    )
    _execute_shell(
        f'gcloud alpha compute tpus queued-resources delete {FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--quiet '
    )


def _subcommand_describe():
    _assert_flags(
        zone=True,
        project=True,
        name=True,
    )
    _execute_shell(
        f'gcloud compute tpus tpu-vm describe {FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--quiet '
    )


def _get_tpu_ips():
    _assert_flags(
        zone=True,
        project=True,
        name=True,
    )
    _, output = _execute_shell(
        f'gcloud compute tpus tpu-vm describe {FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--quiet ',
        print_output=False,
    )

    ips = []
    for line in output.split('\n'):
        ips.extend(re.findall(r'externalIp: ([0-9\.]+)$', line))
    return ips


def _subcommand_ips():
    for ip in _get_tpu_ips():
        print(ip)


def _subcommand_upload():
    _assert_flags(
        zone=True,
        project=True,
        name=True,
        upload_path=True,
    )
    for path in FLAGS.upload_path.split(','):
        local_path, remote_path = path.split(':')
        _execute_shell(
            f'gcloud alpha compute tpus tpu-vm scp '
            f'{local_path} '
            f'{FLAGS.tpu_user}@{FLAGS.name}:{remote_path} '
            f'--recurse '
            f'--worker=all '
            f'--quiet '
            f'--zone={FLAGS.zone} '
            f'--project={FLAGS.project} '
        )


def _ssh_run_command(command):
    _assert_flags(
        zone=True,
        project=True,
        name=True,
        tpu_user=True,
    )
    _execute_shell(
        f'gcloud alpha compute tpus tpu-vm ssh '
        f'{FLAGS.tpu_user}@{FLAGS.name} '
        f'--zone={FLAGS.zone} '
        f'--project={FLAGS.project} '
        f'--worker=all '
        f'--quiet '
        f'--command="{command}" '
    )


def _subcommand_run():
    _assert_flags(
        command=True,
    )
    _ssh_run_command(FLAGS.command)


def _subcommand_launch():
    _assert_flags(
        zone=True,
        project=True,
        name=True,
        tpu_user=True,
        tmux_session_name=True,
        launch_script=True,
        launch_script_remote_path=True,
    )
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(FLAGS.launch_script)
        f.flush()
        os.chmod(f.name, 0o755)
        _ssh_run_command(f'rm -f {FLAGS.launch_script_remote_path}')
        _execute_shell(
            f'gcloud alpha compute tpus tpu-vm scp '
            f'{f.name} '
            f'{FLAGS.tpu_user}@{FLAGS.name}:{FLAGS.launch_script_remote_path} '
            f'--worker=all '
            f'--quiet '
            f'--zone={FLAGS.zone} '
            f'--project={FLAGS.project} '
        )

    _ssh_run_command(
        f'tmux new-session -d -s {FLAGS.tmux_session_name} {FLAGS.launch_script_remote_path}'
    )


def _subcommand_check():
    _assert_flags(
        tmux_session_name=True,
    )
    _ssh_run_command('tmux capture-pane -pt {FLAGS.tmux_session_name} -S -2000')


def _subcommand_stop():
    _assert_flags(
        tmux_session_name=True,
    )
    _ssh_run_command(f'tmux kill-session -t {FLAGS.tmux_session_name}')


def _subcommand_reboot():
    _ssh_run_command(f'tmux new-session -d -s reboot sudo reboot')



def main(args):
    if args.config_file != '':
        with mlxu.open_file(args.config_file, 'r') as f:
            exec(f.read())

    if FLAGS.launch_script_path is not None:
        with mlxu.open_file(FLAGS.launch_script_path, 'r') as f:
            FLAGS.launch_script = f.read()

    # Finalize config with defaults
    if FLAGS.reserved is None:
        FLAGS.reserved = False
    if FLAGS.spot is None:
        FLAGS.spot = False
    if FLAGS.tpu_user is None:
        FLAGS.tpu_user = os.environ['USER']
    if FLAGS.tmux_session_name is None:
        FLAGS.tmux_session_name = 'tpc'
    if FLAGS.show_command is None:
        FLAGS.show_command = True
    if FLAGS.launch_script_remote_path is None:
        FLAGS.launch_script_remote_path = f'/home/{FLAGS.tpu_user}/tpc_launch_script.sh'


    match args.action:
        case 'list':
            _subcommand_list()
        case 'create':
            _subcommand_create()
        case 'queue':
            _subcommand_queue()
        case 'ls_queue':
            _subcommand_ls_queue()
        case 'del_queue':
            _subcommand_del_queue()
        case 'describe':
            _subcommand_describe()
        case 'ips':
            _subcommand_ips()
        case 'upload':
            _subcommand_upload()
        case 'run':
            _subcommand_run()
        case 'launch':
            _subcommand_launch()
        case 'check':
            _subcommand_check()
        case 'stop':
            _subcommand_stop()
        case 'reboot':
            _subcommand_reboot()
        case 'upload+launch':
            _subcommand_upload()
            time.sleep(2)
            _subcommand_launch()



def _parse_flags(argv):
    parser = argparse_flags.ArgumentParser(
        description="TPU pod commander",
        inherited_absl_flags=FLAGS,
    )
    parser.add_argument(
        "action",
        type=str,
        choices=[
            'debug',
            'list',
            'create',
            'queue',
            'ls_queue',
            'del_queue',
            'describe',
            'ips',
            'upload',
            'run',
            'launch',
            'check',
            'stop',
            'reboot',
            'upload+launch'
        ],
        help='Action to execute',
    )
    parser.add_argument(
        'config_file',
        type=str,
        default='',
        nargs='?',
        help='Config file to load',
    )

    return parser.parse_args(argv[1:])


def run_cli():
    mlxu.run(main, flags_parser=_parse_flags)


if __name__ == '__main__':
    run_cli()

