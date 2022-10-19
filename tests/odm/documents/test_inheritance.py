from beanie import init_beanie
from tests.odm.models import (
    Vehicle, Bicycle, Bike, Car, Bus,
)


class TestInheritance:
    async def test_inheritance(self, db):
        await init_beanie(database=db, document_models=[Vehicle, Bicycle, Bike, Car, Bus])

        bicycle_1 = await Bicycle(color='white', frame=54, wheels=29).insert()
        bicycle_2 = await Bicycle(color='red', frame=52, wheels=28).insert()

        bike_1 = await Bike(color='black', fuel='gasoline').insert()

        car_1 = await Car(color='grey', body='sedan', fuel='gasoline').insert()
        car_2 = await Car(color='white', body='crossover', fuel='diesel').insert()

        bus_1 = await Bus(color='white', seats=80, body='bus', fuel='diesel').insert()
        bus_2 = await Bus(color='yellow', seats=26, body='minibus', fuel='diesel').insert()

        white_vehicles = await Vehicle.find(Vehicle.color == 'white').to_list()

        cars_only = await Car.find({'_class_id': 'Car'}).to_list()
        cars_and_buses = await Car.find(Car.fuel == 'diesel').to_list()

        big_bicycles = await Bicycle.find(Bicycle.wheels > 28).to_list()

        await Bike.find().update({"$set": {Bike.color: 'yellow'}})
        sedan = await Car.find_one(Car.body == 'sedan')

        sedan.color = 'yellow'
        await sedan.save()

        # get using Vehicle should return Bike instance
        updated_bike = await Vehicle.get(bike_1.id)

        assert isinstance(sedan, Car)

        assert isinstance(updated_bike, Bike)
        assert updated_bike.color == 'yellow'

        assert Vehicle.get_parent() is Vehicle
        assert Bus.get_parent() is Vehicle

        assert len(big_bicycles) == 1
        assert big_bicycles[0].wheels > 28

        assert len(white_vehicles) == 3
        assert len(cars_only) == 2

        assert {Car, Bus} == set(i.__class__ for i in cars_and_buses)
        assert {Bicycle, Car, Bus} == set(i.__class__ for i in white_vehicles)

        for i in cars_and_buses:
            assert i.fuel == 'diesel'

        for e in (bicycle_1, bicycle_2, bike_1, car_1, car_2, bus_1, bus_2):
            assert isinstance(e, Vehicle)
            await e.delete()
