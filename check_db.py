import sqlite3
conn = sqlite3.connect('/app/data/routes.db')
c = conn.cursor()

print('=== ROUTES ===')
routes = c.execute('SELECT id, name, price FROM route').fetchall()
for r in routes:
    print(r)

print()
print('=== DRIVERS ===')
drivers = c.execute('SELECT id, name, car_type FROM driver').fetchall()
for d in drivers:
    print(d)

conn.close()
