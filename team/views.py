# Third Party Stuff
from django.contrib.auth.models import User
from django.views.generic import ListView


class TeamListView(ListView):
    queryset = None
    paginate_by = 100

    def dispatch(self, *args, **kwargs):
        self.type = kwargs['role']

        if self.type == 'Creation-Team':
            self.queryset = User.objects.filter(
                groups__name__in=['Contributor', 'Quality-Reviewers', 'Animation-Team']).order_by('first_name')
        else:
            self.queryset = User.objects.filter(groups__name=kwargs['role']).order_by('first_name')

        return super(TeamListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        context['role'] = self.type
        return context
