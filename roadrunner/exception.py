class RoadrunnerError(Exception):
    pass


class DefinitionSetNotFound(RoadrunnerError):
    pass


class DefinitionTimeout(RoadrunnerError):
    pass
