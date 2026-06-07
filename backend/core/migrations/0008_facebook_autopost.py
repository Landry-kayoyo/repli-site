from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_color_to_skill'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='facebook_auto_post',
            field=models.BooleanField(
                default=False,
                verbose_name='Publier automatiquement sur Facebook',
                help_text='Quand activé, chaque nouvelle publication est partagée automatiquement sur ta Page Facebook.'
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='facebook_page_id',
            field=models.CharField(
                max_length=100, blank=True,
                verbose_name='ID de la Page Facebook',
                help_text="Exemple : 123456789012345 — visible dans les paramètres de ta Page ou dans l'URL."
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='facebook_page_token',
            field=models.TextField(
                blank=True,
                verbose_name="Token d'accès de la Page (Page Access Token)",
                help_text='Token long-durée généré via Meta for Developers → Graph API Explorer → Get Page Access Token.'
            ),
        ),
    ]
