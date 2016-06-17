#------------------------------------------------------------
# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------
# Exceptions for handling common issues
#------------------------------------------------------------

# An exception raised when you want to say user something
class UserException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)	

# An exception raised when credentials are not valid for an action
class InvalidAuthException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
