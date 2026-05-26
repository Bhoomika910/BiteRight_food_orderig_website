from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0002_restaurant_cuisine_type_restaurant_delivery_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItemIngredientOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('is_default', models.BooleanField(default=True)),
                ('extra_price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('is_active', models.BooleanField(default=True)),
                ('menu_item', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='ingredient_options', to='restaurants.menuitem')),
            ],
            options={
                'ordering': ['-is_default', 'name'],
                'unique_together': {('menu_item', 'name')},
            },
        ),
    ]
