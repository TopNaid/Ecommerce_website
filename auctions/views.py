from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
from .models import User
from .forms import AuctionListingForm, BidForm
from .models import AuctionListing, Watchlist, Bid, Comment
from django.contrib.auth.decorators import login_required
from django.contrib import messages




def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            return redirect('index')  # Redirect to the home page or the listing's detail page after creating
    else:
        form = AuctionListingForm()
    
    return render(request, "auctions/create_listing.html", {
        "form": form
    })
def listing_detail(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    user = request.user
    on_watchlist = False

    if user.is_authenticated:
        on_watchlist = Watchlist.objects.filter(user=user, listings=listing).exists()

    form = BidForm(listing=listing) if request.method == 'GET' else BidForm(request.POST, listing=listing)

    if request.method == 'POST':
        # Handle auction closing
        if 'close_auction' in request.POST and user == listing.created_by:
            listing.is_active = False
            if listing.current_bid:
                highest_bid = listing.current_bid
                winner = Bid.objects.filter(listing=listing, bid_amount=highest_bid).first().user
                listing.winner = winner
                messages.success(request, f'The auction has been closed. The winner is {winner.username}.')
            else:
                messages.info(request, 'The auction was closed with no bids placed.')
            listing.save()
            return redirect('listing_detail', listing_id=listing.id)
        
        # Handle bid submission
        elif 'bid' in request.POST:
            if form.is_valid():
                bid = form.save(commit=False)
                bid.user = request.user
                bid.listing = listing
                bid.save()
                listing.current_bid = bid.bid_amount
                listing.save()
                messages.success(request, 'Your bid was placed successfully!')
                return redirect('listing_detail', listing_id=listing.id)
            else:
                messages.error(request, 'There was an error with your bid. Please try again.')
        
        # Handle comment submission
        elif 'comment' in request.POST:
            comment_content = request.POST.get('comment_content')
            if comment_content:
                Comment.objects.create(
                    user=user,
                    listing=listing,
                    content=comment_content
                )
                messages.success(request, 'Your comment was posted successfully!')
            else:
                messages.error(request, 'You cannot post an empty comment.')
            return redirect('listing_detail', listing_id=listing.id)
        
        elif 'watchlist' in request.POST:
            watchlist, created = Watchlist.objects.get_or_create(user=user)
            if watchlist.listings.filter(id=listing.id).exists():
                # Remove from watchlist
                watchlist.listings.remove(listing)
                messages.success(request, 'Removed from watchlist.')
            else:
                # Add to watchlist
                watchlist.listings.add(listing)
                messages.success(request, 'Added to watchlist.')
            return redirect('listing_detail', listing_id=listing.id)


    is_winner = listing.winner == user if not listing.is_active else False
    comments = listing.comments.all()

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'on_watchlist': on_watchlist,
        'form': form,
        'is_winner': is_winner,
        'comments': comments
    })



@login_required
def watchlist(request):
    user_watchlist = Watchlist.objects.get(user=request.user)
    listings = user_watchlist.listings.all()

    return render(request, 'auctions/watchlist.html', {
        'listings': listings
    })

def category_list(request):
    categories = AuctionListing.objects.values_list('category', flat=True).distinct()
    return render(request, 'auctions/category_list.html', {
        'categories': categories
    })

def category_detail(request, category_name):
    listings = AuctionListing.objects.filter(category=category_name, is_active=True)
    return render(request, 'auctions/category_detail.html', {
        'category': category_name,
        'listings': listings
    })
