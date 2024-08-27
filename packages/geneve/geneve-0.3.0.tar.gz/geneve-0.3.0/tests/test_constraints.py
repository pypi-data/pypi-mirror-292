# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Test constraints."""

import unittest

import tests.utils as tu
from geneve.constraints import Branch, Document

constraints_long = [
    ([], {"value": -447795966606097183}),
    ([], {"value": -447795966606097183}),
    (
        [
            ("!=", 0),
        ],
        {"value": -447795966606097183},
    ),
    (
        [
            ("!=", 0),
            ("!=", 0),
        ],
        {"value": -447795966606097183},
    ),
    (
        [
            ("!=", -447795966606097183),
        ],
        {"value": -391848440526208070},
    ),
    (
        [
            ("!=", -447795966606097183),
            ("!=", -391848440526208070),
        ],
        {"value": -5754650716556900295},
    ),
    (
        [
            ("==", 0),
        ],
        {"value": 0},
    ),
    (
        [
            ("==", 0),
            ("==", 0),
        ],
        {"value": 0},
    ),
    (
        [
            (">=", 0),
            ("<=", 0),
        ],
        {"value": 0},
    ),
    (
        [
            (">", -1),
            ("<", 1),
        ],
        {"value": 0},
    ),
    (
        [
            (">=", 10),
        ],
        {"value": 8255703960756213835},
    ),
    (
        [
            (">=", 10000),
        ],
        {"value": 8255703960756223825},
    ),
    (
        [
            (">=", 10000),
            (">=", 10),
        ],
        {"value": 8255703960756223825},
    ),
    (
        [
            (">=", 10),
            (">=", 10000),
        ],
        {"value": 8255703960756223825},
    ),
    (
        [
            (">", 20),
        ],
        {"value": 8255703960756213846},
    ),
    (
        [
            (">", 20000),
        ],
        {"value": 8255703960756233826},
    ),
    (
        [
            (">", 20000),
            (">", 20),
        ],
        {"value": 8255703960756233826},
    ),
    (
        [
            (">", 20),
            (">", 20000),
        ],
        {"value": 8255703960756233826},
    ),
    (
        [
            ("<=", 40),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<=", 40000),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<=", 40000),
            ("<=", 40),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<=", 40),
            ("<=", 40000),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<", 80),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<", 80000),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<", 80000),
            ("<", 80),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            ("<", 80),
            ("<", 80000),
        ],
        {"value": -1504411726168646672},
    ),
    (
        [
            (">", 0),
            ("<=", 100),
        ]
        + [("!=", x) for x in range(1, 100)],
        {"value": 100},
    ),
    (
        [
            (">=", 0),
            ("<", 100),
        ]
        + [("!=", x) for x in range(1, 100)],
        {"value": 0},
    ),
    (
        [
            (">=", 0),
            ("<=", 100000),
        ]
        + [("!=", x) for x in range(1, 100000)],
        {"value": 0},
    ),
]

constraints_long_cardinality = [
    (
        [
            (">=", "0"),
            ("<=", "10"),
        ],
        [
            {"value": 9},
            {"value": 7},
            {"value": 6},
        ],
    ),
    (
        [
            (">=", "0"),
            ("<=", "10"),
            ("cardinality", 0),
        ],
        [
            {"value": 9},
            {"value": 7},
            {"value": 6},
        ],
    ),
    (
        [
            (">=", "0"),
            ("<=", "10"),
            ("cardinality", 1),
        ],
        [
            {"value": 9},
            {"value": 9},
            {"value": 9},
        ],
    ),
    (
        [
            (">=", "0"),
            ("<=", "10"),
            ("cardinality", 2),
        ],
        [
            {"value": 9},
            {"value": 7},
            {"value": 7},
            {"value": 9},
            {"value": 7},
        ],
    ),
    (
        [
            (">=", "0"),
            ("<=", "10"),
            ("cardinality", 3),
        ],
        [
            {"value": 9},
            {"value": 7},
            {"value": 6},
            {"value": 6},
            {"value": 6},
            {"value": 9},
            {"value": 7},
        ],
    ),
]

