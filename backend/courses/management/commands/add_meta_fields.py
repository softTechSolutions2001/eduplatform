from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = 'Add missing meta_keywords and meta_description columns to courses_course'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Add meta_keywords column if it doesn't exist
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name='courses_course' AND column_name='meta_keywords'
                    ) THEN
                        ALTER TABLE courses_course ADD COLUMN meta_keywords character varying(255) NULL;
                        RAISE NOTICE 'Added meta_keywords column';
                    ELSE
                        RAISE NOTICE 'Column meta_keywords already exists';
                    END IF;

                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name='courses_course' AND column_name='meta_description'
                    ) THEN
                        ALTER TABLE courses_course ADD COLUMN meta_description text NULL;
                        RAISE NOTICE 'Added meta_description column';
                    ELSE
                        RAISE NOTICE 'Column meta_description already exists';
                    END IF;
                END $$;
            """)
            self.stdout.write(self.style.SUCCESS('Successfully added missing columns'))

            # Let's just check if the migration record exists before updating
            cursor.execute("""
                SELECT id FROM django_migrations
                WHERE app = 'courses'
                AND name = '0005_rename_courses_ans_questio_678jkl_idx_courses_ans_questio_aedf7d_idx_and_more';
            """)
            migration_exists = cursor.fetchone()

            if migration_exists:
                # Update the migration record with current timestamp
                cursor.execute("""
                    UPDATE django_migrations
                    SET applied = %s
                    WHERE app = 'courses'
                    AND name = '0005_rename_courses_ans_questio_678jkl_idx_courses_ans_questio_aedf7d_idx_and_more';
                """, [timezone.now()])
                self.stdout.write(self.style.SUCCESS('Updated migration record'))
            else:
                # Insert the migration record if it doesn't exist
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('courses', '0005_rename_courses_ans_questio_678jkl_idx_courses_ans_questio_aedf7d_idx_and_more', %s);
                """, [timezone.now()])
                self.stdout.write(self.style.SUCCESS('Created migration record'))
