from django import forms

from finx_tracker.portfolios.models import Grouping, Trade


class GroupingNameChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ["groupings"]

    def __init__(self, *args, **kwargs):
        ids = kwargs.pop("grouping_id_choices")
        active_groups = (
            Grouping.objects.filter(id__in=ids)
            .filter(status=Grouping.GroupingStatuses.ACTIVE)
            .order_by("name")
        )

        super(TradeForm, self).__init__(*args, **kwargs)

        self.fields["groupings"] = GroupingNameChoiceField(
            queryset=active_groups,
            required=False,
            label="",
        )
