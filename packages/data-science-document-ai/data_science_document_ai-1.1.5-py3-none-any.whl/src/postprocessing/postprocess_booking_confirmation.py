"""Postprocessing of the result of Booking  Confirmation model to match the data schema"""


transport_leg_features = [
    'eta',
    'etd',
    'portOfLoading',
    'vesselName',
    'voyage',
    'imoNumber',
    'portOfDischarge'
]


def postprocess_booking_confirmation(booking_confirmation):
    """
    This postprocessing aggregates transport legs into list and assign ids.
    Model returns transport legs components as 'eta1', 'etd2', 'vesselName3'...
    They are copied into 'transportLegs'[id]"{'eta', 'etd', 'vesselName'...}
    Original labels are deleted.

    Args:
        booking_confirmation: aggregated_data with formatted values from processor response

    Returns:
        booking_confirmation with "transportLegs" list and without original transport legs components

    """
    legs = []
    delete_keys = set()
    for entity_type in booking_confirmation.keys():
        # support for old bookingConfirmation schema
        if entity_type in transport_leg_features:
            index = 1
            while index > len(legs):
                legs.append({"id": len(legs)})
            legs[index - 1][entity_type] = booking_confirmation[entity_type]
            delete_keys.add(entity_type)
        else:

            # e.g. "eta1" = type_without_index:"eta" + index: 1, we won't have legs > 10
            type_without_index = entity_type[:-1]
            if type_without_index in transport_leg_features:
                index = int(entity_type[-1])

                # it is possible to encounter leg3 value before leg1 or leg2
                while index > len(legs):
                    legs.append({"id": len(legs)})
                legs[index-1][type_without_index] = booking_confirmation[entity_type]
                delete_keys.add(entity_type)
    for delete_key in delete_keys:
        del booking_confirmation[delete_key]

    # this function only called for BookingConfirmations, empty list is preferred to no value
    booking_confirmation["transportLegs"] = legs

    return booking_confirmation
