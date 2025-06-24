# File Path: backend/courses/forms.py
# Version: 1.0.0
# Date Created: 2025-06-15 06:16:48
# Date Revised: 2025-06-15 06:16:48
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 06:16:48 UTC
# User: sujibeautysalon
#
# Django Forms: Category Forms with Duplicate Prevention

from django import forms
from django.core.exceptions import ValidationError
from .models import Category


class CategoryForm(forms.ModelForm):
    """
    Category Form with Real-time Duplicate Prevention

    FEATURES:
    - Client-side duplicate checking
    - Name normalization preview
    - Suggestion system for similar names
    - Enhanced error messages
    """

    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name...',
                'data-duplicate-check': 'true',  # Enable JS duplicate checking
                'autocomplete': 'off'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '0'
            })
        }

    def clean_name(self):
        """
        Enhanced name validation with helpful error messages.
        """
        name = self.cleaned_data.get('name')

        if not name:
            raise ValidationError("Category name is required.")

        # The model's validation will handle normalization and uniqueness
        # We just need to check for obvious issues here

        if len(name.strip()) < 2:
            raise ValidationError("Category name must be at least 2 characters long.")

        # Check for existing similar names and provide helpful suggestions
        similar_categories = Category.objects.filter(
            name__icontains=name.strip()
        ).exclude(pk=self.instance.pk if self.instance.pk else None)

        if similar_categories.exists():
            similar_names = [cat.name for cat in similar_categories[:3]]
            suggestion_text = ", ".join(f'"{name}"' for name in similar_names)

            # Don't raise error here, let the model handle exact duplicates
            # Just store suggestions for the template
            self._similar_suggestions = similar_names

        return name

    def get_similar_suggestions(self):
        """Get similar category suggestions for the template."""
        return getattr(self, '_similar_suggestions', [])


class CategorySearchForm(forms.Form):
    """
    Category Search Form for Admin Interface

    FEATURES:
    - Autocomplete with existing categories
    - Duplicate detection warnings
    - Quick category creation
    """

    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search categories...',
            'data-autocomplete': 'categories',
            'autocomplete': 'off'
        })
    )

    include_inactive = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class BulkCategoryImportForm(forms.Form):
    """
    Bulk Category Import Form with Duplicate Prevention

    FEATURES:
    - CSV/text import
    - Duplicate detection and handling
    - Preview before import
    - Conflict resolution options
    """

    DUPLICATE_CHOICES = [
        ('skip', 'Skip duplicates'),
        ('update', 'Update existing'),
        ('error', 'Show errors for duplicates')
    ]

    category_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter category names, one per line...'
        }),
        help_text="Enter one category name per line"
    )

    duplicate_handling = forms.ChoiceField(
        choices=DUPLICATE_CHOICES,
        initial='skip',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_category_data(self):
        """Validate and normalize category names for bulk import."""
        data = self.cleaned_data.get('category_data', '')

        if not data.strip():
            raise ValidationError("Please provide category names to import.")

        # Split into lines and clean each name
        lines = [line.strip() for line in data.split('\n') if line.strip()]

        if not lines:
            raise ValidationError("No valid category names found.")

        # Normalize and validate each name
        normalized_names = []
        errors = []

        for i, name in enumerate(lines, 1):
            try:
                # Create temporary category to normalize name
                temp_cat = Category(name=name)
                normalized = temp_cat.normalize_name(name)

                if normalized in normalized_names:
                    errors.append(f"Line {i}: Duplicate name '{name}' in import data")
                else:
                    normalized_names.append(normalized)

            except ValidationError as e:
                errors.append(f"Line {i}: {e}")

        if errors:
            raise ValidationError("Import validation errors:\n" + "\n".join(errors))

        return normalized_names
