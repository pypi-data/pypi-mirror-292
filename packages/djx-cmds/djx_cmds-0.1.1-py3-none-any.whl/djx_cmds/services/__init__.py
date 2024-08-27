import django


class ImportObject:

    @staticmethod
    def format_class(cls):
        return {
            "module": cls.__module__,
            "name": cls.__name__
        }

    def import_model(self, model_name):
        model = self.get_model(model_name)
        formatted_model = self.format_class(model)
        return formatted_model

    @staticmethod
    def get_app(cls):
        return cls._meta.app_label

    @staticmethod
    def get_model(model_name):
        models = django.apps.apps.get_models()
        for model in models:
            if model.__name__.lower() == model_name.lower():
                return model

    @staticmethod
    def get_model_fields(model):
        fields = [{"name": i.name} for i in model._meta.get_fields()]

        return fields
