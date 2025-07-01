# Django Models Schema Report

**Total Models**: 67

## App: account

### EmailAddress -> `account_emailaddress`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `email` | EmailField | email |  | IDX |  |
| `verified` | BooleanField | verified |  |  |  |
| `primary` | BooleanField | primary |  |  |  |

**Constraints:**
- `unique_primary_email` (UniqueConstraint): [user, primary]
- `unique_verified_email` (UniqueConstraint): [email]
- `unique_together_account_emailaddress` (unique_together): [user, email]

---

### EmailConfirmation -> `account_emailconfirmation`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `email_address` | ForeignKey | email_address |  | IDX | account.emailaddress (CASCADE) |
| `created` | DateTimeField | created |  |  |  |
| `sent` | DateTimeField | sent | Y |  |  |
| `key` | CharField | key |  | UQ |  |

---

## App: ai_course_builder

### AICourseBuilderDraft -> `ai_course_builder_aicoursebuilderdraft`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | ForeignKey | instructor |  | IDX | users.customuser (CASCADE) |
| `created_at` | DateTimeField | created_at |  |  |  |
| `updated_at` | DateTimeField | updated_at |  |  |  |
| `status` | CharField | status |  |  |  |
| `title` | CharField | title | Y |  |  |
| `description` | TextField | description | Y |  |  |
| `course_objectives` | JSONField | course_objectives | Y |  |  |
| `target_audience` | JSONField | target_audience | Y |  |  |
| `difficulty_level` | CharField | difficulty_level | Y |  |  |
| `duration_minutes` | PositiveIntegerField | duration_minutes | Y |  |  |
| `price` | DecimalField | price | Y |  |  |
| `outline` | JSONField | outline | Y |  |  |
| `content` | JSONField | content | Y |  |  |
| `assessments` | JSONField | assessments | Y |  |  |
| `has_outline` | BooleanField | has_outline |  |  |  |
| `has_modules` | BooleanField | has_modules |  |  |  |
| `has_lessons` | BooleanField | has_lessons |  |  |  |
| `has_assessments` | BooleanField | has_assessments |  |  |  |
| `generation_metadata` | JSONField | generation_metadata | Y |  |  |

---

## App: content

### InstructorStatistics -> `content_instructorstatistics`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `courses_created` | PositiveIntegerField | courses_created |  |  |  |
| `total_students` | PositiveIntegerField | total_students |  |  |  |
| `average_rating` | FloatField | average_rating |  |  |  |
| `last_updated` | DateTimeField | last_updated |  |  |  |

---

### PlatformStatistics -> `content_platformstatistics`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `total_courses` | PositiveIntegerField | total_courses |  |  |  |
| `total_students` | PositiveIntegerField | total_students |  |  |  |
| `total_instructors` | PositiveIntegerField | total_instructors |  |  |  |
| `total_lessons_completed` | PositiveIntegerField | total_lessons_completed |  |  |  |
| `total_certificates_issued` | PositiveIntegerField | total_certificates_issued |  |  |  |
| `last_updated` | DateTimeField | last_updated |  |  |  |

---

### Testimonial -> `content_testimonial`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `name` | CharField | name |  |  |  |
| `role` | CharField | role |  |  |  |
| `content` | TextField | content |  |  |  |
| `rating` | IntegerField | rating |  |  |  |
| `avatar` | ImageField | avatar | Y |  |  |
| `featured` | BooleanField | featured |  |  |  |
| `created_at` | DateTimeField | created_at |  |  |  |
| `updated_at` | DateTimeField | updated_at |  |  |  |

---

### UserLearningStatistics -> `content_userlearningstatistics`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `courses_completed` | PositiveIntegerField | courses_completed |  |  |  |
| `hours_spent` | PositiveIntegerField | hours_spent |  |  |  |
| `average_score` | FloatField | average_score |  |  |  |
| `last_updated` | DateTimeField | last_updated |  |  |  |

---

## App: courses

### Answer -> `courses_answer`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `question` | ForeignKey | question |  | IDX | courses.question (CASCADE) |
| `answer_text` | CharField | answer_text |  |  |  |
| `text` | TextField | text |  |  |  |
| `is_correct` | BooleanField | is_correct |  |  |  |
| `explanation` | TextField | explanation | Y |  |  |
| `order` | PositiveIntegerField | order |  |  |  |

**Constraints:**
- `unique_answer_order` (UniqueConstraint): [question, order]

**Indexes:**
- `courses_ans_questio_aedf7d_idx`: [question, order]
- `courses_ans_is_corr_9dd4bc_idx`: [is_correct]

---

### Assessment -> `courses_assessment`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `lesson` | OneToOneField | lesson |  | UQ,IDX | courses.lesson (CASCADE) |
| `title` | CharField | title |  |  |  |
| `description` | TextField | description | Y |  |  |
| `passing_score` | PositiveIntegerField | passing_score |  |  |  |
| `max_attempts` | PositiveIntegerField | max_attempts |  |  |  |
| `time_limit` | PositiveIntegerField | time_limit |  |  |  |
| `time_limit_minutes` | PositiveIntegerField | time_limit_minutes |  |  |  |
| `randomize_questions` | BooleanField | randomize_questions |  |  |  |
| `show_correct_answers` | BooleanField | show_correct_answers |  |  |  |
| `show_results` | BooleanField | show_results |  |  |  |

**Indexes:**
- `courses_ass_lesson__4afa06_idx`: [lesson]
- `courses_ass_passing_b8a83e_idx`: [passing_score]

---

### AssessmentAttempt -> `courses_assessmentattempt`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `assessment` | ForeignKey | assessment |  | IDX | courses.assessment (CASCADE) |
| `start_time` | DateTimeField | start_time |  |  |  |
| `end_time` | DateTimeField | end_time | Y |  |  |
| `time_taken_seconds` | PositiveIntegerField | time_taken_seconds |  |  |  |
| `score` | PositiveIntegerField | score |  |  |  |
| `max_score` | PositiveIntegerField | max_score |  |  |  |
| `is_completed` | BooleanField | is_completed |  |  |  |
| `is_passed` | BooleanField | is_passed |  |  |  |
| `passed` | BooleanField | passed |  |  |  |
| `attempt_number` | PositiveIntegerField | attempt_number |  |  |  |
| `ip_address` | GenericIPAddressField | ip_address | Y |  |  |
| `user_agent` | TextField | user_agent | Y |  |  |

**Indexes:**
- `courses_ass_user_id_fedd97_idx`: [user, assessment]
- `courses_ass_assessm_1f3420_idx`: [assessment, -created_date]
- `courses_ass_is_pass_af4398_idx`: [is_passed]
- `courses_ass_is_comp_5317c4_idx`: [is_completed]
- `courses_ass_attempt_d56abe_idx`: [attempt_number]

---

