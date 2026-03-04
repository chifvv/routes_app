from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/routes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('routes.html')


@app.route('/schedule')
def schedule_page():
    return render_template('schedule.html')


@app.route('/drivers')
def drivers_page():
    return render_template('drivers.html')


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
    monday = db.Column(db.Boolean, default=False)
    tuesday = db.Column(db.Boolean, default=False)
    wednesday = db.Column(db.Boolean, default=False)
    thursday = db.Column(db.Boolean, default=False)
    friday = db.Column(db.Boolean, default=False)
    saturday = db.Column(db.Boolean, default=False)
    sunday = db.Column(db.Boolean, default=False)


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    car_type = db.Column(db.String(20), default="small")
    
    route_ids = db.Column(db.String(200), default="")
    no_trip_days = db.Column(db.String(200), default="")


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    day = db.Column(db.Integer, nullable=False)
    route_id = db.Column(db.String(10), default='')


class MonthConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    holiday_days = db.Column(db.String(100), default='')


@app.route('/api/schedule/holidays/<int:year>/<int:month>', methods=['GET'])
def get_holidays(year, month):
    config = MonthConfig.query.filter_by(year=year, month=month).first()
    if config:
        return jsonify({'holiday_days': config.holiday_days or ''})
    return jsonify({'holiday_days': ''})


@app.route('/api/schedule/holidays', methods=['POST'])
def save_holidays():
    data = request.json
    year = data.get('year')
    month = data.get('month')
    holiday_days = data.get('holiday_days', '')
    
    config = MonthConfig.query.filter_by(year=year, month=month).first()
    if not config:
        config = MonthConfig(year=year, month=month, holiday_days=holiday_days)
        db.session.add(config)
    else:
        config.holiday_days = holiday_days
    db.session.commit()
    
    return jsonify({'message': 'Сохранено'})


@app.route('/api/schedule/generate', methods=['POST'])
def generate_schedule():
    data = request.json
    year = data.get('year')
    month = data.get('month')
    holiday_days_str = data.get('holiday_days', '')
    
    Schedule.query.filter_by(year=year, month=month).delete()
    
    config = MonthConfig.query.filter_by(year=year, month=month).first()
    if not config:
        config = MonthConfig(year=year, month=month, holiday_days=holiday_days_str)
        db.session.add(config)
    else:
        config.holiday_days = holiday_days_str
    
    drivers = Driver.query.order_by(Driver.name).all()
    
    if not drivers:
        return jsonify({'error': 'Нет водителей'}), 400
    
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    holiday_days = [int(d.strip()) for d in holiday_days_str.split(',') if d.strip().isdigit()]
    
    for day in range(1, days_in_month + 1):
        weekday = calendar.weekday(year, month, day)
        is_weekend = (weekday == 5 or weekday == 6) or day in holiday_days
        
        for driver in drivers:
            route_id = 'В' if is_weekend else ''
            schedule = Schedule(
                year=year,
                month=month,
                driver_id=driver.id,
                day=day,
                route_id=route_id
            )
            db.session.add(schedule)
    
    db.session.commit()
    return jsonify({'message': f'График создан для {month}/{year}', 'days': days_in_month, 'drivers': len(drivers)})


@app.route('/api/schedule/<int:year>/<int:month>', methods=['GET'])
def get_schedule(year, month):
    schedules = Schedule.query.filter_by(year=year, month=month).all()
    drivers = Driver.query.order_by(Driver.name).all()
    routes = Route.query.all()
    route_prices = {r.id: r.price for r in routes}
    
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    result = []
    for driver in drivers:
        driver_schedules = [s for s in schedules if s.driver_id == driver.id]
        has_routes = bool(driver.route_ids and driver.route_ids.strip())
        is_big_with_routes = driver.car_type == 'big' and has_routes
        driver_data = {
            'driver_id': driver.id,
            'driver_name': driver.name,
            'car_type': driver.car_type,
            'is_big_with_routes': is_big_with_routes,
            'days': {},
            'trip_count': 0,
            'trip_sum': 0
        }
        for s in driver_schedules:
            driver_data['days'][s.day] = s.route_id
            # Считаем командировки (только числовые ID, не В/О)
            if s.route_id and str(s.route_id).isdigit():
                route_id = int(s.route_id)
                route = next((r for r in routes if r.id == route_id), None)
                if route and route.name != 'Озон':
                    driver_data['trip_count'] += 1
                    driver_data['trip_sum'] += route.price
        result.append(driver_data)
    
    holiday_days = ''
    config = MonthConfig.query.filter_by(year=year, month=month).first()
    if config:
        holiday_days = config.holiday_days or ''
    
    return jsonify({
        'year': year,
        'month': month,
        'days_in_month': days_in_month,
        'holiday_days': holiday_days,
        'drivers': result
    })


