# DuckTools-EnvMan
# Copyright (C) 2024 David C Ellis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ducktools.env import PROJECT_NAME
from ducktools.env.manager import Manager
from ducktools.env.environment_specs import EnvironmentSpec, SpecType


class TestBuildRetrieve:
    def test_build_retrieve(self, testing_catalogue, test_config):
        manager = Manager(PROJECT_NAME)

        spec = EnvironmentSpec(
            spec_type=SpecType.INLINE_METADATA,
            raw_spec="requires-python='>=3.8'\ndependencies=[]\n",
        )

        # Test the env does not exist yet
        assert testing_catalogue.find_env(spec=spec) is None

        real_env = testing_catalogue.find_or_create_env(
            spec=spec,
            config=test_config,
            pip_zipapp=manager.retrieve_pip()
        )

        assert real_env is not None

        retrieve_env = testing_catalogue.find_env(spec=spec)

        assert real_env == retrieve_env
