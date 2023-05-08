from django.shortcuts import render
from rest_framework import generics,permissions
from .serializers import TodoSerializer, TodoToggleCompleteSerializer
from todo.models import Todo

# rest authentication

from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# this class create a list of todos
class TodoListCreate(generics.ListCreateAPIView):
    # ListAPIView requires two mandatory attributes, serializer_class and
    # queryset.
    # We specify TodoSerializer which we have earlier implemented
    serializer_class = TodoSerializer
    # permissions
    permission_classes = [permissions.IsAuthenticated]

    # There are other permissions like:
    #     - IsAdminUser – only admins/superusers have access
    #     - AllowAny – any user, authenticated or not, has full access

    def get_queryset(self):
        user = self.request.user
        todo = Todo.objects.filter(user=user).order_by('-created')
        return todo

        # create a record for the user who is currently logged in

    def perform_create(self, serializer):
        #serializer holds a django model
        serializer.save(user=self.request.user)


# this class retrieve, update and delete a todo

class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # user can only update, delete own posts
        return Todo.objects.filter(user=user)


class TodoToggleComplete(generics.UpdateAPIView):
    serializer_class = TodoToggleCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user)

    def perform_update(self,serializer):
        serializer.instance.completed=not(serializer.instance.completed)
        serializer.save()


# authentication for rest framework view

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request) # data is a dictionary
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)},status=201)
    
        except IntegrityError:
            return JsonResponse(
                {'error':'username taken. choose another username'},
                status=400
            )
        
    return JsonResponse(
        {'error': 'Invalid request method'},
        status=405
    )