### AttemptAnswer -> `courses_attemptanswer`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `attempt` | ForeignKey | attempt |  | IDX | courses.assessmentattempt (CASCADE) |
| `question` | ForeignKey | question |  | IDX | courses.question (CASCADE) |
| `selected_answer` | ForeignKey | selected_answer | Y | IDX | courses.answer (CASCADE) |
| `answer` | ForeignKey | answer | Y | IDX | courses.answer (CASCADE) |
| `text_answer` | TextField | text_answer | Y |  |  |
| `text_response` | TextField | text_response |  |  |  |
| `is_correct` | BooleanField | is_correct |  |  |  |
| `points_earned` | PositiveIntegerField | points_earned |  |  |  |
| `feedback` | TextField | feedback | Y |  |  |
| `answered_at` | DateTimeField | answered_at |  |  |  |

**Constraints:**
- `unique_attempt_answer` (UniqueConstraint): [attempt, question]

**Indexes:**
- `courses_att_attempt_aab6c9_idx`: [attempt, question]
- `courses_att_is_corr_be0997_idx`: [is_correct]

---

### Bookmark -> `courses_bookmark`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `content_type` | ForeignKey | content_type |  | IDX | contenttypes.contenttype (CASCADE) |
| `object_id` | PositiveIntegerField | object_id |  |  |  |
| `title` | CharField | title |  |  |  |
| `notes` | TextField | notes |  |  |  |
| `position` | PositiveIntegerField | position |  |  |  |

**Constraints:**
- `unique_together_courses_bookmark` (unique_together): [user, content_type, object_id]

**Indexes:**
- `courses_boo_user_id_c5e744_idx`: [user, content_type, object_id]
- `courses_boo_user_id_9a294c_idx`: [user, position]

---

### Category -> `courses_category`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `slug` | SlugField | slug |  | UQ,IDX |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `name` | CharField | name |  | UQ |  |
| `description` | TextField | description | Y |  |  |
| `icon` | CharField | icon | Y |  |  |
| `sort_order` | PositiveIntegerField | sort_order |  |  |  |
| `parent` | ForeignKey | parent | Y | IDX | courses.category (CASCADE) |
| `featured` | BooleanField | featured |  |  |  |

**Constraints:**
- `unique_category_slug` (UniqueConstraint): [slug]
- `category_sort_order_positive` (CheckConstraint): []

**Indexes:**
- `courses_cat_created_8cf2cb_idx`: [created_date]
- `courses_cat_updated_67ffb8_idx`: [updated_date]
- `courses_cat_slug_33564e_idx`: [slug]
- `courses_cat_is_acti_61a38c_idx`: [is_active]
- `courses_cat_sort_or_896e38_idx`: [sort_order]
- `courses_cat_name_ab7c10_idx`: [name]
- `courses_cat_parent__abacdd_idx`: [parent]

---

### Certificate -> `courses_certificate`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `enrollment` | OneToOneField | enrollment |  | UQ,IDX | courses.enrollment (CASCADE) |
| `certificate_number` | CharField | certificate_number |  | UQ |  |
| `is_valid` | BooleanField | is_valid |  |  |  |
| `revocation_date` | DateTimeField | revocation_date | Y |  |  |
| `revocation_reason` | TextField | revocation_reason | Y |  |  |
| `verification_hash` | CharField | verification_hash |  | UQ |  |
| `template_version` | CharField | template_version |  |  |  |

**Constraints:**
- `unique_certificate_number` (UniqueConstraint): [certificate_number]
- `unique_verification_hash` (UniqueConstraint): [verification_hash]

**Indexes:**
- `courses_cer_created_6482f3_idx`: [created_date]
- `courses_cer_updated_e6b0b5_idx`: [updated_date]
- `courses_cer_certifi_b5881b_idx`: [certificate_number]
- `courses_cer_verific_19df54_idx`: [verification_hash]
- `courses_cer_is_vali_2f2340_idx`: [is_valid]
- `courses_cer_revocat_79b12c_idx`: [revocation_date]

---

### Course -> `courses_course`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `slug` | SlugField | slug |  | UQ,IDX |  |
| `duration_minutes` | PositiveIntegerField | duration_minutes | Y |  |  |
| `is_published` | BooleanField | is_published |  |  |  |
| `published_date` | DateTimeField | published_date | Y |  |  |
| `view_count` | PositiveIntegerField | view_count |  |  |  |
| `last_accessed` | DateTimeField | last_accessed |  |  |  |
| `title` | CharField | title |  |  |  |
| `subtitle` | CharField | subtitle | Y |  |  |
| `description` | TextField | description |  |  |  |
| `category` | ForeignKey | category |  | IDX | courses.category (CASCADE) |
| `thumbnail` | ImageField | thumbnail | Y |  |  |
| `price` | DecimalField | price |  |  |  |
| `discount_price` | DecimalField | discount_price | Y |  |  |
| `discount_ends` | DateTimeField | discount_ends | Y |  |  |
| `level` | CharField | level |  |  |  |
| `has_certificate` | BooleanField | has_certificate |  |  |  |
| `is_featured` | BooleanField | is_featured |  |  |  |
| `requirements` | JSONField | requirements |  |  |  |
| `skills` | JSONField | skills |  |  |  |
| `learning_objectives` | JSONField | learning_objectives |  |  |  |
| `target_audience` | TextField | target_audience | Y |  |  |
| `creation_method` | CharField | creation_method |  |  |  |
| `completion_status` | CharField | completion_status |  |  |  |
| `completion_percentage` | IntegerField | completion_percentage |  |  |  |
| `version` | DecimalField | version |  |  |  |
| `is_draft` | BooleanField | is_draft |  |  |  |
| `parent_version` | ForeignKey | parent_version | Y | IDX | courses.course (SET_NULL) |
| `meta_keywords` | CharField | meta_keywords | Y |  |  |
| `meta_description` | TextField | meta_description | Y |  |  |
| `preview_token` | CharField | preview_token | Y |  |  |
| `preview_expiry` | DateTimeField | preview_expiry | Y |  |  |
| `enrolled_students_count` | PositiveIntegerField | enrolled_students_count |  |  |  |
| `avg_rating` | DecimalField | avg_rating |  |  |  |
| `total_reviews` | PositiveIntegerField | total_reviews |  |  |  |
| `last_enrollment_date` | DateTimeField | last_enrollment_date | Y |  |  |

**Constraints:**
- `unique_course_slug` (UniqueConstraint): [slug]
- `course_price_positive` (CheckConstraint): []
- `course_discount_price_positive` (CheckConstraint): []
- `course_version_positive` (CheckConstraint): []
- `course_discount_less_than_price` (CheckConstraint): []

**Indexes:**
- `courses_cou_created_7da7d5_idx`: [created_date]
- `courses_cou_updated_517180_idx`: [updated_date]
- `courses_cou_slug_2e551f_idx`: [slug]
- `courses_cou_is_publ_4b99b9_idx`: [is_published]
- `courses_cou_publish_80f4bd_idx`: [published_date]
- `courses_cou_view_co_55d4de_idx`: [view_count]
- `courses_cou_last_ac_9655a6_idx`: [last_accessed]
- `courses_cou_categor_e9e0ba_idx`: [category, is_published]
- `courses_cou_is_feat_6821f1_idx`: [is_featured, is_published]
- `courses_cou_level_a2b259_idx`: [level, is_published]
- `courses_cou_parent__886ac7_idx`: [parent_version, version]
- `courses_cou_creatio_6175b0_idx`: [creation_method]
- `courses_cou_complet_a28d16_idx`: [completion_status]
- `courses_cou_is_draf_460a8b_idx`: [is_draft]
- `courses_cou_price_1fbd18_idx`: [price]
- `courses_cou_avg_rat_82cd8e_idx`: [avg_rating]

