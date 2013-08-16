"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from twisted.trial.unittest import TestCase

from cache_buster.keys import FormattingKeyThingy


class FormattingKeyThingyTests(TestCase):
    def test_keys_for_row_constant_string(self):
        fkt = FormattingKeyThingy({'foo': ["the_big_cache"]})
        self.assertEqual(list(fkt.keys_for_row('foo', {})), ['the_big_cache'])

    def test_keys_for_row_format_pattern(self):
        fkt = FormattingKeyThingy({'foo': ["{user_id}"]})
        self.assertEqual(list(fkt.keys_for_row('foo', {'user_id': 'bob'})), ['bob'])
