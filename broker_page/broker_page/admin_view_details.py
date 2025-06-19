from django.utils import timezone

@login_required(login_url='/admin/login/')
def admin_view_details(request, broker_id):
    broker = Broker.objects.filter(id=broker_id, is_staff=False, is_superuser=False).first()
    current_date = timezone.now().strftime('%A, %dth %B %Y')
    context = {
        'broker': broker,
        'admin_user': request.user,
        'current_date': current_date,
    }
    return render(request, 'admin/view_details.html', context) 