import uuid
import boto3
import os
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
<<<<<<< HEAD
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Campaign, Photo
=======
from django.db.models import Sum
from .models import Campaign, Donation, Photo
>>>>>>> main
from .forms import DonationForm

# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def campaigns_index(request):
  campaigns = Campaign.objects.all()
  return render(request, 'campaigns/index.html', {
    'campaigns': campaigns
  })

def campaigns_detail(request, campaign_id):
  campaign = Campaign.objects.get(id=campaign_id)
  donations = Donation.objects.filter(campaign=campaign)
  total_donations = donations.aggregate(Sum('amount'))['amount__sum'] or 0
  if total_donations is not None:
      goal_percentage = int(total_donations / campaign.goal * 100)
  else:
      goal_percentage = 0
  print(goal_percentage)
  donation_form = DonationForm()
  return render(request, 'campaigns/detail.html', {
    'campaign': campaign, 'donations': donations, 'total_donations': total_donations,'goal_percentage': goal_percentage, 'donation_form': donation_form
  })

class CampaignCreate(LoginRequiredMixin, CreateView):
  model = Campaign
  fields = ['title', 'category', 'goal', 'link', 'about']
  def form_valid(self, form):
    form.instance.user = self.request.user 
    return super().form_valid(form)

class CampaignDelete(LoginRequiredMixin, DeleteView):
  model = Campaign
  success_url = '/campaigns'

class CampaignUpdate(LoginRequiredMixin, UpdateView):
  model = Campaign
  fields = ['title', 'category', 'goal', 'link', 'about']
  success_url = ''

@login_required
def add_donation(request, campaign_id):
  form = DonationForm(request.POST)
  if form.is_valid():
    new_donation = form.save(commit=False)
    new_donation.campaign_id = campaign_id
    new_donation.save()
  return redirect('detail', campaign_id=campaign_id)

@login_required
def add_photo(request, campaign_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # build the full url string
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            Photo.objects.create(url=url, campaign_id=campaign_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('detail', campaign_id=campaign_id)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)
