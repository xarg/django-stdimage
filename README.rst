Django Standarized Image Field
==============================

Django Field that implement those features:

 * Rename files to a standardized name (using object id)
 * Resize images for that field
 * Automatically creates a thumbnail (resizing it)
 * Allow image deletion

Installation
------------

    Install latest PIL - there is really no reason to use this package without it

    easy_install django-stdimage

    Put 'stdimage' in the INSTALLED_APPS

Usage
-----

Import it in your project, and use in your models.

Example::

    [...]
    from stdimage import StdImageField

    class MyClass(models.Model):
        image1 = StdImageField(upload_to='path/to/img') # works as ImageField
        image2 = StdImageField(upload_to='path/to/img', blank=True) # can be deleted throwgh admin
        image3 = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 75)}) # creates a thumbnail resized to maximum size to fit a 100x75 area
        image4 = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 100, True}) # creates a thumbnail resized to 100x100 croping if necessary

        image_all = StdImageField(upload_to='path/to/img', blank=True, variations={'large': (640, 480), 'thumbnail': (100, 100, True)}) # all previous features in one declaration

For using generated thumbnail in templates use "myimagefield.thumbnail". Example::

    [...]
    <a href="{{ object.myimage.url }}"><img alt="" src="{{ object.myimage.thumbnail.url }}"/></a>
    [...]

About image names
-----------------

StdImageField stores images in filesystem modifying its name. Renamed name is set using field name, and object primary key. Also it changes old windows "jpg" extesions to standard "jpeg".

Using `image_all` field previously defined (that creates a thumbnail), if an image called myimage.jpg is uploaded, then resulting images on filesystem would be (supose that this image belongs to a model with pk 14)::

    image_all_14.jpeg
    image_all_14.large.jpeg
    image_all_14.thumbnail.jpeg
