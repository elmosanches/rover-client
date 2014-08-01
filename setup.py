import os
from setuptools import setup

setup(
    name = "rover_client",
    version = "0.0.1",
    author = "Przemyslaw Rekawiecki",
    author_email = "przemek.rek@gmail.com",
    description = ("Rover client sending arduino results to RC server"),
    license = "BSD",
    keywords = "rover client",
    packages=['rover_client'],
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: RC Rover Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        'console_scripts': [
            'rover_client = rover_client.client:main',
        ]
    },
    install_requires=['twisted', 'pyserial']
)
