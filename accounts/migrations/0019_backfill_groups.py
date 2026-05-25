from django.db import migrations


def backfill_groups(apps, schema_editor):
    Animal = apps.get_model('accounts', 'Animal')
    AnimalGroup = apps.get_model('accounts', 'AnimalGroup')
    DailyFarmDiary = apps.get_model('accounts', 'DailyFarmDiary')

    Animal.objects.filter(category='cattle').update(category='cow')
    Animal.objects.filter(category='poultry').update(category='hen')

    pairs = Animal.objects.values_list('owner_id', 'category').distinct()
    for owner_id, category in pairs:
        AnimalGroup.objects.get_or_create(owner_id=owner_id, category=category)

    diary_qs = DailyFarmDiary.objects.filter(animal__isnull=False).select_related('animal')
    for entry in diary_qs:
        group = AnimalGroup.objects.filter(
            owner_id=entry.animal.owner_id,
            category=entry.animal.category,
        ).first()
        if group is None:
            continue
        entry.group_id = group.id
        entry.animal = None
        entry.save(update_fields=['group', 'animal'])


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_animalgroup_dailyfarmdiary_group'),
    ]

    operations = [
        migrations.RunPython(backfill_groups, reverse_noop),
    ]