constraints_long_exceptions = [
    (
        [
            ("==", 0),
            ("==", 1),
        ],
        "Unsolvable constraints ==: test_var (is already 0, cannot set to 1)",
    ),
    (
        [
            ("==", 1),
            ("==", 0),
        ],
        "Unsolvable constraints ==: test_var (is already 1, cannot set to 0)",
    ),
    (
        [
            ("==", 0),
            ("!=", 0),
        ],
        "Unsolvable constraints: test_var (cannot be 0)",
    ),
    (
        [
            ("!=", 0),
            ("==", 0),
        ],
        "Unsolvable constraints: test_var (cannot be 0)",
    ),
    (
        [
            (">", 0),
            ("<", 0),
        ],
        "Unsolvable constraints: test_var (empty solution space, 1 <= x <= -1)",
    ),
    (
        [
            ("<", 0),
            (">", 0),
        ],
        "Unsolvable constraints: test_var (empty solution space, 1 <= x <= -1)",
    ),
    (
        [
            (">", 10),
            ("!=", 11),
            ("!=", 12),
            ("<", 13),
        ],
        "Unsolvable constraints: test_var (empty solution space, 13 <= x <= 10)",
    ),
    (
        [
            ("!=", 10),
            ("!=", 11),
            ("!=", 12),
            ("==", 11),
        ],
        "Unsolvable constraints: test_var (cannot be any of (10, 11, 12))",
    ),
    (
        [
            (">=", 0),
            ("<=", 100000),
            ("max_attempts", 10000),
        ]
        + [("!=", x) for x in range(1, 100000)],
        "Unsolvable constraints: test_var (attempts exausted: 10000)",
    ),
]

constraints_geo_point = []

constraints_geo_point_cardinality = []

constraints_geo_point_exceptions = []

constraints_ip = [
    ([], {"value": "107.31.65.130"}),
    (
        [
            ("!=", "107.31.65.130"),
        ],
        {"value": "229.172.181.141"},
    ),
    (
        [
            ("!=", "107.31.65.130"),
            ("!=", "229.172.181.141"),
        ],
        {"value": "122.143.223.236"},
    ),
    (
        [
            ("==", "1.2.3.5"),
        ],
        {"value": "1.2.3.5"},
    ),
    (
        [
            ("==", "122.110.117.0/24"),
        ],
        {"value": "122.110.117.214"},
    ),
    (
        [
            ("in", "122.110.117.0/24"),
        ],
        {"value": "122.110.117.214"},
    ),
    (
        [
            ("!=", "107.31.65.0/24"),
            ("!=", "229.172.181.0/24"),
        ],
        {"value": "122.143.223.236"},
    ),
    (
        [
            ("not in", "107.31.65.0/24"),
            ("not in", "229.172.181.0/24"),
        ],
        {"value": "122.143.223.236"},
    ),
    (
        [
            ("not in", ("107.31.65.0/24", "229.172.181.0/24")),
        ],
        {"value": "122.143.223.236"},
    ),
    (
        [
            ("in", "127.0.0.0/8"),
        ],
        {"value": "127.214.62.131"},
    ),
    (
        [
            ("in", "169.254.0.0/16"),
        ],
        {"value": "169.254.214.62"},
    ),
    (
        [
            ("in", "10.0.0.0/8"),
            ("in", "192.168.0.0/16"),
        ],
        {"value": "192.168.214.62"},
    ),
    (
        [
            ("in", ("10.0.0.0/8", "192.168.0.0/16")),
        ],
        {"value": "192.168.214.62"},
    ),
    (
        [
            ("==", "::1"),
        ],
        {"value": "::1"},
    ),
    (
        [
            ("in", "fe80::/64"),
        ],
        {"value": "fe80::60a5:3ba:e6ea:94e4"},
    ),
    (
        [
            ("in", "fe80:a::/64"),
            ("in", "fe80:b::/64"),
            ("in", "fe80:c::/64"),
            ("in", "fe80:d::/64"),
        ],
        {"value": "fe80:d::60a5:3ba:e6ea:94e4"},
    ),
    (
        [
            ("in", ("fe80:a::/64", "fe80:b::/64", "fe80:c::/64", "fe80:d::/64")),
        ],
        {"value": "fe80:d::60a5:3ba:e6ea:94e4"},
    ),
    (
        [
            ("!=", "127.0.0.1"),
            ("!=", "::1"),
        ],
        {"value": "aa79:ec58:8d14:2981:f18d:f2a6:6b1f:4182"},
    ),
    (
        [
            ("!=", "aa79:ec58:8d14:2981:f18d:f2a6:6b1f:4182"),
        ],
        {"value": "7a8f:dfeb:60a5:3ba:e6ea:94e4:e5ac:b58d"},
    ),
    (
        [
            ("!=", "aa79:ec58:8d14:2981:f18d:f2a6:6b1f:4182"),
            ("!=", "7a8f:dfeb:60a5:3ba:e6ea:94e4:e5ac:b58d"),
        ],
        {"value": "a92d:c839:9a9f:e89a:c443:b67a:770a:2cd8"},
    ),
    (
        [
            ("not in", "aa79::/16"),
            ("not in", "7a8f::/16"),
        ],
        {"value": "a92d:c839:9a9f:e89a:c443:b67a:770a:2cd8"},
    ),
    (
        [
            ("!=", "aa79::/16"),
            ("!=", "7a8f::/16"),
        ],
        {"value": "a92d:c839:9a9f:e89a:c443:b67a:770a:2cd8"},
    ),
]

