import sys
import os
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from job_application_records import JobApplicationRecords

def test_should_apply():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        test_csv = tmp.name
    try:
        records = JobApplicationRecords(csv_path=test_csv)
        assert records.should_apply('Engineer', 'Acme')
        assert not records.should_apply('Engineer', 'Acme')
        assert not records.should_apply('engineer', 'ACME')
        assert records.should_apply('Engineer', 'Beta')
        assert records.should_apply('Manager', 'Acme')
        print('All tests passed.')
    finally:
        os.remove(test_csv)

if __name__ == '__main__':
    test_should_apply()