@app.route('/api/schedule/update', methods=['POST'])
def update_schedule_day():
    data = request.json
    year = data.get('year')
    month = data.get('month')
    driver_id = data.get('driver_id')
    day = data.get('day')
    value = data.get('value')
    
    schedule = Schedule.query.filter_by(
        year=year, month=month, driver_id=driver_id, day=day
    ).first()
    
    if not schedule:
        schedule = Schedule(year=year, month=month, driver_id=driver_id, day=day, route_id=value)
        db.session.add(schedule)
    else:
        schedule.route_id = value
    db.session.commit()
    
    return jsonify({'message': 'Сохранено'})


@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.order_by(Driver.name).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'car_type': d.car_type,
        'route_ids': d.route_ids,
        'no_trip_days': d.no_trip_days
    } for d in drivers])


@app.route('/api/drivers', methods=['POST'])
def create_driver():
    data = request.json
    driver = Driver(
        name=data['name'],
        car_type=data.get('car_type', 'small'),
        route_ids=data.get('route_ids', ''),
        no_trip_days=data.get('no_trip_days', '')
    )
    db.session.add(driver)
    db.session.commit()
    return jsonify({'id': driver.id, 'message': 'Driver created'})


@app.route('/api/drivers/<int:id>', methods=['PUT'])
def update_driver(id):
    driver = db.session.get(Driver, id)
    if not driver:
        return jsonify({'error': 'Not found'}), 404
    data = request.json
    driver.name = data.get('name', driver.name)
    driver.car_type = data.get('car_type', driver.car_type)
    driver.route_ids = data.get('route_ids', driver.route_ids)
    driver.no_trip_days = data.get('no_trip_days', driver.no_trip_days)
    db.session.commit()
    return jsonify({'message': 'Driver updated'})


@app.route('/api/drivers/<int:id>', methods=['DELETE'])
def delete_driver(id):
    driver = db.session.get(Driver, id)
    if not driver:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(driver)
    db.session.commit()
    return jsonify({'message': 'Driver deleted'})


@app.route('/api/routes', methods=['GET'])
def get_routes():
    routes = Route.query.order_by(Route.name).all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'price': r.price,
        'monday': r.monday,
        'tuesday': r.tuesday,
        'wednesday': r.wednesday,
        'thursday': r.thursday,
        'friday': r.friday,
        'saturday': r.saturday,
        'sunday': r.sunday
    } for r in routes])


@app.route('/api/routes', methods=['POST'])
def create_route():
    data = request.json
    route = Route(
        name=data['name'],
        price=data['price'],
        monday=data.get('monday', False),
        tuesday=data.get('tuesday', False),
        wednesday=data.get('wednesday', False),
        thursday=data.get('thursday', False),
        friday=data.get('friday', False),
        saturday=data.get('saturday', False),
        sunday=data.get('sunday', False)
    )
    db.session.add(route)
    db.session.commit()
    return jsonify({'id': route.id, 'message': 'Route created'})


@app.route('/api/routes/<int:id>', methods=['PUT'])
def update_route(id):
    route = db.session.get(Route, id)
    if not route:
        return jsonify({'error': 'Not found'}), 404
    data = request.json
    route.name = data.get('name', route.name)
    route.price = data.get('price', route.price)
    route.monday = data.get('monday', route.monday)
    route.tuesday = data.get('tuesday', route.tuesday)
    route.wednesday = data.get('wednesday', route.wednesday)
    route.thursday = data.get('thursday', route.thursday)
    route.friday = data.get('friday', route.friday)
    route.saturday = data.get('saturday', route.saturday)
    route.sunday = data.get('sunday', route.sunday)
    db.session.commit()
    return jsonify({'message': 'Route updated'})


@app.route('/api/routes/<int:id>', methods=['DELETE'])
def delete_route(id):
    route = db.session.get(Route, id)
    if not route:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(route)
    db.session.commit()
    return jsonify({'message': 'Route deleted'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
