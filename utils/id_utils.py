# MIT License
#
# Copyright (c) 2025 Rani Høgnason Hansen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations
import secrets
from typing import Final

ALPHABET: Final[str] = "abcdefghijklmnopqrstuvwxyz234567"
_ALEN: Final[int] = len(ALPHABET)  # 32

# Sanity check: ensure the alphabet is exactly 32 unique characters.
if _ALEN != 32 or len(set(ALPHABET)) != _ALEN:
    raise RuntimeError("Alphabet must contain 32 unique characters.")

def _generate_b32_id(length: int = 10) -> str:
    """
    Return a cryptographically secure random ID of `length` characters
    from the Base32 alphabet above. Each char is selected uniformly
    with secrets.randbelow(32); no modulo bias.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    return "".join(ALPHABET[secrets.randbelow(_ALEN)] for _ in range(length))

def generate_b32_id(length: int = 10) -> str:
    tries = 100

    while tries > 0:
        generated_id = _generate_b32_id(length)

        if generated_id[0].isalpha():
            return generated_id

        tries -= 1

    raise ValueError("Could not generate a b32 id.")