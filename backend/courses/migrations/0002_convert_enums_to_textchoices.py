from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="level",
            field=models.CharField(
                choices=[
                    ("beginner", "Beginner"),
                    ("intermediate", "Intermediate"),
                    ("advanced", "Advanced"),
                    ("all_levels", "All Levels"),
                ],
                default="beginner",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="completion_status",
            field=models.CharField(
                choices=[
                    ("not_started", "Not Started"),
                    ("in_progress", "In Progress"),
                    ("partially_complete", "Partially Complete"),
                    ("complete", "Complete"),
                    ("published", "Published"),
                    ("archived", "Archived"),
                    ("suspended", "Suspended"),
                ],
                default="not_started",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("completed", "Completed"),
                    ("dropped", "Dropped"),
                    ("suspended", "Suspended"),
                    ("unenrolled", "Unenrolled"),
                    ("expired", "Expired"),
                    ("pending", "Pending"),
                ],
                default="active",
                max_length=20,
            ),
        ),
    ]
