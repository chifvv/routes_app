import calendar

# monthrange(year, month) - month is 1-12
wd, days = calendar.monthrange(2026, 4)
days_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
print(f'April 2026 starts: {wd} = {days_names[wd]}')
print(f'April 2026 has {days} days')

print('\nApril 2026:')
for d in range(1, 11):
    wd = calendar.weekday(2026, 4, d)
    print(f'{d}: {wd} = {days_names[wd]}')
