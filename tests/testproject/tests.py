import os
from django.test import TestCase
from django.contrib.auth.models import User

from testproject import models

def img_dir():
    return os.path.join(os.path.dirname(__file__), 'media', 'img')

class TestStdImage(TestCase):
    def setUp(self):
        user = User.objects.create_superuser('admin', 'admin@email.com',
                                             'admin')
        user.save()
        self.client.login(username='admin', password='admin')

        self.fixtures = {}
        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        fixture_paths = os.listdir(fixtures_dir)
        for fixture_filename in fixture_paths:
            fixture_path = os.path.join(fixtures_dir, fixture_filename)
            if os.path.isfile(fixture_path):
                content = None
                self.fixtures[fixture_filename] = open(fixture_path, 'rb')

    def tearDown(self):
        """Close all open fixtures and delete everything from media"""
        for fixture in self.fixtures.values():
            fixture.close()

        for root, dirs, files in os.walk(img_dir(), topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

class TestWidget(TestStdImage):
    """ Functional mostly """

    def test_simple(self):
        """ Upload an image using the admin interface """
        self.client.post('/admin/testproject/simplemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertEqual(models.SimpleModel.objects.count(), 1)

    def test_empty_fail(self):
        """ Will raise an validation error and will not add an intance """
        self.client.post('/admin/testproject/simplemodel/add/', {})
        self.assertEqual(models.SimpleModel.objects.count(), 0)

    def test_empty_success(self):
        """ AdminDeleteModel has blan=True and will add an instance of the
        Model

        """
        self.client.post('/admin/testproject/admindeletemodel/add/', {})
        self.assertEqual(models.AdminDeleteModel.objects.count(), 1)

    def test_uploaded(self):
        """ Test simple upload """
        self.client.post('/admin/testproject/simplemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertTrue(os.path.exists(os.path.join(img_dir(), 'image_1.gif')))

    def test_delete(self):
        """ Test if an image can be deleted """

        self.client.post('/admin/testproject/admindeletemodel/add/', {
            'image': self.fixtures['100.gif']
        })
        #delete
        res = self.client.post('/admin/testproject/admindeletemodel/1/', {
            'image_delete': 'checked'
        })
        self.assertFalse(os.path.exists(os.path.join(img_dir(),
                                                     'image_1.gif')))

    def test_thumbnail(self):
        """ Test if the thumbnail is there """

        self.client.post('/admin/testproject/thumbnailmodel/add/', {
            'image': self.fixtures['100.gif']
        })
        self.assertTrue(os.path.exists(os.path.join(img_dir(), 'image_1.gif')))
        self.assertTrue(os.path.exists(os.path.join(img_dir(),
                                                    'image_1.thumbnail.gif')))

    def test_delete_thumbnail(self):
        """ Delete an image with thumbnail """

        self.client.post('/admin/testproject/thumbnailmodel/add/', {
            'image': self.fixtures['100.gif']
        })

        #delete
        self.client.post('/admin/testproject/thumbnailmodel/1/', {
            'image_delete': 'checked'
        })
        self.assertFalse(os.path.exists(os.path.join(img_dir(),
                                                     'image_1.gif')))
        self.assertFalse(os.path.exists(os.path.join(img_dir(),
                                                    'image_1.thumbnail.gif')))
