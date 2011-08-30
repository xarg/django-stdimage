# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class DelAdminFileWidget(AdminFileWidget):
    """An AdminFileWidget that shows a delete checkbox"""
    input_type = 'file'

    def render(self, name, value, attrs=None):
        input = super(forms.widgets.FileInput, self).render(name, value, attrs)
        if value and hasattr(value, 'field'):
            return mark_safe(render_to_string('stdimage/admin_widget.html', {
                'name': name,
                'value': value,
                'input': input,
                'show_delete_button': value.field.blank,
                'MEDIA_URL': settings.MEDIA_URL,
            }))
        else:
            return mark_safe(input)

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(DelAdminFileWidget, self).\
                            value_from_datadict(data, files, name)
        else:
            return '__deleted__'
