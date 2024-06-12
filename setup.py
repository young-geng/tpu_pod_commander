from setuptools import setup, find_packages

setup(
    name='tpu_pod_commander',
    version='0.1.0',
    license='Apache-2.0',
    description='TPU pod commander is a command line tool to manage cloud TPU pods.',
    url='https://github.com/young-geng/tpu_pod_commander',
    packages=find_packages(include=['tpu_pod_commander']),
    python_requires=">=3.8",
    install_requires=[
        'absl-py',
        'mlxu>=0.2.0',
    ],
    entry_points={
        'console_scripts': [
            'tpc = tpu_pod_commander.cli:run_cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ],
)