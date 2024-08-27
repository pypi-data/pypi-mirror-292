from homeassistant.core import HomeAssistant
import logging


def handle_lux_feedback(hass: HomeAssistant, info: dict):
    """
    Handle the feedback from a Lux sensor.
    """
    device_id = info["device_id"]
    lux = int(info["additional_bytes"][6])

    event_data = {
        "device_id": device_id,
        "lux": lux,
    }
    try:
        hass.bus.async_fire(str(info["device_id"]), event_data)
        logging.error(
            f"control response event fired for {info['device_id']}, additional bytes: {info['additional_bytes']}"
        )
    except Exception as e:
        logging.error(f"error in firing even for feedbackt: {e}")
