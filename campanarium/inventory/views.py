from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import BellForm, FeedbackForm
from .models import Bell, Carillon, Founder, Tower


def _paginate(request, queryset, per_page=25):
    """Paginate a queryset and return (page, querystring-without-page) so list
    templates can keep active filters in their page links."""
    page = Paginator(queryset, per_page).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return page, params.urlencode()


def home_view(request):
    # Landing page: headline counts + the most recently added bells.
    context = {
        'bell_count': Bell.objects.count(),
        'carillon_count': Carillon.objects.count(),
        'tower_count': Tower.objects.count(),
        'founder_count': Founder.objects.count(),
        'recent_bells': Bell.objects.order_by('-created_at')[:6],
    }
    return render(request, 'home.html', context)


# --- Bells -------------------------------------------------------------------

def bell_view(request):
    # Full bell list, optionally filtered by function, paginated.
    bells = Bell.objects.all().order_by('name')
    selected_function = request.GET.get('function', '')
    if selected_function:
        bells = bells.filter(function=selected_function)
    page, querystring = _paginate(request, bells)
    context = {
        'page_obj': page,
        'querystring': querystring,
        'function_choices': Bell.FUNCTION_CHOICES,
        'selected_function': selected_function,
    }
    return render(request, 'bells.html', context)


def bell_detail_view(request, pk):
    # One bell with everything linked to it. select_related on each junction
    # avoids a query per related row when the template loops.
    bell = get_object_or_404(Bell, pk=pk)
    context = {
        'bell': bell,
        'partials': bell.partials.all(),
        'founder_links': bell.founder_links.select_related('founder'),
        'tower_links': bell.tower_links.select_related('tower'),
        'carillon_links': bell.carillon_links.select_related('carillon', 'carillon__tower'),
        'files': bell.files.all(),
    }
    return render(request, 'bell_detail.html', context)


def add_bell_view(request):
    # Create a bell (its own attributes only; relations are linked afterwards).
    if request.method == 'POST':
        form = BellForm(request.POST)
        if form.is_valid():
            bell = form.save(commit=False)
            if request.user.is_authenticated:
                bell.created_by = request.user
            bell.save()
            messages.success(request, f'Klok "{bell.name or "zonder naam"}" is toegevoegd.')
            return redirect('bell_detail', pk=bell.pk)
    else:
        form = BellForm()
    return render(request, 'add_bell.html', {'form': form})


# --- Carillons ---------------------------------------------------------------

def carillon_view(request):
    # select_related('tower') because the card shows the tower name.
    carillons = Carillon.objects.select_related('tower').all()
    page, querystring = _paginate(request, carillons, per_page=24)
    return render(request, 'carillons.html', {'page_obj': page, 'querystring': querystring})


def carillon_detail_view(request, pk):
    carillon = get_object_or_404(Carillon.objects.select_related('tower'), pk=pk)
    context = {
        'carillon': carillon,
        'bell_links': carillon.bell_links.select_related('bell').order_by('bell__year'),
    }
    return render(request, 'carillon_detail.html', context)


# --- Towers ------------------------------------------------------------------

def tower_view(request):
    page, querystring = _paginate(request, Tower.objects.all(), per_page=24)
    return render(request, 'towers.html', {'page_obj': page, 'querystring': querystring})


def tower_detail_view(request, pk):
    tower = get_object_or_404(Tower, pk=pk)
    context = {
        'tower': tower,
        'carillons': tower.carillons.all(),
        'bell_links': tower.bell_links.select_related('bell'),
    }
    return render(request, 'tower_detail.html', context)


# --- Founders (klokkengieters) ----------------------------------------------

def manufacturer_view(request):
    page, querystring = _paginate(request, Founder.objects.all())
    return render(request, 'manufacturers.html', {'page_obj': page, 'querystring': querystring})


def manufacturer_detail_view(request, pk):
    founder = get_object_or_404(Founder, pk=pk)
    context = {
        'founder': founder,
        'bell_links': founder.bell_links.select_related('bell'),
    }
    return render(request, 'manufacturer_detail.html', context)


# --- Search ------------------------------------------------------------------

def search_view(request):
    # Combined (AND) filters over bells. Founder and location filters reach
    # through the junction tables — a strength of the normalised schema.
    query = request.GET.get('q', '').strip()
    function = request.GET.get('function', '')
    year_from = request.GET.get('year_from', '').strip()
    year_to = request.GET.get('year_to', '').strip()
    founder = request.GET.get('founder', '').strip()
    location = request.GET.get('location', '').strip()

    has_criteria = any([query, function, year_from, year_to, founder, location])
    page = querystring = None
    if has_criteria:
        results = Bell.objects.all()
        if query:
            results = results.filter(
                Q(name__icontains=query)
                | Q(inscription__icontains=query)
                | Q(comments__icontains=query)
            )
        if function:
            results = results.filter(function=function)
        if year_from.isdigit():
            results = results.filter(year__gte=int(year_from))
        if year_to.isdigit():
            results = results.filter(year__lte=int(year_to))
        if founder:
            results = results.filter(founder_links__founder__primary_name__icontains=founder)
        if location:
            results = results.filter(
                Q(tower_links__tower__name__icontains=location)
                | Q(tower_links__tower__city__icontains=location)
            )
        # distinct() because the relational filters can join multiple rows per bell.
        page, querystring = _paginate(request, results.distinct().order_by('name'))

    context = {
        'query': query, 'function': function,
        'year_from': year_from, 'year_to': year_to,
        'founder': founder, 'location': location,
        'function_choices': Bell.FUNCTION_CHOICES,
        'page_obj': page, 'querystring': querystring,
        'has_criteria': has_criteria,
    }
    return render(request, 'search.html', context)


# --- Feedback (beta testing) -------------------------------------------------

def feedback_view(request):
    # Both the floating widget (base.html) and the standalone page post here.
    # page_url and created_by are captured server-side, not typed by the tester.
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        page = request.POST.get('page') or request.META.get('HTTP_REFERER', '')
        back = page if page and url_has_allowed_host_and_scheme(
            page, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
        ) else reverse('home')

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.page_url = page[:300]
            if request.user.is_authenticated:
                feedback.created_by = request.user
            feedback.save()
            messages.success(request, 'Bedankt voor je feedback!')
            return redirect(back)
        # The modal can't show inline errors, so report and bounce back.
        if request.POST.get('from_modal'):
            messages.error(request, 'Feedback niet verstuurd — schrijf eerst een bericht.')
            return redirect(back)
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})
