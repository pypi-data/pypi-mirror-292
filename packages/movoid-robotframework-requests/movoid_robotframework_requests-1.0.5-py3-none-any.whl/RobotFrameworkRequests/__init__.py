#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/30 21:16
# Description   : 
"""
from .main import RobotRequestsBasic


class RobotFrameworkRequests(RobotRequestsBasic):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
