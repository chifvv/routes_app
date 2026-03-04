import calendar
year, month = 2026, 4
print('April 2026:')
for day in range(1, 16):
    wd = calendar.weekday(year, month-1, day)
    day_name = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'][wd]
    is_weekend = wd == 5 or wd == 6
    print(f'{day}: {day_name} - {"В" if is_weekend else "раб"}')
