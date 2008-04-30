from django.db.models.fields import ImageField
from django.dispatch import dispatcher
from django.db.models import signals
from django.conf import settings
from widgets import DelAdminFileWidget
from forms import StdImageFormField
import os, shutil

class StdImageField(ImageField):
	'''
	'''
	def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, size=None, thumbnail_size=None, **kwargs):
		'''
		Added fields:
			- size: a tuple containing width and height to resize image, and an optional boolean setting if is wanted forcing that size (None for not resizing).
				* Example: (640, 480, True) -> Will resize image to a width of 640px and a height of 480px. File will be cutted if necessary for forcing te image to have the desired size
			- thumbnail_size: a tuple with same values than `size' (None for not creating a thumbnail 
		'''
		params_size = ('width', 'height', 'force')
		for att_name, att in {'size': size, 'thumbnail_size': thumbnail_size}.items():
			if att and (isinstance(att, tuple) or isinstance(att, list)):
				setattr(self, att_name, dict(map(None, params_size, att)))
			else:
				setattr(self, att_name, None)
		super(StdImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

	def _get_thumbnail_filename(self, filename):
		splitted_filename = list(os.path.splitext(filename))
		splitted_filename.insert(1, '.thumbnail')
		return ''.join(splitted_filename)

	def _resize_image(self, filename, size):
		WIDTH, HEIGHT = 0, 1
		from PIL import Image
		img = Image.open(filename)
		if size['force']:
			ratio = lambda t: float(t[1]) / float(t[0])
			if ratio((size['width'], size['height'])) > ratio(img.size):
				x, y = float(img.size[WIDTH]) / img.size[HEIGHT] * size['height'], size['height']
				pos_x, pos_y = float(x - size['width']) / 2, 0
			else:
				x, y = size['width'], float(img.size[HEIGHT]) / img.size[WIDTH] * size['width']
				pos_x, pos_y = 0, float(y - size['height']) / 2
			# don't do anything if image already has desired size
			img = img.resize((int(x), int(y)), Image.ANTIALIAS)
			img = img.crop((int(pos_x), int(pos_y), int(pos_x + size['width']), int(pos_y + size['height'])))
		else:
			img.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
		img.save(filename)

	def _rename_resize_image(self, instance=None):
		filename = getattr(instance, 'get_%s_filename' % self.name)()
		if filename:
			ext = os.path.splitext(filename)[1].lower().replace('jpg', 'jpeg')
			dst = '%s/%s_%s%s' % (self.upload_to, self.name, instance._get_pk_val(), ext)
			dst_fullpath = os.path.join(settings.MEDIA_ROOT, dst)
			if filename != dst_fullpath:
				os.rename(filename, dst_fullpath)
				if self.size:
					self._resize_image(dst_fullpath, self.size)
				if self.thumbnail_size:
					thumbnail_filename = self._get_thumbnail_filename(dst_fullpath)
					shutil.copyfile(dst_fullpath, thumbnail_filename)
					self._resize_image(thumbnail_filename, self.thumbnail_size)
				setattr(instance, self.attname, dst)
				instance.save()

	def _set_thumbnail(self, instance=None):
		filename = getattr(instance, self.name)
		thumbnail_filename = self._get_thumbnail_filename(filename)
		setattr(instance, '%s_thumbnail' % self.attname, thumbnail_filename)

	def formfield(self, **kwargs):
		kwargs['widget'] = DelAdminFileWidget
		kwargs['form_class'] = StdImageFormField
		return super(StdImageField, self).formfield(**kwargs)

	def save_form_data(self, instance, data):
		if data == '__deleted__':
			filename = getattr(instance, 'get_%s_filename' % self.name)()
			if os.path.exists(filename):
				os.remove(filename)
			thumbnail_filename = self._get_thumbnail_filename(filename)
			if os.path.exists(thumbnail_filename):
				os.remove(thumbnail_filename)
			setattr(instance, self.name, None)
		else:
			super(StdImageField, self).save_form_data(instance, data)

	def get_db_prep_save(self, value):
		if value:	
			return super(StdImageField, self).get_db_prep_save(value)
		else:
			return u''

	def contribute_to_class(self, cls, name):
		super(StdImageField, self).contribute_to_class(cls, name)
		dispatcher.connect(self._rename_resize_image, signals.post_save, sender=cls)
		dispatcher.connect(self._set_thumbnail, signals.post_init, sender=cls)

