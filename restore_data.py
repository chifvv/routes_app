import sqlite3

backup_db = '/app/data/backup_20260301_185357.db'
target_db = '/app/data/routes.db'

conn_backup = sqlite3.connect(backup_db)
conn_target = sqlite3.connect(target_db)

conn_target.execute('DELETE FROM route')
conn_target.execute('DELETE FROM driver')

for row in conn_backup.execute('SELECT id, name, price, monday, tuesday, wednesday, thursday, friday, saturday, sunday FROM route'):
    conn_target.execute('INSERT INTO route VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', row)

for row in conn_backup.execute('SELECT id, name, car_type, route_ids, no_trip_days FROM driver'):
    conn_target.execute('INSERT INTO driver VALUES (?, ?, ?, ?, ?)', row)

conn_target.commit()
print('Routes:', conn_target.execute('SELECT COUNT(*) FROM route').fetchone())
print('Drivers:', conn_target.execute('SELECT COUNT(*) FROM driver').fetchone())

conn_backup.close()
conn_target.close()
