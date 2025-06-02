from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import *
from .models import *
import pandas as pd


def region_view(request, pk=None):
    obj = get_object_or_404(Region, pk=pk) if pk else None
    preview_data = None
    form = RegionForm(instance=obj)

    if request.method == "POST":
        # Prévisualisation du fichier CSV
        if "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_csv(fichier)
                preview_data = df.to_dict(orient="records")
            except Exception as e:
                messages.error(request, f"Erreur de lecture du fichier CSV : {e}")

        # Importation définitive du fichier CSV
        elif "import" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_csv(fichier)
                for _, row in df.iterrows():
                    numero = row.get("numero")
                    nom = str(row.get("nom", "")).strip().upper()
                    if numero and nom:
                        Region.objects.get_or_create(numero=numero, nom=nom)
                messages.success(request, "Importation réussie !")
                return redirect("region")
            except Exception as e:
                messages.error(request, f"Erreur d'importation CSV : {e}")

        # Enregistrement manuel
        elif "save" in request.POST:
            form = RegionForm(request.POST, instance=obj)
            if form.is_valid():
                region = form.save(commit=False)
                region.nom = region.nom.strip().upper()  # Normalisation
                region.save()
                return redirect("region")
            else:
                messages.error(request, "Veuillez corriger les erreurs du formulaire.")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("region")

    # Chargement standard
    regions = Region.objects.all()
    return render(
        request,
        "pages/region.html",
        {
            "form": form,
            "regions": regions,
            "obj": obj,
            "preview_data": preview_data,
        },
    )

def region_detail(request, pk):
    region = get_object_or_404(Region, pk=pk)
    
    # ✅ Correction ici : utilise le related_name
    prefectures = region.prefectures.all().select_related('region')
    
    try:
        prefecture_ids = list(map(int, request.GET.getlist("prefectures")))
    except (ValueError, TypeError):
        prefecture_ids = []

    try:
        secteur_ids = list(map(int, request.GET.getlist("secteurs")))
    except (ValueError, TypeError):
        secteur_ids = []

    try:
        communes_qs = Commune.objects.filter(
            sous_prefecture__prefecture__region=region
        ).select_related('sous_prefecture__prefecture__region')

        if prefecture_ids:
            communes_qs = communes_qs.filter(
                sous_prefecture__prefecture_id__in=prefecture_ids
            )

        centres = CentreFormation.objects.filter(
            commune__in=communes_qs
        ).select_related('commune').prefetch_related('secteurs')

        if secteur_ids:
            centres = centres.filter(
                secteurs__id__in=secteur_ids
            ).distinct()

        nombre_centres = centres.count()

    except Exception as e:
        print(f"Erreur dans la requête: {e}")
        centres = CentreFormation.objects.none()
        nombre_centres = 0

    secteurs = Secteur.objects.filter(
        centres__commune__sous_prefecture__prefecture__region=region
    ).distinct()

    data = []
    for pref in prefectures:
        sous_data = []
        for sous in pref.sousprefectures.all().select_related('prefecture'):
            commune_data = []
            for commune in sous.communes.all().select_related('sous_prefecture'):
                centres_commune = centres.filter(commune=commune)
                commune_data.append((commune, centres_commune))
            sous_data.append((sous, commune_data))
        data.append((pref, sous_data))

    return render(request, "pages/region_detail.html", {
        "region": region,
        "hierarchie": data,
        "nombre_centres": nombre_centres,
        "centres": centres,
        "prefecture_ids": prefecture_ids,
        "secteur_ids": secteur_ids,
        "secteurs": secteurs,
        "prefectures": prefectures,
    })


