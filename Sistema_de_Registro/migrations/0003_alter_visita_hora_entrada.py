from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("Sistema_de_Registro", "0002_visita_delete_producto")]
    operations = [
        migrations.AlterField(
            model_name="visita",
            name="hora_entrada",
            field=models.DateTimeField(verbose_name="Fecha y hora de entrada"),
        ),
        migrations.AlterField(
            model_name="visita",
            name="hora_salida",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Fecha y hora de salida"),
        ),
        migrations.AlterModelOptions(
            name="visita",
            options={"ordering": ["-hora_entrada"], "verbose_name": "visita", "verbose_name_plural": "visitas"},
        ),
    ]
