
# django-model-viewer

An application that facilitates identification and operation on models. 

It searches for all available models in the project and allows you to select and view details about them by holding the mouse on the parameter of interest. 

After selecting the path between models through relations, after clicking CREATE we will get a path that allows you to get to the last model. 

It is also possible to select a model and click on its name and it will take you to Visual Studio Code to the file and line of the given model.


## Installation



```bash
  pip install django-model-viewer
```

Open your project settings and add:

```py
INSTALLED_APPS = [
    ***
    'django_model_viewer',
    ***
]

MIDDLEWARE = [
    ***
    'django_model_viewer.middleware.AppendApplication',
    ***
]
```

Add path to main urls file

```py
urlpatterns = [
    path('models-view/', include('django_model_viewer.urls')),
    ***
]
```

### Run server and use at '/models-view' url
    
## Authors

- self

