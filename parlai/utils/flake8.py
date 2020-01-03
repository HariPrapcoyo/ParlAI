#!/usr/bin/env python3

"""
Custom flake8 rules for ParlAI.

Includes:
- Checks for python3 shebang
- Check for copyright message
- Docformatter issues (TODO)
"""

import docformatter
import difflib

PYTHON_SHEBANG = '#!/usr/bin/env python3'
WHITELIST_PHRASES = ['Moscow Institute of Physics and Technology.']
WHITELIST_FNS = ["mlb_vqa"]
COPYRIGHT = [
    "Copyright (c) Facebook, Inc. and its affiliates.",
    "This source code is licensed under the MIT license found in the",
    "LICENSE file in the root directory of this source tree.",
]


class ParlAIChecker:
    """
    Custom flake8 checker for some special ParlAI requirements.
    """

    name = 'flake8-parlai'
    version = '0.1'

    def __init__(self, tree=None, filename=None, lines=None):
        self.filename = filename
        self.lines = lines

    def run(self):
        if self.lines is None:
            with open(self.filename) as f:
                self.lines = f.readlines()

        if self.lines and PYTHON_SHEBANG not in self.lines[0]:
            yield (
                1,
                0,
                'PAI100 Missing python3 shebang. (`#!/usr/bin/env python3`)',
                '',
            )

        # check copyrighting next
        source = "".join(self.lines)
        formatted_source = docformatter.format_code(
            source,
            pre_summary_newline=True,
            description_wrap_length=88,
            summary_wrap_length=88,
            make_summary_multi_line=True,
            force_wrap=False,
        )
        if source != formatted_source:
            diff = difflib.unified_diff(
                source.split('\n'),  # have to strip newlines
                formatted_source.split('\n'),
                f'before/{self.filename}',
                f'after/{self.filename}',
                n=0,
                lineterm='',
            )
            for line in diff:
                if line.startswith('@@'):
                    fields = line.split()
                    line_no, _ = fields[1].split(',')
                    line_no = -int(line_no)
                    yield (
                        line_no,
                        1,
                        f'PAI101 autoformat.sh would reformat the docstring',
                        '',
                    )

        # the rest is checking copyright, but there are some exceptions
        if any(wl in source for wl in WHITELIST_PHRASES):
            return

        for i, msg in enumerate(COPYRIGHT, 1):
            if any(wl in self.filename for wl in WHITELIST_FNS) and i < 3:
                continue
            if msg not in source:
                yield (i, 0, f'PAI20{i} Missing copyright `{msg}`', '')
