import json
import os
import inspect
import re
from django.template import Template, Context
from django.apps import apps
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.http import HttpResponse

from django.db.models import OneToOneRel, ManyToOneRel, ManyToManyRel # reverse 
from django.db.models import OneToOneField, ForeignKey, ManyToManyField # forward


class ShowModelsAll(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["models"] = json.dumps(self.get_models_data())
        return context

    def get_models_data(self):
        models_data = []
        list_of_models = apps.get_models()

        for model in list_of_models:
            model_info = {
                "name": model.__name__,
             }
            
            models_data.append(model_info)
       
        return models_data

    def render_to_response(self, context, **response_kwargs):

        html_content = open('django_model_viewer/templates/main.html', 'r').read()

        template = Template(html_content)

        context = Context(context)

        rendered_html = template.render(context)

        return HttpResponse(rendered_html)


def ajax_call(request):
    model = None
    list_of_models = apps.get_models()
    
    for x in list_of_models:
        if x.__name__ == request.GET.get("model"):
            model = x

    if not model:
        raise ValueError(f"Error finding model {request.GET.get('model')}")

    field_url = os.path.abspath((apps.get_model(f'{model._meta.app_label}.{model._meta.object_name}').__module__).replace('.', '/') + '.py')
    line_number = inspect.getsourcelines(model)[1]
    list_of_parameters_data = inspect.getsourcelines(model)[0]
    list_of_parameters_data.pop(0)
    correct_list = []
    
    for x in list_of_parameters_data:
        cleaned = re.sub(r'\s+', ' ', x.strip())
        correct_list.append(cleaned)
    
    list_of_functions = [method_name for method_name in dir(model) if callable(getattr(model, method_name)) and not method_name.startswith("__") and not method_name == 'DoesNotExist' and not method_name == 'MultipleObjectsReturned' and not method_name.startswith('_')]
    
    correct_list_of_functions = []
    for method_name in list_of_functions:
        method = getattr(model, method_name)  
        try:
            source_code = inspect.getsource(method) 
        except TypeError:

            source_code = "Source code not available"
        
        correct_list_of_functions.append({
            'name': method_name,
            'data': source_code
        })
    
    print(correct_list_of_functions)
    
    model_info = {
        "name": model.__name__,
        "fields": {},
        "relations": {"other": [], "set": []},
        "url": f"vscode://file/{field_url}:{line_number}",
        "functions": json.dumps(correct_list_of_functions)
    }

    for field in model._meta.get_fields():
        field_type = (
            field.get_internal_type()
            if hasattr(field, "get_internal_type")
            else "Unknown"
        )

        data = next((x for x in correct_list if x.startswith(field.name)), None)
        field_info = {"name": field.name, "type": field_type, 'data': data or field_type}

        if field_type not in model_info["fields"]:
            model_info["fields"][field_type] = []

        model_info["fields"][field_type].append(field_info)

        if field.is_relation:
            related_model = field.related_model.__name__ if field.related_model else None
            related_name = getattr(field, "related_name", None) or f"{model.__name__.lower()}_set"
            relation_type = field_type if hasattr(field, "get_internal_type") else "Unknown"

            if related_model:
                relation_info = {
                    "related_model": related_model,
                    "related_name": related_name,
                    "field_name": field.name,
                    "relation_type": relation_type,
                    "data": data or related_model
                }
                from django.db.models import OneToOneRel, ManyToOneRel, ManyToManyRel # reverse 
                from django.db.models import OneToOneField, ForeignKey, ManyToManyField # forward
                
                if isinstance(field, (ManyToOneRel, OneToOneRel, ManyToManyRel)):
                    model_info["relations"]["set"].append(relation_info)
                else:
                    model_info["relations"]["other"].append(relation_info)
    print(model_info)

    return JsonResponse({"data": model_info})


def ajax_call_get_path(request):
    path_json = request.GET.get('list')
    
    if path_json:
        list_of_models = json.loads(path_json)
    else:
        list_of_models = []
        
    model_names = [x.lower() for x in list_of_models]
    correct_list = []
    
    for model_name in model_names:
        found_model = None
        for model in apps.get_models():
            if model_name == model._meta.model_name.lower():
                found_model = model
                break
        if found_model:
            correct_list.append(found_model)
        else:
            print(f"Model not found for name: {model_name}")
    
    
    if not correct_list:
        return JsonResponse({'path': ''})
    elif len(correct_list) < 2:
        return JsonResponse({'path': str(correct_list[0].__name__)})

    path = f'{correct_list[0].__name__}'

    for i in range(len(correct_list) - 1):
        current_model = correct_list[i]
        next_model = correct_list[i + 1]
        found = False
        
        for field in current_model._meta.get_fields():
            if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
                if field.related_model == next_model:
                    path += f".{field.name}"
                    found = True
                    break
            elif isinstance(field, (ManyToOneRel, OneToOneRel, ManyToManyRel)):
                if field.related_model == next_model:
                    path += f".{field.related_name or next_model.__name__.lower() + '_set'}"
                    found = True
                    break

        if not found:
            path = 'Path not found'
            break

    return JsonResponse({'path': path})
