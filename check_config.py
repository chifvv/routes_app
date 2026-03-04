import sqlite3
c = sqlite3.connect('/app/data/routes.db').cursor()
rows = c.execute('SELECT year, month, holiday_days FROM month_config').fetchall()
for r in rows:
    print(r)
