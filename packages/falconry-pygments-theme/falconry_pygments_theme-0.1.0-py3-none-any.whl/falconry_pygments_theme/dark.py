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
    Name,
    Number,
    Operator,
    String,
    Token,
)

from .common import bold, italic, bold_italic


class Colors:
    yellow = '#ffc66d'
    orange = '#c26230'
    crimson = '#dc143c'
    brown = '#bc9458'
    green = '#a5c261'
    pear = '#c9cc3f'
    blue = '#d0d0ff'
    darkgray = '#171717'
    white = '#e6e1dc'


class FalconryDarkStyle(Style):
    """Falconry dark Pygments style."""

    name = 'falconry-dark'

    background_color = Colors.darkgray
    highlight_color = Colors.white

    styles = {
        Token: Colors.white,
        Comment: italic | Colors.brown,
        Comment.PreProc: italic | Colors.brown,
        Comment.Special: bold_italic | Colors.brown,
        Keyword: bold | Colors.orange,
        Keyword.Type: Colors.blue,
        Operator: Colors.white,
        Operator.Word: Colors.white,
        String: Colors.green,
        String.Escape: Colors.pear,
        Number: Colors.pear,
        Name.Builtin: bold | Colors.orange,
        Name.Builtin.Pseudo: Colors.blue,
        Name.Variable: Colors.white,
        Name.Variable.Magic: Colors.blue,
        Name.Constant: Colors.green,
        Name.Class: bold | Colors.yellow,
        Name.Function: bold | Colors.yellow,
        Name.Namespace: Colors.white,
        Name.Exception: Colors.crimson,
        Name.Tag: Colors.white,
        Name.Attribute: Colors.white,
        Name.Decorator: bold | Colors.blue,
        Generic.Heading: bold | Colors.yellow,
        Generic.Subheading: bold | Colors.yellow,
        Generic.Deleted: Colors.crimson,
        Generic.Inserted: Colors.blue,
        Generic.Error: Colors.crimson,
        Generic.Emph: italic,
        Generic.Strong: bold,
        Generic.Prompt: Colors.green,
        Generic.Output: Colors.yellow,
        Generic.Traceback: Colors.crimson,
        Error: Colors.crimson,
    }


__all__ = ['FalconryDarkStyle']
