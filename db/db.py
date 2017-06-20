import csv
import os
import six
from datetime import datetime
from mysql import connector
from .singleton import MetaSingleton
from credentials import DB_HOST, DB_NAME, DB_PWD, DB_USER

if not os.path.exists('results'):
    os.makedirs('results')


@six.add_metaclass(MetaSingleton)
class DB:
    def __init__(self):
        self._db = connector.connect(
            user=DB_USER, passwd=DB_PWD,
            database=DB_NAME, host=DB_HOST
        )

    @property
    def db(self):
        return self._db

    @property
    def get_current_date(self):
        return datetime.now().strftime('%d_%m_%H_%M')

    def form_query(self, args):
        query = f'select {args} from es_users as u' \
                ' LEFT JOIN es_writers as w ON w.writer_id = u.user_id' \
                ' WHERE w.writer_id is not NULL and u.balance > 0 and u.locked = 0 and w.state = 4'

        return query

    def get_stats(self):
        query = self.form_query('u.user_id, u.nickname, u.balance')
        cursor = self.db.cursor()
        cursor.execute(query)
        current_data = self.get_current_date
        file_name = f'results/result_{current_data}.csv'
        with open(file_name, 'w', newline='') as f:
            file = csv.writer(f)
            for item in cursor.fetchall():
                file.writerow(item)

        return file_name

    def get_sum(self):
        query = self.form_query('sum(u.balance)')

        cursor = self.db.cursor()
        cursor.execute(query)
        result = list(cursor.fetchone())
        return str(result[0])

