# Generated to restore the missing migration that introduced Post.slug.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_excerpt'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(
                blank=True,
                help_text='SEO-friendly URL slug (auto-generated from title)',
                max_length=1000,
                null=True,
            ),
        ),
    ]
