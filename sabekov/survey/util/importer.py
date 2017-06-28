from django.db import transaction

from survey.models import *


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
