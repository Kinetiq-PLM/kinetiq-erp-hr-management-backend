from rest_framework import (
    viewsets,
    permissions,
    status
)
from .serializers import (
    Candidate_Serializer,
    Candidate_CreateSerializer,
    DocumentSerializer,
    # InterviewDetailSerializer,
    # OfferDetailSerializer,
    # ContractDetailSerializer
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import Candidate
import json

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('job_postings.view_job_posting'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    lookup_field = 'candidate_id'
    # permission_classes = [IsAuthenticated, IsHRMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Candidate_CreateSerializer
        return Candidate_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail = True, methods = ['patch'], url_path = 'upload-resume')
    def upload_resume(self, request, candidate_id = None):
        candidate = self.get_object()
        resume_path = request.data.get("resume_path")
        if resume_path:
            candidate.resume_path = resume_path
            candidate.save()
            return Response({"message": "Resume uploaded."})
        return Response({"error": "Missing resume_path."}, status=status.HTTP_400_BAD_REQUEST)
 
    # @action(detail = True, methods = ['patch'], url_path = 'add-interview')
    # def add_interview(self, request, candidate_id = None):
    #     candidate = self.get_object()
    #     serializer = InterviewDetailSerializer(data = request.data)
    #     if serializer.is_valid():
    #         current = candidate.interview_details or []
    #         current.append(serializer.validated_data)
    #         candidate.interview_details = current
    #         candidate.save()
    #         return Response(InterviewDetailSerializer(serializer.validated_data).data)
    #     return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    # @action(detail = True, methods = ['get'], url_path = 'interviews')
    # def view_interviews(self, request, candidate_id = None):
    #     candidate = self.get_object()
    #     interviews = candidate.interview_details
    #     if interviews:
    #         return Response(InterviewDetailSerializer(interviews, many = True).data)
    #     return Response({"detail": "No interviews found for this candidate."}, status = status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='add-document')
    def add_document(self, request, candidate_id = None):
        candidate = self.get_object()
        doc_type = request.data.get("doc_type")
        category = request.data.get("category")  # "required" or "optional"
        file_path = request.data.get("file_path")
        
        if not doc_type or not category or not file_path:
            return Response({
                "error": "Missing required fields: doc_type, category, file_path."
            }, status = status.HTTP_400_BAD_REQUEST)
        
        documents = candidate.documents or {}
        if isinstance(documents, str):
            try:
                documents = json.loads(documents)
            except json.JSONDecodeError:
                documents = {}
        
        if "required" not in documents:
            documents["required"] = {}
        if "optional" not in documents:
            documents["optional"] = {}
        
        if category == "required":
            documents["required"][doc_type] = {
                "verified": False,
                "path": file_path,
                "verified_by": None
            }
        elif category == "optional":
            documents["optional"][doc_type] = {
                "path": file_path
            }
        
        candidate.documents = documents
        candidate.save()
        
        return Response({
            "message": f"Document {doc_type} added to {category} category."
        })

    @action(detail = True, methods = ['patch'], url_path = 'verify-document')
    def verify_document(self, request, candidate_id = None):
        candidate = self.get_object()
        doc_type = request.data.get("doc_type")
        category = request.data.get("category", "required")
        verifier_id = request.data.get("verified_by")
        
        documents = candidate.documents
        if isinstance(documents, str):
            try:
                documents = json.loads(documents)
            except json.JSONDecodeError:
                return Response({"error": "Invalid documents format."}, status = status.HTTP_400_BAD_REQUEST)
        
        if not documents:
            return Response({"error": "No documents found."}, status = status.HTTP_404_NOT_FOUND)
            
        if category in documents and doc_type in documents[category]:
            documents[category][doc_type]["verified"] = True
            documents[category][doc_type]["verified_by"] = verifier_id
            candidate.documents = documents
            candidate.save()
            return Response({"message": f"{doc_type} verified."})
        return Response({"error": "Document type or category not found."}, status = status.HTTP_400_BAD_REQUEST)

    @action(detail = True, methods = ['patch'], url_path = 'update-offer')
    def update_offer(self, request, candidate_id = None):
        candidate = self.get_object()
        serializer = OfferDetailSerializer(data=request.data)
        if serializer.is_valid():
            candidate.offer_details = serializer.validated_data
            candidate.save()
            return Response({"message": "Offer details updated."})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail = True, methods = ['patch'], url_path = 'sign-contract')
    def sign_contract(self, request, candidate_id = None):
        candidate = self.get_object()
        serializer = ContractDetailSerializer(data = request.data)
        if serializer.is_valid():
            candidate.contract_details = serializer.validated_data
            candidate.save()
            return Response({"message": "Contract signed."})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    @action(detail = True, methods = ['post'])
    def archive(self, request, candidate_id = None):
        candidate = self.get_object()
        if candidate.is_archived:
            return Response({"detail": "Candidate already archived."}, status = status.HTTP_400_BAD_REQUEST)
        candidate.is_archived = True
        candidate.save()
        return Response({"detail": "Candidate archived successfully."}, status = status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def unarchive(self, request, candidate_id = None):
        candidate = self.get_object()
        if not candidate.is_archived:
            return Response({"detail": "Candidate is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        candidate.is_archived = False
        candidate.save()
        return Response({"detail": "Candidate unarchived successfully."}, status = status.HTTP_200_OK)
    
    @action(detail = True, methods=['post'])
    def restore(self, request, candidate_id = None):
        candidate = self.get_object()
        if not candidate.is_archived:
            return Response({"detail": "Candidate is not archived."}, status = status.HTTP_400_BAD_REQUEST)
        candidate.is_archived = False
        candidate.save()
        return Response({"detail": "Candidate restored successfully."}, status = status.HTTP_200_OK)

    @action(detail = False, methods=['get'])
    def archived(self, request):
        archived_candidates = Candidate.objects.filter(is_archived = True)
        serializer = self.get_serializer(archived_candidates, many = True)
        return Response(serializer.data)