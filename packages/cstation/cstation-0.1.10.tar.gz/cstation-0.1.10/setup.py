from setuptools import setup

setup(
    name='cstation',
    version='0.1.10',
    py_modules=['cstation'],
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