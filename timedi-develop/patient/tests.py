from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from patient import viewsets


class TestPatient(APITestCase):
    fixtures = ['db']

    def setUp(self):
        self.user = self.setup_user()
        self.factory = APIRequestFactory()

    @staticmethod
    def setup_user():
        User = get_user_model()
        return User.objects.get(username='neosoft')

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

    def test_crud_patient(self):

        view = viewsets.PatientViewSet.as_view({'get': 'retrieve',
                                                'post': 'create',
                                                'put': 'update',
                                                'delete': 'destroy'})
        uri = '/patient/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='170c15ea-f045-4dc7-a573-6c1f6ad3b577')
        create_data = {
            "status": "active",
            "first_name": "Pooja",
            "last_name": "Patel",
            "label_printing": "Pooja ManePatel",
            "hospital": "e06c336e-a3b1-49c2-9d50-4573ccdd5f59",
            "applications": [],
            "assign_centre_module": "cf252902-ce8f-4756-ab6a-a25c342f4912"
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "status": "active",
            "first_name": "ajay",
            "last_name": "Naveen",
            "label_printing": "Naveen Patel",
            "profile": "sfsdfdsf",
            "room_number": "2",
            "ss_id": "ss12",
            "assign_centre_module": "lhljsakjh",
            "doctor_name": "Dr. Diksha",
            "hospital": "e06c336e-a3b1-49c2-9d50-4573ccdd5f59",
            "date_of_birth": "2020-04-03",
            "DNI": "12",
            "location": "Indore",
            "postal_code": 455001,
            "patient_id": "patient_id",
            "address": "221, ram nagar indore",
            "contact_person": "Mr. Naveen Patel",
            "telephone_1": 8817446991,
            "telephone_2": 8319462105,
            "registration_date": "2020-04-03",
            "reason": "symptoms of corona",
            "blister_responsible": "blood",
            "assign_centre_module": "cf252902-ce8f-4756-ab6a-a25c342f4912",
            "applications": []
        }
        self.crud(uri=uri, view=view, action='update', obj_id='170c15ea-f045-4dc7-a573-6c1f6ad3b577', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='170c15ea-f045-4dc7-a573-6c1f6ad3b577')

    def test_list_patient(self):
        uri = '/patients/'
        view = viewsets.PatientListViewSet.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')

    def test_crud_patient_absence_reason(self):
        view = viewsets.AbsenceReasontViewSet.as_view({'get': 'retrieve',
                                                       'post': 'create',
                                                       'put': 'update',
                                                       'delete': 'destroy'})
        uri = '/absence-reason/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='4ba812be-8e02-4e25-b037-62bc71b76eab')
        create_data = {
            "reason": "tonsils with corona effe",
            "release_date": "2020-04-05",
            "patient": "170c15ea-f045-4dc7-a573-6c1f6ad3b577"
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "reason": "tonsils with corona effect",
            "release_date": "2020-04-03",
            "no_return_date": True,
            "patient": "170c15ea-f045-4dc7-a573-6c1f6ad3b577"
        }
        self.crud(uri=uri, view=view, action='update', obj_id='4ba812be-8e02-4e25-b037-62bc71b76eab', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='4ba812be-8e02-4e25-b037-62bc71b76eab')

    def test_list_absence_reason(self):
        uri = '/absence-reason/'
        view = viewsets.AbsenceReasontViewSet.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')

    def test_crud_patient_intermediate_production(self):
        view = viewsets.PatientIntermediateProductionViewSet.as_view({'get': 'retrieve',
                                                                      'post': 'create',
                                                                      'put': 'update',
                                                                      'delete': 'destroy'})
        uri = '/intermediate-productions/'
        self.crud(uri=uri, view=view, action='retrieve', obj_id='72232474-2099-42e5-b90b-7b1bccb15fcc')
        create_data = {
            "days": [
                "tuesday",
                "wednesday"
            ],
            "intake_moments": [],
            "daysFlag": True,
            "floors": [],
            "medicines": [
                "paracetmol",
                "deoflam"
            ],
            "time": ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
                     "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                     "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
                     "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
                     "22:00", "22:30", "23:00", "23:30"],
            "production_type": "patient",
            "setting_applied_to": "floors",
            "patient": "170c15ea-f045-4dc7-a573-6c1f6ad3b577"
        }
        self.crud(uri=uri, view=view, action='create', data=create_data)
        update_data = {
            "days": [
                "tuesday",
                "wednesday"
            ],
            "intake_moments": [],
            "daysFlag": True,
            "floors": [],
            "medicines": [
                "paracetmol",
                "deoflam"
            ],
            "time": ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
                     "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                     "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
                     "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
                     "22:00", "22:30", "23:00", "23:30"],
            "production_type": "patient",
            "setting_applied_to": "floors",
            "patient": "170c15ea-f045-4dc7-a573-6c1f6ad3b577"
        }
        self.crud(uri=uri, view=view, action='update', obj_id='72232474-2099-42e5-b90b-7b1bccb15fcc', data=update_data)
        self.crud(uri=uri, view=view, action='destroy', obj_id='72232474-2099-42e5-b90b-7b1bccb15fcc')

    def test_list_intermediate_productions(self):
        uri = 'intermediate-productions'
        view = viewsets.PatientIntermediateProductionViewSet.as_view({'get': 'list'})
        self.crud(uri=uri, view=view, action='list')
