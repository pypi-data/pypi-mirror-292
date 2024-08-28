from thinking_tests.aspect.protocol import TestAspect

CUSTOM_ASPECTS = []

def register_aspect(aspect_or_type: TestAspect | type[TestAspect]):
    if isinstance(aspect_or_type, type):
        aspect_or_type = aspect_or_type()
    CUSTOM_ASPECTS.append(aspect_or_type)