---

### CourseProgress -> `courses_courseprogress`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `course` | ForeignKey | course |  | IDX | courses.course (CASCADE) |
| `completion_percentage` | DecimalField | completion_percentage |  |  |  |
| `last_accessed` | DateTimeField | last_accessed |  |  |  |
| `started_at` | DateTimeField | started_at |  |  |  |
| `completed_at` | DateTimeField | completed_at | Y |  |  |
| `current_lesson` | ForeignKey | current_lesson | Y | IDX | courses.lesson (SET_NULL) |
| `total_time_spent` | PositiveIntegerField | total_time_spent |  |  |  |
| `lessons_completed` | PositiveIntegerField | lessons_completed |  |  |  |
| `assessments_passed` | PositiveIntegerField | assessments_passed |  |  |  |
| `study_streak_days` | PositiveIntegerField | study_streak_days |  |  |  |
| `last_study_date` | DateField | last_study_date | Y |  |  |

**Constraints:**
- `unique_course_progress` (UniqueConstraint): [user, course]
- `course_progress_percentage_range` (CheckConstraint): []
- `course_progress_lessons_completed_positive` (CheckConstraint): []
- `course_progress_assessments_passed_positive` (CheckConstraint): []
- `course_progress_study_streak_positive` (CheckConstraint): []

**Indexes:**
- `courses_cou_created_6c9322_idx`: [created_date]
- `courses_cou_updated_2dc6a5_idx`: [updated_date]
- `courses_cou_user_id_06f975_idx`: [user, course]
- `courses_cou_course__4ab7f3_idx`: [course, completion_percentage]
- `courses_cou_user_id_d1c82f_idx`: [user, last_accessed]
- `courses_cou_complet_96dc1c_idx`: [completion_percentage]
- `courses_cou_complet_977240_idx`: [completed_at]
- `courses_cou_study_s_9cf964_idx`: [study_streak_days]

---

### CourseStats -> `courses_coursestats`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `course` | OneToOneField | course |  | UQ,IDX | courses.course (CASCADE) |
| `total_students` | PositiveIntegerField | total_students |  |  |  |
| `active_students` | PositiveIntegerField | active_students |  |  |  |
| `completion_count` | PositiveIntegerField | completion_count |  |  |  |
| `average_completion_days` | PositiveIntegerField | average_completion_days |  |  |  |
| `engagement_score` | DecimalField | engagement_score |  |  |  |
| `assessment_stats` | JSONField | assessment_stats |  |  |  |
| `revenue_data` | JSONField | revenue_data |  |  |  |

---

### Enrollment -> `courses_enrollment`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `course` | ForeignKey | course |  | IDX | courses.course (CASCADE) |
| `status` | CharField | status |  |  |  |
| `completion_date` | DateTimeField | completion_date | Y |  |  |
| `last_accessed` | DateTimeField | last_accessed |  |  |  |
| `enrolled_date` | DateTimeField | enrolled_date |  |  |  |
| `total_time_spent` | PositiveIntegerField | total_time_spent |  |  |  |
| `progress_percentage` | PositiveIntegerField | progress_percentage |  |  |  |
| `last_lesson_accessed` | ForeignKey | last_lesson_accessed | Y | IDX | courses.lesson (SET_NULL) |

**Constraints:**
- `unique_active_enrollment` (UniqueConstraint): [user, course]

**Indexes:**
- `courses_enr_created_2cb035_idx`: [created_date]
- `courses_enr_updated_05225a_idx`: [updated_date]
- `courses_enr_user_id_ce8b5b_idx`: [user, status]
- `courses_enr_course__78d524_idx`: [course, status]
- `courses_enr_status_4fd017_idx`: [status]
- `courses_enr_complet_57338c_idx`: [completion_date]
- `courses_enr_progres_dba947_idx`: [progress_percentage]
- `courses_enr_enrolle_17cda0_idx`: [enrolled_date]

---

### Lesson -> `courses_lesson`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `order` | PositiveIntegerField | order |  |  |  |
| `duration_minutes` | PositiveIntegerField | duration_minutes | Y |  |  |
| `module` | ForeignKey | module |  | IDX | courses.module (CASCADE) |
| `title` | CharField | title |  |  |  |
| `content` | TextField | content |  |  |  |
| `guest_content` | TextField | guest_content | Y |  |  |
| `registered_content` | TextField | registered_content | Y |  |  |
| `access_level` | CharField | access_level |  |  |  |
| `type` | CharField | type |  |  |  |
| `activity_type` | CharField | activity_type |  |  |  |
| `has_assessment` | BooleanField | has_assessment |  |  |  |
| `has_lab` | BooleanField | has_lab |  |  |  |
| `is_free_preview` | BooleanField | is_free_preview |  |  |  |
| `video_url` | URLField | video_url | Y |  |  |
| `transcript` | TextField | transcript | Y |  |  |

**Constraints:**
- `unique_lesson_order` (UniqueConstraint): [module, order]

**Indexes:**
- `courses_les_created_7fbce2_idx`: [created_date]
- `courses_les_updated_ac21ad_idx`: [updated_date]
- `courses_les_order_ffd43c_idx`: [order]
- `courses_les_module__4accd4_idx`: [module, order]
- `courses_les_access__657329_idx`: [access_level]
- `courses_les_type_805272_idx`: [type]
- `courses_les_activit_845908_idx`: [activity_type]
- `courses_les_is_free_a8e681_idx`: [is_free_preview]
- `courses_les_has_ass_d9b62a_idx`: [has_assessment]
- `courses_les_has_lab_01b267_idx`: [has_lab]

---

### Module -> `courses_module`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `order` | PositiveIntegerField | order |  |  |  |
| `duration_minutes` | PositiveIntegerField | duration_minutes | Y |  |  |
| `is_published` | BooleanField | is_published |  |  |  |
| `published_date` | DateTimeField | published_date | Y |  |  |
| `course` | ForeignKey | course |  | IDX | courses.course (CASCADE) |
| `title` | CharField | title |  |  |  |
| `description` | TextField | description | Y |  |  |

**Constraints:**
- `unique_module_order` (UniqueConstraint): [course, order]

**Indexes:**
- `courses_mod_created_9a6a7d_idx`: [created_date]
- `courses_mod_updated_141b50_idx`: [updated_date]
- `courses_mod_order_e9c068_idx`: [order]
- `courses_mod_is_publ_875329_idx`: [is_published]
- `courses_mod_publish_823717_idx`: [published_date]
- `courses_mod_course__20183c_idx`: [course, order]
- `courses_mod_course__92d7f3_idx`: [course, is_published]

---

