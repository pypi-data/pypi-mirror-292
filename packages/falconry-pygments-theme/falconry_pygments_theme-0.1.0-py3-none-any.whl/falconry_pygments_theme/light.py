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
    darkred = '#990000'
    # sienna = '#a0522d'
    # tuscanred = '#7c3030'
    purple = '#803070'
    darkpink = '#aa336a'

    olive = '#606000'
    green = '#355e3b'

    charcoal = '#36454f'

    # wheat = '#f5deb3'
    # almond = '#eaddca'
    # beige = '#f5f5dc'
    light = '#fff6cc'
    black = '#000000'


class FalconryLightStyle(Style):
    """Falconry light Pygments style."""

    name = 'falconry-light'

    background_color = Colors.light
    highlight_color = '#ff5733'

    styles = {
        Token: Colors.black,
        Comment: italic | Colors.charcoal,
        Comment.PreProc: italic | Colors.charcoal,
        Comment.Special: bold_italic | Colors.charcoal,
        Keyword: bold | Colors.darkred,
        Keyword.Type: Colors.olive,
        Operator: Colors.black,
        Operator.Word: Colors.black,
        String: Colors.olive,
        String.Escape: Colors.purple,
        Number: Colors.purple,
        Name.Builtin: bold | Colors.darkred,
        Name.Builtin.Pseudo: Colors.purple,
        Name.Variable: Colors.black,
        Name.Variable.Magic: Colors.purple,
        Name.Constant: Colors.green,
        Name.Class: bold | Colors.green,
        Name.Function: bold | Colors.green,
        Name.Namespace: Colors.black,
        Name.Exception: Colors.darkpink,
        Name.Tag: Colors.black,
        Name.Attribute: Colors.black,
        Name.Decorator: bold | Colors.charcoal,
        Generic.Heading: bold | Colors.green,
        Generic.Subheading: bold | Colors.green,
        Generic.Deleted: Colors.darkpink,
        Generic.Inserted: Colors.green,
        Generic.Error: Colors.darkpink,
        Generic.Emph: italic,
        Generic.Strong: bold,
        Generic.Prompt: Colors.green,
        Generic.Output: Colors.green,
        Generic.Traceback: Colors.darkpink,
        Error: Colors.darkpink,
    }


__all__ = ['FalconryLightStyle']
