class BaseView:
    def update(self, screen, camera_x, camera_y, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the update method")

    def handle_events(self, events, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the handle_events method")
    
    def handle_keys(self, keys, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the handle_keys method")