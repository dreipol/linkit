# 🔗 LinkIt

LinkIt gives you a new field type `LinkField` to use on your models which allows you to effortlessly link to different models on your site. This could be a django-cms Page model,
a filer File or anything custom like a News model.

## Installation 
Install the latest version with pip and you're good to go.

    $ pip install linkit

## Usage    
You're now able to use the new `LinkField` on any of your models:

```python
from django.db.models import Model, CharField
from linkit.model_fields import LinkField

class Foo(Model):
    title = CharField(max_length=255)
    link = LinkField(types=['page', 'file', 'input'])  # <-- Yay!
```

If you register this model in django admin you'll get a dropdown field where yru can choose between cms pages, filer files or just a plain input field. 
Your model is now able to link to any of these entities with one single field.  

In a template you could use this link field like this:
````html
<a href="{{ instance.link.href }}" target="{{ instance.link.target }}">{{ instance.link.label }}</a>
````
    
## Configuration
The `LinkField` takes some options which will define how the rendered widget looks and what options the content editor has:

- `types: list = None` Defines which link types are allowed (see more bellow in the section «Types») 
- `allow_target: bool = False` If set to true, the widget renders a checkbox so the editor can choose the `_target` of the link  
- `allow_label: bool = True` Renders an additonal input field so a custom label can be set
- `allow_no_follow: bool = False` If set to true, the widget renders a checkbox so the editor can choose the `rel="nofollow"` for the link  

## Types
Out of the Box LinkIt ships with three types: link, file, page. The `LinkType` base class makes it easy to implement your own link type, whatever
it may be. If you want to link to another existing model in your app, e.g. News, all you need to do is register a new link type.

1. Create a file `link_types.py` in any of your apps:

```python
from linkit.types import ModelLinkType

class NewsLinkType(ModelLinkType):
    identifier = 'news'
    type_label = 'News'
    model = YourNewsModel
```

2. Register the new type, preferably in a `AppConfig` `ready` method:

````python
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ContentConfig(AppConfig):
    name = 'contents'

    def ready(self):
        from contents.link_types import NewsLinkType
        from linkit.types import type_manager as linkit_manager

        linkit_manager.register(NewsLinkType)
````

3. Profit! You can now create a field like this on any of your models: `link = LinkField(types=['news', 'page])` and link to any of your news or cms pages.

Check `linkit/types.py` to see how the core types are implemented.
