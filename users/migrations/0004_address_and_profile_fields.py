from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_user_link'),
    ]

    operations = [
        migrations.AddField(model_name='userprofile', name='phone',
                            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AddField(model_name='useraddress', name='full_name',
                            field=models.CharField(blank=True, default='', max_length=120)),
        migrations.AddField(model_name='useraddress', name='phone',
                            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AddField(model_name='useraddress', name='house',
                            field=models.CharField(blank=True, default='', max_length=120)),
        migrations.AddField(model_name='useraddress', name='street',
                            field=models.CharField(blank=True, default='', max_length=200)),
        migrations.AddField(model_name='useraddress', name='state',
                            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AlterField(model_name='useraddress', name='address_line',
                              field=models.CharField(blank=True, default='', max_length=255)),
        migrations.AlterField(model_name='useraddress', name='city',
                              field=models.CharField(blank=True, default='Bangalore', max_length=100)),
        migrations.AlterField(model_name='useraddress', name='pincode',
                              field=models.CharField(blank=True, default='', max_length=10)),
    ]
