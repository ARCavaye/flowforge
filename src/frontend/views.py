from django.core.exceptions import PermissionDenied
from core.models import TeamMembership, Plan
from django.views.generic import DetailView



class TeamOwnershipMixin:
    """Mixin for CBV to restrict access to objects owned by a Team.

    Usage:
      - Inherit this mixin in generic views and call `self.check_team_permission(request, obj, 'read'|'write'|'manage')`
      - Override get_queryset to call super().get_queryset(request) and then filter with this mixin's helper if needed.
    """

    def check_team_permission(self, request, obj, required="read"):
        if request.user.is_superuser:
            return True

        owner_team = getattr(obj, "owner_team", None)
        if not owner_team:
            # deny access to objects without an owner team by default
            raise PermissionDenied("No owning team assigned")

        try:
            membership = TeamMembership.objects.get(team=owner_team, user=request.user)
        except TeamMembership.DoesNotExist:
            raise PermissionDenied("You are not a member of the owning team")

        if required == "read":
            if membership.can_read():
                return True
        elif required == "write":
            if membership.can_write():
                return True
        elif required == "manage":
            if membership.can_manage():
                return True

        raise PermissionDenied("Insufficient team permissions")

    def get_team_filtered_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        team_ids = request.user.team_memberships.values_list("team", flat=True)
        return qs.filter(owner_team__in=team_ids).distinct()

class PlanDetailView(TeamOwnershipMixin,DetailView):
    model = Plan
    template_name = "frontend/plan_detail.html"
