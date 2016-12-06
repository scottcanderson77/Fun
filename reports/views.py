# -*- coding: utf-8 -*-
from django.shortcuts import render
from .forms import *
from reports.models import *
from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from registration.models import UserProfile
from django.core.files import File
import os
from django.conf import settings
import mimetypes
import ast
from django.utils.encoding import smart_str
from Crypto.PublicKey import *
from django.db.models import Q
import geoip2.database
from groupmanagement.models import *
from django.contrib.auth.models import User, Group


# Create your views here.
@csrf_exempt
def createReport(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        files = FileForm(request.POST, request.FILES)
        print(files)
        if form.is_valid() and files.is_valid():
            reader = geoip2.database.Reader(settings.BASE_DIR + '/geoip/GeoLite2-City.mmdb')
            ip = request.META.get('REMOTE_ADDR', None)
            if ip == '127.0.0.1':
                response = reader.city('128.143.22.36')
                city = response.city.name
            else:
                response = reader.city(ip)
                city = response.city.name
            checked = False
            if request.POST.get("is_private", False):
                checked =True
            # clean_title = form.clean('title')
            newdoc = report(title=form.cleaned_data['title'],
                timestamp=timezone.now(),
                short_description=form.cleaned_data['short_description'],
                detailed_description=form.cleaned_data['detailed_description'],
                is_private = checked,
                location=city,
                username_id= request.user)
            newdoc.save()
            if files.cleaned_data['is_encrypted'] == True:
                f = files.cleaned_data['document']
                pubKey = UserProfile.objects.get(user_id=newdoc.username_id_id).publicKey
                pubKeyOb = RSA.importKey(pubKey)
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted'])
                newfile.save()
                enc = encrypt_file(pubKeyOb, str(newfile.document))
                Document.objects.filter(name=f).delete()
                os.remove(settings.MEDIA_ROOT + '/' + str(newfile.document))
                newfile2 = Document(document=enc, report_document=newdoc, name=enc, is_encrypted=files.cleaned_data['is_encrypted'])
                newfile2.save()
            elif files.cleaned_data['document']:
                f = files.cleaned_data['document']
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted'])
                newfile.save()
            if files.cleaned_data['is_encrypted2'] == True:
                f = files.cleaned_data['document2']
                pubKey = UserProfile.objects.get(user_id=newdoc.username_id_id).publicKey
                pubKeyOb = RSA.importKey(pubKey)
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted2'])
                newfile.save()
                enc = encrypt_file(pubKeyOb, str(newfile.document))
                Document.objects.filter(name=f).delete()
                os.remove(settings.MEDIA_ROOT + '/' + str(newfile.document))
                newfile2 = Document(document=enc, report_document=newdoc, name=enc, is_encrypted=files.cleaned_data['is_encrypted2'])
                newfile2.save()
            elif files.cleaned_data['document2']:
                f = files.cleaned_data['document2']
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted2'])
                newfile.save()
            if files.cleaned_data['is_encrypted3'] == True:
                f = files.cleaned_data['document3']
                pubKey = UserProfile.objects.get(user_id=newdoc.username_id_id).publicKey
                pubKeyOb = RSA.importKey(pubKey)
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted3'])
                newfile.save()
                enc = encrypt_file(pubKeyOb, str(newfile.document))
                Document.objects.filter(name=f).delete()
                os.remove(settings.MEDIA_ROOT + '/' + str(newfile.document))
                newfile2 = Document(document=enc, report_document=newdoc, name=enc, is_encrypted=files.cleaned_data['is_encrypted3'])
                newfile2.save()
            elif files.cleaned_data['document3']:
                f = files.cleaned_data['document3']
                newfile = Document(document=f, report_document=newdoc, name=f, is_encrypted=files.cleaned_data['is_encrypted3'])
                newfile.save()


    else:
        form = ReportForm()
        files = FileForm()
    variables = RequestContext(request, {
        'form': form,
        'files': files
    })


    return render_to_response(
        'reports/createReports.html',
        variables,
    )

@csrf_exempt
def encrypt_file(key, filename):
    print(key)
    file = settings.MEDIA_ROOT + "/" + filename
    with open(file, 'rb') as in_file:
        with  open(file + '.enc','w') as out_file:
            chunk = in_file.read()
            #chunk = bytes(chunk, 'utf-8')
            #chunk = key.encrypt(chunk, 32)
            enc_data = key.encrypt(chunk, 32)
            out_file.write(str(enc_data))
            file = '/documents/' + filename + '.enc'
            return file

@csrf_exempt
def createFolder(request):
    reports = report.objects.all()
    username_id = request.user
    if request.method == 'POST':
        form = FolderForm(request.POST, request.FILES)
        selected = request.POST.getlist('selected_report[]')
        if form.is_valid():
            folder_object = folder.objects.create(
                title=form.cleaned_data['title'], username_id=username_id
            )
            for report_selected in selected:
                re = report.objects.get(title=report_selected)
                folder_object.added_reports.add(re)

    else:
        form = FolderForm()
    variables = RequestContext(request, {
        'form': form, 'reports':reports, 'username_id':username_id,
    })

    return render_to_response(
        'reports/createFolder.html',
        variables,
    )


@csrf_exempt
def addToFolder(request):
    folder_title = request.POST.get('selected_folder')
    f = folder.objects.get(id=request.POST.get('selected_folder'))
    added = f.added_reports.all().values_list('id', flat=True)
    added = list(added)

    reports = report.objects.all().filter(username_id_id=request.user.id).values("title").exclude(id__in=added)
    #filteredReports = list(reports)
    #temp = []

    username_id = request.user
    if request.POST.get('selected_report[]'):
        # form = FolderForm(request.POST, request.FILES)
        folder_title = request.POST.get('selected_folder')
        selectedReport = request.POST.getlist('selected_report[]')
        for sr in selectedReport:
            r = report.objects.get(title=sr)
            f.added_reports.add(r)
            f.save()
        added = f.added_reports.all().values_list('id', flat=True)
        added = list(added)
        reports = report.objects.all().filter(username_id_id=request.user.id).values("title").exclude(id__in=added)
    else:
        form = FolderForm()
    variables = RequestContext(request, {'reports':reports, 'folder_title': folder_title})

    return render_to_response('reports/viewFolderDescription.html', variables,)




@csrf_exempt
def renameFolder(request):
    folders = folder.objects.all()
    selected = request.POST.getlist('selected_folder[]')
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data['title']

            for folder_selected in selected:
                print(folder_selected)
                fs = folder.objects.get(title=folder_selected)
                fs.title = title
                fs.save()
    else:
        form = FolderForm()
    variables = RequestContext(request, {
        'form': form, 'folders':folders
    })

    return render_to_response(
        'reports/renameFolder.html',
        variables,
    )

@csrf_exempt
def deleteFolder(request):
    folders = folder.objects.all()
    selected = request.POST.getlist('selected_folder[]')
    if request.method == 'POST':
        for folder_selected in selected:
            fs = folder.objects.get(title=folder_selected)
            fs.delete()
    else:
        pass
    variables = RequestContext(request, {
        'folders': folders
    })

    return render_to_response(
        'reports/deleteFolder.html',
        variables,
    )
def viewFolderContent(request):
    if request.POST.get("remove"):
        folder_title = request.POST.get("selected_folder")
        report_title = request.POST.get("selected_report")
        removeReports(request, folder_title, report_title)

    folder_title = request.POST.get("selected_folder")
    f = folder.objects.get(id=folder_title)
    print(f)
    rep = f.added_reports.all().values_list('id', flat=True)
    rep = list(rep)
    r = report.objects.all().filter(id__in=rep)
    return render(request, 'reports/viewFolderContent.html', {'r':r, 'folder_title': folder_title})

def viewFolderDescription(request):
    user = request.user
    folder_title = request.POST.get("selected_folder")
    selected = request.POST.getlist('selected_report[]')
    reports = report.objects.all()
    # folders = folder.objects.get(title=title)
    return render(request, 'reports/viewFolderDescription.html', {'folder_title':folder_title, 'reports':reports})

def removeReports(request, folder_title, report_title):
    f = folder.objects.get(id=folder_title)
    r = report.objects.all().filter(title=report_title).values_list('id', flat=True)
    print(r)
    #r = r.get('id')
    f.added_reports.remove(r[0])
    f.save()
    # return redirect(viewFolderContent)


@csrf_exempt
def viewFolder(request):
    user = request.user
    folders = folder.objects.all().filter(username_id_id=request.user.id)
    return render(request, 'reports/viewFolders.html', {'folders': folders, 'user': user})

@csrf_exempt
def viewReport(request):
    user = request.user
    if user.is_superuser:
        reports = report.objects.all()
    else:
        reports = report.objects.all().filter(is_private=False)
        print(reports)
    folders = folder.objects.all()
    return render(request, 'reports/viewReports.html', {'user': user, 'reports': reports, 'folders':folders})

@csrf_exempt
def viewReports(request):
    user = request.user
    title = request.POST.get("selected_report")
    rs = report.objects.get(title=title)
    files = Document.objects.all().filter(report_document=rs.id)
    owner = User.objects.get(id=rs.username_id_id)

    print(owner.username)
    return render(request, 'reports/viewReportDescription.html', {'rs': rs, 'user': user, 'files': files, 'owner': owner})

@csrf_exempt
def download(request, file_name):
    file_path = settings.MEDIA_ROOT + '/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    print(file_mimetype)
    print((file_wrapper))
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(file_name)

    # f = open(file_path, 'r')
    # myFile = File(f)
    # # print(filename)
    # print("puppies")
    return response


@csrf_exempt
def viewYourReports(request):
    user = request.user
    reports = report.objects.all().filter(username_id=user)
    #At this point reports has all the reports created by the current user
    folders = folder.objects.all().filter(username_id=user)
    # for report_document in report.objects.all():
    #     for group in report_document.groupreports_set.select_related().all():

    # print()



    #We have to append all the reports that are not created by the user but ones that he has  access to



    return render(request, 'reports/viewYourReports.html', {'reports':reports, 'user': user, 'folders':folders })


@csrf_exempt
def editReport(request):
    user = request.user
    title = request.POST.get("title")
    short = request.POST.get("short")
    detailed = request.POST.get("detailed")
    is_private = request.POST.get("private")
    original = request.POST.get("original")
    if(request.POST.getlist('updated')):
        reports = report.objects.get(title=original)
        reports.title = title
        reports.short_description = short
        reports.detailed_description = detailed
        if is_private == "private":
            reports.is_private = True
        else:
            reports.is_private = False

        #reports.is_private = is_private
        reports.save()

    return render(request, 'reports/editReport.html', {'user': user, 'title': title, 'short': short, 'detailed':detailed, 'private': is_private})

@csrf_exempt
def deleteReport(request):
    user = request.user
    id = request.POST.get("id")
    report.objects.filter(id=id).delete()
    return render(request, 'reports/viewYourReports.html', {'user':user})

@csrf_exempt
def searchReports(request):
    query_string = request.GET.get('q')
    loc = request.GET.get('location')
    if request.GET.get('start-date') and request.GET.get('end=date'):
        start_date = request.GET.get('start-date') + ' 00:00:00.000000-00'
        end_date = request.GET.get('end-date') + ' 00:00:00.000000-00'
    if request.GET.get('q'):
        results = report.objects.annotate(
            search=SearchVector('title', 'short_description', 'detailed_description'),
        ).filter(search=query_string).exclude(is_private=True).order_by('timestamp')
        if request.GET.get('location'):
            results = report.objects.annotate(
                search=SearchVector('title', 'short_description', 'detailed_description'),
            ).filter(search=query_string).filter(location=loc).exclude(is_private=True).order_by('timestamp')
            if request.GET.get('start-date') and request.GET.get('end-date'):
                results = report.objects.annotate(
                    search=SearchVector('title', 'short_description', 'detailed_description'),
                ).filter(search=query_string).filter(location=loc).filter(timestamp__range=(start_date,end_date)).exclude(is_private=True).order_by('timestamp')
                return render(request, 'reports/searchReports.html', {'results': results})
            return render(request,'reports/searchReports.html', {'results': results })
        return render(request, 'reports/searchReports.html', {'results': results})
    if request.GET.get('location'):
        results = report.objects.all().filter(location=loc).exclude(is_private=True).order_by('timestamp')
        if request.GET.get('start-date') and request.GET.get('end-date'):
            results = report.objects.all().filter(location=loc).filter(timestamp__range=(start_date,end_date)).exclude(is_private=True).order_by('timestamp')
            return render(request, 'reports/searchReports.html', {'results': results})
        return render(request,'reports/searchReports.html', {'results': results })
    if request.GET.get('start-date') and request.GET.get('end-date'):
        print(request.GET.get('start-date'))
        results = report.objects.all().filter(timestamp__range=(start_date, end_date)).exclude(is_private=True).order_by('timestamp')
        return render(request, 'reports/searchReports.html', {'results': results})
    return render(request, 'reports/searchReports.html', {})


@csrf_exempt
def reportHome(request):
    user = request.user
    return render_to_response("reports/reportHome.html", {"user":user})

@csrf_exempt
def folderHome(request):
    user = request.user
    return render_to_response("reports/folderHome.html", {"user":user})