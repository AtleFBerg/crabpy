class BaseView:
    def update(self, screen, camera_x, camera_y):
        raise NotImplementedError("Subclasses must implement the update method")

    def draw(self, screen, camera_x, camera_y):
        raise NotImplementedError("Subclasses must implement the draw method")

