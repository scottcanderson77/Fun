from django.shortcuts import render
from .models import Message
from .forms import *
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from registration import *
from message.templates import *


# Create your views here.


@csrf_exempt
def createMessage(request):
    if request.method == 'POST':
        user = request.user
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message.objects.create(
                receiver=User.objects.get(username__iexact=form.cleaned_data['sendToUser ']),
                sender=user,  # User.objects.get(username__iexact=request.user),
                message_title=form.cleaned_data['title'],
                message_body=form.cleaned_data['body'],
            )

        return HttpResponseRedirect('/messageHome/')
    else:
        form = MessageForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response('createMessage.html',variables,)


@csrf_exempt
def displayMessage(request):
    title = None
    if request.method == 'POST':
        form = searchTitleForm(request.POST)
        if (form.is_valid()):
            messages = []
            title = form.cleaned_data['title']

            if title != None:
                messages = Message.objects.filter(sender=request.user, message_title=title)
            else:
                messages = Message.objects.filter(sender=request.user)

            return render_to_response('allMessages.html', {"messages": messages})
    else:
        form = searchTitleForm()
    variables = RequestContext(request, {'form': form})
    messages = []
    messages = Message.objects.filter(sender=request.user)
    return render_to_response('allMessages.html', {"messages": messages}, variables, )


@csrf_exempt
def checkMessage(request):
    receiver = None
    messages = []
    if request.method == 'POST':
        titleForm = searchTitleForm(request.POST)
        #senderForm = searchSenderForm(request.POST)
        if (titleForm.is_valid()):
            title = titleForm.cleaned_data['title']

            if (title != None):
                messages = Message.objects.filter(sender=request.user, message_title=title)
            else:
                messages = Message.objects.filter(reciever=request.user)

            return render_to_response('checkMessage.html', {"messages": messages})
    else:
        titleForm = searchTitleForm()
        senderForm = searchSenderForm()
    variables = RequestContext(request, {'titleForm': titleForm},)# {'senderForm': senderForm})
    messages = []
    messages = Message.objects.filter(receiver=request.user)
    return render_to_response('checkMessage.html', {"messages": messages}, variables, )


@csrf_exempt
def messageHome(request):
    message = Message.objects.all()
    return render_to_response('messageHome.html', {'user': request.user})

def detail(request, message_id):
    message = Message.objects.get(pk = message_id)
    return render_to_response('messageDetail.html', {'message': message})