# View qui gere les prefectures
def prefecture_view(request, pk=None):
    # Récupération de l'objet à modifier (s'il y a un pk dans l'URL)
    if pk:
        obj = get_object_or_404(Prefecture, pk=pk)
        form = PrefectureForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = PrefectureForm(request.POST or None)

    if request.method == "POST":
        # Enregistrement ou modification
        if "save" in request.POST and form.is_valid():
            form.save()
            messages.success(request, "Préfecture enregistrée avec succès.")
            return redirect("prefecture")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            messages.success(request, "Préfecture supprimée avec succès.")
            return redirect("prefecture")

        # Prévisualisation CSV
        elif "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                # Lecture du fichier CSV avec pandas
                df = pd.read_csv(fichier)

                # Enregistrement dans la session pour l'importation future
                request.session["df_prefecture"] = df.to_dict(orient="records")

                messages.info(request, "Prévisualisation chargée. Cliquez sur 'Importer' pour confirmer.")
                return render(
                    request,
                    "pages/prefecture.html",
                    {
                        "form": form,
                        "prefectures": Prefecture.objects.all(),
                        "df_preview": df.to_dict(orient="records"),
                        "obj": obj,
                    },
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de la lecture du fichier CSV : {e}")

        # Importation finale après prévisualisation
        elif "import" in request.POST:
            data = request.session.pop("df_prefecture", None)
            if data:
                for row in data:
                    try:
                        nom = row.get("nom")
                        region_nom = row.get("region")

                        if not nom or not region_nom:
                            messages.warning(request, f"Ligne incomplète ignorée : {row}")
                            continue

                        # Recherche de la région par son nom (insensible à la casse)
                        try:
                            region_instance = Region.objects.get(nom__iexact=region_nom.strip())
                        except Region.DoesNotExist:
                            messages.warning(request, f"Région '{region_nom}' non trouvée. Ligne ignorée.")
                            continue

                        # Création de la préfecture
                        Prefecture.objects.create(nom=nom.strip(), region=region_instance)

                    except Exception as e:
                        messages.error(request, f"Erreur lors de l’importation d’une ligne : {e}")

                messages.success(request, "Importation terminée avec succès.")
            else:
                messages.error(request, "Aucune donnée disponible pour l'importation.")
            return redirect("prefecture")

    # Rendu de la page principale (GET ou retour après action)
    return render(
        request,
        "pages/prefecture.html",
        {
            "form": form,
            "prefectures": Prefecture.objects.all(),
            "obj": obj,
        },
    )

def prefecture_detail(request, pk):
    prefecture = get_object_or_404(Prefecture, pk=pk)

    # ✅ Correction ici
    sous_prefectures = prefecture.sousprefectures.all().select_related('prefecture')

    try:
        sous_prefecture_ids = list(map(int, request.GET.getlist("sous_prefectures")))
    except (ValueError, TypeError):
        sous_prefecture_ids = []

    try:
        secteur_ids = list(map(int, request.GET.getlist("secteurs")))
    except (ValueError, TypeError):
        secteur_ids = []

    try:
        communes_qs = Commune.objects.filter(
            sous_prefecture__prefecture=prefecture
        ).select_related('sous_prefecture__prefecture')

        if sous_prefecture_ids:
            communes_qs = communes_qs.filter(
                sous_prefecture_id__in=sous_prefecture_ids
            )

        centres = CentreFormation.objects.filter(
            commune__in=communes_qs
        ).select_related('commune').prefetch_related('secteurs')

        if secteur_ids:
            centres = centres.filter(
                secteurs__id__in=secteur_ids
            ).distinct()

        nombre_centres = centres.count()

    except Exception as e:
        print(f"Erreur dans la requête: {e}")
        centres = CentreFormation.objects.none()
        nombre_centres = 0

    secteurs = Secteur.objects.filter(
        centres__commune__sous_prefecture__prefecture=prefecture
    ).distinct()

    data = []
    for sous in sous_prefectures:
        commune_data = []
        for commune in sous.communes.all().select_related('sous_prefecture'):
            centres_commune = centres.filter(commune=commune)
            commune_data.append((commune, centres_commune))
        data.append((sous, commune_data))

    return render(request, "pages/prefecture_detail.html", {
        "prefecture": prefecture,
        "hierarchie": data,
        "nombre_centres": nombre_centres,
        "centres": centres,
        "sous_prefecture_ids": sous_prefecture_ids,
        "secteur_ids": secteur_ids,
        "secteurs": secteurs,
        "sous_prefectures": sous_prefectures,
    })




# Vue qui gere les Sous Prefectures
def sousprefecture_view(request, pk=None):
    if pk:
        obj = get_object_or_404(SousPrefecture, pk=pk)
        form = SousPrefectureForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = SousPrefectureForm(request.POST or None)

    if request.method == "POST":
        # Enregistrement manuel
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("sous_prefecture")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("sous_prefecture")

        # Prévisualisation fichier CSV
        elif "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_csv(fichier)
                request.session["df_sousprefecture"] = df.to_dict(orient="records")
                messages.info(request, "Prévisualisation chargée. Cliquez sur 'Importer' pour confirmer.")
                return render(
                    request,
                    "pages/sousprefecture.html",
                    {
                        "form": form,
                        "sousprefectures": SousPrefecture.objects.all(),
                        "df_preview": df.to_dict(orient="records"),
                        "obj": obj,
                    },
                )
            except Exception as e:
                messages.error(request, f"Erreur lecture fichier CSV : {e}")

        # Importation depuis la session
        elif "import" in request.POST:
            data = request.session.pop("df_sousprefecture", None)
            if data:
                for row in data:
                    try:
                        nom = row.get("nom")
                        prefecture_nom = row.get("prefecture") or row.get("prefecture_nom")
                        if not prefecture_nom:
                            messages.warning(request, f"Préfecture manquante pour la sous-préfecture '{nom}'. Ligne ignorée.")
                            continue
                        prefecture = Prefecture.objects.get(nom__iexact=prefecture_nom.strip())
                        SousPrefecture.objects.create(nom=nom.strip(), prefecture=prefecture)
                    except Prefecture.DoesNotExist:
                        messages.warning(request, f"Préfecture '{prefecture_nom}' non trouvée pour la sous-préfecture '{nom}'. Ligne ignorée.")
                    except Exception as e:
                        messages.error(request, f"Erreur import ligne pour '{nom}' : {e}")
                messages.success(request, "Importation terminée.")
            else:
                messages.error(request, "Aucune donnée à importer.")
            return redirect("sous_prefecture")

    return render(
        request,
        "pages/sousprefecture.html",
        {
            "form": form,
            "sousprefectures": SousPrefecture.objects.all(),
            "obj": obj,
        },
    )



def sousprefecture_detail(request, pk):
    sous_prefecture = get_object_or_404(SousPrefecture, pk=pk)

    # ✅ Correction ici
    communes = sous_prefecture.communes.all().select_related('sous_prefecture')

    try:
        commune_ids = list(map(int, request.GET.getlist("communes")))
    except (ValueError, TypeError):
        commune_ids = []

    try:
        secteur_ids = list(map(int, request.GET.getlist("secteurs")))
    except (ValueError, TypeError):
        secteur_ids = []

    try:
        communes_qs = communes
        if commune_ids:
            communes_qs = communes_qs.filter(id__in=commune_ids)

        centres = CentreFormation.objects.filter(
            commune__in=communes_qs
        ).select_related('commune').prefetch_related('secteurs')

        if secteur_ids:
            centres = centres.filter(
                secteurs__id__in=secteur_ids
            ).distinct()

        nombre_centres = centres.count()

    except Exception as e:
        print(f"Erreur dans la requête: {e}")
        centres = CentreFormation.objects.none()
        nombre_centres = 0

    secteurs = Secteur.objects.filter(
        centres__commune__sous_prefecture=sous_prefecture
    ).distinct()

    data = []
    for commune in communes:
        centres_commune = centres.filter(commune=commune)
        data.append((commune, centres_commune))

    return render(request, "pages/sousprefecture_detail.html", {
        "sous_prefecture": sous_prefecture,
        "hierarchie": data,
        "nombre_centres": nombre_centres,
        "centres": centres,
        "commune_ids": commune_ids,
        "secteur_ids": secteur_ids,
        "secteurs": secteurs,
        "communes": communes,
    })








# Vue qui gere les Communes
def commune_view(request, pk=None):
    if pk:
        obj = get_object_or_404(Commune, pk=pk)
        form = CommuneForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = CommuneForm(request.POST or None)

    if request.method == "POST":
        # Enregistrement manuel
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("commune")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("commune")

        # Prévisualisation fichier CSV
        elif "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_csv(fichier)
                request.session["df_commune"] = df.to_dict(orient="records")
                messages.info(request, "Prévisualisation chargée. Cliquez sur 'Importer' pour confirmer.")
                return render(
                    request,
                    "pages/commune.html",
                    {
                        "form": form,
                        "communes": Commune.objects.all(),
                        "df_preview": df.to_dict(orient="records"),
                        "obj": obj,
                    },
                )
            except Exception as e:
                messages.error(request, f"Erreur lecture fichier CSV : {e}")

        # Importation depuis la session
        elif "import" in request.POST:
            data = request.session.pop("df_commune", None)
            if data:
                for row in data:
                    try:
                        nom = row.get("nom")
                        sous_prefecture_nom = row.get("sous_prefecture") or row.get("sous_prefecture_nom")
                        if not sous_prefecture_nom:
                            messages.warning(request, f"Sous-préfecture manquante pour la commune '{nom}'. Ligne ignorée.")
                            continue
                        sous_prefecture = SousPrefecture.objects.get(nom__iexact=sous_prefecture_nom.strip())
                        Commune.objects.create(nom=nom.strip(), sous_prefecture=sous_prefecture)
                    except SousPrefecture.DoesNotExist:
                        messages.warning(request, f"Sous-préfecture '{sous_prefecture_nom}' non trouvée pour la commune '{nom}'. Ligne ignorée.")
                    except Exception as e:
                        messages.error(request, f"Erreur import ligne pour '{nom}' : {e}")
                messages.success(request, "Importation terminée.")
            else:
                messages.error(request, "Aucune donnée à importer.")
            return redirect("commune")

    return render(
        request,
        "pages/commune.html",
        {
            "form": form,
            "communes": Commune.objects.all(),
            "obj": obj,
        },
    )



def commune_detail(request, pk):
    # Récupération de la commune avec gestion d'erreur 404
    commune = get_object_or_404(Commune, pk=pk)

    # Traitement des paramètres de filtre GET
    try:
        secteur_ids = list(map(int, request.GET.getlist("secteurs")))
    except (ValueError, TypeError):
        secteur_ids = []

    # Construction de la requête des centres
    try:
        centres = CentreFormation.objects.filter(
            commune=commune
        ).select_related('commune').prefetch_related('secteurs')

        # Appliquer le filtre des secteurs si spécifié
        if secteur_ids:
            centres = centres.filter(
                secteurs__id__in=secteur_ids
            ).distinct()

        nombre_centres = centres.count()

    except Exception as e:
        print(f"Erreur dans la requête: {e}")
        centres = CentreFormation.objects.none()
        nombre_centres = 0

    # Obtenir les secteurs disponibles pour cette commune
    secteurs = Secteur.objects.filter(
        centres__commune=commune
    ).distinct()

    return render(request, "pages/commune_detail.html", {
        "commune": commune,
        "centres": centres,
        "nombre_centres": nombre_centres,
        "secteurs": secteurs,
        "secteur_ids": secteur_ids,
    })





# Vue qui gere les Secteurs
def secteur_view(request, pk=None):
    if pk:
        obj = get_object_or_404(Secteur, pk=pk)
        form = SecteurForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = SecteurForm(request.POST or None)

    if request.method == "POST":
        # Enregistrement manuel
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("secteur")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("secteur")

        # Prévisualisation fichier CSV
        elif "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                import pandas as pd
                df = pd.read_csv(fichier)

                # Vérifie que la colonne 'nom' existe
                if "nom" not in df.columns:
                    messages.error(request, "La colonne 'nom' est manquante dans le fichier CSV.")
                else:
                    preview_data = df.to_dict(orient="records")
                    request.session["df_secteur"] = preview_data
                    messages.info(request, "Prévisualisation chargée.")
                    return render(
                        request,
                        "pages/secteur.html",
                        {
                            "form": form,
                            "secteurs": Secteur.objects.all(),
                            "df_preview": preview_data,
                            "obj": obj,
                        },
                    )
            except Exception as e:
                messages.error(request, f"Erreur lecture fichier CSV : {e}")

        # Importation depuis la session
        elif "import" in request.POST:
            data = request.session.pop("df_secteur", None)
            if data:
                for row in data:
                    try:
                        Secteur.objects.create(**row)
                    except Exception as e:
                        messages.error(request, f"Erreur import ligne : {e}")
                messages.success(request, "Importation réussie !")
            else:
                messages.error(request, "Aucune donnée à importer.")
            return redirect("secteur")

    return render(
        request,
        "pages/secteur.html",
        {
            "form": form,
            "secteurs": Secteur.objects.all(),
            "obj": obj,
        },
    )





# Vue qui gere les Public Cible
def publiccible_view(request, pk=None):
    if pk:
        obj = get_object_or_404(PublicCible, pk=pk)
        form = PublicCibleForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = PublicCibleForm(request.POST or None)

    if request.method == "POST":
        # Enregistrement manuel
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("publiccible")

        # Suppression
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("publiccible")

        # Prévisualisation fichier CSV
        elif "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                import pandas as pd
                df = pd.read_csv(fichier)
                request.session["df_publiccible"] = df.to_dict()
                messages.info(request, "Prévisualisation chargée.")
                return render(
                    request,
                    "pages/publiccible.html",
                    {
                        "form": form,
                        "publiccibles": PublicCible.objects.all(),
                        "df_preview": df.to_dict(orient="records"),
                        "obj": obj,
                    },
                )
            except Exception as e:
                messages.error(request, f"Erreur lecture fichier CSV : {e}")

        # Importation depuis la session
        elif "import" in request.POST:
            data = request.session.pop("df_publiccible", None)
            if data:
                for row in data.values():
                    try:
                        PublicCible.objects.create(**row)
                    except Exception as e:
                        messages.error(request, f"Erreur import ligne: {e}")
                messages.success(request, "Importation réussie !")
            else:
                messages.error(request, "Aucune donnée à importer.")
            return redirect("publiccible")

    return render(
        request,
        "pages/publiccible.html",
        {
            "form": form,
            "publiccibles": PublicCible.objects.all(),
            "obj": obj,
        },
    )






def centre_formation_view(request):
    # Récupérer les données des formulaires de chaque étape
    centres = CentreFormation.objects.all()
    document =DocumentAdministratif.objects.all()
    communes = Commune.objects.all()
    secteurs = Secteur.objects.all()

    
    form_centre = CentreFormationForm(request.POST or None)
    form_docs = DocumentAdministratifForm(request.POST or None, request.FILES or None)
    form_ref = PersonneReferenceForm(request.POST or None)

    # Si la méthode est POST et que les trois formulaires sont valides
    if request.method == "POST":
        if form_centre.is_valid() and form_docs.is_valid() and form_ref.is_valid():
            # Sauvegarder le CentreFormation
            centre = form_centre.save()

            # Sauvegarder les documents avec la clé étrangère vers CentreFormation
            doc = form_docs.save(commit=False)
            doc.centre = centre  # Associer le document au centre
            doc.save()

            # Sauvegarder la personne de référence avec la clé étrangère vers CentreFormation
            ref = form_ref.save(commit=False)
            ref.centre = centre  # Associer la référence au centre
            ref.save()

            # Message de succès
            messages.success(
                request, "Les informations ont été enregistrées avec succès !"
            )
            return redirect(
                "centre_formation"
            )  # Rediriger vers une page de succès après soumission

    # Rendre la page avec les formulaires
    return render(
        request,
        "pages/cf.html",
        {
            "form_centre": form_centre,
            "form_docs": form_docs,
            "form_ref": form_ref,
            "centres": centres,
            "document": document,
            "communes": communes,
            "secteurs": secteurs,
        },
    )


def centre_detail(request, pk):
    centre = get_object_or_404(
        CentreFormation.objects.select_related(
            'commune__sous_prefecture__prefecture__region',
            'personne_reference',
            'document_administratif'  # 👈 attention au nom exact du related_name
        ).prefetch_related(
            'secteurs',
            'public_cibles',
        ),
        pk=pk
    )

    try:
        documents = centre.document_administratif  # 👈 corriger ici
    except DocumentAdministratif.DoesNotExist:
        documents = None

    return render(request, "pages/cf_detail.html", {
        "centre": centre,
        "commune": centre.commune,
        "sous_prefecture": centre.commune.sous_prefecture,
        "prefecture": centre.commune.sous_prefecture.prefecture,
        "region": centre.commune.sous_prefecture.prefecture.region,
        "secteurs": centre.secteurs.all(),
        "publics_cibles": centre.public_cibles.all(),
        "documents": documents,
        "personne_reference": centre.personne_reference,
    })

def index(request):
    return render(request, "pages/index.html")


# def calendar(request):
#    return render(request,"pages/index.html")
