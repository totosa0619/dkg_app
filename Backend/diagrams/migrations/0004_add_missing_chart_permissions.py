from django.db import migrations

permissions = [
    "circularMindmap3D",
    "multiCube3D",

    "radarChartMenu",
    "radarChartSection",

    "londonMapStats",
    "ukMapStats",
    "UAEGeoMapStats",
    "walesMapStats",
    "ChisinauMap",
    "gulfRegionMap",
    "GermanyMap",
    "ukmapnew",
    "ScotlandMap",
    "ManchesterMap",
    "ScotlandMapStats",
    "ManchesterMapStats",
    "northIrelandMap",
    "northIrelandMapStats",
    "franceMap",
    "londonMapDark",
    "londonStatsDark",
    "canadaMap",
    "ukMapStatsDark",
    "ukMapDark",
    "chinaMapStats",
    "ukMapStatic",
    "moldovaMapStats",
    "israelMap",
    "japanMap",
    "circularInfographUK",
    "timeSeriesChart",
    "promoBanner",
    "treeMap",
    "leaderBoard",
    "tubeMap",
    "forceDirectedTree",
    "heatMap",
    "heatMapGrid",
    "portraitImage",
]


def get_permission_name(chart, prefix="view"):
    return f"{prefix}_{chart.lower()}"


def revert_default_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    view_permissions = []
    for p in permissions:
        view_permissions.append(get_permission_name(p, "view"))
        view_permissions.append(get_permission_name(p, "edit"))
    Permission.objects.filter(codename__in=view_permissions).delete()


def populate_default_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    group_type = ContentType.objects.get(app_label="auth", model="group")
    user_type = ContentType.objects.get(app_label="auth", model="user")
    Permission = apps.get_model("auth", "Permission")
    to_create = []
    for p in permissions:
        to_create.append(Permission(
            content_type=group_type,
            codename=get_permission_name(p, "view"),
            name=f"view - ({p.lower()})",
        ))
        to_create.append(Permission(
            content_type=group_type,
            codename=get_permission_name(p, "edit"),
            name=f"edit - ({p.lower()})",
        ))
        to_create.append(Permission(
            content_type=user_type,
            codename=get_permission_name(p, "view"),
            name=f"view - ({p.lower()})",
        ))
        to_create.append(Permission(
            content_type=user_type,
            codename=get_permission_name(p, "edit"),
            name=f"edit - ({p.lower()})",
        ))

    Permission.objects.bulk_create(to_create)


class Migration(migrations.Migration):
    dependencies = [
        ('diagrams', '0003_add_chart_group_permissions'),
    ]

    operations = [
        migrations.RunPython(populate_default_permissions, revert_default_permissions),
    ]
