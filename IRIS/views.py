from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

class Inicio(View):
    def get(self, request):
        return render(request, 'presentacion.html')


def registro(request):
    return HttpResponse('Hello world!')
