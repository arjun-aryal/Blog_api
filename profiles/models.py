from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel

User = get_user_model()

class Profile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = ("M","Male")
        FEMALE = ("F","Female")
        OTHER = ("O","Other")
        
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    about_me = models.TextField()
    gender = models.CharField(choices=Gender.choices,default=Gender.MALE,max_length=10)
    
    phone_number = models.CharField(max_length=15)
    country = models.CharField(max_length=20,blank=True)
    city = models.CharField(max_length=200,blank=True)
    
    profile_photo = models.ImageField(default="#")
    twitter_handle = models.CharField(max_length=50,blank=True)
    
    followers= models.ManyToManyField("self",symmetrical=False,blank=True,related_name="following")

    def __str__(self):
        return f"{self.user.first_name}'s Profile"
    
    def follow(self,profile):
        self.followers.add(profile) #add the follower
        
    def unfollow(self,profile):
        self.followers.remove(profile) #unfollow 
    
    def check_following(self,profile):
        return self.followers.filter(pkid=profile.pkid).exists