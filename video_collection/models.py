from django.db import models
from urllib import parse
import requests
from django.core.exceptions import ValidationError

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)


    def save(self, *args, **kwargs):

        # if not self.url.startswith('https://www.youtube.com/watch'):
        #     raise ValidationError(f'Not a Youtube URL {self.url}')
        try:

            # extract the video ID from URL
            url_components = parse.urlparse(self.url)

            if url_components.scheme != 'https':
                raise ValidationError(f'Not a YouTube URL {self.url}')
            if url_components.netloc != 'www.youtube.com':
                raise ValidationError(f'Not a YouTube URL {self.url}')
            if url_components.path != '/watch':
                raise ValidationError(f'Not a YouTube URL {self.url}')

            query_string = url_components.query

            if not query_string:
                raise ValidationError(f'Invalid YouTube URL {self.url}')
            
            parameters = parse.parse_qs(query_string, strict_parsing=True) # dictionary
            v_parameters_list = parameters.get('v') # return None if no key found

            # true if at least one entry in the list
            # save
            if not v_parameters_list: # checking if none or emtpy list
                raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')
            
            self.video_id = v_parameters_list[0]

        except ValueError as e:
            raise ValidationError(f'Unable to parse URL {self.url}') from e
        
        
        super().save(*args, **kwargs)
             





    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Notes: {self.notes[:200]}, Video ID: {self.video_id}'
    
    


