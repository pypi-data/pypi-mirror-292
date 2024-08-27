## Django Summery Admin

Using summaries for totals in Django admin

### Installation:

```shell
pip install -i django-summary-admin
```
```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_summary_admin',
    ...
]
```

### Usage:

```python
# admin.py
from django.db import models

from django_summary_admin.admin import SummaryAdmin


class MyModelAdmin(SummaryAdmin):
    fields = [
        'description',
        'total', # Same name in aggregate
    ]
    
    def get_summary(self, queryset):
        return queryset.aggregate(total=models.Sum('value'))
```

