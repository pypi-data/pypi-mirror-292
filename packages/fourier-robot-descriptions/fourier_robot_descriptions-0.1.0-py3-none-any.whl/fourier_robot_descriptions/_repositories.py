#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Git utility functions to clone model repositories."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Repository:
    """Remote git repository.

    Attributes:
        cache_path: Path to clone the repository to in the local cache.
        commit: Commit ID or tag to checkout after cloning.
        url: URL to the remote git repository.
    """

    cache_path: str
    commit: str
    url: str
    
REPOSITORIES: Dict[str, Repository] = {
    "fourier_descriptions": Repository(
        url="https://gitee.com/FourierIntelligence/Fourier_Models.git",
        commit="333163820380615be81fd373a6baec0adf3e398e",
        cache_path="fourier_descriptions",
    )}