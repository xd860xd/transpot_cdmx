from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializer import (
    DistrictUnitsMetrobusSerializer,
    TokenDistrictUnitsMetrobusSerializer,
    UnitMetrobusSerializer,
    UnitUbicationMetrobusSerializer,
)

# Create your views here.


class UnitsMetrobusViewSet(GenericViewSet):

    queryset = []
    site_api_cdmx = "https://datos.cdmx.gob.mx/api/3/action/datastore_search"
    api_cdmx = site_api_cdmx + "?resource_id=ad360a0e-b42f-482c-af12-1fd72140032e"

    """This view shows all the units its a intermediate url to the consumed api"""

    def list(self, *args, **kwargs):
        params = self.request.query_params
        limit_query = "11" if "limit" not in params else params["limit"]
        query_offset = "" if "offset" not in params else "&offset=" + params["offset"]

        url = self.api_cdmx + "&limit=" + limit_query + query_offset
        serializer = UnitMetrobusSerializer({"url": url})
        return Response(serializer.data["results"])

    """This view show one unit and its ubication"""

    def retrieve(self, request, *args, **kwargs):
        id_unit = kwargs["pk"]
        serializer = UnitUbicationMetrobusSerializer({"id": id_unit})
        return Response(serializer.data["unit"])


class DistrictsViewSet(GenericViewSet):

    queryset = []

    """This is the view to return the dictricts (alcaldias)"""

    def list(self, *args, **kwargs):
        return Response(settings.DISTRICTS)

    """
    This view send a task to update the the db
    returns a couples of urls witch have the respectives
    queries, to get the units for a district.
    """

    def retrieve(self, request, *args, **kwargs):

        district = kwargs["pk"]

        serializer = DistrictUnitsMetrobusSerializer(data={"district": district})

        serializer.is_valid(raise_exception=True)

        data = serializer.save()

        return Response(data)

    """
    This view shows the units for a district (alcaldia)
    and the state of the task wich is getting the units for the current district
    """

    @action(
        methods=[
            "GET",
        ],
        detail=True,
        url_name="units",
        url_path="units",
    )
    def get_units(self, request, *args, **kwargs):
        district = kwargs["pk"]
        token = request.query_params.get("token", "")
        data = {"token": token, "district": district}
        serilaizer = TokenDistrictUnitsMetrobusSerializer(data=data)
        serilaizer.is_valid(raise_exception=True)
        data = serilaizer.save()
        return Response(data)
