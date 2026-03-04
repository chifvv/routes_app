import sqlite3
c = sqlite3.connect('/app/data/routes.db').cursor()
rows = c.execute('SELECT day, route_id FROM schedule WHERE year=2026 AND month=4 AND driver_id=1 ORDER BY day').fetchall()
for r in rows[:20]:
    print(r)
