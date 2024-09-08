from .models import Watchlist

def watchlist_count(request):
    if request.user.is_authenticated:
        try:
            watchlist = Watchlist.objects.get(user=request.user)
            count = watchlist.listings.count()
        except Watchlist.DoesNotExist:
            count = 0
    else:
        count = 0
    return {
        'watchlist_count': count
    }
