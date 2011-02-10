import os
from django.test import TestCase
from django.contrib.auth.models import User

from testproject import models

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

        img_dir = os.path.join(os.path.dirname(__file__), 'media', 'img')
        for root, dirs, files in os.walk(img_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

class TestWidget(TestStdImage):
    """ Functional mostly """

    def test_simple(self):
        """ Upload an image using the admin interface """
        data = {
            'image': self.fixtures['100.gif']
        }
        res = self.client.post('/admin/testproject/simplemodel/add/', data)
        self.assertEqual(models.SimpleModel.objects.count(), 1)

    def test_empty_fail(self):
        """ Will raise an validation error and will not add an intance """
        res = self.client.post('/admin/testproject/simplemodel/add/', {})
        self.assertEqual(models.SimpleModel.objects.count(), 0)

    def test_empty_success(self):
        """ AdminDeleteModel has blan=True and will add an instance of the
        Model

        """
        res = self.client.post('/admin/testproject/admindeletemodel/add/', {})
        self.assertEqual(models.AdminDeleteModel.objects.count(), 1)

    def test_uploaded(self):
        data = {
            'image': self.fixtures['100.gif']
        }
        res = self.client.post('/admin/testproject/simplemodel/add/', data)
        import pdb; pdb.set_trace()

    def test_delete(self):
        """ """
        #data = {
        #    'image': self.fixtures['100.gif']
        #}
        #res = self.client.post('/admin/testproject/simplemodel/add/', data)
        #res = self.client.post('/admin/testproject/simplemodel/add/', data)
