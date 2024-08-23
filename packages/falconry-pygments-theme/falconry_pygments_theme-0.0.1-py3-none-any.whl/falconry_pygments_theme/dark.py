# Copyright 2024 by Falconry maintainers.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Other,
    Punctuation,
    String,
    Text,
)


class FontStyle:
    bold = 'bold'
    italic = 'italic'


class Colors:
    yellow = '#ffc66d'
    orange = '#c26230'
    crimson = '#dc143c'
    brown = '#bc9458'
    green = '#a5c261'
    blue = '#d0d0ff'
    darkgray = '#202020'
    white = '#e6e1dc'


class DarkTheme(Style):
    """Falconry dark Pygments style."""

    default_style = ''

    background_color = Colors.darkgray
    highlight_color = '#ffd9002e'

    styles = {
        Text: Colors.white,  # class:  ''
        Error: Colors.crimson,  # class: 'err'
        Other: '',  # class 'x'
        Comment: FontStyle.italic + ' ' + Colors.brown,  # class: 'c'
        Keyword: Colors.orange,  # class: 'k'
        Keyword.Constant: Colors.orange,  # class: 'kc'
        # Keyword.Declaration:       "",            # class: 'kd'
        # Keyword.Namespace:         "",            # class: 'kn'
        # Keyword.Pseudo:            "",            # class: 'kp'
        # Keyword.Reserved:          "",            # class: 'kr'
        Keyword.Type: Colors.orange,  # class: 'kt'
        Operator: Colors.green,  # class: 'o'
        Operator.Word: Colors.white,  # class: 'ow'
        Punctuation: Colors.white,  # class: 'p'
        Name: Colors.white,  # class: 'n'
        Name.Attribute: Colors.yellow,  # class: 'na'
        Name.Builtin: Colors.orange,  # class: 'nb'
        Name.Builtin.Pseudo: Colors.orange,  # class: 'bp'
        Name.Class: Colors.yellow,  # class: 'nc'
        Name.Constant: Colors.blue,  # class: 'no'
        Name.Decorator: Colors.orange,  # class: 'nd'
        Name.Entity: Colors.green,  # class: 'ni'
        Name.Exception: Colors.crimson,  # class: 'ne'
        Name.Function: Colors.yellow,  # class: 'nf'
        Name.Property: Colors.white,  # class: 'py'
        Name.Label: Colors.white,  # class: 'nl'
        Name.Namespace: Colors.white,  # class: 'nn'
        # Name.Other:                "",            # class: 'nx'
        Name.Tag: Colors.blue,  # class: 'nt'
        Name.Variable: Colors.white,  # class: 'nv'
        Name.Variable.Magic: Colors.orange,
        # Name.Variable.Class:       "",            # class: 'vc'
        # Name.Variable.Global:      "",            # class: 'vg'
        # Name.Variable.Instance:    "",            # class: 'vi'
        Number: Colors.orange,  # class: 'm'
        # Number.Float:              "",            # class: 'mf'
        # Number.Hex:                "",            # class: 'mh'
        # Number.Integer:            "",            # class: 'mi'
        # Number.Integer.Long:       "",            # class: 'il'
        # Number.Oct:                "",            # class: 'mo'
        Literal: Colors.blue,  # class: 'l'
        # Literal.Date:              "",            # class: 'ld'
        String: Colors.green,  # class: 's'
        String.Backtick: Colors.green,  # class: 'sb'
        # String.Char:               "",            # class: 'sc'
        # String.Doc:                "",            # class: 'sd'
        # String.Double:             "",            # class: 's2'
        # String.Escape:             "",            # class: 'se'
        # String.Heredoc:            "",            # class: 'sh'
        # String.Interpol:           "",            # class: 'si'
        # String.Other:              "",            # class: 'sx'
        String.Regex: Colors.crimson,  # class: 'sr'
        # String.Single:             "",            # class: 's1'
        String.Symbol: Colors.blue,  # class: 'ss'
        # Generic:                   "",            # class: 'g'
        Generic.Deleted: Colors.crimson,  # class: 'gd',
        Generic.Emph: FontStyle.italic,  # class: 'ge'
        # Generic.Error:             "",            # class: 'gr'
        Generic.Heading: Colors.yellow,  # class: 'gh'
        Generic.Subheading: Colors.blue,  # class: 'gu'
        # Generic.Inserted:          "",            # class: 'gi'
        # Generic.Output:            "",            # class: 'go'
        # Generic.Prompt:            "",            # class: 'gp'
        Generic.Strong: FontStyle.bold,  # class: 'gs'
        # Generic.Traceback:         "",            # class: 'gt'
    }
