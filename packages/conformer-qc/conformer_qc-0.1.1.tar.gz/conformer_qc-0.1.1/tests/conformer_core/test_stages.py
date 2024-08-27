#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import List

from conformer_core.accessors import Accessor
from conformer_core.db.models import DBStage
from conformer_core.registry import load_yaml
from conformer_core.stages import (
    FilterStack,
    Link,
    LinkType,
    ModStack,
    Stack,
    StackType,
    Stage,
    StageOptions,
    StoredStage,
    reconstitute,
)
from tests.conformer_core import ConformerCoreTestCase

TEST_YAML = """
stages:
  -
    name: test_stage 
    note: This is an OPTIONAL note
    type: TestStage
    links:
      link:
        name: link
        type: TestStage 
        links:
            link: link # Self reference. Probably OK
      stack:
        - filt1
        -
          name: mod1
          type: AddToMod
          options:
            addto: 1
      mods: [mod1, mod2]
      filters: [filt1, filt2]
  -
    name: filt1
    type: FalseIfInFilter
    options:
      ifin: [1]
  -
    name: filt2
    type: FalseIfInFilter
    options:
      ifin: [2]
  -
    name: mod2
    type: AddToMod 
    options:
      addto: 2
"""


class AddToMod(Stage, Accessor):
    """Test mod that appends `addto` to a given array"""

    class Options(StageOptions):
        addto: int

    def churn(self) -> None:
        while not self.in_queue.empty():
            args = self.in_queue.get()
            args[0].append(self.opts.addto)
            self.out_queue.put(args)
            self.in_queue.task_done()


class FalseIfInFilter(Stage, Accessor):
    """Test stage that returns false if a value is in infin"""

    class Options(StageOptions):
        ifin: List[int]

    def churn(self) -> None:
        while not self.in_queue.empty():
            ar = self.in_queue.get()
            isin = ar[0] not in self.opts.ifin
            self.out_queue.put((ar, isin))
            self.in_queue.task_done()


class TestStage(Stage):
    link: LinkType = Link()
    stack: StackType = Stack()
    mods: StackType = ModStack()
    filters: StackType = FilterStack()

    class Options(StageOptions):
        a: int = 0
        b: str = "str"


STAGE_REGISTRY = {
    FalseIfInFilter.__name__: FalseIfInFilter,
    TestStage.__name__: TestStage,
    AddToMod.__name__: AddToMod,
}


class StageTestCases(ConformerCoreTestCase):
    def setUp(self) -> None:
        # We will use a local world so as not to contaminate DEFAULT_WORLD
        self.WORLD = {}
        stage = TestStage.from_options(
            name="test_stage",
            links={
                "link": "link",
                "stack": ["filt1", "mod1"],
                "mods": ["mod1", "mod2"],
                "filters": ["filt1", "filt2"],
            },
            a=1,
            b="b",
            meta={"note": "This is an OPTIONAL note"},
            _world=self.WORLD,
        )

        # We should be able to make the links after the fact
        # A circular dependency...
        TestStage.from_options(name="link", links={"link": "link"}, _world=self.WORLD)
        AddToMod.from_options(name="mod1", addto=1, _world=self.WORLD)
        AddToMod.from_options(name="mod2", addto=2, _world=self.WORLD)
        FalseIfInFilter.from_options(name="filt1", ifin=[1], _world=self.WORLD)
        FalseIfInFilter.from_options(name="filt2", ifin=[2], _world=self.WORLD)

        self.stage = stage

    # def test_accessors(self):
    #     stage = self.stage

    #     # Test filters
    #     task1 = stage.filters.deferred(1)
    #     task2 = stage.filters.deferred(2)
    #     task3 = stage.filters.deferred(3)
    #     task4 = stage.link.filters.deferred(1)

    #     done, not_done = stage.filters.wait([task1, task2, task3])
    #     self.assertListEqual([t.value for t in done], [False, False, True])
    #     self.assertListEqual([t.value for t in not_done], [])

    #     self.assertTrue(stage.link.filters.get([task4])[0].value)

    #     # Test mods
    #     task1 = stage.mods.deferred([0])
    #     task2 = stage.link.mods.deferred([0])

    #     self.assertListEqual(stage.mods.get([task1])[0].value, [0,1,2])
    #     self.assertListEqual(stage.link.mods.get([task2])[0].value, [0])

    def _stage_test(self, stage: Stage, WORLD):
        self.assertTrue(stage.meta["note"])
        self.assertIs(stage.link, WORLD["link"])
        self.assertListEqual(stage.stack, [WORLD["filt1"], WORLD["mod1"]])
        self.assertListEqual(stage.filters.layers, [WORLD["filt1"], WORLD["filt2"]])
        self.assertListEqual(stage.mods.layers, [WORLD["mod1"], WORLD["mod2"]])

        # Test Filters
        self.assertEqual(stage.filters(1), ((1,), False))
        self.assertEqual(stage.filters(2), ((2,), False))
        self.assertEqual(stage.filters(3), ((3,), True))
        self.assertEqual(stage.link.filters(1), ((1,), True))

        # Test mods
        self.assertListEqual(stage.mods([0])[0], [0, 1, 2])
        self.assertListEqual(stage.link.mods([0])[0], [0])

    def test_stage(self):
        self._stage_test(self.stage, self.WORLD)

    def test_from_yaml(self):
        WORLD = {}
        for d in load_yaml(TEST_YAML)["stages"]:
            reconstitute(StoredStage(**d), STAGE_REGISTRY, WORLD)
        self._stage_test(WORLD["test_stage"], WORLD)

    def test_from_db(self):
        WORLD = {}

        DBStage.add_stages([self.stage])
        for stage in self.WORLD.values():
            self.assertNotEqual(stage._saved, 0)

        # Test deduplication
        self.assertEqual(DBStage.select().count(), 6)
        DBStage.add_stages([self.stage])
        self.assertEqual(DBStage.select().count(), 6)

        stage = DBStage.get_stages([self.stage._saved], WORLD, STAGE_REGISTRY)[
            self.stage._saved
        ]
        self._stage_test(stage, WORLD)

        stage = DBStage.get_stages_by_name(["test_stage"], WORLD, STAGE_REGISTRY)[
            "test_stage"
        ]
        self._stage_test(stage, WORLD)
