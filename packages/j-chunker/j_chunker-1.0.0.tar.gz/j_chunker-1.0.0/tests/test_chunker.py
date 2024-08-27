# SPDX-License-Identifier: Apache-2.0
import unittest
from pathlib import Path
from j_chunker import chunker

class TestChunker(unittest.TestCase):
    def test_chunker(self):
        # This is a basic test. You should expand it with more specific tests.
        pdf_paths = [str(Path(__file__).parent / "test_data" / "test.pdf")]
        output_dir = Path(__file__).parent / "test_output"
        raw_dir = output_dir / "raw"
        processed_dir = output_dir / "processed"
        embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

        result = chunker(pdf_paths, str(output_dir), str(raw_dir), str(processed_dir), embedding_model_name)
        self.assertIsInstance(result, dict)
        # Add more assertions here

if __name__ == '__main__':
    unittest.main()