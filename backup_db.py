import sqlite3
import shutil
from datetime import datetime

src = '/app/data/routes.db'
backup = f'/app/data/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

shutil.copy2(src, backup)
print(f'Backup created: {backup}')

conn = sqlite3.connect(src)
c = conn.cursor()

print('\n=== ROUTES ===')
routes = c.execute('SELECT id, name, price, monday, tuesday, wednesday, thursday, friday, saturday, sunday FROM route').fetchall()
for r in routes:
    print(r)

print('\n=== DRIVERS ===')
drivers = c.execute('SELECT id, name, car_type, route_ids, no_trip_days FROM driver').fetchall()
for d in drivers:
    print(d)

conn.close()
