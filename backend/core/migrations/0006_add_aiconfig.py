from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_technology'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Ex: ChatAnywhere GPT-4, OpenAI principal, Backup gratuit', max_length=100, verbose_name='Nom de la configuration')),
                ('api_key', models.CharField(help_text='Votre clé API compatible OpenAI (sk-...)', max_length=500, verbose_name='Clé API')),
                ('api_base_url', models.CharField(default='https://api.chatanywhere.tech/v1', help_text='ChatAnywhere: https://api.chatanywhere.tech/v1 | OpenAI: https://api.openai.com/v1', max_length=300, verbose_name='URL de base API')),
                ('model', models.CharField(default='gpt-3.5-turbo', help_text='gpt-3.5-turbo | gpt-4o-mini | gpt-4 | gpt-4o', max_length=100, verbose_name='Modèle')),
                ('is_active', models.BooleanField(default=False, help_text='Une seule configuration peut être active à la fois', verbose_name='Configuration active')),
                ('notes', models.TextField(blank=True, help_text='Ex: quota restant, date expiration, usage', verbose_name='Notes personnelles')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuration IA',
                'verbose_name_plural': 'Configurations IA',
                'ordering': ['-is_active', '-updated_at'],
            },
        ),
    ]
