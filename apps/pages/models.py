from django.db import models


class Page(models.Model):
    title = models.CharField('Title', max_length=32)
    slug = models.SlugField('Slug', max_length=32,
                            help_text='Contains only small letters and hyphen. Example: terms-and-conditions')
    header = models.CharField('Header', max_length=64)
    content = models.TextField('Content', max_length=4096)
    seo_text = models.TextField('SEO Text', max_length=4096)

    POSITION_HEADER = 'Header'
    POSITION_FOOTER = 'Footer'
    LINK_POSITIONS = (
        (POSITION_HEADER, POSITION_HEADER),
        (POSITION_FOOTER, POSITION_FOOTER),
    )
    link_position = models.CharField('Link Position', max_length=16,
                                     default=POSITION_FOOTER,
                                     choices=LINK_POSITIONS)

    active = models.BooleanField('Active', default=False)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return self.title
