"""
MIT License

Copyright (c) 20234 Isabelle Phoebe <izzy@uwu.gal>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Final, TypedDict

from httpcord.enums import InteractionResponseType, InteractionOptionType
from httpcord.interaction import User


__all__: Final[tuple[str, ...]] = (
    "JSONResponseError",
    "Choice",
)


TYPE_CONVERSION_TABLE: dict[type, InteractionOptionType] = {
    bool: InteractionOptionType.BOOLEAN,
    int: InteractionOptionType.INTEGER,
    float: InteractionOptionType.NUMBER,
    str: InteractionOptionType.STRING,
    User: InteractionOptionType.USER,
    # file: InteractionOptionType.ATTACHMENT,
    # channel: InteractionOptionType.CHANNEL,
    # mentionable: InteractionOptionType.MENTIONABLE,
    # role: InteractionOptionType.ROLE,
}


class JSONResponseError(TypedDict):
    error: str


class JsonResponseType(TypedDict):
    type: InteractionResponseType


class Choice(TypedDict):
    name: str
    value: str
