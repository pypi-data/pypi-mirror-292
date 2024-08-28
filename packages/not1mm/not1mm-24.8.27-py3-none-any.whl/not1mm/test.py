#!/usr/bin/env python3
"""
NOT1MM Logger
Purpose: test alternative sound playing interface
"""
# pylint: disable=unused-import, c-extension-no-member, no-member, invalid-name, too-many-lines, no-name-in-module
# pylint: disable=logging-fstring-interpolation, logging-not-lazy, line-too-long, bare-except

from not1mm.lib.ham_utility import parse_udc

filename = "./testing/K1USNSSTOP.udc"

print(f"{parse_udc(filename)}")
