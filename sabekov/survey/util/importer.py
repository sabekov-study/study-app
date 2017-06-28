from django.db import transaction

from survey.models import *


@transaction.atomic
def import_sites_from_file(path, listing, pub_date):
    l, created = Listing.objects.get_or_create(
        name=listing,
    )
    issue, created = l.issues.get_or_create(
        pub_date = pub_date,
    )
    with open(path, "r") as f:
        for rank, l in enumerate(f.readlines(), 1):
            sn = l.strip().lower()
            syn = None
            try:
                syn = SiteSynonym.objects.get(name=sn)
            except SiteSynonym.DoesNotExist:
                __update_synonyms([sn])
                syn = SiteSynonym.objects.get(name=sn)
            issue.entries.update_or_create(
                site=syn,
                defaults={'rank': rank},
            )



@transaction.atomic
def import_site_synonyms(path):
    with open(path, "r") as f:
        for l in f.readlines():
            grouper, synonyms = l.split(":", 1)
            synonyms = [s.lower() for s in synonyms.split()]
            __update_synonyms(synonyms)

def __update_synonyms(synonyms):
    site = None
    try:
        site = Site.objects.get(name__in=synonyms)
    except Site.DoesNotExist as e:
        site = Site.objects.create(
            name=synonyms[0],
        )
    except MultipleObjectsReturned as e:
        # sites exist for more than one synonym
        raise e

    for syn in synonyms:
        site.synonyms.get_or_create(
            name=syn,
        )
