import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from jalert.score import Scorer


class KeywordConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("config.json").read_text(encoding="utf-8"))
        cls.groups = {item["label"]: item["terms"] for item in cls.config["keywords"]}

    def test_adds_new_fuel_and_renewable_topics(self):
        self.assertIn("green hydrogen", self.groups["氢氨醇等新燃料"])
        self.assertIn("green ammonia", self.groups["氢氨醇等新燃料"])
        self.assertIn("e-methanol", self.groups["氢氨醇等新燃料"])
        self.assertIn("sustainable aviation fuel", self.groups["氢氨醇等新燃料"])
        self.assertIn("enhanced geothermal systems", self.groups["地热与其他可再生能源"])
        self.assertIn("tidal energy", self.groups["地热与其他可再生能源"])
        self.assertIn("hydropower", self.groups["地热与其他可再生能源"])

    def test_expands_existing_topics_and_keeps_beccs_under_cdr_only(self):
        expected = {
            "CO2减排与碳排放": "greenhouse gas emissions",
            "CCUS与地质封存": "co2 enhanced oil recovery",
            "CDR碳移除与负排放": "ocean carbon dioxide removal",
            "电力系统与风光资源": "power system planning",
            "能源地理与全球空间布局": "facility siting",
            "气候变化与极端天气": "precipitation extremes",
            "城市与环境空间建模": "urban energy planning",
            "生命周期与技术经济评价": "social cost of carbon",
            "减排政策与能源战略": "climate justice",
        }
        for label, term in expected.items():
            with self.subTest(label=label, term=term):
                self.assertIn(term, self.groups[label])
        for term in ("beccs", "bioenergy with carbon capture and storage"):
            self.assertIn(term, self.groups["CDR碳移除与负排放"])
            self.assertNotIn(term, self.groups["CCUS与地质封存"])

    def test_avoids_unqualified_fuel_and_oil_recovery_terms(self):
        terms = {term for group in self.groups.values() for term in group}
        for term in ("hydrogen", "ammonia", "methanol", "enhanced oil recovery", "enhanced gas recovery"):
            self.assertNotIn(term, terms)

    def test_labels_and_terms_are_unique(self):
        labels = [item["label"] for item in self.config["keywords"]]
        self.assertEqual(len(labels), len(set(labels)))
        for item in self.config["keywords"]:
            with self.subTest(label=item["label"]):
                self.assertEqual(len(item["terms"]), len(set(item["terms"])))

    def test_scorer_assigns_representative_articles_to_new_or_expanded_topics(self):
        scorer = Scorer(
            self.config["keywords"],
            self.config["exclude_terms"],
            self.config["exclude_doi_prefixes"],
        )
        cases = [
            ("Green hydrogen storage for a net-zero energy system", "", "氢氨醇等新燃料"),
            ("Enhanced geothermal systems for clean electricity", "", "地热与其他可再生能源"),
            ("CO2-EOR and permanent storage in depleted reservoirs", "", "CCUS与地质封存"),
            ("Climate justice in a just transition", "", "减排政策与能源战略"),
        ]
        for title, abstract, expected_label in cases:
            with self.subTest(title=title):
                scored = scorer.score(SimpleNamespace(title=title, abstract=abstract, doi=""))
                self.assertIn(expected_label, scored.labels)

    def test_unqualified_hydrogen_does_not_match_new_fuel_topic(self):
        scorer = Scorer(
            self.config["keywords"],
            self.config["exclude_terms"],
            self.config["exclude_doi_prefixes"],
        )
        scored = scorer.score(SimpleNamespace(
            title="Hydrogen adsorption on a novel catalyst surface",
            abstract="",
            doi="",
        ))
        self.assertNotIn("氢氨醇等新燃料", scored.labels)


if __name__ == "__main__":
    unittest.main()
