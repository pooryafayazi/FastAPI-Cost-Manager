# mkdir -p i18n/translations

# 1) استخراج همه‌ی رشته‌های _("...") به قالب POT
# pybabel extract -o i18n/translations/messages.pot .

# 2) ایجاد فایل‌های PO برای زبان‌ها
# pybabel init   -i i18n/translations/messages.pot -d i18n/translations -l en
# pybabel init   -i i18n/translations/messages.pot -d i18n/translations -l fa

# 3) ترجمه‌ی متن‌ها را داخل فایل‌های .po وارد کن (فیلد msgstr)
# 4) کامپایل به .mo برای اجرا
# pybabel compile -d i18n/translations



# هر بار رشته‌ی جدید اضافه کردی:

# pybabel extract -o i18n/translations/messages.pot .
# pybabel update  -i i18n/translations/messages.pot -d i18n/translations
# فایل‌های .po را ترجمه کن (fa)
# pybabel compile -d i18n/translations



