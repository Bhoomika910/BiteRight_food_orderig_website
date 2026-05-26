from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users',  '0003_userprofile_user_link'),
        ('orders', '0002_order_payment_method_order_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='paid_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='users.useraddress'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='selected_ingredients',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='special_instructions',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.CreateModel(
            name='PaymentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('method', models.CharField(choices=[('card', 'Card'), ('upi', 'UPI'), ('cod', 'Cash on Delivery')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('card_last4', models.CharField(blank=True, default='', max_length=4)),
                ('card_brand', models.CharField(blank=True, default='', max_length=20)),
                ('upi_id', models.CharField(blank=True, default='', max_length=100)),
                ('error_message', models.CharField(blank=True, default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_attempts', to='orders.order')),
            ],
        ),
    ]
