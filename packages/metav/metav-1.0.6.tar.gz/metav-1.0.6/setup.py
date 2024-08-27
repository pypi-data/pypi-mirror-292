# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r",encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name="metav",
  version="1.0.6",
  author="Zhi-Jian Zhou",
  author_email="zjzhou@hnu.edu.cn",
  description="rapid detection and classification of viruses in metagenomics sequencing.",
  keywords="virus detection, sequencing, metagenomics",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ZhijianZhou01/nextvirus",
  packages=setuptools.find_packages(),

  classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        
    ],
  entry_points={
             'console_scripts': [
                 'metav = metav.main:starts',
             ],
    }
)
