# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_otpverification"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="avatar_key",
        ),
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                help_text="Profile picture for the user",
                null=True,
                upload_to="avatars/%Y/%m/",
                verbose_name="avatar",
            ),
        ),
    ]
