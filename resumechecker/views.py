from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import JobDescriptionSerializer,JobDescription,ResumeSerializer,Resume
from .analyzer import process_resume
from .models import JobDescription
from django.core.files.storage import FileSystemStorage

# Create your views here.

def home(request):
    if request.method == "POST":
        selected_job_id = request.POST.get("job_title")
        resume_file = request.FILES.get("resume")

        if selected_job_id and resume_file:
            job = JobDescription.objects.get(id=selected_job_id)
            resume_data = process_resume(resume_file, job.job_description)

            # Save the file and store only the file name in session
            fs = FileSystemStorage()
            file_name = fs.save(resume_file.name, resume_file)
            file_url = fs.url(file_name)  # Get file URL

            request.session['resume_data'] = resume_data
            request.session['job_title'] = job.job_title
            request.session['resume_uploaded_name'] = resume_file.name  # Store only name
            request.session['resume_uploaded_url'] = file_url  # Store file URL
            
            return redirect('result')  # Redirect to result page

    data = JobDescription.objects.all()
    return render(request, 'resumechecker/home.html', {'data': data})


def result(request):
    resume_data = request.session.get('resume_data')
    job_title = request.session.get('job_title')
    resume_uploaded_name = request.session.get('resume_uploaded_name')
    resume_uploaded_url = request.session.get('resume_uploaded_url')

    if not resume_data:
        return redirect('home')  # Fallback if accessed directly
    
    return render(request, 'resumechecker/result.html', {
        'resume_data': resume_data,
        'selected_job_title': job_title,
        'resume_uploaded_name': resume_uploaded_name,
        'resume_uploaded_url': resume_uploaded_url
    })




class JobDescriptionAPI(APIView):
    def get(self,request):
        queryset = JobDescription.objects.all()
        serializer = JobDescriptionSerializer(queryset,many=True)
        response = Response({'status':True,'data':serializer.data})
        return render(request,'resumechecker/jobdesc.html')

    
class AnalyzeResumeAPI(APIView):
    def post(self,request):
        try:
            data = request.data
            if not data.get('job_description'):
                return Response({
                    'status':False,
                    'message':'job_description is required',
                    'data':{}
                })
            
            serializer = ResumeSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                        'status':False,
                        'message':'errors',
                        'data':serializer.errors
                    })
        
            serializer.save()
            _data = serializer.data
            resume_instance = Resume.objects.get(id=_data['id'])
            resume_path = resume_instance.resume.path
            data = process_resume(resume_path,JobDescription.objects.get(id=data.get('job_description')).job_description)
            return Response({
                'status':True,
                'message':'resume analyzed',
                'data': data

            })
        except Exception as e:
            return Response({
                'data':False
            })
    