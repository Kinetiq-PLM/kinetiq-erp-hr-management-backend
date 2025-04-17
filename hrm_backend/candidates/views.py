from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Candidate
from .serializers import (
    Candidate_Serializer,
    Candidate_CreateSerializer,
    Resume_Upload_Serializer,
    Document_Verification_Serializer,
    Interview_Add_Serializer,
    Offer_Update_Serializer,
    Contract_Sign_Serializer,
)

class Candidate_ViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = Candidate_Serializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Candidate_CreateSerializer
        elif self.action == 'upload_resume':
            return Resume_Upload_Serializer
        elif self.action == 'verify_documents':
            return Document_Verification_Serializer
        elif self.action == 'add_interview':
            return Interview_Add_Serializer
        elif self.action == 'update_offer':
            return Offer_Update_Serializer
        elif self.action == 'sign_contract':
            return Contract_Sign_Serializer
        return Candidate_Serializer

    @action(detail = True, methods = ['patch'], url_path = 'upload_resume')
    def upload_resume(self, request, pk = None):
        candidate = self.get_object()

        directory = request.data.get('directory', 'Human_Resource_Management/Candidates/Resumes')
        file = request.FILES.get('file')

        if not file:
            return Response({'detail': 'File not provided'}, status = status.HTTP_400_BAD_REQUEST)

        api_url = 'https://s9v4t5i8ej.execute-api.ap-southeast-1.amazonaws.com/dev/api/upload-to-s3/'
        response = requests.post(api_url, data={'directory': directory})

        if response.status_code != 200:
            return Response({'detail': 'Failed to generate pre-signed URL'}, status = status.HTTP_400_BAD_REQUEST)

        data = response.json()
        upload_url = data.get('uploadUrl')
        file_url = data.get('fileUrl')

        if not upload_url or not file_url:
            return Response({'detail': 'Failed to get valid URLs from S3 API'}, status = status.HTTP_400_BAD_REQUEST)

        files = {'file': (file.name, file.read(), file.content_type)}
        upload_response = requests.post(upload_url, files = files)

        if upload_response.status_code == 200:
            documents = candidate.documents or {}
            required_docs = documents.get('required', {})
            required_docs['resume'] = {
                'path': file_url,
                'verified': False
            }
            documents['required'] = required_docs
            candidate.documents = documents
            candidate.save()

            return Response({
                'detail': 'Resume uploaded successfully!',
                'file_url': file_url
            }, status = status.HTTP_200_OK)
        else:
            return Response({'detail': 'Failed to upload file to S3'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail = True, methods = ['patch'], url_path = 'update_resume')
    def update_resume(self, request, pk = None):
        candidate = self.get_object()
        file_url = request.data.get('file_url')

        if not file_url:
            return Response({'detail': 'Missing file_url'}, status = 400)

        documents = candidate.documents or {}
        required_docs = documents.get('required', {})
        required_docs['resume'] = {
            'path': file_url,
            'verified': False
        }
        documents['required'] = required_docs
        candidate.documents = documents
        candidate.save()

        return Response({'detail': 'Resume uploaded successfully', 'documents': candidate.documents})

    @action(detail = True, methods = ['patch'], url_path = 'verify-documents')
    def verify_documents(self, request, pk = None):
        candidate = self.get_object()
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        candidate.documents = serializer.validated_data['documents']
        candidate.save()
        return Response({'message': 'Documents verified'}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['patch'], url_path = 'add-interview')
    def add_interview(self, request, pk = None):
        candidate = self.get_object()
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        interviews = candidate.interview_details or []
        interviews.extend(serializer.validated_data['interview_details'])
        candidate.interview_details = interviews
        candidate.save()
        return Response({'message': 'Interview(s) added'}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['patch'], url_path = 'update-offer')
    def update_offer(self, request, pk = None):
        candidate = self.get_object()
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        candidate.offer_details = serializer.validated_data['offer_details']
        candidate.save()
        return Response({'message': 'Offer details updated'}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['patch'], url_path = 'sign-contract')
    def sign_contract(self, request, pk = None):
        candidate = self.get_object()
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        candidate.contract_details = serializer.validated_data['contract_details']
        candidate.save()
        return Response({'message': 'Contract signed'}, status = status.HTTP_200_OK)