from django.db import models
import os

class Region(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Prefecture(models.Model):
    nom = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class SousPrefecture(models.Model):
    nom = models.CharField(max_length=100)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class Commune(models.Model):
    nom = models.CharField(max_length=100)
    sous_prefecture = models.ForeignKey(SousPrefecture, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class Secteur(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class CentreFormation(models.Model):
    secteurs = models.ManyToManyField(Secteur, related_name='centres')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    intitule = models.CharField(max_length=200)
    sigle = models.CharField(max_length=50, blank=True)
    public_cibles = models.ManyToManyField('PublicCible', related_name='centres', blank=True)
    adresse = models.CharField(max_length=30)
    telephone = models.CharField(max_length=30)
    email = models.EmailField()
    capacite_max= models.IntegerField(default=0, help_text="Capacité d'accueil maximale du centre")

    def __str__(self):
        return self.intitule

def document_upload_path(instance, filename):
    return os.path.join("documents", f"centre_{instance.centre.id}", filename)

class DocumentAdministratif(models.Model):
    centre = models.OneToOneField('CentreFormation', on_delete=models.CASCADE)

    contrat_bail = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    titre_foncier = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    autre_document = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    immatriculation_cnss = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    immatriculation_acfpe = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    acquittement_fiscal = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    agrement_valide = models.FileField(upload_to=document_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Documents administratifs pour {self.centre}"
    
class PublicCible(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom
    

class PersonneReference(models.Model):
    centre = models.ForeignKey('CentreFormation', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    fonction_libre = models.CharField(max_length=100, help_text="Ex: contact principal, tuteur, etc.")

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.fonction_libre})"
