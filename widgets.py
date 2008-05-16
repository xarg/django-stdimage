from django.contrib.admin.widgets import AdminFileWidget
from django import newforms as forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings

class DelAdminFileWidget(AdminFileWidget):
    '''
    A AdminFileWidget that shows a delete checkbox
    '''
    input_type = 'file'

    def render(self, name, value, attrs=None):
        valuetype = type(value)
        error = not isinstance(value, unicode)
        output = []
        if not error and value:
            output.append('%s <a target="_blank" href="%s%s">%s</a> <br />%s ' % \
                (_('Currently:'), settings.MEDIA_URL, value, value, _('Change:')))

        output.append(super(forms.widgets.FileInput, self).render(name, value, attrs))

        #output = [super(DelAdminFileWidget, self).render(name, value, attrs)]
        if not error and value: # TODO condition should include if field is required
            output.append('<br/>%s: <input type="checkbox" name="%s_delete"/>' % (_('Delete'), name))
        return mark_safe(u''.join(output))

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(DelAdminFileWidget, self).value_from_datadict(data, files, name)
        else:
            return '__deleted__'

