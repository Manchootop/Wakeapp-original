from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import mixins as auth_mixin
from django.urls import reverse_lazy
from django.views import generic as views
from WakeApp.core.models import Event


class DashboardView(views.ListView):
    model = Event
    template_name = 'core/dashboard.html'
    context_object_name = 'events'




def search_view(request):
    qs = Event.objects.all()
    title_query = request.GET.get('title')
    location_query = request.GET.get('location')
    last_hour_query = request.GET.get('last_hour')

    if title_query != '' and title_query is not None:
        qs = qs.filter(title__icontains=title_query)

    elif location_query != '' and location_query is not None:
        qs = qs.filter(location__icontains=location_query)
    context = {
        'queryset': qs
    }
    return render(request, 'core/dashboard.html', context)


class EventDetailsView(auth_mixin.LoginRequiredMixin, views.DetailView):
    model = Event
    template_name = 'core/event_details.html'
    context_object_name = 'event'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        viewed_events = request.session.get('last_viewed_events_ids', [])
        viewed_events.insert(0, self.kwargs['pk'])
        request.session['last_viewed_events_ids'] = viewed_events[:4]

        return response

    # def get_queryset(self):
    #     return super().get_queryset().prefetch_related('tagged_pets')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_owner'] = self.object.organizer == self.request.user

        return context


class CreateEventView(auth_mixin.LoginRequiredMixin, views.CreateView):
    model = Event
    template_name = 'core/event_create.html'
    fields = ('type', 'title', 'description', 'location', 'recommendations',)
    success_url = reverse_lazy('dashboard')


class MyEvents(views.ListView):
    model = Event
    template_name = 'core/my_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


def like_event(request, pk):
    event = Event.objects.get(pk=pk)
    event.likes += 1
    event.save()

    return redirect('dashboard')

