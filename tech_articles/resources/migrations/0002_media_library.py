# Generated migration for media library models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('name', models.CharField(help_text='Tag name', max_length=100, unique=True, verbose_name='name')),
                ('slug', models.SlugField(db_index=True, help_text='URL-friendly identifier', max_length=120, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'media tag',
                'verbose_name_plural': 'media tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MediaFolder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('name', models.CharField(help_text='Folder name', max_length=255, verbose_name='name')),
                ('slug', models.SlugField(db_index=True, help_text='URL-friendly identifier', max_length=255, verbose_name='slug')),
                ('description', models.TextField(blank=True, default='', help_text='Folder description', verbose_name='description')),
                ('created_by', models.ForeignKey(help_text='User who created this folder', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_folders', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('parent', models.ForeignKey(blank=True, help_text='Parent folder for nested structure', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subfolders', to='resources.mediafolder', verbose_name='parent folder')),
            ],
            options={
                'verbose_name': 'media folder',
                'verbose_name_plural': 'media folders',
                'ordering': ['name'],
                'unique_together': {('parent', 'slug')},
            },
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('title', models.CharField(help_text='Media file title', max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, default='', help_text='Detailed description of the media', verbose_name='description')),
                ('alt_text', models.CharField(blank=True, default='', help_text='Alternative text for accessibility', max_length=255, verbose_name='alt text')),
                ('file_key', models.CharField(db_index=True, help_text='S3 key/path to the file', max_length=512, unique=True, verbose_name='file key')),
                ('file_name', models.CharField(help_text='Original file name', max_length=255, verbose_name='file name')),
                ('file_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document'), ('audio', 'Audio'), ('other', 'Other')], db_index=True, help_text='Type of file', max_length=20, verbose_name='file type')),
                ('mime_type', models.CharField(help_text='MIME type of the file', max_length=100, verbose_name='MIME type')),
                ('file_size', models.PositiveBigIntegerField(help_text='File size in bytes', verbose_name='file size')),
                ('width', models.PositiveIntegerField(blank=True, help_text='Image width in pixels', null=True, verbose_name='width')),
                ('height', models.PositiveIntegerField(blank=True, help_text='Image height in pixels', null=True, verbose_name='height')),
                ('thumbnail_key', models.CharField(blank=True, default='', help_text='S3 key for thumbnail version', max_length=512, verbose_name='thumbnail key')),
                ('optimized_key', models.CharField(blank=True, default='', help_text='S3 key for optimized version', max_length=512, verbose_name='optimized key')),
                ('access_level', models.CharField(choices=[('free', 'Free'), ('premium', 'Premium'), ('purchase_required', 'Purchase Required')], db_index=True, default='free', help_text='Access level required to view this file', max_length=30, verbose_name='access level')),
                ('download_count', models.PositiveIntegerField(default=0, help_text='Number of times file has been downloaded', verbose_name='download count')),
                ('folder', models.ForeignKey(blank=True, help_text='Folder containing this file', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='resources.mediafolder', verbose_name='folder')),
                ('tags', models.ManyToManyField(blank=True, help_text='Tags for categorization', related_name='files', to='resources.mediatag', verbose_name='tags')),
                ('uploaded_by', models.ForeignKey(help_text='User who uploaded this file', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_media', to=settings.AUTH_USER_MODEL, verbose_name='uploaded by')),
            ],
            options={
                'verbose_name': 'media file',
                'verbose_name_plural': 'media files',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='resourcedocument',
            name='media_file',
            field=models.ForeignKey(blank=True, help_text='Linked media file from library', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resource_documents', to='resources.mediafile', verbose_name='media file'),
        ),
        migrations.AlterField(
            model_name='resourcedocument',
            name='file_key',
            field=models.CharField(blank=True, db_index=True, default='', help_text='S3 key/path to the document file (legacy)', max_length=512, verbose_name='file key'),
        ),
        migrations.AddIndex(
            model_name='mediafolder',
            index=models.Index(fields=['parent', 'name'], name='resources_m_parent__82a87a_idx'),
        ),
        migrations.AddIndex(
            model_name='mediafile',
            index=models.Index(fields=['file_type', 'created_at'], name='resources_m_file_ty_b9b31f_idx'),
        ),
        migrations.AddIndex(
            model_name='mediafile',
            index=models.Index(fields=['folder', 'file_type'], name='resources_m_folder__2c8b51_idx'),
        ),
        migrations.AddIndex(
            model_name='mediafile',
            index=models.Index(fields=['uploaded_by', 'created_at'], name='resources_m_uploade_a76f52_idx'),
        ),
    ]
