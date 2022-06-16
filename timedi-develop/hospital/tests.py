from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from hospital import viewsets


class TestHospital(APITestCase):

    fixtures = ['db']

    def setUp(self):
        # ...
        self.user = self.setup_user()
        self.factory = APIRequestFactory()

    @staticmethod
    def setup_user():
        User = get_user_model()
        return User.objects.get(username='admin')

    def crud(self, uri, view, action, obj_id=None, data=None):

        if action == 'list':
            request = self.factory.get(uri)
            force_authenticate(request, user=self.user)
            response = view(request)
            print("-------------->", action, response.data)
            self.assertEqual(response.status_code, 200,
                             'Expected Response Code 200, received {0} instead.'
                             .format(response.status_code))

        elif action == 'retrieve':
            request = self.factory.get(uri + obj_id)
            force_authenticate(request, user=self.user)
            response = view(request, pk=obj_id)
            print("-------------->", action, response.data)
            self.assertEqual(response.status_code, 200,
                             'Expected Response Code 200, received {0} instead.'
                             .format(response.status_code))

        elif action == 'create':
            request = self.factory.post(uri, data=data)
            force_authenticate(request, user=self.user)
            response = view(request)
            print("-------------->", action, response.data)

            self.assertEqual(response.status_code, 201,
                             'Expected Response Code 201, received {0} instead.'
                             .format(response.status_code))

        elif action == 'update':
            request = self.factory.put(uri + obj_id, data=data)
            force_authenticate(request, user=self.user)
            response = view(request, pk=obj_id)
            print("-------------->", action, response.data)

            self.assertEqual(response.status_code, 200,
                             'Expected Response Code 200, received {0} instead.'
                             .format(response.status_code))

        elif action == 'destroy':
            request = self.factory.delete(uri + obj_id)
            force_authenticate(request, user=self.user)
            response = view(request, pk=obj_id)
            print("-------------->", action, response)

            self.assertEqual(response.status_code, 204,
                             'Expected Response Code 204, received {0} instead.'
                             .format(response.status_code))

    def test_crud_hospital(self):

        view = viewsets.HospitalViewSet.as_view({'get': 'retrieve',
                                                 'post': 'create',
                                                 'put': 'update',
                                                 'delete': 'destroy'})
        uri = '/hospital/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='2')
        create_data = {
            "hospital_name": "NeoHospital"
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "applications": [],
            "patient_assign_modules": [],
            "hospital_image": "",
            "assign_centre_modules": [],
            "phone_number": "",
            "hospital_address": "",
            "postal_code": "",
            "contact_person": "",
            "is_active": True,
            "hospital_name": "NeoHosp"
        }
        self.crud(uri=uri, view=view, action='update', obj_id='4', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='4')

    def test_list_hospital(self):
        uri = '/hospitals/'
        view = viewsets.HospitalListViewSet.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')

    def test_crud_production_setting(self):
        view = viewsets.ProductionSettingViewset.as_view({'get': 'retrieve',
                                                          'post': 'create',
                                                          'put': 'update',
                                                          'delete': 'destroy'})
        uri = '/production-setting/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='2')
        create_data = {
            "hospital": '3',
            "produce_external_treatment": True,
            "produce_treatment_if_needed": True,
            "produce_treatment_in_variable_dosage": True
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "hospital": '3',
            "produce_external_treatment": True,
            "produce_treatment_if_needed": False,
            "produce_treatment_in_variable_dosage": True
        }
        self.crud(uri=uri, view=view, action='update', obj_id='3', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='3')

    def test_list_production_setting(self):

        uri = '/production-setting/'
        view = viewsets.ProductionSettingViewset.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')

    def test_crud_hospital_stock_management(self):
        view = viewsets.HospitalStockManagementViewset.as_view({'get': 'retrieve',
                                                                'post': 'create',
                                                                'put': 'update',
                                                                'delete': 'destroy'})
        uri = '/stock-management/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='2')
        create_data = {
            "codes_to": 7,
            "hospital": 3,
            "codes_from": 5,
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "codes_to": 80,
            "hospital": 3,
            "codes_from": 20,
        }
        self.crud(uri=uri, view=view, action='update', obj_id='3', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='3')

    def test_list_hospital_stock_management(self):

        uri = '/stock-management/'
        view = viewsets.HospitalStockManagementViewset.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')

    def test_crud_intermediate_production(self):
        view = viewsets.IntermediateProductionViewSet.as_view({'get': 'retrieve',
                                                               'post': 'create',
                                                               'put': 'update',
                                                               'delete': 'destroy'})
        uri = '/intermediate-productions/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='2')
        create_data = {
            "hospital": 1,
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "produce_external_treatment": True,
            "produce_treatment_if_needed": True,
            "hospital": 1,
            "produce_treatment_in_variable_dosage": False
        }
        self.crud(uri=uri, view=view, action='update', obj_id='3', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='3')

    def test_list_intermediate_production(self):

        uri = '/intermediate-productions/'
        view = viewsets.IntermediateProductionViewSet.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')