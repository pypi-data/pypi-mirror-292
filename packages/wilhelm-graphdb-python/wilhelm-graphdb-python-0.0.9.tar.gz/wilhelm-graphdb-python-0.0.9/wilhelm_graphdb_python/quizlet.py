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


def processing_study_set(exported_filepath: str) -> list[tuple[str, str]]:
    """
    Read in a Quizlet export file in .txt format and returns a dictionary whose key is the term and value is the
    definition.

    It is assumed that the separator of term and definition is tab and line separator being new line

    :param exported_filepath:  The absolute or relative path to the exported Quizlet vocabularies

    :return: a list of tuples whose first element is the term and the second element is the definition.
    """
    with open(exported_filepath, "r") as file:
        return [(line.split('\t')[0], line.split('\t')[1]) for line in file.read().splitlines()]