constraints_ip_cardinality = [
    (
        [
            ("in", "10.0.0.0/24"),
        ],
        [
            {"value": "10.0.0.214"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.108"},
        ],
    ),
    (
        [
            ("in", "10.0.0.0/24"),
            ("cardinality", 0),
        ],
        [
            {"value": "10.0.0.214"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.108"},
        ],
    ),
    (
        [
            ("in", "10.0.0.0/24"),
            ("cardinality", 1),
        ],
        [
            {"value": "10.0.0.214"},
            {"value": "10.0.0.214"},
            {"value": "10.0.0.214"},
        ],
    ),
    (
        [
            ("in", "10.0.0.0/24"),
            ("cardinality", 2),
        ],
        [
            {"value": "10.0.0.214"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.214"},
            {"value": "10.0.0.193"},
        ],
    ),
    (
        [
            ("in", "10.0.0.0/24"),
            ("cardinality", 3),
        ],
        [
            {"value": "10.0.0.214"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.108"},
            {"value": "10.0.0.193"},
            {"value": "10.0.0.108"},
            {"value": "10.0.0.108"},
            {"value": "10.0.0.214"},
        ],
    ),
]

constraints_ip_exceptions = [
    (
        [
            ("!=", "127.0.0.1"),
            ("==", "127.0.0.1"),
        ],
        "Unsolvable constraints: test_var (cannot be 127.0.0.1)",
    ),
    (
        [
            ("==", "127.0.0.1"),
            ("!=", "127.0.0.1"),
        ],
        "Unsolvable constraints: test_var (cannot be 127.0.0.1)",
    ),
    (
        [
            ("!=", "::1"),
            ("==", "::1"),
        ],
        "Unsolvable constraints: test_var (cannot be ::1)",
    ),
    (
        [
            ("==", "::1"),
            ("!=", "::1"),
        ],
        "Unsolvable constraints: test_var (cannot be ::1)",
    ),
    (
        [
            ("not in", "127.0.0.0/8"),
            ("==", "127.0.0.1"),
        ],
        "Unsolvable constraints: test_var (cannot be in net 127.0.0.0/8)",
    ),
    (
        [
            ("not in", "::/96"),
            ("==", "::1"),
        ],
        "Unsolvable constraints: test_var (cannot be in net ::/96)",
    ),
    (
        [
            ("not in", "127.0.0.0/8"),
            ("not in", "10.10.0.0/16"),
            ("==", "10.10.10.10"),
        ],
        "Unsolvable constraints: test_var (cannot be in any of nets (10.10.0.0/16, 127.0.0.0/8))",
    ),
    (
        [
            ("not in", ("127.0.0.0/8", "10.10.0.0/16")),
            ("==", "10.10.10.10"),
        ],
        "Unsolvable constraints: test_var (cannot be in any of nets (10.10.0.0/16, 127.0.0.0/8))",
    ),
    (
        [
            ("==", "127.0.0.1"),
            ("==", "1.2.3.4"),
        ],
        "Unsolvable constraints ==: test_var (is already 127.0.0.1, cannot set to 1.2.3.4)",
    ),
    (
        [
            ("==", "::1"),
            ("==", "::2"),
        ],
        "Unsolvable constraints ==: test_var (is already ::1, cannot set to ::2)",
    ),
    (
        [
            ("not in", "10.0.0.0/24"),
            ("in", "10.0.0.0/24"),
            ("not in", "10.0.1.0/24"),
            ("in", "10.0.1.0/24"),
        ],
        "Unsolvable constraints: test_var (net(s) both included and excluded: 10.0.0.0/24, 10.0.1.0/24)",
    ),
    (
        [
            ("not in", ("10.0.0.0/24", "10.0.1.0/24")),
            ("in", ("10.0.0.0/24", "10.0.1.0/24")),
        ],
        "Unsolvable constraints: test_var (net(s) both included and excluded: 10.0.0.0/24, 10.0.1.0/24)",
    ),
    (
        [
            ("in", "fe80::/64"),
            ("not in", "fe80::/64"),
        ],
        "Unsolvable constraints: test_var (net(s) both included and excluded: fe80::/64)",
    ),
]

constraints_keyword = [
    ([], {"value": "TvCfUyyFjS"}),
    ([], {"value": "TvCfUyyFjS"}),
    (
        [
            ("!=", "TvCfUyyFjS"),
        ],
        {"value": "xTFlEzs"},
    ),
    (
        [
            ("!=", "TvCfUyyFjS"),
            ("!=", "xTFlEzs"),
        ],
        {"value": "xBnLeOAa"},
    ),
    (
        [
            ("wildcard", "*.exe"),
        ],
        {"value": "XIUtkNI.exe"},
    ),
    (
        [
            ("wildcard", "*.exe"),
            ("not wildcard", "XIUtk*.exe"),
        ],
        {"value": "vIL.exe"},
    ),
    (
        [
            ("wildcard", "*.exe"),
            ("not wildcard", "XIUtk*.exe"),
            ("not wildcard", "*IL.exe"),
        ],
        {"value": "Ezswu.exe"},
    ),
    (
        [
            ("==", "cmd.exe"),
        ],
        {"value": "cmd.exe"},
    ),
    (
        [
            ("wildcard", "cmd.exe"),
        ],
        {"value": "cmd.exe"},
    ),
    (
        [
            ("wildcard", "cmd.exe"),
            ("==", "cmd.exe"),
        ],
        {"value": "cmd.exe"},
    ),
    (
        [
            ("wildcard", ("cmd.exe",)),
            ("==", "cmd.exe"),
        ],
        {"value": "cmd.exe"},
    ),
    (
        [
            ("wildcard", ("cmd.exe", "powershell.exe")),
            ("==", "cmd.exe"),
        ],
        {"value": "cmd.exe"},
    ),
    (
        [
            ("wildcard", ("cmd.exe", "powershell.exe", "regedit.exe")),
        ],
        {"value": "regedit.exe"},
    ),
]

constraints_keyword_cardinality = [
    (
        [],
        [
            {"value": "TvCfUyyFjS"},
            {"value": "xTFlEzs"},
            {"value": "xBnLeOAa"},
        ],
    ),
    (
        [
            ("cardinality", 0),
        ],
        [
            {"value": "TvCfUyyFjS"},
            {"value": "xTFlEzs"},
            {"value": "xBnLeOAa"},
        ],
    ),
    (
        [
            ("cardinality", 1),
        ],
        [
            {"value": "TvCfUyyFjS"},
            {"value": "TvCfUyyFjS"},
            {"value": "TvCfUyyFjS"},
        ],
    ),
    (
        [
            ("cardinality", 2),
        ],
        [
            {"value": "TvCfUyyFjS"},
            {"value": "xTFlEzs"},
            {"value": "xTFlEzs"},
            {"value": "xTFlEzs"},
            {"value": "xTFlEzs"},
        ],
    ),
    (
        [
            ("cardinality", 3),
        ],
        [
            {"value": "TvCfUyyFjS"},
            {"value": "xTFlEzs"},
            {"value": "xBnLeOAa"},
            {"value": "TvCfUyyFjS"},
            {"value": "TvCfUyyFjS"},
            {"value": "TvCfUyyFjS"},
            {"value": "TvCfUyyFjS"},
        ],
    ),
]

constraints_keyword_exceptions = [
    (
        [
            ("!=", "cmd.exe"),
            ("==", "cmd.exe"),
        ],
        "Unsolvable constraints: test_var (not in Strings(everything(), exclude=Strings({'cmd.exe'})): ('cmd.exe'))",
    ),
    (
        [
            ("==", "cmd.exe"),
            ("!=", "cmd.exe"),
        ],
        "Unsolvable constraints: test_var (excluded by Strings({'cmd.exe'}): ('cmd.exe'))",
    ),
    (
        [
            ("==", "cmd.exe"),
            ("not wildcard", "*.exe"),
        ],
        "Unsolvable constraints: test_var (excluded by Strings({'cmd.exe'}): ('*.exe'))",
    ),
    (
        [
            ("wildcard", "powershell.exe"),
            ("==", "cmd.exe"),
        ],
        "Unsolvable constraints: test_var (not in Strings({'powershell.exe'}): ('cmd.exe'))",
    ),
    (
        [
            ("wildcard", ("powershell.exe",)),
            ("==", "cmd.exe"),
        ],
        "Unsolvable constraints: test_var (not in Strings({'powershell.exe'}): ('cmd.exe'))",
    ),
    (
        [
            ("wildcard", "cmd.exe"),
            ("wildcard", "powershell.exe"),
        ],
        "Unsolvable constraints: test_var (not in Strings({'cmd.exe'}): ('powershell.exe'))",
    ),
    (
        [
            ("wildcard", ("cmd.exe", "powershell.exe")),
            ("==", "regedit.exe"),
        ],
        "Unsolvable constraints: test_var (not in Strings({'cmd.exe', 'powershell.exe'}): ('regedit.exe'))",
    ),
    (
        [
            ("wildcard", ("cmd.exe", "powershell.exe")),
            ("not wildcard", "*.exe"),
        ],
        "Unsolvable constraints: test_var (excluded by Strings({'cmd.exe', 'powershell.exe'}): ('*.exe'))",
    ),  # noqa: E501
    (
        [
            ("wildcard", ("cmd.exe", "powershell.exe")),
            ("not wildcard", ("*.exe", "cmd.*")),
        ],
        "Unsolvable constraints: test_var (excluded by Strings({'cmd.exe', 'powershell.exe'}): ('*.exe', 'cmd.*'))",
    ),  # noqa: E501
]

branch_fields = [
    (
        [
            {"a": [(">=", 10), ("<=", 20)], "b": [("!=", 0)]},
            {"c": [("==", "any")]},
        ],
        {
            "a",
            "b",
            "c",
        },
    ),
]

branch_products = [
    (
        [
            {"a": [(">=", 10), ("<=", 20)]},
        ],
        [
            {"b": [("==", 50)]},
        ],
        [
            {"a": [(">=", 10), ("<=", 20)], "b": [("==", 50)]},
        ],
    ),
    (
        [
            {"a": [(">=", 10), ("<=", 20)]},
        ],
        [
            {"a": [("!=", 15)]},
        ],
        [
            {"a": [(">=", 10), ("<=", 20), ("!=", 15)]},
        ],
    ),
    (
        [
            {"a": [(">=", 10), ("<=", 20)]},
        ],
        [
            {"a": [("!=", 15)]},
            {"a": [("!=", 16)]},
        ],
        [
            {"a": [(">=", 10), ("<=", 20), ("!=", 15)]},
            {"a": [(">=", 10), ("<=", 20), ("!=", 16)]},
        ],
    ),
    (
        [
            {"a": [(">=", 10), ("<=", 20)]},
            {"a": [(">=", 100), ("<=", 200)]},
        ],
        [
            {"a": [("!=", 15)]},
        ],
        [
            {"a": [(">=", 10), ("<=", 20), ("!=", 15)]},
            {"a": [(">=", 100), ("<=", 200), ("!=", 15)]},
        ],
    ),
    (
        [
            {"a": [(">=", 10), ("<=", 20)]},
            {"b": [("wildcard", ("one", "two"))]},
        ],
        [
            {"a": [("!=", 15)], "c": [("!=", None)]},
            {"b": [("not wildcard", "three")]},
        ],
        [
            {"a": [(">=", 10), ("<=", 20), ("!=", 15)], "c": [("!=", None)]},
            {"a": [(">=", 10), ("<=", 20)], "b": [("not wildcard", "three")]},
            {"b": [("wildcard", ("one", "two"))], "a": [("!=", 15)], "c": [("!=", None)]},
            {"b": [("wildcard", ("one", "two")), ("not wildcard", "three")]},
        ],
    ),
]

constraints_exceptions = [
    (
        [
            ("cardinality", "a"),
        ],
        """invalid literal for int() with base 10: 'a'""",
    ),
    (
        [
            ("cardinality", ("a")),
        ],
        """invalid literal for int() with base 10: 'a'""",
    ),
    (
        [
            ("cardinality", (0, 1)),
        ],
        """Too many arguments for cardinality of 'test_var': (0, 1)""",
    ),
]


class TestConstraints(tu.SeededTestCase, unittest.TestCase):
    maxDiff = None

    def test_long(self):
        from geneve.solver.type_long import LongField as solver

        for i, (constraints, test_value) in enumerate(constraints_long):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_value, solver("test_var", constraints, [], None)(None, env))

        for i, (constraints, msg) in enumerate(constraints_long_exceptions + constraints_exceptions):
            with self.subTest(constraints, i=i):
                with self.assertRaises(ValueError, msg=msg) as cm:
                    env = {}
                    self.assertEqual(None, solver("test_var", constraints, [], None)(None, env))
                self.assertEqual(msg, str(cm.exception))

        for i, (constraints, test_values) in enumerate(constraints_long_cardinality):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_values, [solver("test_var", constraints, [], None)(None, env) for _ in test_values])

    def test_geo_point(self):
        from geneve.solver.type_geo_point import GeoPointField as solver

        for i, (constraints, test_value) in enumerate(constraints_geo_point):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_value, solver("test_var", constraints, [], None)(None, env))

        for i, (constraints, msg) in enumerate(constraints_geo_point_exceptions + constraints_exceptions):
            with self.subTest(constraints, i=i):
                with self.assertRaises(ValueError, msg=msg) as cm:
                    env = {}
                    self.assertEqual(None, solver("test_var", constraints, [], None)(None, env))
                self.assertEqual(msg, str(cm.exception))

        for i, (constraints, test_values) in enumerate(constraints_geo_point_cardinality):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_values, [solver("test_var", constraints, [], None)(None, env) for _ in test_values])

    def test_ip(self):
        from geneve.solver.type_ip import IPField as solver

        for i, (constraints, test_value) in enumerate(constraints_ip):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_value, solver("test_var", constraints, [], None)(None, env))

        for i, (constraints, msg) in enumerate(constraints_ip_exceptions + constraints_exceptions):
            with self.subTest(constraints, i=i):
                with self.assertRaises(ValueError, msg=msg) as cm:
                    env = {}
                    self.assertEqual(None, solver("test_var", constraints, [], None)(None, env))
                self.assertEqual(msg, str(cm.exception))

        for i, (constraints, test_values) in enumerate(constraints_ip_cardinality):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_values, [solver("test_var", constraints, [], None)(None, env) for _ in test_values])

    def test_keyword(self):
        from geneve.solver.type_keyword import KeywordField as solver

        for i, (constraints, test_value) in enumerate(constraints_keyword):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_value, solver("test_var", constraints, [], None)(None, env))

        for i, (constraints, msg) in enumerate(constraints_keyword_exceptions + constraints_exceptions):
            with self.subTest(constraints, i=i):
                with self.assertRaises(ValueError, msg=msg) as cm:
                    env = {}
                    self.assertEqual(None, solver("test_var", constraints, [], None)(None, env))
                self.assertEqual(msg, str(cm.exception))

        for i, (constraints, test_values) in enumerate(constraints_keyword_cardinality):
            with self.subTest(constraints, i=i):
                env = {}
                self.assertEqual(test_values, [solver("test_var", constraints, [], None)(None, env) for _ in test_values])

    def test_entity(self):
        schema = {}
        d = Document()

        for field in [
            "@timestamp",
            "ecs.version",
            "process.name",
            "process.thread.id",
            "process.thread.name",
            "process.tty.char_device.major",
            "process.tty.char_device.minor",
            "source.geo.",
        ]:
            d.append_constraint(field)

        d.optimize(schema)
        entities = list(d.entities())

        self.assertEqual(
            [
                "ecs",
                "process",
                "process.thread",
                "process.tty.char_device",
                "process.tty",
                "source.geo",
                "source",
                "",
            ],
            [e.group for e in entities],
        )


