from django.contrib import admin


class SummaryAdmin(admin.ModelAdmin):
    change_list_template = 'django_summary_admin/summary_change_list.html'

    def get_summary(self, queryset):
        return None

    def changelist_view(self, request, extra_context=None):
        view = super().changelist_view(request, extra_context)
        try:
            view.context_data['summary'] = self.get_summary(view.context_data['cl'].queryset)
        except KeyError:
            pass
        except AttributeError:
            pass
        return view
