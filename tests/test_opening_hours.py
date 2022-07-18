import json

from locations.hours import OpeningHours


def test_two_ranges():
    o = OpeningHours()
    o.add_range("Mo", "07:00", "17:00")
    o.add_range("Tu", "07:00", "17:00")
    o.add_range("We", "07:00", "17:00")

    o.add_range("Fr", "08:00", "17:00")
    o.add_range("Sa", "08:00", "17:00")

    assert o.as_opening_hours() == "Mo-We 07:00-17:00; Fr-Sa 08:00-17:00"


def test_mixed_ranges():
    o = OpeningHours()
    o.add_range("Mo", "08:00", "17:00")
    o.add_range("Tu", "08:00", "17:00")
    o.add_range("We", "09:00", "18:00")
    o.add_range("Th", "09:00", "18:00")
    o.add_range("Fr", "07:00", "17:00")
    o.add_range("Su", "09:00", "17:00")

    assert (
        o.as_opening_hours()
        == "Mo-Tu 08:00-17:00; We-Th 09:00-18:00; Fr 07:00-17:00; Su 09:00-17:00"
    )


def test_closed_sunday():
    o = OpeningHours()
    o.add_range("Mo", "07:00", "17:00")
    o.add_range("Tu", "07:00", "17:00")
    o.add_range("We", "07:00", "17:00")
    o.add_range("Th", "07:00", "17:00")
    o.add_range("Fr", "07:00", "17:00")
    o.add_range("Sa", "07:00", "17:00")

    assert o.as_opening_hours() == "Mo-Sa 07:00-17:00"


def test_closed_tuesday():
    o = OpeningHours()
    o.add_range("Mo", "07:00", "17:00")
    o.add_range("We", "07:00", "17:00")
    o.add_range("Th", "07:00", "17:00")
    o.add_range("Fr", "07:00", "17:00")
    o.add_range("Sa", "07:00", "17:00")
    o.add_range("Su", "07:00", "17:00")

    assert o.as_opening_hours() == "Mo 07:00-17:00; We-Su 07:00-17:00"


def test_twentyfour_seven():
    o = OpeningHours()
    o.add_range("Mo", "0:00", "23:59")
    o.add_range("Tu", "0:00", "23:59")
    o.add_range("We", "0:00", "23:59")
    o.add_range("Th", "0:00", "23:59")
    o.add_range("Fr", "0:00", "23:59")
    o.add_range("Sa", "0:00", "23:59")
    o.add_range("Su", "0:00", "23:59")

    assert o.as_opening_hours() == "24/7"


def test_no_opening_hours():
    o = OpeningHours()
    assert o.as_opening_hours() == ""


def test_multiple_times():
    o = OpeningHours()
    o.add_range("Mo", "08:00", "12:00")
    o.add_range("Mo", "13:00", "17:30")
    assert o.as_opening_hours() == "Mo 08:00-12:00,13:00-17:30"


def test_ld_parse():
    o = OpeningHours()
    o.from_linked_data(
        json.loads(
            """
            {
                "@context": "https://schema.org",
                "@type": "Store",
                "name": "Middle of Nowhere Foods",
                "openingHoursSpecification":
                [
                    {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": [
                            "http://schema.org/Monday",
                            "https://schema.org/Tuesday",
                            "Wednesday",
                            "http://schema.org/Thursday",
                            "http://schema.org/Friday"
                        ],
                        "opens": "09:00",
                        "closes": "11:00"
                    },
                    {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": "http://schema.org/Saturday",
                        "opens": "12:00",
                        "closes": "14:00"
                    }
                ]
            }
            """
        )
    )
    assert o.as_opening_hours() == "Mo-Fr 09:00-11:00; Sa 12:00-14:00"


def test_ld_parse_openingHours():
    o = OpeningHours()
    o.from_linked_data(
        json.loads(
            """
            {
                "@context": "https://schema.org",
                "@type": "Pharmacy",
                "name": "Philippa's Pharmacy",
                "description": "A superb collection of fine pharmaceuticals for your beauty and healthcare convenience, a department of Delia's Drugstore.",
                "openingHours": "Mo,Tu,We,Th 09:00-12:00",
                "telephone": "+18005551234"
            }
            """
        )
    )
    assert o.as_opening_hours() == "Mo-Th 09:00-12:00"


def test_ld_parse_openingHours_array():
    o = OpeningHours()
    o.from_linked_data(
        json.loads(
            """
            {
                "@context": "https://schema.org",
                "@type": ["TouristAttraction", "AmusementPark"],
                "name": "Disneyland Paris",
                "description": "It's an amusement park in Marne-la-Vallée, near Paris, in France and is the most visited theme park in all of France and Europe.",
                "openingHours":["Mo-Fr 10:00-19:00", "Sa 10:00-22:00", "Su 10:00-21:00"],
                "isAccessibleForFree": false,
                "currenciesAccepted": "EUR",
                "paymentAccepted":"Cash, Credit Card",
                "url":"http://www.disneylandparis.it/"
            }
            """
        )
    )
    assert o.as_opening_hours() == "Mo-Fr 10:00-19:00; Sa 10:00-22:00; Su 10:00-21:00"


def test_ld_parse_time_format():
    o = OpeningHours()
    o.from_linked_data(
        json.loads(
            """
            {
                "@context": "https://schema.org",
                "@type": "Store",
                "name": "Middle of Nowhere Foods",
                "openingHoursSpecification":
                [
                    {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": "http://schema.org/Saturday",
                        "opens": "12:00:00",
                        "closes": "14:00:00"
                    }
                ]
            }
            """
        ),
        "%H:%M:%S",
    )
    assert o.as_opening_hours() == "Sa 12:00-14:00"