class TestBranches(tu.SeededTestCase, unittest.TestCase):
    maxDiff = None

    def test_fields(self):
        for a, fields in branch_fields:
            a = Branch([Document.from_dict(x) for x in a])
            with self.subTest(f"{a}"):
                self.assertEqual(fields, a.fields())

    def test_product(self):
        for a, b, c in branch_products:
            a = Branch([Document.from_dict(x) for x in a])
            b = Branch([Document.from_dict(x) for x in b])
            c = Branch([Document.from_dict(x) for x in c])
            with self.subTest(f"{a} * {b}"):
                self.assertEqual(a * b, c)

    def test_join_fields(self):
        schema = {}
        d1 = Document()
        d2 = Document()

        d1.append_constraint("process.name", "wildcard", ("*.exe", "*.bat"))
        d2.append_constraint("process.name", "wildcard", ("*.dll", "*.scr"))

        jd = Document()
        d1 = jd.join_fields(d1, ["process.name"])
        d2 = jd.join_fields(d2, ["process.parent.name"])

        branch = Branch([d1, d2])
        branch.optimize(schema)

        self.assertEqual(
            [
                {"process": {"name": "LbS.exe"}},
                {"process": {"name": "rJjN.dll", "parent": {"name": "LbS.exe"}}},
            ],
            list(branch.solve({})),
        )
        self.assertEqual(
            [
                {"process": {"name": "gMefKdjabqgZ.exe"}},
                {"process": {"name": "Siid.dll", "parent": {"name": "gMefKdjabqgZ.exe"}}},
            ],
            list(branch.solve({})),
        )
        self.assertEqual(
            [
                {"process": {"name": "lIkqw.bat"}},
                {"process": {"name": "uxRWqYK.dll", "parent": {"name": "lIkqw.bat"}}},
            ],
            list(branch.solve({})),
        )
