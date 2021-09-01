# Generated by Django 3.1.6 on 2021-03-04 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voice_cloning', '0003_auto_20210304_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='input_audio',
            field=models.FileField(blank=True, help_text='Allowed type - .wav, .ogg, .mp3, .m4a, .flac', upload_to='media/'),
        ),
    ]