# 🔗 LinkIt

LinkIt gives you a new field type `LinkField` to use on your models which allows you to effortlessly link to different models on your site. This could be a django-cms Page model,
a filer File or anything custom like a News model.

<img src="https://github.com/dreipol/linkit/raw/master/doc/linkit.gif"/>

## Installation 
Install the latest version with pip and add `linkit` to your `INSTALLED_APPS` - and you're good to go.

    $ pip install LinkIt

## Usage    
You're now able to use the new `LinkField` on any of your models:

```python
from django.db.models import Model, CharField
from linkit.model_fields import LinkField

class Foo(Model):
    title = CharField(max_length=255)
    link = LinkField(types=['page', 'file', 'input'])  # <-- Yay!
```

If you register this model in django admin you'll get a dropdown field where you can choose between cms pages, filer files or just a plain input field. 
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
Out of the Box LinkIt ships with three types: input, file, page. The `LinkType` base class makes it easy to implement your own link type, whatever
it may be. If you want to link to another existing model in your app, e.g. News, all you need to do is register a new link type.

1. Create a file `link_types.py` in any of your apps:

```python
from linkit.types.model import ModelLinkType


class NewsLinkType(ModelLinkType):
    identifier = 'news'
    type_label = 'News'
    model = News

```

2. Register the new type, preferably in an `AppConfig` `ready` method:

````python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentConfig(AppConfig):
    name = 'contents'

    def ready(self):
        from contents.link_types import NewsLinkType
        from linkit.types import type_manager as linkit_manager


        linkit_manager.register(NewsLinkType)
````

3. Profit! You can now create a field like this on any of your models: `link = LinkField(types=['news', 'page])` and link to any of your news or cms pages.

Check `linkit/types` to see how the core types are implemented.

### EmailType example
Say we have a totally different new type we want to implement and can't just extend from the `ModelLinkType`. See the example bellow
of a link type used to link to e-mail addresses with an optional subject field.

````python
class EmailTypeForm(TypeForm):
    address = EmailField(label='E-Mail', required=True)
    subject = CharField(label='Subject', required=False, max_length=20)


class EmailType(LinkType):
    identifier = 'email'
    type_label = 'E-Mail'
    form_class = EmailTypeForm

    def real_value(self):
        return self.link.data('value')

    @property
    def href(self) -> Optional[str]:
        mail = self.real_value().get('address')
        subject = self.real_value().get('subject', '')

        return f'mailto:{mail}?subject={subject}'

    @property
    def label(self) -> Optional[str]:
        return self.real_value().get('address')
````