### Note -> `courses_note`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `lesson` | ForeignKey | lesson |  | IDX | courses.lesson (CASCADE) |
| `content` | TextField | content |  |  |  |
| `timestamp_seconds` | PositiveIntegerField | timestamp_seconds |  |  |  |
| `is_private` | BooleanField | is_private |  |  |  |
| `tags` | JSONField | tags |  |  |  |

**Indexes:**
- `courses_not_user_id_eece44_idx`: [user, lesson]
- `courses_not_lesson__5f16a2_idx`: [lesson, is_private]
- `courses_not_is_priv_3def52_idx`: [is_private]

---

### Notification -> `courses_notification`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `title` | CharField | title |  |  |  |
| `message` | TextField | message |  |  |  |
| `notification_type` | CharField | notification_type |  |  |  |
| `course` | ForeignKey | course | Y | IDX | courses.course (CASCADE) |
| `is_read` | BooleanField | is_read |  |  |  |
| `read_date` | DateTimeField | read_date | Y |  |  |
| `action_url` | URLField | action_url |  |  |  |

**Indexes:**
- `courses_not_user_id_149621_idx`: [user, -created_date]
- `courses_not_is_read_7c54d4_idx`: [is_read]
- `courses_not_notific_2eee2c_idx`: [notification_type]

---

### Progress -> `courses_progress`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `enrollment` | ForeignKey | enrollment |  | IDX | courses.enrollment (CASCADE) |
| `lesson` | ForeignKey | lesson |  | IDX | courses.lesson (CASCADE) |
| `is_completed` | BooleanField | is_completed |  |  |  |
| `completed_date` | DateTimeField | completed_date | Y |  |  |
| `time_spent` | PositiveIntegerField | time_spent |  |  |  |
| `progress_percentage` | PositiveIntegerField | progress_percentage |  |  |  |
| `notes` | TextField | notes | Y |  |  |
| `last_accessed` | DateTimeField | last_accessed |  |  |  |

**Constraints:**
- `unique_progress_record` (UniqueConstraint): [enrollment, lesson]

**Indexes:**
- `courses_pro_created_6822b9_idx`: [created_date]
- `courses_pro_updated_f54b15_idx`: [updated_date]
- `courses_pro_enrollm_e8bb03_idx`: [enrollment, is_completed]
- `courses_pro_lesson__76321e_idx`: [lesson, is_completed]
- `courses_pro_complet_5ebc5b_idx`: [completed_date]
- `courses_pro_progres_c67c74_idx`: [progress_percentage]

---

### Question -> `courses_question`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `assessment` | ForeignKey | assessment |  | IDX | courses.assessment (CASCADE) |
| `question_text` | TextField | question_text |  |  |  |
| `text` | TextField | text |  |  |  |
| `question_type` | CharField | question_type |  |  |  |
| `points` | PositiveIntegerField | points |  |  |  |
| `order` | PositiveIntegerField | order |  |  |  |
| `explanation` | TextField | explanation | Y |  |  |
| `feedback` | TextField | feedback |  |  |  |

**Constraints:**
- `unique_question_order` (UniqueConstraint): [assessment, order]

**Indexes:**
- `courses_que_assessm_2927ae_idx`: [assessment, order]
- `courses_que_questio_beffac_idx`: [question_type]
- `courses_que_points_6da46d_idx`: [points]

---

### Resource -> `courses_resource`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `order` | PositiveIntegerField | order |  |  |  |
| `duration_minutes` | PositiveIntegerField | duration_minutes | Y |  |  |
| `storage_key` | CharField | storage_key | Y |  |  |
| `uploaded` | BooleanField | uploaded |  |  |  |
| `file_size` | PositiveBigIntegerField | file_size | Y |  |  |
| `mime_type` | CharField | mime_type | Y |  |  |
| `lesson` | ForeignKey | lesson |  | IDX | courses.lesson (CASCADE) |
| `title` | CharField | title |  |  |  |
| `type` | CharField | type |  |  |  |
| `description` | TextField | description | Y |  |  |
| `file` | FileField | file | Y |  |  |
| `url` | URLField | url | Y |  |  |
| `premium` | BooleanField | premium |  |  |  |
| `download_count` | PositiveIntegerField | download_count |  |  |  |

**Constraints:**
- `unique_resource_order` (UniqueConstraint): [lesson, order]

**Indexes:**
- `courses_res_created_2d1e4f_idx`: [created_date]
- `courses_res_updated_5e9c80_idx`: [updated_date]
- `courses_res_order_e289a6_idx`: [order]
- `courses_res_uploade_42c1ed_idx`: [uploaded]
- `courses_res_mime_ty_616554_idx`: [mime_type]
- `courses_res_lesson__12dbf2_idx`: [lesson, order]
- `courses_res_type_380823_idx`: [type]
- `courses_res_premium_945503_idx`: [premium]

---

### Review -> `courses_review`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `course` | ForeignKey | course |  | IDX | courses.course (CASCADE) |
| `rating` | PositiveSmallIntegerField | rating |  |  |  |
| `title` | CharField | title | Y |  |  |
| `content` | TextField | content |  |  |  |
| `helpful_count` | PositiveIntegerField | helpful_count |  |  |  |
| `is_verified_purchase` | BooleanField | is_verified_purchase |  |  |  |
| `is_approved` | BooleanField | is_approved |  |  |  |
| `is_featured` | BooleanField | is_featured |  |  |  |
| `moderation_notes` | TextField | moderation_notes | Y |  |  |

**Constraints:**
- `unique_user_course_review` (UniqueConstraint): [user, course]

**Indexes:**
- `courses_rev_course__c5c65a_idx`: [course, -created_date]
- `courses_rev_user_id_6a1f95_idx`: [user, -created_date]
- `courses_rev_rating_004eae_idx`: [rating]
- `courses_rev_is_appr_03a92f_idx`: [is_approved, is_featured]

---

### UserActivity -> `courses_useractivity`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `activity_type` | CharField | activity_type |  |  |  |
| `course` | ForeignKey | course | Y | IDX | courses.course (CASCADE) |
| `lesson` | ForeignKey | lesson | Y | IDX | courses.lesson (CASCADE) |
| `resource` | ForeignKey | resource | Y | IDX | courses.resource (CASCADE) |
| `assessment` | ForeignKey | assessment | Y | IDX | courses.assessment (CASCADE) |
| `data` | JSONField | data |  |  |  |

**Indexes:**
- `courses_use_user_id_b38400_idx`: [user, -created_date]
- `courses_use_activit_804475_idx`: [activity_type]
- `courses_use_course__fa711b_idx`: [course, -created_date]

---

### UserPreference -> `courses_userpreference`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `email_notifications` | BooleanField | email_notifications |  |  |  |
| `reminder_frequency` | CharField | reminder_frequency |  |  |  |
| `theme` | CharField | theme |  |  |  |
| `language` | CharField | language |  |  |  |
| `content_filters` | JSONField | content_filters |  |  |  |
| `accessibility` | JSONField | accessibility |  |  |  |

---

