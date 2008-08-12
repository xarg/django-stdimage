from django.db.models.fields.files import ImageField
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
        if img.size[0] > size['width'] or img.size[1] > size['height']:
            if size['force']:
                target_height = float(size['height'] * img.size[WIDTH]) / size['width']
                if target_height < img.size[HEIGHT]: # Crop height
                    crop_side_size = int((img.size[HEIGHT] - target_height) / 2)
                    img = img.crop((0, crop_side_size, img.size[WIDTH], img.size[HEIGHT] - crop_side_size))
                elif target_height > img.size[HEIGHT]: # Crop width
                    target_width = float(size['width'] * img.size[HEIGHT]) / size['height']
                    crop_side_size = int((img.size[WIDTH] - target_width) / 2)
                    img = img.crop((crop_side_size, 0, img.size[WIDTH] - crop_side_size, img.size[HEIGHT]))
            img.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
            try:
                img.save(filename, optimize=1)
            except IOError:
                img.save(filename)

    def _rename_resize_image(self, instance=None, **kwargs):
        if getattr(instance, self.name):
            filename = getattr(instance, self.name).path
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

    def _set_thumbnail(self, instance=None, **kwargs):
        if getattr(instance, self.name):
            filename = getattr(instance, self.name).path
            thumbnail_filename = self._get_thumbnail_filename(filename)
            setattr(instance, '%s_thumbnail' % self.attname, thumbnail_filename)

    def formfield(self, **kwargs):
        kwargs['widget'] = DelAdminFileWidget
        kwargs['form_class'] = StdImageFormField
        return super(StdImageField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        if data == '__deleted__':
            filename = getattr(instance, self.name).path
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
        signals.post_save.connect(self._rename_resize_image, sender=cls)
        signals.post_init.connect(self._set_thumbnail, sender=cls)

