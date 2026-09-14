import unittest
import json
import os
import glob
import jsonschema

class TestCourseSchemas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'course_schema.json')
        with open(schema_path, 'r') as f:
            cls.schema = json.load(f)

    def test_all_course_files_against_schema(self):
        course_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses')
        course_files = glob.glob(os.path.join(course_dir, '*.json'))
        # Exclude courses_index.json
        course_files = [f for f in course_files if not f.endswith('courses_index.json')]
        
        self.assertGreaterEqual(len(course_files), 7, "Should have at least 7 course files")
        
        for file_path in course_files:
            with self.subTest(file=os.path.basename(file_path)):
                with open(file_path, 'r') as f:
                    course_data = json.load(f)
                
                # 1. Validate against JSON schema
                jsonschema.validate(instance=course_data, schema=self.schema)
                
                # 2. Assert category weights sum to exactly 100.0%
                total_cat_weight = sum(cat['weight_percent'] for cat in course_data['categories'])
                self.assertAlmostEqual(total_cat_weight, 100.0, places=1,
                                       msg=f"{course_data['course_code']} category weights do not sum to 100%")
                
                # 3. Assert items in each category have valid properties
                for cat in course_data['categories']:
                    self.assertGreater(len(cat['items']), 0, f"Category {cat['name']} has no items")
                    for item in cat['items']:
                        self.assertGreater(item['max_points'], 0, f"Item {item['name']} max_points must be > 0")
                        self.assertGreater(item['weight_percent'], 0, f"Item {item['name']} weight must be > 0")

    def test_courses_index_integrity(self):
        index_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses', 'courses_index.json')
        self.assertTrue(os.path.exists(index_path))
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        self.assertEqual(len(index_data['courses']), 7)
        total_credits = sum(c['credits'] for c in index_data['courses'])
        self.assertEqual(total_credits, 19.0)
        
        # Verify technical vs non-technical breakdown
        tech_courses = [c['code'] for c in index_data['courses'] if c['is_technical']]
        self.assertEqual(sorted(tech_courses), ['CSN305', 'DAT330', 'MST300', 'OPS345', 'SEC320'])

if __name__ == '__main__':
    unittest.main()
