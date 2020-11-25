from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden


from .models import Video
from .forms import VideoForm, SearchForm


def home(request):
    app_name = 'Exercise Videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})

def add(request):

    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')

            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'You already added that video')
        
        messages.warning(request, 'Please check the data entered.')
        # Render the form again so user can edit it
        return render(request, 'video_collection/add.html',{'new_video_form': new_video_form} )

    # GET request
    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form} )


def video_list(request):

    # build form from data user has sent to app
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term'] # search term to search on db
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
    
    else: # form is not filled in or this is the first time the user sess the page
        search_form = SearchForm() # make a new search form here
        videos = Video.objects.order_by(Lower('name'))


    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})


def video_info(request, video_pk):

    # retrieve the video with pk 
    video = get_object_or_404(Video, pk = video_pk)

    return render(request, 'video_collection/video_info.html', {'video': video})



def delete_video(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    video.delete()
    return redirect('video_list')