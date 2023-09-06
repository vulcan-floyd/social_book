from cmath import log
from xml.dom import UserDataHandler
from django.shortcuts import render, redirect
from django.http  import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.models import User, auth

from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    
    latest_posts = []
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        for post in feed_lists:
            latest_posts.append([post, post.created_at])

    latest_posts.sort(key=lambda x: x[1])
    feed_lists = [post[0] for post in latest_posts]

    all_users = User.objects.all()

    user_following_set = set()
    for user in user_following:
        user_following_set.add(user.user)

    username_profile_list = []
    for user in all_users:
        if user.username not in user_following_set and user.username != request.user.username:
            profile_lists = Profile.objects.filter(id_user=user.id)
            if profile_lists:
                username_profile_list.append(profile_lists)

    random.shuffle(username_profile_list)
    suggestions_username_profile_list = list(chain(*username_profile_list))

    posts = Post.objects.all()
    context = {
        'user_profile': user_profile,
        'posts': feed_lists,
        'suggestions_username_profile_list': suggestions_username_profile_list[:4]
    }
    return render(request, 'index.html', context)

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

    return redirect('/')

@login_required(login_url='signin')
def user_followers(request, pk):
    login_user_object = User.objects.get(username=request.user.username)
    login_user_profile = Profile.objects.get(user=login_user_object)
    user_object = User.objects.get(username=pk)
    user_followers = FollowersCount.objects.filter(user=pk)
    followers_lists = []
    for follower in user_followers:
        user_follower = User.objects.get(username=follower.follower)
        follower_profile = Profile.objects.get(id_user=user_follower.id)
        followers_lists.append(follower_profile)
    
    context = {
        "user_profile": login_user_profile,
        "username_profile_list": followers_lists
    }
    return render(request, 'search.html', context)

@login_required(login_url='signin')
def user_following(request, pk):
    login_user_object = User.objects.get(username=request.user.username)
    login_user_profile = Profile.objects.get(user=login_user_object)
    user_object = User.objects.get(username=pk)
    user_followers = FollowersCount.objects.filter(follower=pk)
    following_lists = []
    for following in user_followers:
        user_following = User.objects.get(username=following.user)
        following_profile = Profile.objects.get(id_user=user_following.id)
        following_lists.append(following_profile)
    
    context = {
        "user_profile": login_user_profile,
        "username_profile_list": following_lists
    }
    return render(request, 'search.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            new_follower = FollowersCount(follower=follower, user=user)
            new_follower.save()
        return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)
        
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
        context = {
            "user_profile": user_profile,
            "username_profile_list": username_profile_list
        }
    return render(request, 'search.html', context)

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    print(user_profile.coverphoto)
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    print(context)

    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(username=username, post_id=post_id).first()

    if not like_filter:
        new_like = LikePost.objects.create(username=username, post_id=post_id)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')
        
        if request.FILES.get('coverimage') == None:
            cover_image = user_profile.coverphoto
        else:
            cover_image = request.FILES.get('coverimage')

        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.coverphoto = cover_image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect('/')
    return render(request, 'setting.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'username is already taken')
                return redirect('signup')
            # elif User.objects.filter(email=email).exists():
            #     messages.info(request, 'email already exists')
            #     return render(request, 'signup.html')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                
                user_model = User.objects.get(username=username)
                user_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                user_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'password does not match')
            return render(request, 'signup.html')
    else:
        return render(request, 'signup.html')
    
#@login_required(login_url='signin')
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

def logout(request):
    auth.logout(request)
    return redirect('signin')
