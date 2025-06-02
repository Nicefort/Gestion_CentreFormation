from django.db import models
import os

# ---------- ZONE GÉOGRAPHIQUE ----------

class Region(models.Model):
    numero = models.PositiveIntegerField(unique=True, help_text="Numéro de la région")
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ['numero']

    def __str__(self):
        return f"Région N°{self.numero} : {self.nom}"



class Prefecture(models.Model):
    nom = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='prefectures')

    class Meta:
        unique_together = ('nom', 'region')

    def __str__(self):
        return f"{self.nom} ({self.region})"


class SousPrefecture(models.Model):
    nom = models.CharField(max_length=50)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.CASCADE, related_name='sousprefectures')

    class Meta:
        unique_together = ('nom', 'prefecture')

    def __str__(self):
        return f"{self.nom} ({self.prefecture})"


class Commune(models.Model):
    nom = models.CharField(max_length=50)
    sous_prefecture = models.ForeignKey(SousPrefecture, on_delete=models.CASCADE, related_name='communes')

    class Meta:
        unique_together = ('nom', 'sous_prefecture')

    def __str__(self):
        return f"{self.nom} ({self.sous_prefecture})"


# ---------- DOMAINES ET CIBLES ----------

class Secteur(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nom


class PublicCible(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nom


# ---------- CENTRE DE FORMATION ----------

class CentreFormation(models.Model):
    intitule = models.CharField(max_length=100, unique=True)
    sigle = models.CharField(max_length=20, blank=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='centres')
    secteurs = models.ManyToManyField(Secteur, related_name='centres')
    public_cibles = models.ManyToManyField(PublicCible, related_name='centres', blank=True)
    adresse = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    capacite_max = models.PositiveIntegerField(default=0, help_text="Capacité d'accueil maximale")

    def __str__(self):
        return self.intitule


# ---------- DOCUMENTS ADMINISTRATIFS ----------

def document_upload_path(instance, filename):
    return os.path.join("documents", f"centre_{instance.centre.id}", filename)

class DocumentAdministratif(models.Model):
    centre = models.OneToOneField(CentreFormation, on_delete=models.CASCADE, related_name='document_administratif')

    contrat_bail = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    titre_foncier = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    autre_document = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    immatriculation_cnss = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    immatriculation_acfpe = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    acquittement_fiscal = models.FileField(upload_to=document_upload_path, blank=True, null=True)
    agrement_valide = models.FileField(upload_to=document_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Documents pour {self.centre}"


# ---------- PERSONNE DE RÉFÉRENCE ----------

class PersonneReference(models.Model):
    centre = models.OneToOneField(CentreFormation, on_delete=models.CASCADE, related_name='personne_reference')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    fonction_libre = models.CharField(max_length=50, help_text="Ex : directeur, tuteur, etc.")

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.fonction_libre})"
