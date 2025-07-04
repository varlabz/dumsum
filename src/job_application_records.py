import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import sqlite3
from typing_extensions import Final

JOB_APPLICATION_RECORDS_CSV: Final = 'data/_records.csv'
JOB_APPLICATION_RECORDS_DB: Final =  'data/_records.db'

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

class JobApplicationRecordsSQLite:
    def __init__(self, db_path=JOB_APPLICATION_RECORDS_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    job_position TEXT NOT NULL COLLATE NOCASE,
                    company TEXT NOT NULL COLLATE NOCASE,
                    date_str TEXT NOT NULL,
                    PRIMARY KEY (job_position, company)
                )
            ''')

    def should_apply(self, job_position: str, company: str) -> bool:
        now = datetime.now().date()
        job_position = job_position.strip()
        company = company.strip()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT date_str FROM applications WHERE job_position=? AND company=?',
                (job_position, company)
            )
            row = cur.fetchone()
            if row:
                try:
                    last_date = datetime.strptime(row[0], '%Y-%m-%d').date()
                except Exception:
                    last_date = now - timedelta(days=31)
                if (now - last_date).days < 30:
                    return False
                cur.execute(
                    'UPDATE applications SET date_str=? WHERE job_position=? AND company=?',
                    (now.strftime('%Y-%m-%d'), job_position, company)
                )
            else:
                cur.execute(
                    'INSERT INTO applications (job_position, company, date_str) VALUES (?, ?, ?)',
                    (job_position, company, now.strftime('%Y-%m-%d'))
                )
            conn.commit()
            return True
