# Copyright Jiaqi (Hutao of Emberfire)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest

from wilhelm_graphdb_python.quizlet import processing_study_set


class TestQuizlet(unittest.TestCase):

    def test_processing_study_set(self):
        self.assertEqual(
            [("null", "0"), ("eins", "1"), ("zwei", "2"), ("drei", "3")],
            processing_study_set("tests/export.txt"),
        )