### UserStats -> `courses_userstats`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `courses_enrolled` | PositiveIntegerField | courses_enrolled |  |  |  |
| `courses_completed` | PositiveIntegerField | courses_completed |  |  |  |
| `total_time_spent_seconds` | PositiveBigIntegerField | total_time_spent_seconds |  |  |  |
| `assessment_avg_score` | DecimalField | assessment_avg_score |  |  |  |
| `last_activity` | DateTimeField | last_activity | Y |  |  |
| `activity_streak` | PositiveIntegerField | activity_streak |  |  |  |
| `learning_habits` | JSONField | learning_habits |  |  |  |

---

## App: django_celery_beat

### ClockedSchedule -> `django_celery_beat_clockedschedule`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `clocked_time` | DateTimeField | clocked_time |  |  |  |

---

### CrontabSchedule -> `django_celery_beat_crontabschedule`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `minute` | CharField | minute |  |  |  |
| `hour` | CharField | hour |  |  |  |
| `day_of_month` | CharField | day_of_month |  |  |  |
| `month_of_year` | CharField | month_of_year |  |  |  |
| `day_of_week` | CharField | day_of_week |  |  |  |
| `timezone` | TimeZoneField | timezone |  |  |  |

---

### IntervalSchedule -> `django_celery_beat_intervalschedule`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `every` | IntegerField | every |  |  |  |
| `period` | CharField | period |  |  |  |

---

### PeriodicTask -> `django_celery_beat_periodictask`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `name` | CharField | name |  | UQ |  |
| `task` | CharField | task |  |  |  |
| `interval` | ForeignKey | interval | Y | IDX | django_celery_beat.intervalschedule (CASCADE) |
| `crontab` | ForeignKey | crontab | Y | IDX | django_celery_beat.crontabschedule (CASCADE) |
| `solar` | ForeignKey | solar | Y | IDX | django_celery_beat.solarschedule (CASCADE) |
| `clocked` | ForeignKey | clocked | Y | IDX | django_celery_beat.clockedschedule (CASCADE) |
| `args` | TextField | args |  |  |  |
| `kwargs` | TextField | kwargs |  |  |  |
| `queue` | CharField | queue | Y |  |  |
| `exchange` | CharField | exchange | Y |  |  |
| `routing_key` | CharField | routing_key | Y |  |  |
| `headers` | TextField | headers |  |  |  |
| `priority` | PositiveIntegerField | priority | Y |  |  |
| `expires` | DateTimeField | expires | Y |  |  |
| `expire_seconds` | PositiveIntegerField | expire_seconds | Y |  |  |
| `one_off` | BooleanField | one_off |  |  |  |
| `start_time` | DateTimeField | start_time | Y |  |  |
| `enabled` | BooleanField | enabled |  |  |  |
| `last_run_at` | DateTimeField | last_run_at | Y |  |  |
| `total_run_count` | PositiveIntegerField | total_run_count |  |  |  |
| `date_changed` | DateTimeField | date_changed |  |  |  |
| `description` | TextField | description |  |  |  |

---

### PeriodicTasks -> `django_celery_beat_periodictasks`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `ident` | SmallIntegerField | ident |  | PK,UQ |  |
| `last_update` | DateTimeField | last_update |  |  |  |

---

### SolarSchedule -> `django_celery_beat_solarschedule`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `event` | CharField | event |  |  |  |
| `latitude` | DecimalField | latitude |  |  |  |
| `longitude` | DecimalField | longitude |  |  |  |

**Constraints:**
- `unique_together_django_celery_beat_solarschedule` (unique_together): [event, latitude, longitude]

---

## App: instructor_portal

### CourseContentDraft -> `instructor_portal_coursecontentdraft`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `session` | ForeignKey | session |  | IDX | instructor_portal.coursecreationsession (CASCADE) |
| `content_type` | CharField | content_type |  |  |  |
| `file_path` | FileField | file_path | Y |  |  |
| `content_hash` | CharField | content_hash |  |  |  |
| `version` | PositiveIntegerField | version |  |  |  |
| `is_processed` | BooleanField | is_processed |  |  |  |
| `processing_status` | CharField | processing_status |  |  |  |
| `processing_error` | TextField | processing_error |  |  |  |
| `file_size` | PositiveIntegerField | file_size | Y |  |  |
| `mime_type` | CharField | mime_type |  |  |  |
| `original_filename` | CharField | original_filename |  |  |  |
| `processing_metadata` | JSONField | processing_metadata |  |  |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `processed_date` | DateTimeField | processed_date | Y |  |  |

**Constraints:**
- `unique_together_instructor_portal_coursecontentdraft` (unique_together): [session, content_type, version]

**Indexes:**
- `instructor__session_f8b88d_idx`: [session, processing_status]
- `instructor__content_c32597_idx`: [content_hash]
- `instructor__is_proc_36af61_idx`: [is_processed, created_date]
- `instructor__process_5df0ce_idx`: [processing_status, created_date]

---

### CourseCreationSession -> `instructor_portal_coursecreationsession`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `session_id` | UUIDField | session_id |  | UQ |  |
| `instructor` | ForeignKey | instructor |  | IDX | instructor_portal.instructorprofile (CASCADE) |
| `creation_method` | CharField | creation_method |  |  |  |
| `template` | ForeignKey | template | Y | IDX | instructor_portal.coursetemplate (SET_NULL) |
| `status` | CharField | status |  |  |  |
| `current_step` | PositiveIntegerField | current_step |  |  |  |
| `total_steps` | PositiveIntegerField | total_steps |  |  |  |
| `completion_percentage` | DecimalField | completion_percentage |  |  |  |
| `course_data` | JSONField | course_data |  |  |  |
| `metadata` | JSONField | metadata |  |  |  |
| `steps_completed` | JSONField | steps_completed |  |  |  |
| `validation_errors` | JSONField | validation_errors |  |  |  |
| `template_used` | CharField | template_used |  |  |  |
| `ai_prompts_used` | JSONField | ai_prompts_used |  |  |  |
| `expires_at` | DateTimeField | expires_at |  |  |  |
| `last_activity` | DateTimeField | last_activity |  |  |  |
| `published_course` | ForeignKey | published_course | Y | IDX | courses.course (SET_NULL) |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |

**Indexes:**
- `instructor__instruc_fffdb5_idx`: [instructor, status]
- `instructor__status_ff6efa_idx`: [status, expires_at]
- `instructor__session_1a1386_idx`: [session_id]
- `instructor__creatio_af8e34_idx`: [creation_method, status]

---

### CourseInstructor -> `instructor_portal_courseinstructor`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `course` | ForeignKey | course |  | IDX | courses.course (CASCADE) |
| `instructor` | ForeignKey | instructor |  | IDX | users.customuser (CASCADE) |
| `role` | CharField | role |  |  |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `is_lead` | BooleanField | is_lead |  |  |  |
| `can_edit_content` | BooleanField | can_edit_content |  |  |  |
| `can_manage_students` | BooleanField | can_manage_students |  |  |  |
| `can_view_analytics` | BooleanField | can_view_analytics |  |  |  |
| `revenue_share_percentage` | DecimalField | revenue_share_percentage |  |  |  |
| `joined_date` | DateTimeField | joined_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |

