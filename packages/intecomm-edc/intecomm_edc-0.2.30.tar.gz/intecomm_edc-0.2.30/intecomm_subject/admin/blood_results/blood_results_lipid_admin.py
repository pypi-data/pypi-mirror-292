from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_lab_results.admin import BloodResultsModelAdminMixin
from edc_lab_results.fieldsets import BloodResultFieldset

from ...admin_site import intecomm_subject_admin
from ...forms import BloodResultsLipidForm
from ...models import BloodResultsLipid
from ..modeladmin_mixins import CrfModelAdmin


@admin.register(BloodResultsLipid, site=intecomm_subject_admin)
class BloodResultsLipidAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
    form = BloodResultsLipidForm
    fieldsets = BloodResultFieldset(
        BloodResultsLipid.lab_panel,
        model_cls=BloodResultsLipid,
        extra_fieldsets=[
            (-1, action_fieldset_tuple),
        ],
    ).fieldsets
