from rest_framework import routers

from api.views import DistrictsViewSet, UnitsMetrobusViewSet

router = routers.SimpleRouter()


router.register("units-metrobus", UnitsMetrobusViewSet, basename="units-metrobus")
router.register("districts", DistrictsViewSet, basename="districts")

urlpatterns = router.urls
