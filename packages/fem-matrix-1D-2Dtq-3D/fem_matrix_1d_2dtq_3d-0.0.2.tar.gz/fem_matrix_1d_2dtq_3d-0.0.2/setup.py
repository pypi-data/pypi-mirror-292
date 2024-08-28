#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 17:49:58 2024

@author: diegomorencos
"""

from setuptools import setup,find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
      name="fem_matrix_1D_2Dtq_3D",
      version="0.0.2",
      author="Diego Morencos Pazos",
      author_email="diegomorencos3@gmail.com",
      description="Package with functions to create mass and stiffness matrix for the FEM method",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/dmorencos/fem_matrix_1D_2Dtq_3D",
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"
          ],
      install_requires=['numpy','scipy'],
      python_requires=">=3.7"
)