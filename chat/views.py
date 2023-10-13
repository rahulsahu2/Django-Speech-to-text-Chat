import os
from chat.models import Chat
import pandas as pd
import speech_recognition as sr
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def home(request):
    chats = Chat.objects.all()
    all_users = User.objects.filter(messages__isnull=False).distinct()
    ctx = {
        'home': 'active',
        'chat': chats,
        'allusers': all_users
    }
    if request.user.is_authenticated:
        return render(request, 'chat.html', ctx)
    else:
        return render(request, 'base.html', None)


def upload(request):
    customHeader = request.META['HTTP_MYCUSTOMHEADER']

    # obviously handle correct naming of the file and place it somewhere like media/uploads/
    filename = str(Chat.objects.count())
    filename = filename + "name" + ".wav"
    uploadedFile = open(filename, "wb")
    # the actual file is in request.body
    uploadedFile.write(request.body)
    uploadedFile.close()
    # put additional logic like creating a model instance or something like this here
    r = sr.Recognizer()
    harvard = sr.AudioFile(filename)
    with harvard as source:
        audio = r.record(source)
    msg1 = r.recognize_google(audio)
    msg = ProcessData(msg1)
    os.remove(filename)
    chat_message = Chat(user=msg1, message=msg)
    if msg != '':
        chat_message.save()
    return redirect('/')


def post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)
        print('Our value = ', msg)
        msg = ProcessData(msg)
        chat_message = Chat(user=request.user, message=msg)
        if msg != '':
            chat_message.save()
        return JsonResponse({'msg': msg, 'user': chat_message.user.username})
    else:
        return HttpResponse('Request should be POST.')


def messages(request):
    chat = Chat.objects.all()
    return render(request, 'messages.html', {'chat': chat})

def search_string(s, search):
    return str(search).lower() in str(s).lower()

def ProcessData(text):
    try:
        df = pd.read_csv('medicine.csv')
        df.dropna(inplace = True)

        # Search for the string 'al' in all columns
        mask = df.map(lambda x: search_string(x, text))

        # Filter the DataFrame based on the mask
        filtered_df = df.loc[mask.any(axis=1)]

        result = "Decoded Text : {}#".format(text)
        result = "{}".format(filtered_df["name"].to_numpy())
        return result
    except Exception as ex:

        return "Not found matched result for {}".format(text)
