"""Convert existing coach_qualification_required labels to machine-friendly keys

This migration changes stored values like "I2C BMX Freestyle" to keys like
"i2c_bmx_freestyle" so the code can use stable machine-friendly choice values.

The reverse migration maps keys back to the original labels.
"""
from django.db import migrations


OLD_TO_NEW = {
    "I2C BMX Freestyle": "i2c_bmx_freestyle",
    "I2C BMX Race": "i2c_bmx_race",
    "I2C Cycle Speedway": "i2c_cycle_speedway",
    "I2C Cycling": "i2c_cycling",
    "I2C Off-Road": "i2c_off_road",
    "I2C Road": "i2c_road",
    "I2C Track": "i2c_track",
    "CIC BMX Freestyle": "cic_bmx_freestyle",
    "CIC BMX Race": "cic_bmx_race",
    "CIC CX": "cic_cx",
    "CIC MTB XC": "cic_mtb_xc",
    "CIC MTB Gravity": "cic_mtb_gravity",
    "CIC Road": "cic_road",
    "CIC Track": "cic_track",
}

NEW_TO_OLD = {v: k for k, v in OLD_TO_NEW.items()}


def forwards(apps, schema_editor):
    Plan = apps.get_model("core", "Plan")
    db_alias = schema_editor.connection.alias
    for plan in Plan.objects.using(db_alias).all():
        val = plan.coach_qualification_required
        if not val:
            continue
        # if value already a key (we're running migration twice), skip
        if val in NEW_TO_OLD:
            continue
        new = OLD_TO_NEW.get(val)
        if new:
            plan.coach_qualification_required = new
            plan.save(update_fields=["coach_qualification_required"])


def backwards(apps, schema_editor):
    Plan = apps.get_model("core", "Plan")
    db_alias = schema_editor.connection.alias
    for plan in Plan.objects.using(db_alias).all():
        val = plan.coach_qualification_required
        if not val:
            continue
        old = NEW_TO_OLD.get(val)
        if old:
            plan.coach_qualification_required = old
            plan.save(update_fields=["coach_qualification_required"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_plan_coach_qualification_required"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
