class ModelRegistry:
    
    registry = {}

    @classmethod
    def register(cls, name):
        def decorator(model_class):
            if name in cls.registry:
                raise KeyError(f"Model '{name}' is already registered.")
            cls.registry[name] = model_class
            return model_class
        return decorator

    @classmethod
    def get_model(cls, name):
        model_class = cls.registry.get(name)
        if model_class is None:
            available_models = ", ".join(cls.registry.keys())
            raise ValueError(f"Model '{name}' not found. Available models: {available_models}")
        return model_class

    
    @classmethod
    def unregister(cls, name):
        if name in cls.registry:
            del cls.registry[name]
        else:
            raise ValueError(f"Model '{name}' not registered.")
