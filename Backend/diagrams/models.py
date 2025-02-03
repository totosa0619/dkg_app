from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import os


class DiagramFrame(models.Model):
    title = models.CharField(
        max_length=256, 
        help_text="Title of diagram")
    slug = models.SlugField(
        max_length=128, 
        unique=True)
    diagram_type = models.CharField(
        max_length=32, 
        default="", blank=True)
    source = models.FileField(
        upload_to="iframe-diagrams/",
        help_text="JSON file with list of objects",
        max_length=300,
    )
    updated_time = models.DateTimeField(auto_now=True)
    updated_user_name = models.CharField(default="", max_length=500, blank=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    accessible_by = models.ManyToManyField(
        User, 
        related_name="accessible_diagrams", 
        blank=True,
        help_text="Restrict access to diagram to specific users, empty means everyone can access"
    )
    passkey = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        help_text="Password to access diagram",
    )
    is_protected = models.BooleanField(
        default=False,
        help_text="If true, the entire diagram is protected with a password and Email/password authentication",
        )
    
    def set_passkey(self, raw_passkey):
        self.passkey = make_password(raw_passkey)

    def check_passkey(self, raw_passkey):
        return check_password(raw_passkey, self.passkey)

    def __str__(self):
        return self.title
    


class DiagramLogs(models.Model):
    diagram = models.ForeignKey(DiagramFrame, on_delete=models.CASCADE, related_name='logs',
                            help_text='Diagram to which this log belongs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagram_logs', null=True,
                            help_text='User who made changes')
    path = models.CharField(max_length=600, default='', blank=True, null=True,
                            help_text='Path of old json file')
    changes = models.JSONField(default=dict, blank=True, null=True,
                            help_text='Changes made to diagram')
    dt_created = models.DateTimeField(auto_now_add=True,  null=True,
                            help_text='Date and time when log was created')
    
    def __str__(self):
        return f"{self.user} changed {self.diagram} at {self.dt_created}" if self.user else f"{self.diagram} was changed at {self.dt_created}"
    
    class Meta:
        ordering = ['-dt_created']
        verbose_name = 'Diagram Log'
        verbose_name_plural = 'Diagram Logs'


class RawDataBlock(models.Model):
    slug = models.CharField(max_length=256, verbose_name='Text ID of data')
    source_name = models.CharField(max_length=32, default='', blank=True)
    param1 = models.CharField(max_length=128, verbose_name='Custom Parameter 1', null=True, blank=True)
    param2 = models.CharField(max_length=128, verbose_name='Custom Parameter 2', null=True, blank=True)
    data = models.TextField(default='', blank=True)
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.slug} [{self.source_name}]'
    


class PlatformAccess(models.Model):
    ACCESS_LEVELS = [
        ('view_platform', 'View Platform'),
    ]
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='platform_access', help_text='User who has requested access')
    access_level = models.CharField(max_length=32, help_text='Access level', choices=ACCESS_LEVELS, default='view_platform')
    status = models.CharField(max_length=32, help_text='Request status', default='pending', choices=REQUEST_STATUS)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.access_level}'
    
    class Meta:
        verbose_name = 'Platform Access'
        verbose_name_plural = 'Platform Access'
        
        
        

class DeployedDashboards(models.Model):
    panel_url = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deployed_dashboards', help_text='User who has deployed dashboard')
    domain = models.CharField(max_length=500)
    diagram_slug = models.CharField(max_length=500)
    diagram_instance = models.ForeignKey(DiagramFrame, on_delete=models.CASCADE, related_name='deployed_diagrams', help_text='Diagram instance')
    metadata = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} deployed  {self.domain}  {self.diagram_slug} - {self.diagram_instance}'

    class Meta:
        verbose_name = 'Deployed Dashboard'
        verbose_name_plural = 'Deployed Dashboards'
        ordering = ['-created']
        


def upload_image_to(instance, filename):
    # Check if instance.pk is None
    if instance.pk is None:
        return f'temporary/images/{filename}'  # Store temporarily before save

    return f'ittools/{instance.pk}/images/{filename}'

def upload_file_to(instance, filename):
    # Check if instance.pk is None
    if instance.pk is None:
        return f'temporary/files/{filename}'  # Store temporarily before save

    return f'ittools/{instance.pk}/files/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Category name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class ITToolProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who created the tool", related_name="ittool_products", blank=True, null=True)
    title = models.CharField(max_length=256, unique=True, help_text="Unique title for the tool")
    image = models.ImageField(upload_to=upload_image_to, help_text="Image representing the tool")
    description = models.TextField(help_text="Description of the tool", blank=True, null=True)
    demo_link = models.URLField(help_text="Link to the demo of the tool", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tools', help_text="Category the tool belongs to", blank=True, null=True)
    create_link = models.URLField(help_text="Link to create/access the tool")
    file_example = models.FileField(upload_to=upload_file_to, help_text="Example file for the tool", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save the instance first to generate a primary key (pk) if it's not yet saved
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Update the image path if necessary
        if self.image and 'temporary/images' in self.image.name:
            new_image_path = f'ittools/{self.pk}/images/{os.path.basename(self.image.name)}'
            if self.image.name != new_image_path:
                self.image.name = new_image_path
                super().save(*args, **kwargs)  # Save again to update the image path

        # Update the file_example path if necessary
        if self.file_example and 'temporary/files' in self.file_example.name:
            new_file_path = f'ittools/{self.pk}/files/{os.path.basename(self.file_example.name)}'
            if self.file_example.name != new_file_path:
                self.file_example.name = new_file_path
                super().save(*args, **kwargs)  # Save again to update the file_example path

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ittool Product'
        verbose_name_plural = 'Ittool Products'
        ordering = ['-created_at']