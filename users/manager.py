from django.contrib.auth.models import BaseUserManager

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def email_validator(self,email):
        # Checks if email syntax is valid
        try:
            validate_email(email)
            return True
        except ValidationError:
            raise ValidationError(_("Provide a Valid Email Address"))
    
    def create_user(self,first_name, last_name, email, password, **extra_fields):
        if not first_name:
            raise ValidationError(_("User must have First NMame."))
        if not last_name:
            raise ValidationError(_("User must have Last Name."))
        
        if email:
            email = self.normalize_email(email) #Standardizes email string
            self.email_validator(email)
        else:
            raise ValidationError(_("User must have an Email Address."))
        
        user = self.model(first_name=first_name,last_name=last_name,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Super user must have is_staff set to True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Super user must have is_superuser set to True."))

        if not password:
            raise ValueError(_("Superuser must have a password."))
        
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
            
            user = self.create_user(first_name, last_name, email, password, **extra_fields)
            return user