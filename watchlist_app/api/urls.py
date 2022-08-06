from django.urls import path, include
from rest_framework.routers import DefaultRouter
from watchlist_app.api.views import ( WatchListAPI, WatchDetailAPI, ReviewList,ReviewDetail,
                                    ReviewCreate, UserReview, WatchListLAV,
                                    #StreamViewSet
                                    StreamPlatformVS)
                            

router = DefaultRouter()
#router.register(r'stream', StreamViewSet, basename='streamingplatform')
router.register('stream', StreamPlatformVS, basename='streamingplatform')
urlpatterns=[
    path('list/', WatchListAPI.as_view(), name='watch-list'),
    path('<int:pk>/', WatchDetailAPI.as_view(), name='watchlist-detail'),
    path('new-list/', WatchListLAV.as_view(), name='watchlist'),

    path('', include(router.urls)),
    # path('stream/', StreamPlatformAPI.as_view(), name='stream'),
    # path('stream/<int:pk>', StreamPlatformDetailAPI.as_view(), name='streamingplatform-detail'),

    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
    path('reviews/', UserReview.as_view(), name='user-review'),
    # path('review/', ReviewList.as_view(), name='review-list'),
    # path('review/<int:pk>', ReviewDetail.as_view(), name='review-detail')
]