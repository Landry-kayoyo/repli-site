from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_facebook_autopost'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='indexnow_key',
            field=models.CharField(
                max_length=128, blank=True,
                verbose_name='Clé IndexNow',
                help_text='Clé auto-générée pour soumettre vos URLs à Bing/Google via IndexNow.'
            ),
        ),
    ]
