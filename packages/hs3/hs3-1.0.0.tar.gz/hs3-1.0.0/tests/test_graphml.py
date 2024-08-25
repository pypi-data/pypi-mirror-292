import unittest
import tempfile
import os
import json
from xml.etree import ElementTree as ET
from hs3.graphml import build_elements, build_graph_model, write_graphml

class TestHS3ToGraphML(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to store input/output files
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Clean up the temporary directory after tests
        self.test_dir.cleanup()

    def test_build_elements(self):
        # Sample HS3 data
        hs3_data = {
            "functions": [{"name": "func1"}],
            "distributions": [{"name": "dist1"}],
            "domains": [{"axes": [{"name": "axis1"}]}]
        }

        elements = build_elements(hs3_data)
        expected_elements = {
            "func1": {"name": "func1"},
            "dist1": {"name": "dist1"},
            "axis1": {"name": "axis1"}
        }
        self.assertEqual(elements, expected_elements)

    def test_build_graph_model(self):
        # Sample elements and data
        elements = {
            "func1": {"name": "func1"},
            "dist1": {"name": "dist1"},
            "axis1": {"name": "axis1"}
        }
        likelihood = {"distributions": ["dist1"], "aux_distributions": []}

        model = build_graph_model({}, likelihood, elements)
        self.assertIn("dist1", model)
        self.assertEqual(model["dist1"], set())

    def test_write_graphml(self):
        # Sample graph model
        model = {
            "node1": {"node2"},
            "node2": set()
        }

        # Output file path
        output_file = os.path.join(self.test_dir.name, 'output.gml')

        # Write the GraphML
        write_graphml(model, output_file)

        # Verify the output file exists
        self.assertTrue(os.path.exists(output_file))

        # Parse the GraphML file and check the content
        tree = ET.parse(output_file)
        root = tree.getroot()

        # Check the number of nodes (should be 2)
        nodes = root.findall('.//{http://graphml.graphdrawing.org/xmlns}node')
        self.assertEqual(len(nodes), 2)

        # Check the number of edges (should be 1)
        edges = root.findall('.//{http://graphml.graphdrawing.org/xmlns}edge')
        self.assertEqual(len(edges), 1)

if __name__ == "__main__":
    unittest.main()