**Constraints:**
- `valid_revenue_share_percentage` (CheckConstraint): []
- `unique_together_instructor_portal_courseinstructor` (unique_together): [course, instructor]

**Indexes:**
- `instructor__course__80570e_idx`: [course, is_active]
- `instructor__instruc_6c0904_idx`: [instructor, is_active]
- `instructor__role_dc193b_idx`: [role, is_active]

---

### CourseTemplate -> `instructor_portal_coursetemplate`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `name` | CharField | name |  |  |  |
| `description` | TextField | description |  |  |  |
| `template_type` | CharField | template_type |  |  |  |
| `template_data` | JSONField | template_data |  |  |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `is_premium` | BooleanField | is_premium |  |  |  |
| `required_tier` | CharField | required_tier |  |  |  |
| `usage_count` | PositiveIntegerField | usage_count |  |  |  |
| `success_rate` | DecimalField | success_rate |  |  |  |
| `created_by` | ForeignKey | created_by | Y | IDX | users.customuser (SET_NULL) |
| `tags` | JSONField | tags |  |  |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |

**Indexes:**
- `instructor__templat_e5f5ef_idx`: [template_type, is_active]
- `instructor__is_acti_bb05a8_idx`: [is_active, required_tier]
- `instructor__usage_c_377784_idx`: [usage_count]

---

### DraftCourseContent -> `instructor_portal_draftcoursecontent`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `session` | ForeignKey | session |  | IDX | instructor_portal.coursecreationsession (CASCADE) |
| `content_type` | CharField | content_type |  |  |  |
| `content_id` | CharField | content_id |  |  |  |
| `version` | PositiveIntegerField | version |  |  |  |
| `content_data` | JSONField | content_data |  |  |  |
| `title` | CharField | title |  |  |  |
| `order` | PositiveIntegerField | order |  |  |  |
| `is_complete` | BooleanField | is_complete |  |  |  |
| `validation_errors` | JSONField | validation_errors |  |  |  |
| `auto_save_version` | PositiveIntegerField | auto_save_version |  |  |  |
| `last_saved` | DateTimeField | last_saved |  |  |  |
| `ai_generated` | BooleanField | ai_generated |  |  |  |
| `ai_prompt` | TextField | ai_prompt |  |  |  |

**Constraints:**
- `unique_together_instructor_portal_draftcoursecontent` (unique_together): [session, content_type, content_id, version]

**Indexes:**
- `instructor__session_60ca31_idx`: [session, content_type]
- `instructor__session_126edb_idx`: [session, order]
- `instructor__session_ab2b78_idx`: [session, content_type, version]
- `instructor__is_comp_5366a4_idx`: [is_complete, last_saved]

---

### InstructorAnalytics -> `instructor_portal_instructoranalytics`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | OneToOneField | instructor |  | UQ,IDX | instructor_portal.instructorprofile (CASCADE) |
| `total_students` | PositiveIntegerField | total_students |  |  |  |
| `total_courses` | PositiveIntegerField | total_courses |  |  |  |
| `average_rating` | DecimalField | average_rating |  |  |  |
| `total_reviews` | PositiveIntegerField | total_reviews |  |  |  |
| `total_revenue` | DecimalField | total_revenue |  |  |  |
| `completion_rate` | DecimalField | completion_rate |  |  |  |
| `student_satisfaction_rate` | DecimalField | student_satisfaction_rate |  |  |  |
| `monthly_revenue` | DecimalField | monthly_revenue |  |  |  |
| `last_updated` | DateTimeField | last_updated |  |  |  |
| `last_calculated` | DateTimeField | last_calculated | Y |  |  |

**Constraints:**
- `analytics_valid_rating` (CheckConstraint): []
- `analytics_positive_revenue` (CheckConstraint): []

**Indexes:**
- `instructor__instruc_b18673_idx`: [instructor, last_updated]
- `instructor__total_s_6586c2_idx`: [total_students, average_rating]

---

### InstructorAnalyticsHistory -> `instructor_portal_instructoranalyticshistory`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | ForeignKey | instructor |  | IDX | instructor_portal.instructorprofile (CASCADE) |
| `date` | DateTimeField | date |  |  |  |
| `total_students` | PositiveIntegerField | total_students |  |  |  |
| `total_courses` | PositiveIntegerField | total_courses |  |  |  |
| `average_rating` | DecimalField | average_rating |  |  |  |
| `total_revenue` | DecimalField | total_revenue |  |  |  |
| `completion_rate` | DecimalField | completion_rate |  |  |  |
| `data_type` | CharField | data_type |  |  |  |
| `additional_data` | JSONField | additional_data |  |  |  |

**Indexes:**
- `instructor__instruc_a853b6_idx`: [instructor, -date]
- `instructor__instruc_105e89_idx`: [instructor, data_type, -date]

---

### InstructorDashboard -> `instructor_portal_instructordashboard`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | OneToOneField | instructor |  | UQ,IDX | instructor_portal.instructorprofile (CASCADE) |
| `show_analytics` | BooleanField | show_analytics |  |  |  |
| `show_recent_students` | BooleanField | show_recent_students |  |  |  |
| `show_performance_metrics` | BooleanField | show_performance_metrics |  |  |  |
| `show_revenue_charts` | BooleanField | show_revenue_charts |  |  |  |
| `show_course_progress` | BooleanField | show_course_progress |  |  |  |
| `notify_new_enrollments` | BooleanField | notify_new_enrollments |  |  |  |
| `notify_new_reviews` | BooleanField | notify_new_reviews |  |  |  |
| `notify_course_completions` | BooleanField | notify_course_completions |  |  |  |
| `widget_order` | JSONField | widget_order |  |  |  |
| `custom_colors` | JSONField | custom_colors |  |  |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |

---

### InstructorNotification -> `instructor_portal_instructornotification`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | ForeignKey | instructor |  | IDX | instructor_portal.instructorprofile (CASCADE) |
| `notification_type` | CharField | notification_type |  |  |  |
| `priority` | CharField | priority |  |  |  |
| `title` | CharField | title |  |  |  |
| `message` | TextField | message |  |  |  |
| `action_url` | URLField | action_url |  |  |  |
| `action_text` | CharField | action_text |  |  |  |
| `metadata` | JSONField | metadata |  |  |  |
| `is_read` | BooleanField | is_read |  |  |  |
| `read_at` | DateTimeField | read_at | Y |  |  |
| `is_dismissed` | BooleanField | is_dismissed |  |  |  |
| `dismissed_at` | DateTimeField | dismissed_at | Y |  |  |
| `email_sent` | BooleanField | email_sent |  |  |  |
| `email_sent_at` | DateTimeField | email_sent_at | Y |  |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `expires_at` | DateTimeField | expires_at | Y |  |  |

**Indexes:**
- `instructor__instruc_7d1457_idx`: [instructor, is_read, -created_date]
- `instructor__instruc_bf496b_idx`: [instructor, notification_type]
- `instructor__priorit_1cb57a_idx`: [priority, created_date]
- `instructor__expires_657510_idx`: [expires_at]

