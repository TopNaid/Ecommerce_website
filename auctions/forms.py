from django import forms
from django.core.exceptions import ValidationError
from .models import AuctionListing
from .models import Bid
from .models import Comment

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Title',
            'description' : 'Description',
            'starting_bid' : 'Starting Bid',
            'image_url': 'Image URL',
            'category':'Category'
        }

class BidForm(forms.ModelForm):
    bid_amount = forms.DecimalField(label='Bid Amount', max_digits=10, decimal_places=2)
    
    class Meta:
        model = Bid
        fields = ['bid_amount']

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        super(BidForm, self).__init__(*args, **kwargs)

    def clean_bid_amount(self):
        bid_amount = self.cleaned_data['bid_amount']

        if self.listing:
            if bid_amount < self.listing.starting_bid:
                raise ValidationError(f"Your bid must be at least as large as the starting bid of {self.listing.starting_bid}")
            
            if self.listing.current_bid and bid_amount <= self.listing.current_bid:
                raise ValidationError(f"Your bid must be greater than the current bid of {self.listing.current_bid}")
        
        return bid_amount
    


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment...'}),
        }
        labels = {
            'content': ''
        }
