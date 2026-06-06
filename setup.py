from setuptools import setup, find_packages

setup(
    name="freeride",
    version="2.0.0",
    description="Free AI for Hermes Agent - Automatic free model management via OpenRouter",
    author="Shaishav Pidadi",
    url="https://github.com/Shaivpidadi/FreeRide",
    py_modules=["main", "watcher"],
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "freeride=main:main",
            "freeride-watcher=watcher:main",
        ],
    },
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)