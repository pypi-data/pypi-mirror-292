import os

import inflection
from django.conf import settings
from django.core.management.base import BaseCommand

from djx_cmds.format_with_jinja import format_with_jinja
from djx_cmds.services import ImportObject


class Command(BaseCommand):
    help = ''

    def __init__(self):
        super(Command, self).__init__()
        self.available_methods = [
            {'code': 'c', 'action': 'Create'},
            {'code': 'r', 'action': ''},
            {'code': 'u', 'action': 'Update'},
            {'code': 'd', 'action': 'Delete'},
        ]

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='name')
        parser.add_argument('--action', type=str, default='r')

    def handle(self, *args, **options):
        name = options['name']
        allowed_actions = options['action']
        model_data = ImportObject().import_model(name)
        model_name = model_data['name']
        model_module = model_data['module']

        self.create_serializer(model_name, model_module, allowed_actions)
        self.create_views(model_name, model_module, allowed_actions)

    def create_views(self, model_name, model_module, actions):
        model = ImportObject().get_model(model_name)
        app_name = ImportObject.get_app(model)
        view_content = ""
        view_content += f"from {model_module} import {model_name}\n"
        view_content += f"from rest_framework.permissions import IsAuthenticated\n"
        view_content += f"from rest_framework import viewsets\n"
        suffixes = []
        for element in actions:
            suffixes.append([item['action'] for item in self.available_methods if item['code'] == element][0])

        serializers = ", ".join([f"{model_name}{suffix}Serializer" for suffix in suffixes])
        view_content += f"from {app_name}.serializers.{inflection.underscore(model_name)}_serializers " \
                        f"import {serializers}\n"

        view_content += format_with_jinja({'model_name': model_name, 'actions': actions},
                                          'view.txt')
        view_file_name = inflection.underscore(f"{model_name}_views.py")

        view_file_path = os.path.join(settings.BASE_DIR, app_name, 'views', view_file_name)
        self.create_file(file_path=view_file_path, file_content=view_content)
        self.create_urls(app_name, model_name)

    def create_serializer(self, model_name, model_module, allowed_actions):

        serializer_content = ""
        serializer_content += f"from {model_module} import {model_name}\n"
        serializer_content += f"from rest_framework import serializers\n"

        model = ImportObject().get_model(model_name)
        app_name = ImportObject.get_app(model)
        fields = ImportObject().get_model_fields(model)

        for method in self.available_methods:
            if method['code'] in allowed_actions:
                serializer_content += format_with_jinja(
                    {'model_name': model_name, 'method': method['action'], "fields": fields}, 'serializer.txt')
        serializer_file_name = inflection.underscore(f"{model_name}_serializers.py")

        serializer_file_path = os.path.join(settings.BASE_DIR, app_name, 'serializers', serializer_file_name)
        self.create_file(file_path=serializer_file_path, file_content=serializer_content)

    @staticmethod
    def create_file(file_path, file_content, mode='w'):
        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(file_content)

    def create_urls(self, app_name, model_name):
        dash = inflection.dasherize(inflection.underscore(model_name))
        register = f"router.register('{dash}', {model_name}ViewSet, basename='{dash}')"
        file_path = os.path.join(settings.BASE_DIR, app_name, 'urls.py')
        with open(file_path, 'r') as f:
            content = f.read()
        tag = "# registration"
        import_str = f"from {app_name}.views.{inflection.underscore(model_name)}_views import {model_name}ViewSet"
        content = content.replace(f"{tag}", f'{register}\n{tag}')
        content = f"{import_str}\n{content}"
        with open(file_path, 'w') as f:
            content = f.write(content)
