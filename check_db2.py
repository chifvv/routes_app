import sqlite3
conn = sqlite3.connect('/app/data/routes.db')
c = conn.cursor()

print('=== Месяцы в schedule ===')
months = c.execute('SELECT DISTINCT year, month FROM schedule ORDER BY year, month').fetchall()
for m in months:
    print(m)

print('\n=== Апрель 2026, driver_id=1 ===')
rows = c.execute('SELECT day, route_id FROM schedule WHERE year=2026 AND month=4 AND driver_id=1 ORDER BY day').fetchall()
for r in rows[:20]:
    print(r)
