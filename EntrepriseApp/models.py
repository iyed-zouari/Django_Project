from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator ,MaxLengthValidator, RegexValidator, ValidationError
# Create your models here.

def validate_email(value):
    if not value.endswith('@gmail.com'):
        raise ValidationError('L\'adresse e-mail doit se terminer par @gmail.com.')
    if not value:
        raise ValidationError('L\'adresse e-mail ne peut pas être vide.')


matricule_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Format du matricule fiscal invalide."
)

def _generate_user_id():
    annee = datetime.now().strftime("%Y")
    prefix = f"{annee}USER"
    last_user = Utilisateur.objects.filter(user_id__startswith=prefix).order_by('user_id').last()
    if last_user:
        last_user_id = last_user.user_id
        last_number = int(last_user_id[-2:])
        new_number = last_number + 1
    else:
        new_number = 1
    if new_number > 99:
        raise ValidationError(
            "Le nombre d'utilisateurs a atteint la limite maximale pour cette année."
        )
    
    return f"{prefix}{new_number:02d}"


class Utilisateur(AbstractUser):
    user_id = models.CharField(primary_key=True, max_length=8, unique=True)
    email = models.EmailField(unique=True,validators=[validate_email])
    telephone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('c', 'Chargeur'),('t','Transporteur')], default='c')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200,blank=False, null=False)
    matricule_fiscale = models.CharField(max_length=17,unique=True, validators=[matricule_validator])
    adresse = models.TextField(validators=[MinLengthValidator(20,"L'adresse doit contenir au moins 20 caractères."),MaxLengthValidator(400,"L'adresse ne peut pas dépasser 400 caractères.")],blank=False, null=False)
    type_entreprise = models.CharField(max_length=100,choices=[('c','Chargeur'),('t','Transporteur')],default='c')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')