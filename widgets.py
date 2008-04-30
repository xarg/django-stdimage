from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

class DelAdminFileWidget(AdminFileWidget):
	'''
	A AdminFileWidget that shows a delete checkbox
	'''
	def render(self, name, value, attrs=None):
		output = []
		output.append(super(DelAdminFileWidget, self).render(name, value, attrs))
		if value:
			output.append('<br/>%s <input type="checkbox" name="%s_delete"/>' % (_('Delete:'), name))
		return mark_safe(u''.join(output))

	def value_from_datadict(self, data, files, name):
		if not data.get('%s_delete' % name):
			return super(DelAdminFileWidget, self).value_from_datadict(data, files, name)
		else:
			return '__deleted__'

