import calendar
print('April 2026:')
for d in [1, 2, 3, 4, 5, 6, 7, 8]:
    wd = calendar.weekday(2026, 3, d)
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    print(f'{d}: {wd} = {days[wd]}')
