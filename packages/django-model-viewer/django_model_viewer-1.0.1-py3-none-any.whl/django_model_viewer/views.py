import json
import os
import inspect
import re
from django.template import Template, Context
from django.apps import apps
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.http import HttpResponse

from django.db.models import ManyToManyRel, OneToOneField, ForeignKey, ManyToOneRel, ManyToManyField, OneToOneRel


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

        html_content = """
        <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Model Relations Visualization</title>
    <!-- jQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Flowbite -->
    <script src="https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.js"></script>
  </head>
  <body class="bg-gray-100">
    <div class="container mx-auto py-10">
      <div class="mb-5">
        <div class="grid grid-cols-8 gap-2 w-full max-w-[23rem]">
          <input id="path_input" type="text" class="bg-violet-300 col-span-6 bg-gray-50 border border-gray-300 text-gray-500 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" readonly>
          <button id="copy-btn" onclick="CopyRelationsPath()" class="col-span-2 text-white bg-violet-600 hover:bg-violet-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-2.5 text-center items-center inline-flex justify-center">
            <span id="default-message">Create path</span>
            <span id="success-message" class="hidden inline-flex items-center">
              <svg class="w-3 h-3 text-white me-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
              </svg>
              Copied!
            </span>
          </button>  
        </div>
      </div>
      <button data-modal-target="default-modal" data-modal-toggle="default-modal" class="absolute top-5 right-5 text-white bg-violet-600 hover:bg-violet-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center" type="button">About</button>
        <label for="model-select" class="block text-sm font-medium text-gray-700">Select Model:</label>
        <select id="model-select" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm">
          <option selected disabled>Select a model</option>
        </select>
      </div>   
      <!-- Main modal -->
      <div id="default-modal" tabindex="-1" aria-hidden="true" class="hidden overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full">
        <div class="relative p-4 w-full max-w-2xl max-h-full">
            <!-- Modal content -->
            <div class="relative bg-white rounded-lg shadow">
                <!-- Modal header -->
                <div class="flex items-center justify-between p-4 md:p-5 border-b rounded-t">
                    <h3 class="text-xl text-gray-900 text-center">
                        About <span class="font-semibold underline">Django-Model-Viewer</span>
                    </h3>
                </div>
                <!-- Modal body -->
                <div class="p-4 md:p-5 space-y-4">
                    <p class="text-base leading-relaxed text-gray-700">
                      An application that facilitates the identification and operation of models. It searches for all available models in the project and allows you to select and view details about them by holding the mouse on the parameter of interest. After selecting the path between models through relations, after clicking CREATE we will get a path that allows you to get to the last model. It is also possible to select a model and click on its name and it will take you to Visual Studio Code to the file and line of the given model
                    </p>
                    <p class="text-base leading-relaxed text-gray-700">
                      <strong class="text-grey-800">Relations:</strong><br>
                      Green color means normal relation.<br>
                      Orange color means reverse relation.
                    </p>
                </div>
                <!-- Modal footer -->
                <div class="flex items-center p-4 md:p-5 border-t border-gray-200 rounded-b">
                    <button data-modal-hide="default-modal" type="button" class="text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:outline-none focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center">Close</button>
                </div>
            </div>
        </div>
      </div>
      <div class="relative overflow-x-auto shadow-md sm:rounded-lg">
        <table class="w-full text-sm text-left text-gray-700">
          <thead class="text-xs uppercase bg-gray-200">
            <tr>
              <th class="px-6 py-3">Model Name</th>
              <th class="px-6 py-3">Fields</th>
              <th class="px-6 py-3">Relations</th>
            </tr>
          </thead>
          <tbody id="model-table-body" class="bg-white divide-y divide-gray-200"></tbody>
        </table>
      </div>
    </div>

  <script>
    $(document).ready(function () {
      let displayedModels = new Set(); 

      let data = JSON.parse("{{ models | escapejs }}");

      $.each(data, function (index, object) {
        $("#model-select").append(
        `<option value='${index}' name='${object.name}'>${object.name}</option>`
        );
      });

      $("#model-select").on("change", function () {
        const selectedIndex = $(this).val();
        const selectedName = $("#model-select option:selected").attr("name");
        const selectedModel = data[selectedIndex];
        $("#model-table-body").empty();  
        displayedModels.clear();         

        if (selectedModel) {
          $.ajax({
            url: '{% url "aqSFrOMAEQgBlduCuYfr" %}',
            data: {
              model: selectedName,
            },
            success: function (response) {
              const modelData = response.data;
              if (modelData) {
              appendModelRow(modelData);
              displayedModels.add(modelData.name);
              }
            },
            error: function (xhr, status, error) {
              console.error(`Error fetching data for model ${selectedName}: ${error}`);
            },
          });
        }
      });

      function appendModelRow(modelData) {
        let fieldsContent = "";
        let relationsContent = "";
        $.each(modelData.fields, function (fieldType, fieldsArray) {
          if (fieldType !== "ForeignKey" && fieldType !== "ManyToManyField") {
            $.each(fieldsArray, function (index, field) {
              const field_data = field.data.replace(/\"/g, "'")
              fieldsContent += `<span class="inline-block bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded" title="${field_data}">${field.name}</span>`;
            });
          }
        });

        $.each(modelData.relations, function (relationType, relationsArray) {
          $.each(relationsArray, function (index, relation) {
            const colorClass = relationType === "set" ? "#983412" : "#166534";
            const bgcolorClass = relationType === "set" ? "#ffedd5" : "#dcfce7";
            const name = relationType === "set" ? "reverse" : "foreign";
            const relation_data = relation.data.replace(/\"/g, "'");
            relationsContent += `<button name="${name}" style="color:${colorClass}; background-color:${bgcolorClass}" class="inline-block text-xs font-semibold mr-2 px-2.5 py-0.5 rounded hover:underline" title="${relation_data}" onclick="fetchRelatedModel('${relation.related_model}', this)">${relation.field_name}</button>`;
          });
        });
        $("#model-table-body").append(`
          <tr id="${modelData.name}">
            <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap hover:bg-gray-300 cursor-pointer" onclick="window.location.href='${modelData.url}'">
              ${modelData.name}
            </td>
            <td class="px-6 py-4">${fieldsContent || "N/A"}</td>
            <td class="px-6 py-4">${relationsContent || "N/A"}</td>
          </tr>
`);
      }

      window.fetchRelatedModel = function (modelName, btnElement) {

      $(btnElement).closest('td').find('button').each(function() {
        if ($(this).attr('name') == 'reverse') {
          $(this).css('color', '#983412').css('background-color', '#ffedd5');
        } else {
          $(this).css('color', '#166534').css('background-color', '#dcfce7');
        }
        });

        $(btnElement).css('color', 'white').css('background-color', '#f916d6');

        let currentRow = $(btnElement).closest("tr");
        currentRow.nextAll("tr").remove();

        $.ajax({
          url: '{% url "ajax-call" %}',
          data: {
            model: modelName,
          },
          success: function (response) {
            const modelData = response.data;
            if (modelData) {
            appendModelRow(modelData);
            displayedModels.add(modelData.name);
            }
          },
          error: function (xhr, status, error) {
            console.error(`Error fetching data for model ${modelName}: ${error}`);
          },
        });
      };

      window.CopyRelationsPath = function(){
        const list_of_elemenets = [];
        elements = $('#model-table-body').children();
        $.each(elements, function(index, element){
          list_of_elemenets.push(element.id)
        });
        console.log(list_of_elemenets)

        $.ajax({
          url: '{% url "AZVTNbMJfPHKWIorjAIz" %}',
          data: {
            list: JSON.stringify(list_of_elemenets),
          },
          success: function (response) {
            $('#path_input').val(response.path);
            navigator.clipboard.writeText(response.path);
            showSuccessMessage();
          },
          error: function (xhr, status, error) {
            console.error(`Error finding relation for model ${list_of_elemenets}`);
          },
        });
      };
      function showSuccessMessage() {
        $("#default-message").addClass("hidden");
        $("#success-message").removeClass("hidden");
        setTimeout(() => {
          $("#default-message").removeClass("hidden");
          $("#success-message").addClass("hidden");
        }, 2000);
      }
      });
    </script>
  </body>
</html>

        """

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
    
    model_info = {
        "name": model.__name__,
        "fields": {},
        "relations": {"other": [], "set": []},
        "url": f"vscode://file/{field_url}:{line_number}"
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

                if isinstance(field, (ManyToOneRel, OneToOneRel, ManyToManyRel)):
                    model_info["relations"]["set"].append(relation_info)
                else:
                    model_info["relations"]["other"].append(relation_info)

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