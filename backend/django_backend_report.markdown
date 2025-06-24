# Django Backend Analysis Report

_Generated on 2025-05-01 22:58:44_

## Table of Contents

1. [Models](#models)
2. [API Endpoints](#api-endpoints)
3. [Views](#views)
4. [Serializers](#serializers)
5. [Forms](#forms)
6. [Authentication](#authentication)

## Models

### LogEntry

**App:** admin

**Description:** LogEntry(id, action_time, user, content_type, object_id, object_repr, action_flag, change_message)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | AutoField | No |  |  |  |
| action_time | DateTimeField | Yes | <function: now> |  |  |
| object_id | TextField | No |  |  |  |
| object_repr | CharField | Yes |  |  |  |
| action_flag | PositiveSmallIntegerField | Yes |  | Addition, Change, Deletion |  |
| change_message | TextField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | logentry_set |  |
| ForeignKey | ContentType | logentry_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_action_flag_display()`: 
- `get_admin_url()`: 
Return the admin URL to edit the object represented by this log entry.

- `get_change_message()`: 
If self.change_message is a JSON structure, interpret it as a change
string, properly translated.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_edited_object()`: Return the edited object represented by this log entry.
- `get_next_by_action_time()`: 
- `get_previous_by_action_time()`: 
- `is_addition()`: 
- `is_change()`: 
- `is_deletion()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Permission

**App:** auth

**Description:** 
The permissions system provides a way to assign permissions to specific
users and groups of users.

The permission system is used by the Django admin site, but may also be
useful in your own code. The Django admin site uses permissions as follows:

    - The "add" permission limits the user's ability to view the "add" form
      and add an object.
    - The "change" permission limits a user's ability to view the change
      list, view the "change" form and change an object.
    - The "delete" permission limits the ability to delete an object.
    - The "view" permission limits the ability to view an object.

Permissions are set globally per type of object, not per specific object
instance. It is possible to say "Mary may change news stories," but it's
not currently possible to say "Mary may change news stories, but only the
ones she created herself" or "Mary may only change news stories that have a
certain status or publication date."

The permissions listed above are automatically created for each model.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | AutoField | No |  |  |  |
| name | CharField | Yes |  |  |  |
| codename | CharField | Yes |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ManyToManyField | Group |  |  |
| ManyToManyField | CustomUser |  |  |
| ForeignKey | ContentType | permission_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `natural_key()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Group

**App:** auth

**Description:** 
Groups are a generic way of categorizing users to apply permissions, or
some other label, to those users. A user can belong to any number of
groups.

A user in a group automatically has all the permissions granted to that
group. For example, if the group 'Site editors' has the permission
can_edit_home_page, any user in that group will have that permission.

Beyond permissions, groups are a convenient way to categorize users to
apply some label, or extended functionality, to them. For example, you
could create a group 'Special users', and you could write code that would
do special things to those users -- such as giving them access to a
members-only portion of your site, or sending them members-only email
messages.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | AutoField | No |  |  |  |
| name | CharField | Yes |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ManyToManyField | CustomUser |  |  |
| ManyToManyField | Permission | group_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `natural_key()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### ContentType

**App:** contenttypes

**Description:** ContentType(id, app_label, model)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | AutoField | No |  |  |  |
| app_label | CharField | Yes |  |  |  |
| model | CharField | Yes |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | LogEntry |  |  |
| ForeignKey | Permission |  |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_all_objects_for_this_type()`: 
Return all objects of this type for the keyword arguments given.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_object_for_this_type(using)`: 
Return an object of this type for the keyword arguments given.
Basically, this is a proxy around this object_type's get_object() model
method. The ObjectNotExist exception, if thrown, will not be caught,
so code that calls this method should catch it.

- `model_class()`: Return the model class for this type of content.
- `natural_key()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Session

**App:** sessions

**Description:** 
Django provides full support for anonymous sessions. The session
framework lets you store and retrieve arbitrary data on a
per-site-visitor basis. It stores data on the server side and
abstracts the sending and receiving of cookies. Cookies contain a
session ID -- not the data itself.

The Django sessions framework is entirely cookie-based. It does
not fall back to putting session IDs in URLs. This is an intentional
design decision. Not only does that behavior make URLs ugly, it makes
your site vulnerable to session-ID theft via the "Referer" header.

For complete documentation on using Sessions in your code, consult
the sessions documentation that is shipped with Django (also available
on the Django web site).


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| session_key | CharField | Yes |  |  |  |
| session_data | TextField | Yes |  |  |  |
| expire_date | DateTimeField | Yes |  |  |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_decoded()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_expire_date()`: 
- `get_previous_by_expire_date()`: 
- `get_session_store_class(cls)`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### CustomUser

**App:** users

**Description:** 
Custom User model with email authentication and role-based permissions.
This extends Django's AbstractUser with additional fields and functionality.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| password | CharField | Yes |  |  |  |
| is_superuser | BooleanField | Yes | False |  | Designates that this user has all permissions without explicitly assigning them. |
| first_name | CharField | No |  |  |  |
| last_name | CharField | No |  |  |  |
| is_staff | BooleanField | Yes | False |  | Designates whether the user can log into this admin site. |
| email | CharField | Yes |  |  |  |
| username | CharField | Yes |  |  |  |
| role | CharField | Yes | student | Student, Instructor, Administrator, Staff |  |
| is_email_verified | BooleanField | Yes | False |  |  |
| date_joined | DateTimeField | Yes | <function: now> |  |  |
| last_login | DateTimeField | No |  |  |  |
| failed_login_attempts | PositiveIntegerField | Yes | 0 |  |  |
| temporary_ban_until | DateTimeField | No |  |  |  |
| is_active | BooleanField | Yes | True |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | LogEntry |  |  |
| OneToOneField | Profile |  |  |
| ForeignKey | EmailVerification |  |  |
| ForeignKey | PasswordReset |  |  |
| ForeignKey | LoginLog |  |  |
| ForeignKey | UserSession |  |  |
| OneToOneField | Subscription |  |  |
| ForeignKey | CourseInstructor |  |  |
| ForeignKey | Enrollment |  |  |
| ForeignKey | AssessmentAttempt |  |  |
| ForeignKey | Review |  |  |
| ForeignKey | Note |  |  |
| ManyToManyField | Group | user_set |  |
| ManyToManyField | Permission | user_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `acheck_password(raw_password)`: See check_password().
- `adelete(using, keep_parents)`: 
- `aget_all_permissions(obj)`: 
- `aget_group_permissions(obj)`: See get_group_permissions()
- `aget_user_permissions(obj)`: See get_user_permissions()
- `ahas_module_perms(app_label)`: See has_module_perms()
- `ahas_perm(perm, obj)`: See has_perm()
- `ahas_perms(perm_list, obj)`: See has_perms()
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `check_password(raw_password)`: 
Return a boolean of whether the raw_password was correct. Handles
hashing formats behind the scenes.

- `clean()`: 
- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `email_user(subject, message, from_email)`: Send an email to this user.
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_all_permissions(obj)`: 
- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_email_field_name(cls)`: 
- `get_full_name()`: 
Return the first_name plus the last_name, with a space in between.

- `get_group_permissions(obj)`: 
Return a list of permission strings that this user has through their
groups. Query all available auth backends. If an object is passed in,
return only permissions matching this object.

- `get_next_by_date_joined()`: 
- `get_previous_by_date_joined()`: 
- `get_role_display()`: 
- `get_session_auth_fallback_hash()`: 
- `get_session_auth_hash()`: 
Return an HMAC of the password field.

- `get_short_name()`: Return the short name for the user.
- `get_user_permissions(obj)`: 
Return a list of permission strings that this user has directly.
Query all available auth backends. If an object is passed in,
return only permissions matching this object.

- `get_username()`: Return the username for this User.
- `has_module_perms(app_label)`: 
Return True if the user has any permissions in the given app label.
Use similar logic as has_perm(), above.

- `has_perm(perm, obj)`: 
Return True if the user has the specified permission. Query all
available auth backends, but return immediately if any backend returns
True. Thus, a user who has permission from a single auth backend is
assumed to have permission in general. If an object is provided, check
permissions for that object.

- `has_perms(perm_list, obj)`: 
Return True if the user has each of the specified permissions. If
object is passed, check if the user has all required perms for it.

- `has_role(role)`: 
Check if the user has a specific role.

- `has_usable_password()`: 
Return False if set_unusable_password() has been called for this user.

- `is_account_locked()`: 
Check if the account is temporarily locked due to failed login attempts.

- `is_admin()`: Check if user is an admin.
- `is_instructor()`: Check if user is an instructor.
- `is_staff_member()`: Check if user is a staff member.
- `is_student()`: Check if user is a student.
- `natural_key()`: 
- `normalize_username(cls, username)`: 
- `prepare_database_save(field)`: 
- `record_login_attempt(successful)`: 
Record a login attempt and handle failed attempt security measures.
Returns True if the account is temporarily locked.

- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `set_password(raw_password)`: 
- `set_unusable_password()`: 
- `unique_error_message(model_class, unique_check)`: 
- `username_validator(value)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Profile

**App:** users

**Description:** 
Extended user profile information.
Contains additional user data beyond authentication needs.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| profile_picture | FileField | No |  |  |  |
| bio | TextField | No |  |  |  |
| date_of_birth | DateField | No |  |  |  |
| phone_number | CharField | No |  |  |  |
| address | TextField | No |  |  |  |
| city | CharField | No |  |  |  |
| state | CharField | No |  |  |  |
| country | CharField | No |  |  |  |
| postal_code | CharField | No |  |  |  |
| website | CharField | No |  |  |  |
| linkedin | CharField | No |  |  |  |
| twitter | CharField | No |  |  |  |
| github | CharField | No |  |  |  |
| expertise | CharField | No |  |  |  |
| teaching_experience | PositiveIntegerField | Yes | 0 |  |  |
| educational_background | TextField | No |  |  |  |
| interests | TextField | No |  |  |  |
| receive_email_notifications | BooleanField | Yes | True |  |  |
| receive_marketing_emails | BooleanField | Yes | False |  |  |
| created_at | DateTimeField | No |  |  |  |
| updated_at | DateTimeField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| OneToOneField | CustomUser | profile |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_created_at()`: 
- `get_next_by_updated_at()`: 
- `get_previous_by_created_at()`: 
- `get_previous_by_updated_at()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### EmailVerification

**App:** users

**Description:** 
Email verification token management.
Used for verifying user email addresses during registration.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| token | UUIDField | Yes | <function: uuid4> |  |  |
| created_at | DateTimeField | No |  |  |  |
| expires_at | DateTimeField | Yes |  |  |  |
| verified_at | DateTimeField | No |  |  |  |
| is_used | BooleanField | Yes | False |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | email_verifications |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_created_at()`: 
- `get_next_by_expires_at()`: 
- `get_previous_by_created_at()`: 
- `get_previous_by_expires_at()`: 
- `is_valid()`: 
Check if the verification token is still valid.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `use_token()`: 
Mark the token as used and the user's email as verified.

- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### PasswordReset

**App:** users

**Description:** 
Password reset token management.
Used for secure password reset functionality.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| token | UUIDField | Yes | <function: uuid4> |  |  |
| created_at | DateTimeField | No |  |  |  |
| expires_at | DateTimeField | Yes |  |  |  |
| used_at | DateTimeField | No |  |  |  |
| is_used | BooleanField | Yes | False |  |  |
| ip_address | GenericIPAddressField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | password_resets |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_created_at()`: 
- `get_next_by_expires_at()`: 
- `get_previous_by_created_at()`: 
- `get_previous_by_expires_at()`: 
- `is_valid()`: 
Check if the password reset token is still valid.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `use_token()`: 
Mark the token as used.

- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### LoginLog

**App:** users

**Description:** 
Log of user login attempts.
Used for security auditing and detecting suspicious activity.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| timestamp | DateTimeField | No |  |  |  |
| ip_address | GenericIPAddressField | Yes |  |  |  |
| user_agent | TextField | Yes |  |  |  |
| successful | BooleanField | Yes | False |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | login_logs |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_timestamp()`: 
- `get_previous_by_timestamp()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### UserSession

**App:** users

**Description:** 
Track active user sessions.
Useful for managing concurrent logins and session invalidation.


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| session_key | CharField | Yes |  |  |  |
| ip_address | GenericIPAddressField | Yes |  |  |  |
| user_agent | TextField | Yes |  |  |  |
| created_at | DateTimeField | No |  |  |  |
| expires_at | DateTimeField | Yes |  |  |  |
| last_activity | DateTimeField | No |  |  |  |
| is_active | BooleanField | Yes | True |  |  |
| device_type | CharField | No |  |  |  |
| location | CharField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | sessions |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `extend_session(duration_hours)`: 
Extend the session expiration time.

- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_created_at()`: 
- `get_next_by_expires_at()`: 
- `get_next_by_last_activity()`: 
- `get_previous_by_created_at()`: 
- `get_previous_by_expires_at()`: 
- `get_previous_by_last_activity()`: 
- `invalidate()`: 
Invalidate this session.

- `is_valid()`: 
Check if session is still valid.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Subscription

**App:** users

**Description:** 
Subscription model for tracking user subscription status

This model tracks:
1. Subscription tier (free, basic, premium)
2. Payment status and history
3. Expiration dates

Variables to modify:
- SUBSCRIPTION_TIERS: Update if subscription level names change
- DEFAULT_SUBSCRIPTION_DAYS: Change default subscription length


**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| tier | CharField | Yes | free | Free, Basic, Premium |  |
| status | CharField | Yes | active | Active, Expired, Cancelled, Pending |  |
| start_date | DateTimeField | No |  |  |  |
| end_date | DateTimeField | No |  |  |  |
| is_auto_renew | BooleanField | Yes | False |  |  |
| last_payment_date | DateTimeField | No |  |  |  |
| payment_method | CharField | No |  |  |  |
| payment_id | CharField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| OneToOneField | CustomUser | subscription |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `create_for_user(cls, user, tier, days)`: Create a new subscription for user
- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_start_date()`: 
- `get_previous_by_start_date()`: 
- `get_status_display()`: 
- `get_tier_display()`: 
- `is_active()`: Check if subscription is active
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Category

**App:** courses

**Description:** Category(id, name, description, icon, slug)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| name | CharField | Yes |  |  |  |
| description | TextField | No |  |  |  |
| icon | CharField | No |  |  |  |
| slug | SlugField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Course |  |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Course

**App:** courses

**Description:** Course(id, title, subtitle, slug, description, category, thumbnail, price, discount_price, discount_ends, level, duration, has_certificate, is_featured, is_published, published_date, updated_date, requirements, skills)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | Yes |  |  |  |
| subtitle | CharField | No |  |  |  |
| slug | SlugField | No |  |  |  |
| description | TextField | Yes |  |  |  |
| thumbnail | FileField | No |  |  |  |
| price | DecimalField | Yes | 490 |  |  |
| discount_price | DecimalField | No |  |  |  |
| discount_ends | DateTimeField | No |  |  |  |
| level | CharField | Yes | all_levels | Beginner, Intermediate, Advanced, All Levels |  |
| duration | CharField | No |  |  |  |
| has_certificate | BooleanField | Yes | False |  |  |
| is_featured | BooleanField | Yes | False |  |  |
| is_published | BooleanField | Yes | False |  |  |
| published_date | DateTimeField | No |  |  |  |
| updated_date | DateTimeField | No |  |  |  |
| requirements | JSONField | No | <function: dict> |  |  |
| skills | JSONField | No | <function: dict> |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CourseInstructor |  |  |
| ForeignKey | Module |  |  |
| ForeignKey | Enrollment |  |  |
| ForeignKey | Review |  |  |
| ForeignKey | Category | courses |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_level_display()`: 
- `get_next_by_published_date()`: 
- `get_next_by_updated_date()`: 
- `get_previous_by_published_date()`: 
- `get_previous_by_updated_date()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### CourseInstructor

**App:** courses

**Description:** CourseInstructor(id, course, instructor, title, bio, is_lead)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | No |  |  |  |
| bio | TextField | No |  |  |  |
| is_lead | BooleanField | Yes | False |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Course | instructors |  |
| ForeignKey | CustomUser | courses_teaching |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Module

**App:** courses

**Description:** Module(id, course, title, description, order, duration)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | Yes |  |  |  |
| description | TextField | No |  |  |  |
| order | PositiveIntegerField | Yes | 1 |  |  |
| duration | CharField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Lesson |  |  |
| ForeignKey | Course | modules |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Lesson

**App:** courses

**Description:** Lesson(id, module, title, content, basic_content, intermediate_content, access_level, duration, type, order, has_assessment, has_lab, is_free_preview)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | Yes |  |  |  |
| content | TextField | Yes |  |  | Full content visible to all users (or premium content if access_level is set) |
| basic_content | TextField | No |  |  | Preview content for unregistered users |
| intermediate_content | TextField | No |  |  | Limited content for registered users |
| access_level | CharField | Yes | intermediate | Basic - Unregistered Users, Intermediate - Registered Users, Advanced - Paid Users | Minimum access level required to view this lesson |
| duration | CharField | No |  |  |  |
| type | CharField | Yes | video | Video, Reading, Interactive, Quiz, Lab Exercise |  |
| order | PositiveIntegerField | Yes | 1 |  |  |
| has_assessment | BooleanField | Yes | False |  |  |
| has_lab | BooleanField | Yes | False |  |  |
| is_free_preview | BooleanField | Yes | False |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Resource |  |  |
| OneToOneField | Assessment |  |  |
| ForeignKey | Progress |  |  |
| ForeignKey | Note |  |  |
| ForeignKey | Module | lessons |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_access_level_display()`: 
- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_type_display()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Resource

**App:** courses

**Description:** Resource(id, lesson, title, type, file, url, description, premium)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | Yes |  |  |  |
| type | CharField | Yes |  | Document, Video, External Link, Code Sample, Tool/Software |  |
| file | FileField | No |  |  |  |
| url | CharField | No |  |  |  |
| description | TextField | No |  |  |  |
| premium | BooleanField | Yes | False |  | Whether this resource requires a premium subscription |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Lesson | resources |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_type_display()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Assessment

**App:** courses

**Description:** Assessment(id, lesson, title, description, time_limit, passing_score)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| title | CharField | Yes |  |  |  |
| description | TextField | No |  |  |  |
| time_limit | PositiveIntegerField | Yes | 0 |  |  |
| passing_score | PositiveIntegerField | Yes | 70 |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Question |  |  |
| ForeignKey | AssessmentAttempt |  |  |
| OneToOneField | Lesson | assessment |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Question

**App:** courses

**Description:** Question(id, assessment, question_text, question_type, order, points)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| question_text | TextField | Yes |  |  |  |
| question_type | CharField | Yes |  | Multiple Choice, True/False, Short Answer, Matching |  |
| order | PositiveIntegerField | Yes | 1 |  |  |
| points | PositiveIntegerField | Yes | 1 |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Answer |  |  |
| ForeignKey | AttemptAnswer |  |  |
| ForeignKey | Assessment | questions |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_question_type_display()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Answer

**App:** courses

**Description:** Answer(id, question, answer_text, is_correct, explanation)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| answer_text | CharField | Yes |  |  |  |
| is_correct | BooleanField | Yes | False |  |  |
| explanation | TextField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | AttemptAnswer |  |  |
| ForeignKey | Question | answers |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Enrollment

**App:** courses

**Description:** Enrollment(id, user, course, enrolled_date, last_accessed, status, completion_date)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| enrolled_date | DateTimeField | No |  |  |  |
| last_accessed | DateTimeField | No |  |  |  |
| status | CharField | Yes | active | Active, Completed, Dropped |  |
| completion_date | DateTimeField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Progress |  |  |
| OneToOneField | Certificate |  |  |
| ForeignKey | CustomUser | enrollments |  |
| ForeignKey | Course | enrollments |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_enrolled_date()`: 
- `get_next_by_last_accessed()`: 
- `get_previous_by_enrolled_date()`: 
- `get_previous_by_last_accessed()`: 
- `get_status_display()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Progress

**App:** courses

**Description:** Progress(id, enrollment, lesson, is_completed, completed_date, time_spent)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| is_completed | BooleanField | Yes | False |  |  |
| completed_date | DateTimeField | No |  |  |  |
| time_spent | PositiveIntegerField | Yes | 0 |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | Enrollment | progress |  |
| ForeignKey | Lesson | progress_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### AssessmentAttempt

**App:** courses

**Description:** AssessmentAttempt(id, user, assessment, start_time, end_time, score, passed)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| start_time | DateTimeField | No |  |  |  |
| end_time | DateTimeField | No |  |  |  |
| score | PositiveIntegerField | Yes | 0 |  |  |
| passed | BooleanField | Yes | False |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | AttemptAnswer |  |  |
| ForeignKey | CustomUser | assessment_attempts |  |
| ForeignKey | Assessment | attempts |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_start_time()`: 
- `get_previous_by_start_time()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### AttemptAnswer

**App:** courses

**Description:** AttemptAnswer(id, attempt, question, selected_answer, text_answer, is_correct, points_earned)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| text_answer | TextField | No |  |  |  |
| is_correct | BooleanField | Yes | False |  |  |
| points_earned | PositiveIntegerField | Yes | 0 |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | AssessmentAttempt | answers |  |
| ForeignKey | Question | attemptanswer_set |  |
| ForeignKey | Answer | attemptanswer_set |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Review

**App:** courses

**Description:** Review(id, user, course, rating, title, content, date_created, helpful_count)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| rating | PositiveSmallIntegerField | Yes |  |  |  |
| title | CharField | No |  |  |  |
| content | TextField | Yes |  |  |  |
| date_created | DateTimeField | No |  |  |  |
| helpful_count | PositiveIntegerField | Yes | 0 |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | reviews |  |
| ForeignKey | Course | reviews |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_date_created()`: 
- `get_previous_by_date_created()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Note

**App:** courses

**Description:** Note(id, user, lesson, content, created_date, updated_date)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| content | TextField | Yes |  |  |  |
| created_date | DateTimeField | No |  |  |  |
| updated_date | DateTimeField | No |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| ForeignKey | CustomUser | notes |  |
| ForeignKey | Lesson | notes |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_created_date()`: 
- `get_next_by_updated_date()`: 
- `get_previous_by_created_date()`: 
- `get_previous_by_updated_date()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


### Certificate

**App:** courses

**Description:** Certificate(id, enrollment, issue_date, certificate_number)

**Fields:**

| Name | Type | Required | Default | Choices | Help Text |
|------|------|----------|---------|---------|----------|
| id | BigAutoField | No |  |  |  |
| issue_date | DateTimeField | No |  |  |  |
| certificate_number | CharField | Yes |  |  |  |

**Relationships:**

| Relationship Type | Related Model | Related Name | Through |
|-------------------|--------------|--------------|--------|
| OneToOneField | Enrollment | certificate |  |

**Methods:**

- `__repr__()`: 
- `__str__()`: 
- `adelete(using, keep_parents)`: 
- `arefresh_from_db(using, fields, from_queryset)`: 
- `asave()`: 
- `check(cls)`: 
- `clean()`: 
Hook for doing any extra model-wide validation after clean() has been
called on every field by self.clean_fields. Any ValidationError raised
by this method will not be associated with a particular field; it will
have a special-case association with the field defined by NON_FIELD_ERRORS.

- `clean_fields(exclude)`: 
Clean all fields and raise a ValidationError containing a dict
of all validation errors if any occur.

- `date_error_message(lookup_type, field_name, unique_for)`: 
- `delete(using, keep_parents)`: 
- `from_db(cls, db, field_names, values)`: 
- `full_clean(exclude, validate_unique, validate_constraints)`: 
Call clean_fields(), clean(), validate_unique(), and
validate_constraints() on the model. Raise a ValidationError for any
errors that occur.

- `get_constraints()`: 
- `get_deferred_fields()`: 
Return a set containing names of deferred fields for this instance.

- `get_next_by_issue_date()`: 
- `get_previous_by_issue_date()`: 
- `prepare_database_save(field)`: 
- `refresh_from_db(using, fields, from_queryset)`: 
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn't loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.

- `save()`: 
Save the current instance. Override this in a subclass if you want to
control the saving process.

The 'force_insert' and 'force_update' parameters can be used to insist
that the "save" must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.

- `save_base(raw, force_insert, force_update, using, update_fields)`: 
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The 'raw' argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.

- `serializable_value(field_name)`: 
Return the value of the field name for this instance. If the field is
a foreign key, return the id value instead of the object. If there's
no Field object with this name on the model, return the model
attribute's value.

Used to serialize a field's value (in the serializer, or form output,
for example). Normally, you would just access the attribute directly
and not use this method.

- `unique_error_message(model_class, unique_check)`: 
- `validate_constraints(exclude)`: 
- `validate_unique(exclude)`: 
Check unique constraints on the model and raise ValidationError if any
failed.


## API Endpoints

| Path | HTTP Methods | View/Viewset | Serializer | Model |
|------|-------------|-------------|------------|-------|
| admin/ |  | index |  |  |
| admin/login/ |  | login |  |  |
| admin/logout/ |  | logout |  |  |
| admin/password_change/ |  | password_change |  |  |
| admin/password_change/done/ |  | password_change_done |  |  |
| admin/autocomplete/ |  | autocomplete |  |  |
| admin/jsi18n/ |  | jsi18n |  |  |
| admin/r/<path:content_type_id>/<path:object_id>/ | GET | view_on_site |  |  |
| admin/auth/group/ |  | auth_group_changelist |  |  |
| admin/auth/group/add/ |  | auth_group_add |  |  |
| admin/auth/group/<path:object_id>/history/ |  | auth_group_history |  |  |
| admin/auth/group/<path:object_id>/delete/ |  | auth_group_delete |  |  |
| admin/auth/group/<path:object_id>/change/ |  | auth_group_change |  |  |
| admin/auth/group/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/users/customuser/<id>/password/ |  | auth_user_password_change |  |  |
| admin/users/customuser/ |  | users_customuser_changelist |  |  |
| admin/users/customuser/add/ |  | users_customuser_add |  |  |
| admin/users/customuser/<path:object_id>/history/ |  | users_customuser_history |  |  |
| admin/users/customuser/<path:object_id>/delete/ |  | users_customuser_delete |  |  |
| admin/users/customuser/<path:object_id>/change/ |  | users_customuser_change |  |  |
| admin/users/customuser/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/users/emailverification/ |  | users_emailverification_changelist |  |  |
| admin/users/emailverification/add/ |  | users_emailverification_add |  |  |
| admin/users/emailverification/<path:object_id>/history/ |  | users_emailverification_history |  |  |
| admin/users/emailverification/<path:object_id>/delete/ |  | users_emailverification_delete |  |  |
| admin/users/emailverification/<path:object_id>/change/ |  | users_emailverification_change |  |  |
| admin/users/emailverification/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/users/passwordreset/ |  | users_passwordreset_changelist |  |  |
| admin/users/passwordreset/add/ |  | users_passwordreset_add |  |  |
| admin/users/passwordreset/<path:object_id>/history/ |  | users_passwordreset_history |  |  |
| admin/users/passwordreset/<path:object_id>/delete/ |  | users_passwordreset_delete |  |  |
| admin/users/passwordreset/<path:object_id>/change/ |  | users_passwordreset_change |  |  |
| admin/users/passwordreset/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/users/loginlog/ |  | users_loginlog_changelist |  |  |
| admin/users/loginlog/add/ |  | users_loginlog_add |  |  |
| admin/users/loginlog/<path:object_id>/history/ |  | users_loginlog_history |  |  |
| admin/users/loginlog/<path:object_id>/delete/ |  | users_loginlog_delete |  |  |
| admin/users/loginlog/<path:object_id>/change/ |  | users_loginlog_change |  |  |
| admin/users/loginlog/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/users/usersession/ |  | users_usersession_changelist |  |  |
| admin/users/usersession/add/ |  | users_usersession_add |  |  |
| admin/users/usersession/<path:object_id>/history/ |  | users_usersession_history |  |  |
| admin/users/usersession/<path:object_id>/delete/ |  | users_usersession_delete |  |  |
| admin/users/usersession/<path:object_id>/change/ |  | users_usersession_change |  |  |
| admin/users/usersession/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/course/ |  | courses_course_changelist |  |  |
| admin/courses/course/add/ |  | courses_course_add |  |  |
| admin/courses/course/<path:object_id>/history/ |  | courses_course_history |  |  |
| admin/courses/course/<path:object_id>/delete/ |  | courses_course_delete |  |  |
| admin/courses/course/<path:object_id>/change/ |  | courses_course_change |  |  |
| admin/courses/course/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/module/ |  | courses_module_changelist |  |  |
| admin/courses/module/add/ |  | courses_module_add |  |  |
| admin/courses/module/<path:object_id>/history/ |  | courses_module_history |  |  |
| admin/courses/module/<path:object_id>/delete/ |  | courses_module_delete |  |  |
| admin/courses/module/<path:object_id>/change/ |  | courses_module_change |  |  |
| admin/courses/module/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/lesson/ |  | courses_lesson_changelist |  |  |
| admin/courses/lesson/add/ |  | courses_lesson_add |  |  |
| admin/courses/lesson/<path:object_id>/history/ |  | courses_lesson_history |  |  |
| admin/courses/lesson/<path:object_id>/delete/ |  | courses_lesson_delete |  |  |
| admin/courses/lesson/<path:object_id>/change/ |  | courses_lesson_change |  |  |
| admin/courses/lesson/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/question/ |  | courses_question_changelist |  |  |
| admin/courses/question/add/ |  | courses_question_add |  |  |
| admin/courses/question/<path:object_id>/history/ |  | courses_question_history |  |  |
| admin/courses/question/<path:object_id>/delete/ |  | courses_question_delete |  |  |
| admin/courses/question/<path:object_id>/change/ |  | courses_question_change |  |  |
| admin/courses/question/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/enrollment/ |  | courses_enrollment_changelist |  |  |
| admin/courses/enrollment/add/ |  | courses_enrollment_add |  |  |
| admin/courses/enrollment/<path:object_id>/history/ |  | courses_enrollment_history |  |  |
| admin/courses/enrollment/<path:object_id>/delete/ |  | courses_enrollment_delete |  |  |
| admin/courses/enrollment/<path:object_id>/change/ |  | courses_enrollment_change |  |  |
| admin/courses/enrollment/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/progress/ |  | courses_progress_changelist |  |  |
| admin/courses/progress/add/ |  | courses_progress_add |  |  |
| admin/courses/progress/<path:object_id>/history/ |  | courses_progress_history |  |  |
| admin/courses/progress/<path:object_id>/delete/ |  | courses_progress_delete |  |  |
| admin/courses/progress/<path:object_id>/change/ |  | courses_progress_change |  |  |
| admin/courses/progress/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/assessmentattempt/ |  | courses_assessmentattempt_changelist |  |  |
| admin/courses/assessmentattempt/add/ |  | courses_assessmentattempt_add |  |  |
| admin/courses/assessmentattempt/<path:object_id>/history/ |  | courses_assessmentattempt_history |  |  |
| admin/courses/assessmentattempt/<path:object_id>/delete/ |  | courses_assessmentattempt_delete |  |  |
| admin/courses/assessmentattempt/<path:object_id>/change/ |  | courses_assessmentattempt_change |  |  |
| admin/courses/assessmentattempt/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/review/ |  | courses_review_changelist |  |  |
| admin/courses/review/add/ |  | courses_review_add |  |  |
| admin/courses/review/<path:object_id>/history/ |  | courses_review_history |  |  |
| admin/courses/review/<path:object_id>/delete/ |  | courses_review_delete |  |  |
| admin/courses/review/<path:object_id>/change/ |  | courses_review_change |  |  |
| admin/courses/review/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/certificate/ |  | courses_certificate_changelist |  |  |
| admin/courses/certificate/add/ |  | courses_certificate_add |  |  |
| admin/courses/certificate/<path:object_id>/history/ |  | courses_certificate_history |  |  |
| admin/courses/certificate/<path:object_id>/delete/ |  | courses_certificate_delete |  |  |
| admin/courses/certificate/<path:object_id>/change/ |  | courses_certificate_change |  |  |
| admin/courses/certificate/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/category/ |  | courses_category_changelist |  |  |
| admin/courses/category/add/ |  | courses_category_add |  |  |
| admin/courses/category/<path:object_id>/history/ |  | courses_category_history |  |  |
| admin/courses/category/<path:object_id>/delete/ |  | courses_category_delete |  |  |
| admin/courses/category/<path:object_id>/change/ |  | courses_category_change |  |  |
| admin/courses/category/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/resource/ |  | courses_resource_changelist |  |  |
| admin/courses/resource/add/ |  | courses_resource_add |  |  |
| admin/courses/resource/<path:object_id>/history/ |  | courses_resource_history |  |  |
| admin/courses/resource/<path:object_id>/delete/ |  | courses_resource_delete |  |  |
| admin/courses/resource/<path:object_id>/change/ |  | courses_resource_change |  |  |
| admin/courses/resource/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/answer/ |  | courses_answer_changelist |  |  |
| admin/courses/answer/add/ |  | courses_answer_add |  |  |
| admin/courses/answer/<path:object_id>/history/ |  | courses_answer_history |  |  |
| admin/courses/answer/<path:object_id>/delete/ |  | courses_answer_delete |  |  |
| admin/courses/answer/<path:object_id>/change/ |  | courses_answer_change |  |  |
| admin/courses/answer/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/attemptanswer/ |  | courses_attemptanswer_changelist |  |  |
| admin/courses/attemptanswer/add/ |  | courses_attemptanswer_add |  |  |
| admin/courses/attemptanswer/<path:object_id>/history/ |  | courses_attemptanswer_history |  |  |
| admin/courses/attemptanswer/<path:object_id>/delete/ |  | courses_attemptanswer_delete |  |  |
| admin/courses/attemptanswer/<path:object_id>/change/ |  | courses_attemptanswer_change |  |  |
| admin/courses/attemptanswer/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/note/ |  | courses_note_changelist |  |  |
| admin/courses/note/add/ |  | courses_note_add |  |  |
| admin/courses/note/<path:object_id>/history/ |  | courses_note_history |  |  |
| admin/courses/note/<path:object_id>/delete/ |  | courses_note_delete |  |  |
| admin/courses/note/<path:object_id>/change/ |  | courses_note_change |  |  |
| admin/courses/note/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/assessment/ |  | courses_assessment_changelist |  |  |
| admin/courses/assessment/add/ |  | courses_assessment_add |  |  |
| admin/courses/assessment/<path:object_id>/history/ |  | courses_assessment_history |  |  |
| admin/courses/assessment/<path:object_id>/delete/ |  | courses_assessment_delete |  |  |
| admin/courses/assessment/<path:object_id>/change/ |  | courses_assessment_change |  |  |
| admin/courses/assessment/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/courses/courseinstructor/ |  | courses_courseinstructor_changelist |  |  |
| admin/courses/courseinstructor/add/ |  | courses_courseinstructor_add |  |  |
| admin/courses/courseinstructor/<path:object_id>/history/ |  | courses_courseinstructor_history |  |  |
| admin/courses/courseinstructor/<path:object_id>/delete/ |  | courses_courseinstructor_delete |  |  |
| admin/courses/courseinstructor/<path:object_id>/change/ |  | courses_courseinstructor_change |  |  |
| admin/courses/courseinstructor/<path:object_id>/ | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |  |  |  |
| admin/^(?P<app_label>auth|users|courses)/$ |  | app_list |  |  |
| admin/(?P<url>.*)$ |  |  |  |  |
| api/^categories/$ | GET | category-list |  |  |
| api/^categories\.(?P<format>[a-z0-9]+)/?$ | GET | category-list |  |  |
| api/^categories/(?P<slug>[^/.]+)/$ | GET | category-detail |  |  |
| api/^categories/(?P<slug>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET | category-detail |  |  |
| api/^courses/$ | GET | course-list |  |  |
| api/^courses\.(?P<format>[a-z0-9]+)/?$ | GET | course-list |  |  |
| api/^courses/(?P<slug>[^/.]+)/$ | GET | course-detail |  |  |
| api/^courses/(?P<slug>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET | course-detail |  |  |
| api/^courses/(?P<slug>[^/.]+)/enroll/$ | POST | course-enroll |  |  |
| api/^courses/(?P<slug>[^/.]+)/enroll\.(?P<format>[a-z0-9]+)/?$ | POST | course-enroll |  |  |
| api/^courses/(?P<slug>[^/.]+)/modules/$ | GET | course-modules |  |  |
| api/^courses/(?P<slug>[^/.]+)/modules\.(?P<format>[a-z0-9]+)/?$ | GET | course-modules |  |  |
| api/^courses/(?P<slug>[^/.]+)/review/$ | POST | course-review |  |  |
| api/^courses/(?P<slug>[^/.]+)/review\.(?P<format>[a-z0-9]+)/?$ | POST | course-review |  |  |
| api/^courses/(?P<slug>[^/.]+)/reviews/$ | GET | course-reviews |  |  |
| api/^courses/(?P<slug>[^/.]+)/reviews\.(?P<format>[a-z0-9]+)/?$ | GET | course-reviews |  |  |
| api/^modules/$ | GET | module-list |  |  |
| api/^modules\.(?P<format>[a-z0-9]+)/?$ | GET | module-list |  |  |
| api/^modules/(?P<pk>[^/.]+)/$ | GET | module-detail |  |  |
| api/^modules/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET | module-detail |  |  |
| api/^modules/(?P<pk>[^/.]+)/lessons/$ | GET | module-lessons |  |  |
| api/^modules/(?P<pk>[^/.]+)/lessons\.(?P<format>[a-z0-9]+)/?$ | GET | module-lessons |  |  |
| api/^lessons/$ | GET | lesson-list |  |  |
| api/^lessons\.(?P<format>[a-z0-9]+)/?$ | GET | lesson-list |  |  |
| api/^lessons/(?P<pk>[^/.]+)/$ | GET | lesson-detail |  |  |
| api/^lessons/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET | lesson-detail |  |  |
| api/^enrollments/$ | GET, POST | enrollment-list |  |  |
| api/^enrollments\.(?P<format>[a-z0-9]+)/?$ | GET, POST | enrollment-list |  |  |
| api/^enrollments/(?P<pk>[^/.]+)/$ | GET, PUT, PATCH, DELETE | enrollment-detail |  |  |
| api/^enrollments/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET, PUT, PATCH, DELETE | enrollment-detail |  |  |
| api/ | GET, OPTIONS | api-root |  |  |
| api/<drf_format_suffix:format> | GET, OPTIONS | api-root |  |  |
| api/token/ | POST, OPTIONS | token_obtain_pair |  |  |
| api/token/refresh/ | POST, OPTIONS | token_refresh |  |  |
| api/system/db-status/ | GET, OPTIONS | db-status |  |  |
| api/system/db-stats/ | GET, OPTIONS | db-stats |  |  |
| api/user/register/ | POST, OPTIONS | register |  |  |
| api/user/login/ | POST, OPTIONS | login |  |  |
| api/user/logout/ | POST, OPTIONS | logout |  |  |
| api/user/token/refresh/ | POST, OPTIONS | token_refresh |  |  |
| api/user/me/ | GET, PUT, PATCH, OPTIONS | user-detail |  |  |
| api/user/profile/ | GET, PUT, PATCH, OPTIONS | user-profile |  |  |
| api/user/password/change/ | POST, OPTIONS | password-change |  |  |
| api/user/password/reset/ | POST, OPTIONS | password-reset-request |  |  |
| api/user/password/reset/confirm/ | POST, OPTIONS | password-reset-confirm |  |  |
| api/user/email/verify/ | POST, OPTIONS | email-verify |  |  |
| api/user/email/verify/resend/ | POST, OPTIONS | email-verify-resend |  |  |
| api/user/^sessions/$ | GET, POST | user-sessions-list |  |  |
| api/user/^sessions\.(?P<format>[a-z0-9]+)/?$ | GET, POST | user-sessions-list |  |  |
| api/user/^sessions/(?P<pk>[^/.]+)/$ | GET, PUT, PATCH, DELETE | user-sessions-detail |  |  |
| api/user/^sessions/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ | GET, PUT, PATCH, DELETE | user-sessions-detail |  |  |
| api/user/ | GET, OPTIONS | api-root |  |  |
| api/user/<drf_format_suffix:format> | GET, OPTIONS | api-root |  |  |
| api-auth/login/ | GET, POST, PUT, OPTIONS | login |  |  |
| api-auth/logout/ | GET, POST, OPTIONS | logout |  |  |

## Views

### logout_then_login

**Type:** Function-based
**App:** auth

**Description:** Log out the user if they are logged in. Then redirect to the login page.

### dispatch

**Type:** Function-based
**App:** auth

### dispatch

**Type:** Function-based
**App:** auth

### post

**Type:** Function-based
**App:** auth

**Description:** Logout may be done via POST.

### shortcut

**Type:** Function-based
**App:** contenttypes

**Description:** Redirect to an object's page based on a content-type ID and an object ID.

### serve

**Type:** Function-based
**App:** staticfiles

**Description:** Serve static files below a given point in the directory structure or
from locations inferred from the staticfiles finders.

To use, put a URL pattern such as::

    from django.contrib.staticfiles import views

    path('<path:path>', views.serve)

in your URLconf.

It uses the django.views.static.serve() view to serve the found files.

### APIView

**Type:** Class-based
**App:** rest_framework

**Methods:**

- `as_view`
- `allowed_methods`
- `default_response_headers`
- `http_method_not_allowed`
- `permission_denied`
- `throttled`
- `get_authenticate_header`
- `get_parser_context`
- `get_renderer_context`
- `get_exception_handler_context`
- `get_view_name`
- `get_view_description`
- `get_format_suffix`
- `get_renderers`
- `get_parsers`
- `get_authenticators`
- `get_permissions`
- `get_throttles`
- `get_content_negotiator`
- `get_exception_handler`
- `perform_content_negotiation`
- `perform_authentication`
- `check_permissions`
- `check_object_permissions`
- `check_throttles`
- `determine_version`
- `initialize_request`
- `initial`
- `finalize_response`
- `handle_exception`
- `raise_uncaught_exception`
- `dispatch`
- `options`

**Custom get_permissions Method:**

```python
def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]
```

**Custom get_throttles Method:**

```python
def get_throttles(self):
        """
        Instantiates and returns the list of throttles that this view uses.
        """
        return [throttle() for throttle in self.throttle_classes]
```

### http_method_not_allowed

**Type:** Function-based
**App:** rest_framework

**Description:** If `request.method` does not correspond to a handler method,
determine what kind of exception to raise.

### permission_denied

**Type:** Function-based
**App:** rest_framework

**Description:** If request is not permitted, determine what kind of exception to raise.

### throttled

**Type:** Function-based
**App:** rest_framework

**Description:** If request is throttled, determine what kind of exception to raise.

### get_authenticate_header

**Type:** Function-based
**App:** rest_framework

**Description:** If a request is unauthenticated, determine the WWW-Authenticate
header to use for 401 responses, if any.

### perform_content_negotiation

**Type:** Function-based
**App:** rest_framework

**Description:** Determine which renderer and media type to use render the response.

### perform_authentication

**Type:** Function-based
**App:** rest_framework

**Description:** Perform authentication on the incoming request.

Note that if you override this and simply 'pass', then authentication
will instead be performed lazily, the first time either
`request.user` or `request.auth` is accessed.

### check_permissions

**Type:** Function-based
**App:** rest_framework

**Description:** Check if the request should be permitted.
Raises an appropriate exception if the request is not permitted.

### check_object_permissions

**Type:** Function-based
**App:** rest_framework

**Description:** Check if the request should be permitted for a given object.
Raises an appropriate exception if the request is not permitted.

### check_throttles

**Type:** Function-based
**App:** rest_framework

**Description:** Check if request should be throttled.
Raises an appropriate exception if the request is throttled.

### determine_version

**Type:** Function-based
**App:** rest_framework

**Description:** If versioning is being used, then determine any API version for the
incoming request. Returns a two-tuple of (version, versioning_scheme)

### initialize_request

**Type:** Function-based
**App:** rest_framework

**Description:** Returns the initial request object.

### initial

**Type:** Function-based
**App:** rest_framework

**Description:** Runs anything that needs to occur prior to calling the method handler.

### finalize_response

**Type:** Function-based
**App:** rest_framework

**Description:** Returns the final response object.

### dispatch

**Type:** Function-based
**App:** rest_framework

**Description:** `.dispatch()` is pretty much the same as Django's regular dispatch,
but with extra hooks for startup, finalize, and exception handling.

### options

**Type:** Function-based
**App:** rest_framework

**Description:** Handler method for HTTP 'OPTIONS' request.

### TokenViewBase

**Type:** Class-based
**App:** rest_framework_simplejwt

**Methods:**

- `get_serializer_class`
- `get_authenticate_header`
- `post`

### get_authenticate_header

**Type:** Function-based
**App:** rest_framework_simplejwt

### post

**Type:** Function-based
**App:** rest_framework_simplejwt

### LoginView

**Type:** Class-based
**App:** users

**Description:** API view to authenticate users and return tokens.

**Permission Classes:**

- permissions.AllowAny

**Methods:**

- `post`
- `_get_client_ip`
- `_get_device_type`
- `_get_location_from_ip`

**Serializers:**

- LoginSerializer

### LogoutView

**Type:** Class-based
**App:** users

**Description:** API view to log out users by invalidating tokens.

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `post`

### UpdateProfileView

**Type:** Class-based
**App:** users

**Description:** Comprehensive API view to update both user and profile information.

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `get_object`
- `put`

**Serializers:**

- UpdateProfileSerializer

### PasswordChangeView

**Type:** Class-based
**App:** users

**Description:** API view to change user password.

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `post`

**Serializers:**

- PasswordChangeSerializer

### PasswordResetRequestView

**Type:** Class-based
**App:** users

**Description:** API view to request a password reset.

**Permission Classes:**

- permissions.AllowAny

**Methods:**

- `post`
- `_get_client_ip`
- `_send_reset_email`

**Serializers:**

- PasswordResetRequestSerializer

### PasswordResetConfirmView

**Type:** Class-based
**App:** users

**Description:** API view to confirm password reset with token.

**Permission Classes:**

- permissions.AllowAny

**Methods:**

- `post`

**Serializers:**

- PasswordResetConfirmSerializer

### EmailVerificationView

**Type:** Class-based
**App:** users

**Description:** API view to verify email with token.

**Permission Classes:**

- permissions.AllowAny

**Methods:**

- `post`

**Serializers:**

- EmailVerificationSerializer

### ResendVerificationView

**Type:** Class-based
**App:** users

**Description:** API view to resend verification email.

**Permission Classes:**

- permissions.AllowAny

**Methods:**

- `post`
- `_send_verification_email`

### UserSessionViewSet

**Type:** Class-based
**App:** users

**Description:** API viewset to manage user sessions.

**Permission Classes:**

- permissions.IsAuthenticated
- IsOwnerOrAdmin

**Methods:**

- `get_queryset`
- `destroy`

### SubscriptionViewSet

**Type:** Class-based
**App:** users

**Description:** API viewset to manage user subscriptions and tiered access.

Endpoints:
- GET /subscription/ - List user subscriptions
- GET /subscription/current/ - Get current subscription
- POST /subscription/upgrade/ - Upgrade to a paid tier
- POST /subscription/cancel/ - Cancel a subscription
- POST /subscription/downgrade/ - Downgrade to a lower tier

Access Levels:
- Unregistered users: Basic content
- Free tier: Intermediate content
- Paid tiers: Advanced content with certificates

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `get_queryset`
- `get_object`
- `current`
- `upgrade`
- `cancel`
- `downgrade`

**Serializers:**

- SubscriptionSerializer

### create

**Type:** Function-based
**App:** users

### post

**Type:** Function-based
**App:** users

### _get_client_ip

**Type:** Function-based
**App:** users

**Description:** Get client IP address from request.

### post

**Type:** Function-based
**App:** users

### update

**Type:** Function-based
**App:** users

### put

**Type:** Function-based
**App:** users

### post

**Type:** Function-based
**App:** users

### post

**Type:** Function-based
**App:** users

### _get_client_ip

**Type:** Function-based
**App:** users

**Description:** Get client IP address from request.

### post

**Type:** Function-based
**App:** users

### post

**Type:** Function-based
**App:** users

### post

**Type:** Function-based
**App:** users

### destroy

**Type:** Function-based
**App:** users

### current

**Type:** Function-based
**App:** users

**Description:** Get current subscription status

### upgrade

**Type:** Function-based
**App:** users

**Description:** Upgrade to a paid subscription tier

### cancel

**Type:** Function-based
**App:** users

**Description:** Cancel a paid subscription

### downgrade

**Type:** Function-based
**App:** users

**Description:** Downgrade to a lower tier at end of current period

### CategoryViewSet

**Type:** Class-based
**App:** courses

**Permission Classes:**

- IsAuthenticatedOrReadOnly

**Serializers:**

- CategorySerializer

### LessonViewSet

**Type:** Class-based
**App:** courses

**Permission Classes:**

- IsAuthenticatedOrReadOnly

**Methods:**

- `get_serializer_context`

**Serializers:**

- LessonSerializer

### EnrollmentViewSet

**Type:** Class-based
**App:** courses

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `get_queryset`
- `perform_create`

**Serializers:**

- EnrollmentSerializer

### CourseViewSet

**Type:** Class-based
**App:** courses

**Permission Classes:**

- IsAuthenticatedOrReadOnly

**Methods:**

- `get_serializer_class`
- `get_serializer_context`
- `enroll`
- `modules`
- `reviews`
- `review`

### ModuleViewSet

**Type:** Class-based
**App:** courses

**Methods:**

- `get_serializer_class`
- `get_serializer_context`
- `lessons`

### NoteViewSet

**Type:** Class-based
**App:** courses

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `get_queryset`
- `perform_create`

**Serializers:**

- NoteSerializer

### CertificateViewSet

**Type:** Class-based
**App:** courses

**Description:** ViewSet for accessing course completion certificates.
Only available to users with premium subscriptions.

**Permission Classes:**

- permissions.IsAuthenticated

**Methods:**

- `get_queryset`
- `course`

**Serializers:**

- CertificateSerializer

### enroll

**Type:** Function-based
**App:** courses

### modules

**Type:** Function-based
**App:** courses

### reviews

**Type:** Function-based
**App:** courses

### review

**Type:** Function-based
**App:** courses

### lessons

**Type:** Function-based
**App:** courses

### retrieve

**Type:** Function-based
**App:** courses

### update

**Type:** Function-based
**App:** courses

### create

**Type:** Function-based
**App:** courses

### update

**Type:** Function-based
**App:** courses

### course

**Type:** Function-based
**App:** courses

**Description:** Get certificate for a specific course

## Serializers

### Serializer

**App:** rest_framework
### ListSerializer

**App:** rest_framework
### ModelSerializer

**App:** rest_framework
### HyperlinkedModelSerializer

**App:** rest_framework
### NestedSerializer

**App:** rest_framework
**Fields:**

- __all__

### NestedSerializer

**App:** rest_framework
**Fields:**

- __all__

### TokenObtainSerializer

**App:** rest_framework_simplejwt
### TokenRefreshSerializer

**App:** rest_framework_simplejwt
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| refresh | CharField | No | No | No |  |  |  |
| access | CharField | No | Yes | No |  |  |  |

### TokenRefreshSlidingSerializer

**App:** rest_framework_simplejwt
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| token | CharField | No | No | No |  |  |  |

### TokenVerifySerializer

**App:** rest_framework_simplejwt
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| token | CharField | No | No | Yes |  |  |  |

### TokenBlacklistSerializer

**App:** rest_framework_simplejwt
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| refresh | CharField | No | No | Yes |  |  |  |

### ProfileSerializer

**App:** users
**Model:** Profile

### SubscriptionSerializer

**App:** users
**Model:** Subscription

**Fields:**

- tier
- status
- start_date
- end_date
- is_auto_renew
- last_payment_date
- is_active
- days_remaining

### UserSerializer

**App:** users
**Model:** User

**Fields:**

- id
- email
- username
- first_name
- last_name
- role
- is_email_verified
- date_joined
- last_login
- profile
- subscription

### UserCreateSerializer

**App:** users
**Model:** User

**Fields:**

- email
- username
- password
- password_confirm
- first_name
- last_name
- role

### UpdateProfileSerializer

**App:** users
**Model:** User

**Fields:**

- first_name
- last_name
- profile

### EmailVerificationSerializer

**App:** users
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| token | UUIDField | Yes | No | No |  |  |  |

### PasswordChangeSerializer

**App:** users
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| old_password | CharField | Yes | No | Yes |  |  |  |
| new_password | CharField | Yes | No | Yes |  |  |  |

### PasswordResetRequestSerializer

**App:** users
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| email | EmailField | Yes | No | No |  |  |  |

### PasswordResetConfirmSerializer

**App:** users
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| token | UUIDField | Yes | No | No |  |  |  |
| password | CharField | Yes | No | Yes |  |  |  |

### LoginSerializer

**App:** users
**Fields:**

| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |
|------|------|----------|-----------|------------|---------|---------|------------|
| email | EmailField | Yes | No | No |  |  |  |
| password | CharField | Yes | No | Yes |  |  |  |
| remember_me | BooleanField | No | No | No | False |  |  |

### UserSessionSerializer

**App:** users
**Model:** UserSession

**Fields:**

- id
- session_key
- ip_address
- user_agent
- created_at
- expires_at
- last_activity
- is_active
- device_type
- location

### CategorySerializer

**App:** courses
**Model:** Category

**Fields:**

- id
- name
- description
- icon
- slug

### ResourceSerializer

**App:** courses
**Model:** Resource

**Fields:**

- id
- title
- type
- file
- url
- description
- premium

### AnswerSerializer

**App:** courses
**Model:** Answer

**Fields:**

- id
- answer_text

### QuestionSerializer

**App:** courses
**Model:** Question

**Fields:**

- id
- question_text
- question_type
- order
- answers

### QuestionDetailSerializer

**App:** courses
**Model:** Question

**Fields:**

- id
- question_text
- question_type
- order
- points
- answers

### AssessmentSerializer

**App:** courses
**Model:** Assessment

**Fields:**

- id
- title
- description
- time_limit
- passing_score
- questions

### LessonSerializer

**App:** courses
**Model:** Lesson

**Fields:**

- id
- title
- content
- access_level
- duration
- type
- order
- has_assessment
- has_lab
- is_free_preview
- resources
- premium_resources
- is_completed

### ModuleSerializer

**App:** courses
**Model:** Module

**Fields:**

- id
- title
- description
- order
- duration

### ModuleDetailSerializer

**App:** courses
**Model:** Module

**Fields:**

- id
- title
- description
- order
- duration
- lessons

### CourseInstructorSerializer

**App:** courses
**Model:** CourseInstructor

**Fields:**

- instructor
- title
- bio
- is_lead

### CourseSerializer

**App:** courses
**Model:** Course

**Fields:**

- id
- title
- subtitle
- slug
- description
- category
- category_id
- thumbnail
- price
- discount_price
- discount_ends
- level
- duration
- has_certificate
- is_featured
- published_date
- updated_date
- instructors
- rating
- enrolled_students
- is_enrolled

### EnrollmentSerializer

**App:** courses
**Model:** Enrollment

**Fields:**

- id
- course
- course_id
- enrolled_date
- last_accessed
- status
- completion_date

### ProgressSerializer

**App:** courses
**Model:** Progress

**Fields:**

- id
- lesson
- is_completed
- completed_date
- time_spent

### AssessmentAttemptSerializer

**App:** courses
**Model:** AssessmentAttempt

**Fields:**

- id
- assessment
- start_time
- end_time
- score
- passed
- score_percentage

### AttemptAnswerSerializer

**App:** courses
**Model:** AttemptAnswer

**Fields:**

- id
- question
- selected_answer
- text_answer
- is_correct
- points_earned

### ReviewSerializer

**App:** courses
**Model:** Review

**Fields:**

- id
- user
- rating
- title
- content
- date_created
- helpful_count

### NoteSerializer

**App:** courses
**Model:** Note

**Fields:**

- id
- lesson
- content
- created_date
- updated_date

### CertificateSerializer

**App:** courses
**Model:** Certificate

**Fields:**

- id
- enrollment
- issue_date
- certificate_number
- course
- user

## Authentication

**Authentication Classes:**

- TokenAuthentication
- JWTAuthentication
- SessionAuthentication

**Permission Classes:**

- IsOwnerOrAdmin
- permissions.AllowAny
- permissions.IsAuthenticated
- IsAuthenticatedOrReadOnly

**Authentication Types:**

- Token Authentication
- JWT Authentication
- Session Authentication
