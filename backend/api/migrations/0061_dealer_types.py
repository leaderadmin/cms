from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0060_group_faq_menu")]
    operations = [migrations.AddField(
        model_name="dealer",
        name="dealer_type",
        field=models.CharField(
            choices=[("branch", "Chi nhánh"), ("atm", "ATM"), ("transaction_office", "Phòng giao dịch")],
            default="branch",
            max_length=32,
        ),
    )]