---

### InstructorProfile -> `instructor_portal_instructorprofile`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `display_name` | CharField | display_name |  |  |  |
| `bio` | TextField | bio |  |  |  |
| `title` | CharField | title |  |  |  |
| `organization` | CharField | organization |  |  |  |
| `years_experience` | PositiveIntegerField | years_experience |  |  |  |
| `website` | URLField | website |  |  |  |
| `linkedin_profile` | URLField | linkedin_profile |  |  |  |
| `twitter_handle` | CharField | twitter_handle |  |  |  |
| `profile_image` | ImageField | profile_image | Y |  |  |
| `cover_image` | ImageField | cover_image | Y |  |  |
| `status` | CharField | status |  |  |  |
| `is_verified` | BooleanField | is_verified |  |  |  |
| `tier` | CharField | tier |  |  |  |
| `email_notifications` | BooleanField | email_notifications |  |  |  |
| `marketing_emails` | BooleanField | marketing_emails |  |  |  |
| `public_profile` | BooleanField | public_profile |  |  |  |
| `approved_by` | ForeignKey | approved_by | Y | IDX | users.customuser (SET_NULL) |
| `approval_date` | DateTimeField | approval_date | Y |  |  |
| `suspension_reason` | TextField | suspension_reason |  |  |  |
| `created_date` | DateTimeField | created_date |  |  |  |
| `updated_date` | DateTimeField | updated_date |  |  |  |
| `last_login` | DateTimeField | last_login | Y |  |  |
| `expertise_areas` | ManyToManyField | expertise_areas |  |  | courses.category (None) |

**Constraints:**
- `valid_experience_years` (CheckConstraint): []

**Indexes:**
- `instructor_status_verified_idx`: [status, is_verified]
- `instructor_tier_created_idx`: [tier, -created_date]
- `instructor_status_tier_idx`: [status, tier]

---

### InstructorProfile_expertise_areas -> `instructor_portal_instructorprofile_expertise_areas`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructorprofile` | ForeignKey | instructorprofile |  | IDX | instructor_portal.instructorprofile (CASCADE) |
| `category` | ForeignKey | category |  | IDX | courses.category (CASCADE) |

**Constraints:**
- `unique_together_instructor_portal_instructorprofile_expertise_areas` (unique_together): [instructorprofile, category]

---

### InstructorSession -> `instructor_portal_instructorsession`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `instructor` | ForeignKey | instructor |  | IDX | instructor_portal.instructorprofile (CASCADE) |
| `session_key` | CharField | session_key |  | UQ |  |
| `ip_address` | GenericIPAddressField | ip_address |  |  |  |
| `user_agent` | TextField | user_agent |  |  |  |
| `device_type` | CharField | device_type |  |  |  |
| `location` | CharField | location |  |  |  |
| `login_time` | DateTimeField | login_time |  |  |  |
| `last_activity` | DateTimeField | last_activity |  |  |  |
| `logout_time` | DateTimeField | logout_time | Y |  |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `is_suspicious` | BooleanField | is_suspicious |  |  |  |
| `security_notes` | TextField | security_notes |  |  |  |

**Indexes:**
- `instructor__instruc_a56576_idx`: [instructor, -login_time]
- `instructor__session_8512ff_idx`: [session_key]
- `instructor__ip_addr_6fb7f3_idx`: [ip_address, login_time]
- `instructor__is_acti_dbf638_idx`: [is_active, last_activity]

---

## App: social_django

### Association -> `social_auth_association`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `server_url` | CharField | server_url |  |  |  |
| `handle` | CharField | handle |  |  |  |
| `secret` | CharField | secret |  |  |  |
| `issued` | IntegerField | issued |  |  |  |
| `lifetime` | IntegerField | lifetime |  |  |  |
| `assoc_type` | CharField | assoc_type |  |  |  |

**Constraints:**
- `unique_together_social_auth_association` (unique_together): [server_url, handle]

---

### Code -> `social_auth_code`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `email` | EmailField | email |  |  |  |
| `code` | CharField | code |  | IDX |  |
| `verified` | BooleanField | verified |  |  |  |
| `timestamp` | DateTimeField | timestamp |  | IDX |  |

**Constraints:**
- `unique_together_social_auth_code` (unique_together): [email, code]

---

### Nonce -> `social_auth_nonce`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `server_url` | CharField | server_url |  |  |  |
| `timestamp` | IntegerField | timestamp |  |  |  |
| `salt` | CharField | salt |  |  |  |

**Constraints:**
- `unique_together_social_auth_nonce` (unique_together): [server_url, timestamp, salt]

---

### Partial -> `social_auth_partial`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `token` | CharField | token |  | IDX |  |
| `next_step` | PositiveSmallIntegerField | next_step |  |  |  |
| `backend` | CharField | backend |  |  |  |
| `data` | JSONField | data |  |  |  |
| `timestamp` | DateTimeField | timestamp |  | IDX |  |

---

### UserSocialAuth -> `social_auth_usersocialauth`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `provider` | CharField | provider |  |  |  |
| `uid` | CharField | uid |  | IDX |  |
| `extra_data` | JSONField | extra_data |  |  |  |
| `created` | DateTimeField | created |  |  |  |
| `modified` | DateTimeField | modified |  |  |  |

**Constraints:**
- `unique_together_social_auth_usersocialauth` (unique_together): [provider, uid]

---

## App: socialaccount

### SocialAccount -> `socialaccount_socialaccount`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `provider` | CharField | provider |  |  |  |
| `uid` | CharField | uid |  |  |  |
| `last_login` | DateTimeField | last_login |  |  |  |
| `date_joined` | DateTimeField | date_joined |  |  |  |
| `extra_data` | JSONField | extra_data |  |  |  |

**Constraints:**
- `unique_together_socialaccount_socialaccount` (unique_together): [provider, uid]

---

### SocialApp -> `socialaccount_socialapp`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `provider` | CharField | provider |  |  |  |
| `provider_id` | CharField | provider_id |  |  |  |
| `name` | CharField | name |  |  |  |
| `client_id` | CharField | client_id |  |  |  |
| `secret` | CharField | secret |  |  |  |
| `key` | CharField | key |  |  |  |
| `settings` | JSONField | settings |  |  |  |
| `sites` | ManyToManyField | sites |  |  | sites.site (None) |

---

### SocialApp_sites -> `socialaccount_socialapp_sites`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `socialapp` | ForeignKey | socialapp |  | IDX | socialaccount.socialapp (CASCADE) |
| `site` | ForeignKey | site |  | IDX | sites.site (CASCADE) |

**Constraints:**
- `unique_together_socialaccount_socialapp_sites` (unique_together): [socialapp, site]

---

### SocialToken -> `socialaccount_socialtoken`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | AutoField | id |  | PK,UQ |  |
| `app` | ForeignKey | app | Y | IDX | socialaccount.socialapp (SET_NULL) |
| `account` | ForeignKey | account |  | IDX | socialaccount.socialaccount (CASCADE) |
| `token` | TextField | token |  |  |  |
| `token_secret` | TextField | token_secret |  |  |  |
| `expires_at` | DateTimeField | expires_at | Y |  |  |

