from .models import HouseAPI, WindowAPI


class WindowRepository:
    def __init__(self):
        self.windows: list[WindowAPI] = []
        
    async def create(self, window):
        self.windows.append(window)
        
    def get_window_by_id(self, search_id):
        return next(filter(lambda window: window.id == search_id, self.windows))
        
        
class HouseRepository:
    def __init__(self, window_repository: WindowRepository):
        self.houses = []
        self.window_repository: WindowRepository = window_repository
        
    async def create(self, house):
        self.houses.append(house)
        
    async def create_house_from_dict(self, house: dict[str, any]):
        windows = [self.create_links_from_windows(window) for window in house["windows"]] 
        new_house = HouseAPI(name=house["name"], windows=[windows]) 
        self.houses.append(new_house)
        
    def create_links_from_windows(self, window):
        window = self.window_repository.get_window_by_id(window.id)
        if not window:
            self.window_repository.create(window)
            
        return window
    