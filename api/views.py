from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import BPRecord
from .serializers import BPRecordSerializer
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q  # For search functionality


def base(request):
    return render(request,'base.html')

@api_view(['POST'])
def create_bp_record(request):
    if request.method == 'POST':
        serializer = BPRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def delete_record(request, pk):
    if request.user.is_superuser:
        record = get_object_or_404(BPRecord, pk=pk)
        record.delete()
    return redirect('admin_dashboard')


@login_required
def admin_dashboard(request):
    search_query = request.GET.get('search', '')  # Get search query from the GET request
    if search_query:
        # Filter records by patient_id if search query exists
        records = BPRecord.objects.filter(patient_id__icontains=search_query)
    else:
        # Show all records if no search query
        records = BPRecord.objects.all()
    return render(request, 'admin_dashboard.html', {'records': records, 'search_query': search_query})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser and password == "BME@123":
                return redirect('admin_dashboard')
            else:
                return redirect('caretaker_dashboard', patient_id=password)
        else:
            messages.error(request,"*Invalid User or Password ")
            return redirect('login')

    return render(request, 'login.html')

def logoutuser(request):
    logout(request)
    return redirect('/')

    
@login_required
def admin_dashboard(request):
    records = BPRecord.objects.all()
    return render(request, 'admin_dashboard.html', {'records': records})

@login_required
def caretaker_dashboard(request, patient_id):
    if request.user.is_authenticated and BPRecord.objects.filter(patient_id=patient_id).exists():
        records = BPRecord.objects.filter(patient_id=patient_id)
        return render(request, 'caretaker_dashboard.html', {'records': records, 'patient_id': patient_id})
    else:
        messages.error(request,"Unauthorized access")
        return redirect('login')