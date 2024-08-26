#!/usr/decentmesh/env python3

import os

from setuptools import setup, find_packages

# get key package details from decentmesh/__version__.py
about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "decentnet", "__version__.py")) as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open("README.md", "r") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.11,<4",
    install_requires=[
        "aiosqlite==0.20.0",
        "alembic==1.13.0",
        "ansicon==1.89.0",
        "argon2-cffi==23.1.0",
        "argon2-cffi-bindings==21.2.0",
        "asn1crypto==1.5.1",
        "blessed==1.20.0",
        "Brotli==1.1.0",
        "cbor2==5.6.2",
        "cffi==1.16.0",
        "click==8.1.7",
        "coincurve==18.0.0",
        "colorama==0.4.6",
        "cryptography==41.0.7",
        "Cython==3.0.6",
        "cytoolz==0.12.2",
        "ecdsa==0.18.0",
        "eciespy==0.4.1",
        "editor==1.6.6",
        "eth-hash==0.5.2",
        "eth-keys==0.4.0",
        "eth-typing==3.5.2",
        "eth-utils==2.3.1",
        "greenlet==3.0.2",
        "inquirer==3.2.4",
        "jinxed==1.2.1",
        "lz4==4.3.2",
        "Mako==1.3.0",
        "markdown-it-py==3.0.0",
        "MarkupSafe==2.1.3",
        "mdurl==0.1.2",
        "networkx==3.2.1",
        "orjson==3.9.13",
        "prometheus-client==0.19.0",
        "pycparser==2.21",
        "pycryptodome==3.19.0",
        "Pygments==2.17.2",
        "pylzma==0.5.0",
        "PyMySQL==1.1.0",
        "readchar==4.0.6",
        "redis==5.0.1",
        "rich==13.7.0",
        "runs==1.2.2",
        "setuptools==69.0.2",
        "six==1.16.0",
        "SQLAlchemy==2.0.23",
        "statsd==4.0.1",
        "statsd-exporter==3.2.1",
        "toolz==0.12.0",
        "typing_extensions==4.9.0",
        "wcwidth==0.2.13",
        "xmod==1.8.1",
        "netifaces==0.11.0",
        "qrcode==7.4.2",
    ],
    extras_require={
        "dev": ["black==22.*"],
    },
    license=about["__license__"],
    zip_safe=True,
    entry_points={
        "console_scripts": ["decentmesh=decentnet.main:main"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="Decentralized P2P Network",
)
