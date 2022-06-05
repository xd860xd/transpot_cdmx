"""Celery auth users tasks."""
import logging
import time

from django.conf import settings
from geopy.geocoders import Nominatim

from api.models import RequestUnitsMetrobusStatus, UnitsMetrobusStatus
from api.utils.exceptions import BadGateWay
from api.utils.utils import do_request
from config import celery_app

logger = logging.getLogger(__name__)


@celery_app.app.task(name="update_database", bind=True, max_retries=2)
def update_database(self, token: str):
    request_unit = RequestUnitsMetrobusStatus.objects.filter(token=token).first()
    try:
        get_results(token)
    except Exception as ex:
        request_unit.request_error = True
        logger.exception(ex)
    finally:
        request_unit.is_completed = True
        request_unit.save()


def get_results(token):
    records = get_records(records=[])

    records = add_ubications(records, token)


def get_records(records, url=None):
    site_api = "https://datos.cdmx.gob.mx"
    if not url:
        url = (
            site_api
            + "/api/3/action/datastore_search?resource_id=ad360a0e-b42f-482c-af12-1fd72140032e"
        )
    else:
        url = site_api + url

    data = do_request(url)

    new_records = data["result"]["records"]
    next_url = data["result"]["_links"]["next"]
    if new_records:
        records += new_records
        get_records(records, next_url)

    return records


def get_units_in_district(records, district):
    units_in_district = []
    for record in records:
        record_district = record.get("district", None)
        if record_district and record_district.strip() == district.strip():
            units_in_district.append(record)

    return units_in_district


def add_ubications(records, token):

    for unit in records:
        unit_instance = UnitsMetrobusStatus.objects.filter(
            unit_id=unit["id"], date_updated=unit["date_updated"]
        )

        if not unit_instance.exists():
            try:
                add_ubication(unit, token)
                time.sleep(1)
            except Exception as ex:
                print(ex)

        else:
            pre_instance_unit = {
                "unit_id": unit["id"],
                "position_latitude": unit["position_latitude"],
                "position_longitude": unit["position_longitude"],
                "date_updated": unit["date_updated"],
                "token": token,
                "address": unit_instance.first().address,
                "district": unit_instance.first().district,
            }
            UnitsMetrobusStatus.objects.create(**pre_instance_unit)
    return records


def add_ubication(unit, token):

    pre_instance_unit = {
        "unit_id": unit["id"],
        "position_latitude": unit["position_latitude"],
        "position_longitude": unit["position_longitude"],
        "date_updated": unit["date_updated"],
        "token": token,
        "geographic_point": unit["geographic_point"],
    }

    update_ubication(pre_instance_unit)
    if pre_instance_unit["district"] and pre_instance_unit["address"]:
        UnitsMetrobusStatus.objects.create(**pre_instance_unit)


def update_ubication(unit):
    address = from_cords_to_direction(unit["geographic_point"])

    if not address:
        return None

    aux_ubication = map(lambda item: item[1:], address.split(","))

    unit["district"], unit["address"] = None, None

    for posible_disctrict in aux_ubication:
        if posible_disctrict in settings.DISTRICTS:
            unit["district"] = posible_disctrict
            unit["address"] = address

    unit.pop("geographic_point")

    if not unit["district"] or not unit["address"]:
        msg = (
            f"No se reconocio la alcaldia en : {address} \n \
            Se intento con :",
            aux_ubication,
        )
        print(msg)


def from_cords_to_direction(cords):

    geolocator = Nominatim(user_agent="transpot_cdmx")
    try:
        address = geolocator.reverse(cords).address
    except Exception:
        raise BadGateWay()
    return address
