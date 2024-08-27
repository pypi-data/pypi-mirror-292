import io
from textwrap import dedent
from unittest import main, TestCase
from unittest.mock import patch, mock_open

import prototools.protodb as p


class Test(TestCase):

    def test_load_protodb(self):
        """Test loading a protodb file."""
        with patch('prototools.protodb.open', mock_open(read_data=dedent("""
            [
                { 
                    "1": {
                        "name": "test",
                        "path": "test.proto",
                        "file_contents": "test"
                    }
                }
            ]
        """))):
            db = p.ProtoDB('test.json').get_data()
            self.assertEqual(db, [
                { 
                    "1": {
                        "name": "test",
                        "path": "test.proto",
                        "file_contents": "test"
                    }
                }
            ])

    def test_add(self):
        """Test adding a new entry to the protodb."""
        with patch('prototools.protodb.open', mock_open(read_data=dedent("""
            [
                { 
                    "1": {
                        "name": "test",
                        "path": "test.proto",
                        "file_contents": "test"
                    }
                }
            ]
        """))):
            db = p.ProtoDB('test.json')
            db.add(
                {
                    "name": "test2",
                    "path": "test2.proto",
                    "file_contents": "test2"},
                "2"
            )
            db._save()
            self.assertEqual(db.get_data(), [
                { 
                    "1": {
                        "name": "test",
                        "path": "test.proto",
                        "file_contents": "test"
                    }
                }
            ])


if __name__ == '__main__':
    main()