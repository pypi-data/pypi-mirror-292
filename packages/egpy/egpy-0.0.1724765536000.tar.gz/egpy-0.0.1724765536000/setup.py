import os
from setuptools import setup

setup(
  name="egpy",
  version=os.environ.get("EGPY_VERSION", "0.0.0"),
  py_modules=["eg", "metrics"],
  install_requires=["grpcio", "grpcio-tools", "uuid7"],
)
