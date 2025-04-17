from rest_framework import serializers
from .models import Candidate
from job_posting.models import Job_Posting as JobPosting

class Document_Serializer(serializers.Serializer):
    verified = serializers.BooleanField(required = False)
    path = serializers.CharField()
    verified_by = serializers.CharField(required = False, allow_blank = True)

class Documents_Field_Serializer(serializers.Serializer):
    required = serializers.DictField(child = Document_Serializer(), required = False)
    optional = serializers.DictField(child = Document_Serializer(), required = False)

class Interview_Detail_Serializer(serializers.Serializer):
    type = serializers.CharField()
    date = serializers.DateTimeField()
    interviewer_id = serializers.CharField(required = False, allow_null = True)
    feedback = serializers.CharField(required = False, allow_blank = True, allow_null = True)
    rating = serializers.FloatField(required = False, allow_null = True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {key: value for key, value in rep.items() if value not in [None, '', []]}

class Offer_Detail_Serializer(serializers.Serializer):
    salary = serializers.FloatField()
    position_id = serializers.CharField()
    benefits = serializers.ListField(child = serializers.CharField())
    start_date = serializers.DateField()
    expiry_date = serializers.DateField()

class Contract_Detail_Serializer(serializers.Serializer):
    signed_date = serializers.DateField()
    contract_path = serializers.CharField()
    witness_id = serializers.CharField()
    hr_approver_id = serializers.CharField()

class Candidate_Serializer(serializers.ModelSerializer):
    job_id = serializers.CharField(write_only = True)
    position_title = serializers.CharField(source = 'job.position_title', read_only = True)

    class Meta:
        model = Candidate
        fields = [
            'candidate_id', 'job_id', 'position_title',
            'first_name', 'last_name', 'email', 'phone',
            'resume_path', 'application_status',
            'documents', 'interview_details',
            'offer_details', 'contract_details',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['candidate_id', 'created_at', 'updated_at']

class Candidate_CreateSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(write_only = True)
    documents = Documents_Field_Serializer(required = False)
    interview_details = serializers.ListSerializer(child = Interview_Detail_Serializer(), required = False)
    offer_details = Offer_Detail_Serializer(required = False)
    contract_details = Contract_Detail_Serializer(required = False)

    class Meta:
        model = Candidate
        fields = [
            'job_id', 'first_name', 'last_name', 'email', 'phone',
            'resume_path', 'application_status',
            'documents', 'interview_details', 'offer_details', 'contract_details'
        ]

    def create(self, validated_data):
        job_id = validated_data.pop('job_id')
        job = JobPosting.objects.get(job_id = job_id)
        validated_data['job'] = job
        validated_data['candidate_id'] = Candidate.generate_candidate_id()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        job_id = validated_data.pop('job_id', None)
        if job_id:
            instance.job = JobPosting.objects.get(job_id = job_id)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['job_id'] = instance.job.job_id if instance.job else None
        return rep

class Resume_Upload_Serializer(serializers.Serializer):
    resume_path = serializers.CharField()

class Document_Verification_Serializer(serializers.Serializer):
    documents = Documents_Field_Serializer()

class Interview_Add_Serializer(serializers.Serializer):
    interview_details = serializers.ListSerializer(child = Interview_Detail_Serializer())

class Offer_Update_Serializer(serializers.Serializer):
    offer_details = Offer_Detail_Serializer()

class Contract_Sign_Serializer(serializers.Serializer):
    contract_details = Contract_Detail_Serializer()
