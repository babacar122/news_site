from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('VISITOR', 'Visiteur'),
        ('EDITOR', 'Éditeur'),
        ('ADMIN', 'Administrateur'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='VISITOR')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_editor(self):
        return self.role in ['EDITOR', 'ADMIN']
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

class AuthToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Token for {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        super().save(*args, **kwargs)
    
    @classmethod
    def create_token(cls, user, days=30):
        from django.utils.timezone import now, timedelta
        return cls.objects.create(
            user=user,
            expires_at=now() + timedelta(days=days)
        )