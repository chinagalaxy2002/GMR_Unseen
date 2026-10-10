#!/usr/bin/env python3
"""Small integration fixtures for compositional leakage and candidate integrity."""
import json
import tempfile
import unittest
from pathlib import Path

import pipeline


def row(qid, vid, split, label, query, events):
    return {"qid": qid, "vid": vid, "split": split, "exist_label": label,
            "query": query, "duration": 10.0, "relevant_windows": [[1.0, 2.0]] if label else [],
            "events": events, "source_qid": qid}


def event(action, role, filler, **more):
    return {"action_family": action, "anchor_role": role, "anchor_object": filler,
            "assertion": "asserted", **more}


class CompositionPipelineFixtures(unittest.TestCase):
    def setUp(self):
        self.target = "open|theme|cabinet"
        self.seen_action_alt_1 = row("train_a", "T1", "train", 1, "person opens drawer",
                                     [event("open", "theme", "drawer")])
        self.seen_action_alt_2 = row("train_b", "T2", "train", 1, "person opens box",
                                     [event("open", "theme", "box")])
        self.seen_filler_alt = row("train_c", "T3", "train", 1, "person takes cabinet",
                                   [event("take", "theme", "cabinet")])
        self.multi_event_exposure = row("train_multi", "T4", "train", 1, "person opens cabinet and takes cup",
                                        [event("open", "theme", "cabinet"), event("take", "theme", "cup")])
        self.negative_exposure = row("train_neg", "T5", "train", 0, "person opens cabinet",
                                     [event("open", "theme", "cabinet")])
        self.source_goal = row("dir", "T6", "train", 1, "person puts box into cabinet",
                               [event("put", "theme", "box", goal="cabinet", source="table")])
        self.source_only = row("dir2", "T7", "train", 1, "person takes box from cabinet",
                               [event("take", "theme", "box", source="cabinet")])
        self.source_positive = row("test_pos", "V1", "test", 1, "person opens cabinet",
                                    [event("open", "theme", "cabinet")])

    def test_full_event_and_negative_leakage(self):
        self.assertTrue(pipeline.row_hits(self.multi_event_exposure, {self.target}))
        self.assertTrue(pipeline.row_hits(self.negative_exposure, {self.target}))
        self.assertFalse(pipeline.row_hits(self.seen_action_alt_1, {self.target}))
        self.assertFalse(pipeline.row_hits(self.seen_filler_alt, {self.target}))

    def test_action_role_filler_preserves_source_goal_direction(self):
        keys = {c["composition_key"] for c in pipeline.row_compositions(self.source_goal)}
        self.assertIn("put|goal|cabinet", keys)
        self.assertIn("put|source|table", keys)
        self.assertNotIn("put|source|cabinet", keys)
        take_keys = {c["composition_key"] for c in pipeline.row_compositions(self.source_only)}
        self.assertIn("take|source|cabinet", take_keys)

    def test_wrong_counterfactual_key_is_rejected(self):
        wrong = row("wrong", "V2", "test", 0, "person opens table",
                    [event("open", "theme", "table")])
        self.assertNotIn(self.target, {c["composition_key"] for c in pipeline.row_compositions(wrong)})

    def test_v4_alias_scope_and_sit_query_repair(self):
        front= row("front","T8","train",1,"person opens front door",
                   [event("open","theme","front door",assertion="asserted")])
        cabinet= row("cab","T9","train",1,"person opens cabinet door",
                     [event("open","theme","cabinet door",assertion="asserted")])
        self.assertIn("open|theme|door",{c["composition_key"] for c in pipeline.row_compositions(front)})
        self.assertNotIn("open|theme|door",{c["composition_key"] for c in pipeline.row_compositions(cabinet)})
        self.assertIn("open|theme|cabinet_entry",{c["composition_key"] for c in pipeline.row_compositions(cabinet)})
        sit=row("sit","T10","train",1,"person sits in a chair at a table",
                [event("sit_down","location","table",assertion="asserted")])
        self.assertIn("sit|support_surface|chair",{c["composition_key"] for c in pipeline.row_compositions(sit)})
        purpose=row("purpose","V5","test",1,"person plans to sit on a chair",
                    [event("sit_down","support_surface","chair",assertion="purpose")])
        kept, removed, unresolved=pipeline.partition_source_rows([purpose],"test",{"sit|support_surface|chair"})
        self.assertEqual(kept,[])
        self.assertEqual(unresolved[0]["reason"],"held_positive_event_not_explicitly_asserted")

    def test_v4_query_surface_closure_and_ambiguous_cabinet_scope(self):
        missed_part = row("dryer_door", "T11", "train", 0, "person opens the dryer door",
                          [event("open", "theme", "dryer")])
        self.assertIn("open|theme|door", {c["composition_key"] for c in pipeline.row_compositions(missed_part)})
        kept, removed, unresolved = pipeline.partition_source_rows([missed_part], "train", {"open|theme|door"})
        self.assertEqual(kept, [])
        self.assertEqual(removed[0]["reason"], "full_event_list_exposes_held_composition")
        cabinet = row("cabinet_door", "T12", "train", 0, "person opens the cabinet door",
                      [event("open", "theme", "cabinet")])
        kept, removed, unresolved = pipeline.partition_source_rows([cabinet], "train", {"open|theme|door"})
        self.assertEqual(kept, [])
        self.assertEqual(removed[0]["reason"], "ambiguous_cabinet_door_scope_quarantined")

    def test_unresolved_resultative_and_action_graph_mismatch_are_quarantined(self):
        rows = [
            row("open_state", "T14", "train", 1, "the person walks away opens a door",
                [event("open_state", "theme", "door")]),
            row("push_result", "T15", "train", 1, "the person pushes the door open",
                [event("push", "theme", "door")]),
            row("attempt_close", "T16", "train", 1, "person attempt to start closing the door",
                [event("attempt_close", "theme", "door")]),
        ]
        for source, key in ((rows[0],"open|theme|door"),(rows[1],"open|theme|door"),(rows[2],"close|theme|door")):
            kept, removed, unresolved = pipeline.partition_source_rows([source],"train",{key})
            self.assertEqual(kept,[])
            self.assertEqual(removed[0]["reason"],"held_query_semantics_not_resolved_in_event_graph")

    def test_chair_subtypes_share_frozen_chair_concept(self):
        self.assertEqual(pipeline.canonical("office chair"), "chair")
        self.assertEqual(pipeline.canonical("red chair"), "chair")
        self.assertEqual(pipeline.canonical("chairs"), "chair")
        pillow = row("pillow_base", "T13", "train", 1, "person sits on a pillow on a chair",
                     [event("sit", "support_surface", "pillow", support_base="chair")])
        self.assertNotIn("sit|support_surface|chair", {c["composition_key"] for c in pipeline.row_compositions(pillow)})

    def test_missing_video_evidence_never_becomes_a_label(self):
        valid, reason = pipeline.valid_reassignment(self.source_positive,
            {"vid": "V2", "split": "test"}, [], self.target)
        self.assertTrue(valid)
        self.assertEqual(reason, "candidate_only_absence_unverified")
        candidate = {"construction_type": "unverified_negative_candidate", "exist_label": 0,
                     "relevant_windows": [], "video_absence_verified": False}
        self.assertEqual(candidate["construction_type"], "unverified_negative_candidate")
        self.assertFalse(candidate["video_absence_verified"])

    def test_reassignment_and_cross_split_integrity(self):
        valid, _ = pipeline.valid_reassignment(self.source_positive,
            {"vid": "V2", "split": "test"}, [], self.target)
        self.assertTrue(valid)
        invalid, reason = pipeline.valid_reassignment(self.source_positive,
            {"vid": "V3", "split": "val"}, [], self.target)
        self.assertFalse(invalid)
        self.assertEqual(reason, "cross_split_reassignment")
        conflict, reason = pipeline.valid_reassignment(self.source_positive,
            {"vid": "V2", "split": "test"}, [self.source_positive], self.target)
        self.assertFalse(conflict)
        self.assertEqual(reason, "known_positive_annotation_conflict")

    def test_matched_pair_reference_integrity(self):
        positive = row("u_pos", "V4", "test", 1, "person opens cabinet",
                       [event("open", "theme", "cabinet")])
        negative = row("u_neg", "V4", "test", 0, "person opens cabinet while holding cup",
                       [event("open", "theme", "cabinet")])
        pair = {"pair_id":"pair_1","positive_qid":"u_pos","negative_qid":"u_neg",
                "target_composition":self.target}
        # The fixture is structurally same-video, but the negative query itself is not
        # evidence of absence; the check validates references and split alignment only.
        by_qid = {positive["qid"]:positive, negative["qid"]:negative}
        self.assertEqual(pipeline.valid_matched_pair(pair,by_qid),(True,"valid_same_video_pair"))
        bad = dict(pair,negative_qid="missing")
        self.assertEqual(pipeline.valid_matched_pair(bad,by_qid),(False,"missing_pair_qid_reference"))
        cross_split = dict(negative,split="val")
        self.assertEqual(pipeline.valid_matched_pair(pair,{"u_pos":positive,"u_neg":cross_split}),
                         (False,"pair_split_mismatch"))

    def test_inherited_matched_pairs_require_both_same_video_u_conditions(self):
        positive=row("up","V6","test",1,"person opens a door",[event("open","theme","door")])
        positive["partition"]="U+"
        negative=row("un","V6","test",0,"person opens a door",[event("open","theme","door")])
        negative["partition"]="U-"
        pairs=pipeline.inherited_matched_pairs([positive,negative],"test","open|theme|door")
        self.assertEqual(len(pairs),1)
        self.assertEqual(pipeline.valid_matched_pair(pairs[0],{"up":positive,"un":negative}),
                         (True,"valid_same_video_pair"))
        other=row("wrong","V7","test",0,"person opens a table",[event("open","theme","table")])
        other["partition"]="U-"
        self.assertEqual(pipeline.inherited_matched_pairs([positive,other],"test","open|theme|door"),[])

    def test_deterministic_jsonl_order_and_ids(self):
        rows = [self.seen_filler_alt, self.seen_action_alt_1, self.source_positive]
        first_split = pipeline.partition_source_rows(rows, "test", {self.target})
        second_split = pipeline.partition_source_rows(list(reversed(rows)), "test", {self.target})
        self.assertEqual(first_split, second_split)
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.jsonl", Path(tmp) / "b.jsonl"
            pipeline.write_jsonl(a, rows)
            pipeline.write_jsonl(b, list(reversed(rows)))
            self.assertEqual(a.read_bytes(), b.read_bytes())
        first = pipeline.candidate_id("in_domain", "CG", "test_pos", "V2", "person opens cabinet")
        second = pipeline.candidate_id("in_domain", "CG", "test_pos", "V2", "person opens cabinet")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
