from django.db import models
from filer.fields.file import FilerFileField


class FakeLink(models.Model):
    """
    In our widget we need to manually render a AdminFileFormField. Basically for every other Field type this is not
    a problem at all, but Failer needs a rel attribute which consists of a reverse relationship. We fake it
    with this model.
    """
    fake_file = FilerFileField(blank=True, null=True, on_delete=models.CASCADE)
