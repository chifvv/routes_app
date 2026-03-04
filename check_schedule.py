import sqlite3
conn = sqlite3.connect('/app/data/routes.db')
c = conn.cursor()

print('=== April 2026, driver_id=1 ===')
rows = c.execute('SELECT day, route_id FROM schedule WHERE year=2026 AND month=4 AND driver_id=1 ORDER BY day').fetchall()
for r in rows[:15]:
    print(r)

print()
print('=== January 2026, driver_id=1 ===')
rows = c.execute('SELECT day, route_id FROM schedule WHERE year=2026 AND month=1 AND driver_id=1 ORDER BY day').fetchall()
for r in rows[:15]:
    print(r)
