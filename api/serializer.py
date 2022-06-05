import jwt
from django.conf import settings
from rest_framework import exceptions, serializers

from api.models import RequestUnitsMetrobusStatus, UnitsMetrobusStatus
from api.tasks.district import update_database, update_ubication
from api.utils.utils import do_request, get_district_info_token


class UnitsMetrobusStatusModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitsMetrobusStatus
        fields = (
            "id",
            "unit_id",
            "position_latitude",
            "position_longitude",
            "date_updated",
            "load_at",
            "address",
            "district",
        )


class UnitMetrobusSerializer(serializers.Serializer):

    url = serializers.CharField()

    results = serializers.SerializerMethodField(
        method_name="get_results", read_only=True
    )

    data_list_not_required = [
        "include_total",
        "limit",
        "records_format",
        "resource_id",
        "total_estimation_threshold",
        "total_was_estimated",
        "fields",
    ]

    def get_results(self, data):
        result = do_request(data["url"])

        result.pop("help")
        result.pop("success")

        for attr in self.data_list_not_required:
            result["result"].pop(attr)

        self.manage_pagination(result)

        return result

    # Manage pagination
    @staticmethod
    def manage_pagination(result):
        query_start = "&".join(result["result"]["_links"]["start"].split("&")[1:])
        result["result"]["_links"]["start"] = (
            settings.SITE_BACKEND + "/api/units-metrobus/?" + query_start
        )

        if result["result"]["_links"].get("next", None):
            query_next = "&".join(result["result"]["_links"]["next"].split("&")[1:])
            result["result"]["_links"]["next"] = (
                settings.SITE_BACKEND + "/api/units-metrobus/?" + query_next
            )

        if result["result"]["_links"].get("prev", None):
            query_prev = "&".join(result["result"]["_links"]["prev"].split("&")[1:])
            result["result"]["_links"]["prev"] = (
                settings.SITE_BACKEND + "/api/units-metrobus/?" + query_prev
            )


class UnitUbicationMetrobusSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    unit = serializers.SerializerMethodField()

    site_api_cdmx = "https://datos.cdmx.gob.mx/api/3/action/datastore_search"
    api_cdmx = site_api_cdmx + "?resource_id=ad360a0e-b42f-482c-af12-1fd72140032e"

    data_retrieve_not_required = [
        "date_updated",
        "vehicle_id",
        "vehicle_label",
        "vehicle_current_status",
        "position_latitude",
        "position_longitude",
        "position_speed",
        "position_odometer",
        "trip_schedule_relationship",
        "rank",
        "_id",
    ]

    def get_unit(self, data):
        url = self.api_cdmx + "&q=" + data["id"]
        result = do_request(url)

        unit = self.find_unit(result=result, id_unit=data["id"])

        update_ubication(unit)

        for attr in self.data_retrieve_not_required:
            unit.pop(attr)

        return unit

    """This method searh the unit among the data fetched, and returns the unit"""

    @staticmethod
    def find_unit(result, id_unit):
        units = result["result"]["records"]
        unit = list(filter(lambda u: u["id"] == int(id_unit), units))
        if not unit:
            raise exceptions.NotFound()

        unit = unit[0]

        return unit


class DistrictUnitsMetrobusSerializer(serializers.Serializer):

    district = serializers.CharField()

    def validate(self, attrs):
        if attrs["district"] not in settings.DISTRICTS:
            raise exceptions.NotFound()
        return attrs

    """
    This method sends the task to update the db and generates
    an url to acces to the data of units in the district selected.
    """

    def create(self, validated_data):
        # Create the token
        token = get_district_info_token(validated_data["district"])

        RequestUnitsMetrobusStatus.objects.create(token=token)

        urls = self.get_urls(validated_data["district"], token)

        # Send the task
        update_database.delay(token)

        return urls

    @staticmethod
    def get_urls(district, token):
        units_district = UnitsMetrobusStatus.objects.filter(district=district)

        unit_last_token = units_district.order_by("id").last()

        district_url = district.replace(" ", "%20")
        default_url = (
            f"{settings.SITE_BACKEND}/api/districts/{district_url}/units/?token="
        )

        msg = "visit the url in a couple of seconds, the query is in progress, \
            there you'll find the requested data"
        urls = {
            "url": default_url + token,
            "msg": msg,
        }
        if unit_last_token:
            current_token_loaded = unit_last_token.token

            unit_previous_token = (
                units_district.exclude(token=current_token_loaded).order_by("id").last()
            )

            previous_token = unit_previous_token.token if unit_previous_token else ""

            previous_urls = {
                "previous_url": default_url + current_token_loaded,
                "previous_previus_url": default_url + previous_token,
            }
            urls.update(previous_urls)
            urls["msg"] += ", here you get a pair of previos queries"

        return urls


class TokenDistrictUnitsMetrobusSerializer(serializers.Serializer):

    token = serializers.CharField()
    district = serializers.CharField()

    def validate(self, attrs):

        if attrs["district"] not in settings.DISTRICTS:
            raise exceptions.NotFound()
        if self.context["payload"]["district"] != attrs["district"]:
            raise serializers.ValidationError({"alcalidia": "Token inválido"})

        return attrs

    def validate_token(self, data):
        """Verify token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            UnitsMetrobusStatus.objects.filter(token=data).delete()
            raise serializers.ValidationError("Link de expirado")
        except jwt.exceptions.PyJWTError:
            raise serializers.ValidationError("Token inválido")

        self.context["payload"] = payload
        return data

    def create(self, validated_data):
        token = validated_data["token"]
        district = self.context["payload"]["district"]
        instances = UnitsMetrobusStatus.objects.filter(token=token, district=district)
        unit_serializer = UnitsMetrobusStatusModelSerializer(instances, many=True)

        request_unit = RequestUnitsMetrobusStatus.objects.filter(token=token).first()
        query_completed = request_unit.is_completed
        succes = not request_unit.request_error
        data = {
            "units": unit_serializer.data,
            "query_completed": query_completed,
            "query_succes": succes,
        }
        return data
