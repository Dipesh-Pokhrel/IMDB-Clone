from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import  AnonRateThrottle, ScopedRateThrottle
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


from watchlist_app.models import WatchList, StreamingPlatform, Review
from watchlist_app.api.serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer
from watchlist_app.api.permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from watchlist_app.api.throttling import ReviewCreateThrottle, ReviewListThrottle
from watchlist_app.api.pagination import WatchListPagination, WatchListLOPagination, WatchListCPagination


class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer
    #throttle_classes = [ReviewListThrottle, AnonRateThrottle]

    # def get_queryset(self):
    #     username = self.kwargs.get('username')
    #     return Review.objects.filter(reviewer__username = username)

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Review.objects.filter(reviewer__username = username)

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle]
    
    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = WatchList.objects.get(pk=pk)

        reviewer = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, reviewer=reviewer)

        if review_queryset.exists():
            raise ValidationError('You have already reviewed this watch.')
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating'])/2
        
        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()
        
        serializer.save(watchlist=watchlist, reviewer=reviewer)

class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reviewer__username', 'active']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle, AnonRateThrottle]
    throttle_scope = 'review-detail'


class StreamPlatformVS(viewsets.ModelViewSet):
    serializer_class = StreamPlatformSerializer
    queryset = StreamingPlatform.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes= [AnonRateThrottle]


# class StreamViewSet(viewsets.ViewSet):
    
#     def list(self, request):
#         queryset = StreamingPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset,many=True, context={'request': request})
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamingPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(watchlist, context={'request': request})
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = StreamPlatformSerializer(data=request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)

#     def delete(self, request, pk):
#         platform = StreamingPlatform.objects.get(pk=pk)
#         platform.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class ReviewList(mixins.ListModelMixin,
#                     mixins.CreateModelMixin,
#                     generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

class StreamPlatformAPI(APIView):
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        platforms = StreamingPlatform.objects.all()
        platforms_serializer = StreamPlatformSerializer(platforms, many=True, context={'request': request})
        return Response(platforms_serializer.data)
    
    def post(self, request):
        platform_serializer = StreamPlatformSerializer(data=request.data)
        if platform_serializer.is_valid():
            platform_serializer.save()
            return Response(platform_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(platform_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamPlatformDetailAPI(APIView):
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, pk):
        try:
            movies = StreamingPlatform.objects.get(pk=pk)
        except StreamingPlatform.DoesNotExist:
            return Response({'Error': 'Streaming Platforms Details Not Found!'})
        serializer = StreamPlatformSerializer(movies, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        movies = StreamingPlatform.objects.get(pk=pk)
        serializer = StreamPlatformSerializer(movies, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        movies = StreamingPlatform.objects.get(pk=pk)
        movies.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WatchListAPI(APIView):
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        movies = WatchList.objects.all()
        movie_serializer = WatchListSerializer(movies, many=True)
        return Response(movie_serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchDetailAPI(APIView):
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, pk):
        try:
            movies = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({'Error':'WatchList not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movies)
        return Response(serializer.data)
    
    def put(self, request, pk):
        movies = WatchList.objects.get(pk=pk)
        serializer = WatchListSerializer(movies, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movies = WatchList.objects.get(pk=pk)
        movies.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WatchListLAV(generics.ListAPIView):
    queryset= WatchList.objects.all()
    serializer_class = WatchListSerializer
    pagination_class = WatchListCPagination
    #filter_backends = [filters.OrderingFilter]
    #filterset_fields = ['title', 'platform__name']
    #ordering_fields = ['avg_rating']