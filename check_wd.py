import calendar
print('April 2026:')
for d in range(1, 31):
    wd = calendar.weekday(2026, 3, d)  # month is 0-based
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    print(f'{d}: {wd} = {days[wd]}')
