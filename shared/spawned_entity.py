from .entity import Entity


class SpawnedEntity(Entity):

    def __init__(self, obj_id=None, name="Unknown", desc="Unknown", room=None):
        super().__init__(obj_id, name, desc)
        self.room = room




