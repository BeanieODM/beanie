## Inheritance for multi-model use case

Beanie `Documents` support inheritance as any other Python classes. But there are additional features available, if you mark the root model with parameter `is_root = True` in the inner Settings class.

This behavior is similar to `UnionDoc`, but you don't need additional entity.
Parent `Document` act like a "controller", that handle proper storing and fetching different type `Document`.
Also, parent `Document` can have some shared attributes which are propagated to all children.
All classes in inheritance chain can be a used as `Link` in foreign `Documents`.

Depend on the business logic, parent `Document` can be like "abstract" class that is not used to store objects of its type (like in example below), as well as can be a full-fledged entity, like its children.

## Examples

Define models

```py hl_lines="20 20"
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from beanie import Document, Link, init_beanie


class Vehicle(Document):
    """Inheritance scheme bellow"""
    #               Vehicle
    #              /   |   \
    #             /    |    \
    #        Bicycle  Bike  Car
    #                         \
    #                          \
    #                          Bus
    # shared attribute for all children
    color: str
    
    class Settings:
        is_root = True


class Fuelled(BaseModel):
    """Just a mixin"""
    fuel: Optional[str]


class Bicycle(Vehicle):
    """Derived from Vehicle, will use its collection"""
    frame: int
    wheels: int


class Bike(Vehicle, Fuelled):
    ...


class Car(Vehicle, Fuelled):
    body: str


class Bus(Car, Fuelled):
    """Inheritance chain is Vehicle -> Car -> Bus, it is also stored in Vehicle collection"""
    seats: int
    
    
class Owner(Document):
    vehicles: Optional[List[Link[Vehicle]]]
```

Insert data

```python
client = AsyncIOMotorClient()
await init_beanie(client.test_db, document_models=[Vehicle, Bicycle, Bike, Car, Bus])

bike_1 = await Bike(color='black', fuel='gasoline').insert()

car_1 = await Car(color='grey', body='sedan', fuel='gasoline').insert()
car_2 = await Car(color='white', body='crossover', fuel='diesel').insert()

bus_1 = await Bus(color='white', seats=80, body='bus', fuel='diesel').insert()
bus_2 = await Bus(color='yellow', seats=26, body='minibus', fuel='diesel').insert()

owner = await Owner(name='John', vehicles=[car_1, car_2, bus_1]).insert()
```

Query data

```python
# this query returns vehicles of all types that have white color, becuase `with_children` is True
white_vehicles = await Vehicle.find(Vehicle.color == 'white', with_children=True).to_list()
# [
#    Bicycle(..., color='white', frame=54, wheels=29),
#    Car(fuel='diesel', ..., color='white', body='crossover'),
#    Bus(fuel='diesel', ..., color='white', body='bus', seats=80)
# ]

# however it is possible to limit by Vehicle type
cars_only = await Car.find().to_list()
# [
#     Car(fuel='gasoline', ..., color='grey', body='sedan'),
#     Car(fuel='diesel', ..., color='white', body='crossover')
# ]

# if search is based on child, query returns this child type and all sub-children
cars_and_buses = await Car.find(Car.fuel == 'diesel', with_children=True).to_list()
# [
#     Car(fuel='diesel', ..., color='white', body='crossover'),
#     Bus(fuel='diesel', ..., color='white', body='bus', seats=80),
#     Bus(fuel='diesel', ..., color='yellow', body='minibus', seats=26)
# ]

# to get a single Document it is not necessary to known its type
# you can query using parent class
await Vehicle.get(bus_2.id, with_children=True)
# returns Bus instance:
# Bus(fuel='diesel', ..., color='yellow', body='minibus', seats=26)

# re-fetch from DB with resolved links (using aggregation under the hood)
owner = await Owner.get(owner.id, fetch_links=True)
print(owner.vehicles)
# returns
# [
#    Car(fuel='diesel', ..., color='white', body='crossover'),
#    Bus(fuel='diesel', ..., color='white', body='bus', seats=80),
#    Car(fuel='gasoline', ..., color='grey', body='sedan')
# ]
# the same result will be if owner get without fetching link, and they will be fetched manually later

# all other operations works the same as simple Documents
await Bike.find().update({"$set": {Bike.color: 'yellow'}})
await Car.find_one(Car.body == 'sedan')
```
