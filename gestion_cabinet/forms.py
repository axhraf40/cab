from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Patient, Dentiste, Secretaire, RendezVous, Consultation, Facture, Produit, MouvementStock, CustomUser
from django.utils import timezone

class UserRegistrationForm(UserCreationForm):
    phone_regex = RegexValidator(
        regex=r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$',
        message="Le numéro de téléphone doit être au format français (ex: 0612345678, 06.12.34.56.78, +33612345678)"
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Choisissez un nom d'utilisateur"
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@email.com'
        })
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    telephone = forms.CharField(
        validators=[phone_regex],
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+33612345678 ou 0612345678'
        })
    )

    date_naissance = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    adresse = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Votre adresse complète'
        })
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choisissez un mot de passe'
        })
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'telephone', 'date_naissance', 'adresse', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.telephone = self.cleaned_data['telephone']
        user.date_naissance = self.cleaned_data['date_naissance']
        user.adresse = self.cleaned_data['adresse']
        
        if commit:
            user.save()
            # Créer l'objet correspondant au rôle
            if user.role == 'PATIENT':
                Patient.objects.create(
                    user=user,
                    telephone=user.telephone,
                    date_naissance=user.date_naissance,
                    adresse=user.adresse
                )
            elif user.role == 'DENTISTE':
                Dentiste.objects.create(
                    user=user,
                    telephone=user.telephone,
                    specialite='À définir'  # Valeur par défaut
                )
            elif user.role == 'SECRETAIRE':
                Secretaire.objects.create(
                    user=user,
                    telephone=user.telephone
                )
        return user

class RendezVousForm(forms.ModelForm):
    date_heure = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Date et heure"
    )

    class Meta:
        model = RendezVous
        fields = ['dentiste', 'date_heure', 'motif']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dentiste'].queryset = Dentiste.objects.all()

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['diagnostic', 'traitement']
        widgets = {
            'diagnostic': forms.Textarea(attrs={'rows': 4}),
            'traitement': forms.Textarea(attrs={'rows': 4}),
        }

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['montant', 'mode_paiement']
        widgets = {
            'montant': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'description', 'quantite', 'seuil_alerte', 'prix_unitaire']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'prix_unitaire': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': 1}),
        }

class DentisteForm(forms.ModelForm):
    class Meta:
        model = Dentiste
        fields = ['specialite', 'telephone']

class SecretaireForm(forms.ModelForm):
    class Meta:
        model = Secretaire
        fields = ['telephone']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'date_naissance', 'adresse', 'photo_profil']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telephone'].validators = [UserRegistrationForm.phone_regex] 