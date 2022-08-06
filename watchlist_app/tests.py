from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from watchlist_app.api import serializers
from watchlist_app import models

class StreamingPlatformTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token' + self.token.key)

        self.stream = models.StreamingPlatform.objects.create(
            name="Netflix", 
            about="Streaming Platform",
            website = "http://netflix.com"
         )

        
    def test_streamplatform_create(self):
        data = {
            'name': 'Netflix',
            'about': 'Streaming platform',
            'website': 'http://netflix.com'
        }
        response = self.client.post(reverse('streamingplatform-list'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_streamingplatform_list(self):
        response = self.client.get(reverse('streamingplatform-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamingplatform_individual(self):
        response = self.client.get(reverse('streamingplatform-detail', 
                                        args = (self.stream.id,)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WatchListTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token' + self.token.key)

        self.stream = models.StreamingPlatform.objects.create(
            name = 'Netflix',
            about ='Streaming Platform',
            website= 'https://www.netflix.com')
        
        self.watchlist = models.WatchList.objects.create(
            platform=self.stream, 
            title="Movie 1", 
            storyline="Movie description",
            active = True
         )

    def test_watchlist_create(self):
        data = {
            "platform": self.stream,
            "title": "Movie 1",
            "storyline": "movie description",
            "active": True
        }
        response = self.client.post(reverse('watch-list'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_list(self):
        response = self.client.get(reverse('watch-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_watchlist_individual(self):
        response = self.client.get(reverse('watchlist-detail', args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.WatchList.objects.get().title, 'Movie 1')
        self.assertEqual(models.WatchList.objects.count(), 1)


class ReviewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token' + self.token.key)
    
        self.stream = models.StreamingPlatform.objects.create(
            name = "Netflix",
            about = "Streaming Platform",
            website = "https://www.netflix.com"
        )
        self.watchlist = models.WatchList.objects.create(
            platform = self.stream,
            title = "Movie 1",
            storyline = "movie description",
            active= True
        )
        self.watchlist2 = models.WatchList.objects.create(
            platform = self.stream,
            title = "Movie 2",
            storyline = "movie description",
            active= True
        )
        self.review = models.Review.objects.create(
            reviewer = self.user,
            rating = 5, 
            description = "Best Movie ever",
            watchlist = self.watchlist2,
            active = True
        )

    def test_review_create(self):
        data = {
            "reviewer": self.user,
            "rating": 5,
            "description": "Great Movie!",
            "watchlist": self.watchlist,
            "active": True
        }
        response = self.client.post(reverse('review-create', args=(self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_review_unauth(self):
        data = {
            "reviewer": self.user,
            "rating": 5,
            "description": "Great Movie!",
            "watchlist": self.watchlist,
            "active": True
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('review-create', args=(self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update(self):
        data = {
            "reviewer": self.user,
            "rating": 4,
            "description": "Good Movie!",
            "watchlist": self.watchlist,
            "active": False
        }
        response = self.client.put(reverse('review-detail', args=(self.review.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_list(self):
        response = self.client.get(reverse('review-list', args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_individual(self):
        response = self.client.get(reverse('review-detail', args = (self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_delete(self):
        response = self.client.delete(reverse('review-detail', args = (self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_review_user(self):
        response = self.client.get('/watch/reviews/?username' + self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)