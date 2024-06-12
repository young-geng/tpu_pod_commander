from setuptools import setup, find_packages

setup(
    name='tpc',
    version='0.1.0',
    license='Apache-2.0',
    description='TPU pod commander.',
    url='https://github.com/young-geng/tpc',
    packages=find_packages(include=['tpc']),
    python_requires=">=3.8",
    install_requires=[
        'absl-py',
        'mlxu>=0.2.0',
    ],
    entry_points={
        'console_scripts': [
            'tpc = tpc.tpc:run_tpc',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ],
)