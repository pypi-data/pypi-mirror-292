from setuptools import setup

setup(
    name='cstation',
    version='0.1.8',
    py_modules=['cstation'],
    package_dir={"commands": "commands"},
    url="https://github.com/ansis-ai/cstation.git",
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'cstation = cstation:cli',
        ],
    },
)