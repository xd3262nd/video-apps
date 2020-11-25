from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Video




class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_homepage(self):

        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')
    

class TestAddVideos(TestCase):
    def test_add_video(self):
        url = reverse('add_video')

        valid_video = {
            'name': 'Yoga',
            'url': 'https://www.youtube.com/watch?v=Nw2oBIrQGLo',
            'notes': 'Yoga for relaxation'
        }

        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html')

        self.assertContains(response, 'Yoga')
        self.assertContains(response, valid_video['url'])
        self.assertContains(response, valid_video['notes'])

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

        video_count = Video.objects.count()

        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('Yoga', video.name)
        self.assertEqual(valid_video['url'], video.url)
        self.assertEqual(valid_video['notes'], video.notes)
        self.assertEqual('Nw2oBIrQGLo', video.video_id)


        valid_video_2 = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=A0pkEgZiRG4',
            'notes': 'Yoga for strecthing'
        }
        response_2 = self.client.post(url, data=valid_video_2, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html')

        self.assertContains(response_2, '2 videos')

        self.assertContains(response_2, 'Yoga')
        self.assertContains(response_2, valid_video['url'])
        self.assertContains(response_2, valid_video['notes'])

        self.assertContains(response_2, 'yoga')
        self.assertContains(response_2, valid_video_2['url'])
        self.assertContains(response_2, valid_video_2['notes'])

        self.assertEqual(2, Video.objects.count())


        video_1_in_db = Video.objects.get(name='Yoga', url='https://www.youtube.com/watch?v=Nw2oBIrQGLo', \
        notes='Yoga for relaxation', video_id='Nw2oBIrQGLo')
        
        video_2_in_db = Video.objects.get(name='yoga', url='https://www.youtube.com/watch?v=A0pkEgZiRG4', \
        notes='Yoga for strecthing', video_id='A0pkEgZiRG4')


        # how about the correct videeos in the context?
        videos_in_context = list(response_2.context['videos'])   # the object in the response is from a database query, so it's a QuerySet object. Convert to a list
        expected_videos_in_context = [video_1_in_db, video_2_in_db]  # in this order, because they'll be sorted by name 
        self.assertEqual(expected_videos_in_context, videos_in_context)

    def test_add_video_no_notes_video_added(self):
        
        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'Yoga',
            'url': 'https://www.youtube.com/watch?v=Nw2oBIrQGLo',
            
        }

        response = self.client.post(add_video_url, data=valid_video, follow=True)
        self.assertTemplateUsed('video_collection/video_list.html')


        self.assertContains(response, 'Yoga')
        self.assertContains(response, valid_video['url'])
        
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

        video_count = Video.objects.count()

        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('Yoga', video.name)
        self.assertEqual(valid_video['url'], video.url)
        self.assertEqual('', video.notes)
        self.assertEqual('Nw2oBIrQGLo', video.video_id)


    def test_add_video_missing_fields(self):
        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'name': '',   # no name, should not be allowed 
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',   
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',  
                # no URL 
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name
                # no URL
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': '',   # blank - not allowed 
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },

        ]
        
        for invalid_video in invalid_videos:

            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed('video_collection/video_list.html')
            self.assertEqual(0, Video.objects.count())
            messages = response.context['messages']
            message_texts = [ message.message for message in messages]
            self.assertIn('Please check the data entered.', message_texts)

            self.assertContains(response, 'Please check the data entered.')


    def test_add_duplicate_video_not_added(self):


        with transaction.atomic():
            new_video = {
                'name': 'yoga',
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            }
            Video.objects.create(**new_video)

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

        with transaction.atomic():
            # try to create it again    
            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('You already added that video', message_texts)

        # still one video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

    def test_add_video_invalid_url_not_added(self):
    
        # what other invalid strings shouldn't be allowed? 

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]


        for invalid_url in invalid_video_urls:

            new_video = {
                'name': 'yoga',
                'url': invalid_url,
                'notes': 'yoga for neck and shoulders'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('Invalid YouTube URL', message_texts)

            # no videos in the database 
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    def test_all_videos_displayed_in_correct_order(self):
    
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    # No video message 

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No Videos')
        self.assertEquals(0, len(videos_in_template))


    # 1 video vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   # check this, because '1 videos' contains '1 video'


    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No Videos')



class TestVideoModel(TestCase):
    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example', url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)  # check contents of two lists/iterables but order doesn't matter.


    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/watch?v1234',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            ''
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_url, notes='example notes')

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)


    def duplicate_video_raises_integrity_error(self):
        Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
class TestVideoInfo(TestCase):
    
    def test_video_list_shows_all_data(self):
        #add videos
        video_01 = Video.objects.create(name='test', notes='example1', url='https://www.youtube.com/watch?v=45asd6')
        video_02 = Video.objects.create(name='test2', notes='example2', url='https://www.youtube.com/watch?v=789dasd')
        
        video_2 = Video.objects.get(pk=2)

        response = self.client.get(reverse('video_info', kwargs={'video_pk':2} )) 
        self.assertTemplateUsed(response, 'video_collection/video_info.html')
        
        #retrieve data sent to template
        data_rendered = response.context['video']
        #confirm that data is same as data for video_2
        self.assertEqual(data_rendered, video_2)
        #confirm correct data shown on page
        self.assertContains(response, 'test')
        self.assertContains(response, 'test2')
        self.assertContains(response, 'https://www.youtube.com/watch?v=789dasd')

    def test_request_video_info_for_nonexistent_video_returns_404(self):
        #add 2 videos
        video_01 = Video.objects.create(name='test', notes='example1', url='https://www.youtube.com/watch?v=4512sa6')
        video_02 = Video.objects.create(name='test2', notes='example2', url='https://www.youtube.com/watch?v=7asda389')
        
        
        response = self.client.get(reverse('video_info', kwargs={'video_pk':23} )) 
        
        self.assertEqual(404, response.status_code)