**Constraints:**
- `unique_together_socialaccount_socialtoken` (unique_together): [app, account]

---

## App: token_blacklist

### BlacklistedToken -> `token_blacklist_blacklistedtoken`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `token` | OneToOneField | token |  | UQ,IDX | token_blacklist.outstandingtoken (CASCADE) |
| `blacklisted_at` | DateTimeField | blacklisted_at |  |  |  |

---

### OutstandingToken -> `token_blacklist_outstandingtoken`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user | Y | IDX | users.customuser (SET_NULL) |
| `jti` | CharField | jti |  | UQ |  |
| `token` | TextField | token |  |  |  |
| `created_at` | DateTimeField | created_at | Y |  |  |
| `expires_at` | DateTimeField | expires_at |  |  |  |

---

## App: users

### CustomUser -> `users_customuser`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `password` | CharField | password |  |  |  |
| `is_superuser` | BooleanField | is_superuser |  |  |  |
| `first_name` | CharField | first_name |  |  |  |
| `last_name` | CharField | last_name |  |  |  |
| `is_staff` | BooleanField | is_staff |  |  |  |
| `email` | EmailField | email |  | UQ |  |
| `username` | CharField | username |  | UQ |  |
| `role` | CharField | role |  |  |  |
| `is_email_verified` | BooleanField | is_email_verified |  |  |  |
| `date_joined` | DateTimeField | date_joined |  |  |  |
| `last_login` | DateTimeField | last_login | Y |  |  |
| `failed_login_attempts` | PositiveIntegerField | failed_login_attempts |  |  |  |
| `temporary_ban_until` | DateTimeField | temporary_ban_until | Y |  |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `groups` | ManyToManyField | groups |  |  | auth.group (None) |
| `user_permissions` | ManyToManyField | user_permissions |  |  | auth.permission (None) |

---

### CustomUser_groups -> `users_customuser_groups`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `customuser` | ForeignKey | customuser |  | IDX | users.customuser (CASCADE) |
| `group` | ForeignKey | group |  | IDX | auth.group (CASCADE) |

**Constraints:**
- `unique_together_users_customuser_groups` (unique_together): [customuser, group]

---

### CustomUser_user_permissions -> `users_customuser_user_permissions`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `customuser` | ForeignKey | customuser |  | IDX | users.customuser (CASCADE) |
| `permission` | ForeignKey | permission |  | IDX | auth.permission (CASCADE) |

**Constraints:**
- `unique_together_users_customuser_user_permissions` (unique_together): [customuser, permission]

---

### EmailVerification -> `users_emailverification`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `token` | UUIDField | token |  | UQ |  |
| `created_at` | DateTimeField | created_at |  |  |  |
| `expires_at` | DateTimeField | expires_at |  |  |  |
| `verified_at` | DateTimeField | verified_at | Y |  |  |
| `is_used` | BooleanField | is_used |  |  |  |

**Indexes:**
- `users_email_token_c80ef6_idx`: [token]
- `users_email_user_id_8f79bf_idx`: [user, is_used]

---

### LoginLog -> `users_loginlog`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `timestamp` | DateTimeField | timestamp |  |  |  |
| `ip_address` | GenericIPAddressField | ip_address |  |  |  |
| `user_agent` | TextField | user_agent |  |  |  |
| `successful` | BooleanField | successful |  |  |  |

**Indexes:**
- `users_login_user_id_312dc6_idx`: [user, timestamp]
- `users_login_ip_addr_651077_idx`: [ip_address, timestamp]

---

### PasswordReset -> `users_passwordreset`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `token` | UUIDField | token |  | UQ |  |
| `created_at` | DateTimeField | created_at |  |  |  |
| `expires_at` | DateTimeField | expires_at |  |  |  |
| `used_at` | DateTimeField | used_at | Y |  |  |
| `is_used` | BooleanField | is_used |  |  |  |
| `ip_address` | GenericIPAddressField | ip_address | Y |  |  |

**Indexes:**
- `users_passw_token_2def9c_idx`: [token]
- `users_passw_user_id_61b761_idx`: [user, is_used]

---

### Profile -> `users_profile`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `profile_picture` | ImageField | profile_picture | Y |  |  |
| `bio` | TextField | bio |  |  |  |
| `date_of_birth` | DateField | date_of_birth | Y |  |  |
| `phone_number` | CharField | phone_number |  |  |  |
| `address` | TextField | address |  |  |  |
| `city` | CharField | city |  |  |  |
| `state` | CharField | state |  |  |  |
| `country` | CharField | country |  |  |  |
| `postal_code` | CharField | postal_code |  |  |  |
| `website` | URLField | website |  |  |  |
| `linkedin` | URLField | linkedin |  |  |  |
| `twitter` | CharField | twitter |  |  |  |
| `github` | CharField | github |  |  |  |
| `expertise` | CharField | expertise |  |  |  |
| `teaching_experience` | PositiveIntegerField | teaching_experience |  |  |  |
| `educational_background` | TextField | educational_background |  |  |  |
| `interests` | TextField | interests |  |  |  |
| `receive_email_notifications` | BooleanField | receive_email_notifications |  |  |  |
| `receive_marketing_emails` | BooleanField | receive_marketing_emails |  |  |  |
| `created_at` | DateTimeField | created_at |  |  |  |
| `updated_at` | DateTimeField | updated_at |  |  |  |

---

### Subscription -> `users_subscription`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | OneToOneField | user |  | UQ,IDX | users.customuser (CASCADE) |
| `tier` | CharField | tier |  |  |  |
| `status` | CharField | status |  |  |  |
| `start_date` | DateTimeField | start_date |  |  |  |
| `end_date` | DateTimeField | end_date | Y |  |  |
| `is_auto_renew` | BooleanField | is_auto_renew |  |  |  |
| `last_payment_date` | DateTimeField | last_payment_date | Y |  |  |
| `payment_method` | CharField | payment_method | Y |  |  |
| `payment_id` | CharField | payment_id | Y |  |  |

---

### UserSession -> `users_usersession`
| Field | Type | Column | Null | Key | Related |
|-------|------|--------|------|-----|---------|
| `id` | BigAutoField | id |  | PK,UQ |  |
| `user` | ForeignKey | user |  | IDX | users.customuser (CASCADE) |
| `session_key` | CharField | session_key |  |  |  |
| `ip_address` | GenericIPAddressField | ip_address |  |  |  |
| `user_agent` | TextField | user_agent |  |  |  |
| `created_at` | DateTimeField | created_at |  |  |  |
| `expires_at` | DateTimeField | expires_at |  |  |  |
| `last_activity` | DateTimeField | last_activity |  |  |  |
| `is_active` | BooleanField | is_active |  |  |  |
| `device_type` | CharField | device_type |  |  |  |
| `location` | CharField | location |  |  |  |
| `login_method` | CharField | login_method | Y |  |  |

**Indexes:**
- `users_users_user_id_3887fe_idx`: [user, is_active]
- `users_users_session_70af4d_idx`: [session_key]

---
