import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

JOB_APPLICATION_RECORDS_CSV = os.path.join('data', 'application_records.csv')

class JobApplicationRecords:
    def __init__(self, csv_path=JOB_APPLICATION_RECORDS_CSV):
        self.csv_path = csv_path
        # Dict: key = (job_position.lower(), company.lower()), value = [job_position, company, date_str]
        self.records = {}
        self._load()

    def _load(self):
        self.records = {}
        try:
            with open(self.csv_path, 'r', newline='') as csvfile:
                for pos, comp, date_str in csv.reader(csvfile):
                    key = (pos.lower(), comp.lower())
                    if key not in self.records:
                        self.records[key] = [pos, comp, date_str]
        except FileNotFoundError:
            pass

    def _save(self):
        with open(self.csv_path, 'w', newline='') as csvfile:
            csv.writer(csvfile).writerows(self.records.values())

    def should_apply(self, job_position: str, company: str) -> bool:
        """
        Return True if not applied in last 30 days, else False. Updates/creates record as needed.
        """
        now = datetime.now().date()
        key = (job_position.lower(), company.lower())
        rec = self.records.get(key)
        if rec:
            try:
                last_date = datetime.strptime(rec[2], '%Y-%m-%d').date()
            except Exception:
                last_date = now - timedelta(days=31)
            if (now - last_date).days >= 30:
                rec[2] = now.strftime('%Y-%m-%d')
                self._save()
                return True
            return False
        # New record
        self.records[key] = [job_position, company, now.strftime('%Y-%m-%d')]
        self._save()
        return True
