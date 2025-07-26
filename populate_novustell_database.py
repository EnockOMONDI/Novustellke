#!/usr/bin/env python
"""
Comprehensive database population script for Novustell Travel
Creates realistic test data for destinations, cities, places, packages, accommodations, and travel modes
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from adminside.models import (
    Destination, Package, Itinerary, ItineraryDay,
    Accommodation, TravelMode
)

def create_destinations():
    """Create 6 diverse country destinations"""
    destinations_data = [
        {
            'name': 'Kenya',
            'description': 'Experience the magic of East Africa with world-renowned safaris, pristine beaches, and rich cultural heritage. From the Great Migration in Maasai Mara to the white sandy beaches of Mombasa.',
            'slug': 'kenya',
        },
        {
            'name': 'Tanzania',
            'description': 'Discover the crown jewel of Africa with Mount Kilimanjaro, Serengeti National Park, and the exotic spice island of Zanzibar. Tanzania offers unparalleled wildlife experiences.',
            'slug': 'tanzania',
        },
        {
            'name': 'South Africa',
            'description': 'Explore the Rainbow Nation with its diverse landscapes, world-class wine regions, vibrant cities, and incredible wildlife. From Cape Town to Kruger National Park.',
            'slug': 'south-africa',
        },
        {
            'name': 'Rwanda',
            'description': 'The Land of a Thousand Hills offers unique mountain gorilla encounters, stunning landscapes, and a remarkable story of resilience and conservation.',
            'slug': 'rwanda',
        },
        {
            'name': 'Dubai',
            'description': 'Experience luxury and innovation in this modern desert oasis. From towering skyscrapers to traditional souks, Dubai offers a perfect blend of tradition and modernity.',
            'slug': 'dubai',
        },
        {
            'name': 'Malaysia',
            'description': 'Discover Southeast Asian charm with tropical rainforests, pristine islands, vibrant cities, and a rich multicultural heritage spanning Malay, Chinese, and Indian influences.',
            'slug': 'malaysia',
        }
    ]

    created_destinations = []
    for dest_data in destinations_data:
        destination, created = Destination.objects.get_or_create(
            slug=dest_data['slug'],
            defaults={
                'name': dest_data['name'],
                'description': dest_data['description'],
                'destination_type': Destination.COUNTRY,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created destination: {destination.name}")
        else:
            print(f"📍 Destination exists: {destination.name}")
        created_destinations.append(destination)

    return created_destinations

def create_cities(destinations):
    """Create 3 cities per destination using hierarchical model"""
    cities_data = {
        'Kenya': [
            {'name': 'Nairobi', 'description': 'The vibrant capital city, gateway to safari adventures'},
            {'name': 'Mombasa', 'description': 'Coastal paradise with pristine beaches and Swahili culture'},
            {'name': 'Maasai Mara', 'description': 'World-famous wildlife reserve, home to the Great Migration'}
        ],
        'Tanzania': [
            {'name': 'Arusha', 'description': 'Safari capital and gateway to northern Tanzania parks'},
            {'name': 'Zanzibar', 'description': 'Exotic spice island with pristine beaches and Stone Town'},
            {'name': 'Serengeti', 'description': 'Endless plains hosting the greatest wildlife spectacle on Earth'}
        ],
        'South Africa': [
            {'name': 'Cape Town', 'description': 'Mother City with Table Mountain and world-class wine regions'},
            {'name': 'Johannesburg', 'description': 'Economic hub with rich history and vibrant culture'},
            {'name': 'Kruger', 'description': 'Premier wildlife destination with Big Five game viewing'}
        ],
        'Rwanda': [
            {'name': 'Kigali', 'description': 'Clean, modern capital city with rich cultural heritage'},
            {'name': 'Volcanoes National Park', 'description': 'Home to endangered mountain gorillas'},
            {'name': 'Lake Kivu', 'description': 'Scenic lake region perfect for relaxation and water activities'}
        ],
        'Dubai': [
            {'name': 'Dubai City', 'description': 'Modern metropolis with iconic skyscrapers and luxury shopping'},
            {'name': 'Dubai Marina', 'description': 'Waterfront district with stunning architecture and dining'},
            {'name': 'Old Dubai', 'description': 'Traditional quarter with souks, museums, and cultural heritage'}
        ],
        'Malaysia': [
            {'name': 'Kuala Lumpur', 'description': 'Dynamic capital with Petronas Towers and diverse cuisine'},
            {'name': 'Langkawi', 'description': 'Tropical island paradise with pristine beaches and rainforests'},
            {'name': 'Penang', 'description': 'UNESCO World Heritage site with rich cultural heritage and street food'}
        ]
    }
    
    created_cities = []
    for destination in destinations:
        if destination.name in cities_data:
            for city_data in cities_data[destination.name]:
                city_slug = f"{destination.slug}-{city_data['name'].lower().replace(' ', '-')}"
                city, created = Destination.objects.get_or_create(
                    slug=city_slug,
                    defaults={
                        'name': city_data['name'],
                        'description': city_data['description'],
                        'destination_type': Destination.CITY,
                        'parent': destination,
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Created city: {city.name} in {destination.name}")
                else:
                    print(f"🏙️ City exists: {city.name}")
                created_cities.append(city)

    return created_cities

def create_places(cities):
    """Create 3 tourist attractions per city using hierarchical model"""
    places_data = {
        'Nairobi': [
            {'name': 'Nairobi National Park', 'category': 'National Park', 'description': 'Unique wildlife park on the edge of a capital city'},
            {'name': 'David Sheldrick Wildlife Trust', 'category': 'Conservation Center', 'description': 'Elephant orphanage and rhino sanctuary'},
            {'name': 'Karen Blixen Museum', 'category': 'Cultural Site', 'description': 'Historic home of the famous "Out of Africa" author'}
        ],
        'Mombasa': [
            {'name': 'Diani Beach', 'category': 'Beach', 'description': 'Pristine white sand beach with crystal clear waters'},
            {'name': 'Fort Jesus', 'category': 'Historical Site', 'description': 'UNESCO World Heritage Portuguese fort'},
            {'name': 'Haller Park', 'category': 'Nature Reserve', 'description': 'Transformed quarry now home to diverse wildlife'}
        ],
        'Maasai Mara': [
            {'name': 'Mara River', 'category': 'Natural Feature', 'description': 'Famous river crossing point during the Great Migration'},
            {'name': 'Maasai Cultural Village', 'category': 'Cultural Site', 'description': 'Authentic Maasai community experience'},
            {'name': 'Balloon Safari Launch Site', 'category': 'Adventure Activity', 'description': 'Hot air balloon safari over the savanna'}
        ],
        'Arusha': [
            {'name': 'Mount Meru', 'category': 'Mountain', 'description': 'Second highest peak in Tanzania, perfect for acclimatization'},
            {'name': 'Arusha National Park', 'category': 'National Park', 'description': 'Diverse ecosystems from lakes to montane forests'},
            {'name': 'Cultural Heritage Centre', 'category': 'Cultural Site', 'description': 'Showcase of Tanzanian art, culture, and crafts'}
        ],
        'Zanzibar': [
            {'name': 'Stone Town', 'category': 'UNESCO Site', 'description': 'Historic quarter with narrow alleys and ancient buildings'},
            {'name': 'Nungwi Beach', 'category': 'Beach', 'description': 'Northern beach paradise with traditional dhow boats'},
            {'name': 'Spice Tour Plantations', 'category': 'Cultural Experience', 'description': 'Aromatic journey through spice plantations'}
        ],
        'Serengeti': [
            {'name': 'Central Serengeti', 'category': 'Wildlife Area', 'description': 'Year-round wildlife viewing with resident predators'},
            {'name': 'Grumeti River', 'category': 'Natural Feature', 'description': 'Dramatic river crossings during migration'},
            {'name': 'Kopjes Rock Formations', 'category': 'Geological Feature', 'description': 'Ancient granite outcrops perfect for big cats'}
        ],
        'Cape Town': [
            {'name': 'Table Mountain', 'category': 'Mountain', 'description': 'Iconic flat-topped mountain with cable car access'},
            {'name': 'V&A Waterfront', 'category': 'Entertainment District', 'description': 'Shopping, dining, and entertainment complex'},
            {'name': 'Robben Island', 'category': 'Historical Site', 'description': 'Former prison island, now UNESCO World Heritage site'}
        ],
        'Johannesburg': [
            {'name': 'Apartheid Museum', 'category': 'Museum', 'description': 'Powerful museum documenting South African history'},
            {'name': 'Soweto Township', 'category': 'Cultural Site', 'description': 'Historic township with rich cultural heritage'},
            {'name': 'Gold Reef City', 'category': 'Theme Park', 'description': 'Entertainment complex built on old gold mine'}
        ],
        'Kruger': [
            {'name': 'Kruger National Park', 'category': 'National Park', 'description': 'Premier Big Five wildlife destination'},
            {'name': 'Blyde River Canyon', 'category': 'Natural Wonder', 'description': 'Third largest canyon in the world'},
            {'name': 'Bourke\'s Luck Potholes', 'category': 'Geological Feature', 'description': 'Unique rock formations carved by water'}
        ],
        'Kigali': [
            {'name': 'Kigali Genocide Memorial', 'category': 'Memorial', 'description': 'Moving tribute to genocide victims'},
            {'name': 'Kimironko Market', 'category': 'Market', 'description': 'Vibrant local market with crafts and produce'},
            {'name': 'Nyamirambo Women\'s Center', 'category': 'Cultural Center', 'description': 'Community center showcasing local culture'}
        ],
        'Volcanoes National Park': [
            {'name': 'Mountain Gorilla Habitat', 'category': 'Wildlife Area', 'description': 'Home to endangered mountain gorillas'},
            {'name': 'Mount Karisimbi', 'category': 'Mountain', 'description': 'Highest peak in Rwanda, challenging trek'},
            {'name': 'Dian Fossey Research Center', 'category': 'Research Center', 'description': 'Gorilla research and conservation center'}
        ],
        'Lake Kivu': [
            {'name': 'Gisenyi Beach', 'category': 'Beach', 'description': 'Freshwater beach resort on Lake Kivu'},
            {'name': 'Congo Nile Trail', 'category': 'Hiking Trail', 'description': 'Scenic trail along the lake shore'},
            {'name': 'Hot Springs', 'category': 'Natural Feature', 'description': 'Natural hot springs for relaxation'}
        ],
        'Dubai City': [
            {'name': 'Burj Khalifa', 'category': 'Skyscraper', 'description': 'World\'s tallest building with observation decks'},
            {'name': 'Dubai Mall', 'category': 'Shopping Center', 'description': 'World\'s largest shopping and entertainment destination'},
            {'name': 'Dubai Fountain', 'category': 'Entertainment', 'description': 'Spectacular water and light show'}
        ],
        'Dubai Marina': [
            {'name': 'Marina Walk', 'category': 'Promenade', 'description': 'Waterfront promenade with dining and shopping'},
            {'name': 'JBR Beach', 'category': 'Beach', 'description': 'Popular beach with water sports and dining'},
            {'name': 'Ain Dubai', 'category': 'Observation Wheel', 'description': 'World\'s largest and tallest observation wheel'}
        ],
        'Old Dubai': [
            {'name': 'Gold Souk', 'category': 'Traditional Market', 'description': 'Traditional gold jewelry market'},
            {'name': 'Dubai Creek', 'category': 'Waterway', 'description': 'Historic waterway with traditional abra boats'},
            {'name': 'Al Fahidi Historical Neighbourhood', 'category': 'Heritage Area', 'description': 'Preserved traditional architecture'}
        ],
        'Kuala Lumpur': [
            {'name': 'Petronas Twin Towers', 'category': 'Skyscraper', 'description': 'Iconic twin towers with sky bridge'},
            {'name': 'Batu Caves', 'category': 'Religious Site', 'description': 'Hindu temple complex in limestone caves'},
            {'name': 'Central Market', 'category': 'Cultural Market', 'description': 'Art deco building with local crafts and food'}
        ],
        'Langkawi': [
            {'name': 'Langkawi Sky Bridge', 'category': 'Bridge', 'description': 'Curved pedestrian bridge with panoramic views'},
            {'name': 'Pantai Cenang', 'category': 'Beach', 'description': 'Main beach with water sports and nightlife'},
            {'name': 'Kilim Karst Geoforest Park', 'category': 'Geopark', 'description': 'UNESCO Global Geopark with mangroves and caves'}
        ],
        'Penang': [
            {'name': 'George Town UNESCO Site', 'category': 'UNESCO Site', 'description': 'Historic city with colonial architecture'},
            {'name': 'Penang Hill', 'category': 'Hill Station', 'description': 'Cool hill retreat with funicular railway'},
            {'name': 'Gurney Drive', 'category': 'Food Street', 'description': 'Famous food court with local delicacies'}
        ]
    }
    
    created_places = []
    for city in cities:
        if city.name in places_data:
            for place_data in places_data[city.name]:
                place_slug = f"{city.slug}-{place_data['name'].lower().replace(' ', '-').replace('\'', '')}"
                place, created = Destination.objects.get_or_create(
                    slug=place_slug,
                    defaults={
                        'name': place_data['name'],
                        'description': place_data['description'],
                        'destination_type': Destination.PLACE,
                        'parent': city,
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Created place: {place.name} in {city.name}")
                else:
                    print(f"📍 Place exists: {place.name}")
                created_places.append(place)

    return created_places

def create_accommodations(destinations):
    """Create 3-5 accommodations per destination with different price ranges"""
    accommodations_data = {
        'Kenya': [
            {'name': 'Nairobi Serena Hotel', 'type': 'luxury', 'price': 250, 'rating': 5, 'rooms': 183, 'occupancy': 2},
            {'name': 'Sarova Stanley Hotel', 'type': 'mid-range', 'price': 150, 'rating': 4, 'rooms': 217, 'occupancy': 2},
            {'name': 'Wildebeest Eco Camp', 'type': 'budget', 'price': 45, 'rating': 3, 'rooms': 20, 'occupancy': 4},
            {'name': 'Mara Safari Lodge', 'type': 'luxury', 'price': 400, 'rating': 5, 'rooms': 74, 'occupancy': 2},
            {'name': 'Diani Beach Resort', 'type': 'mid-range', 'price': 180, 'rating': 4, 'rooms': 145, 'occupancy': 3}
        ],
        'Tanzania': [
            {'name': 'Four Seasons Safari Lodge', 'type': 'luxury', 'price': 800, 'rating': 5, 'rooms': 77, 'occupancy': 2},
            {'name': 'Serengeti Sopa Lodge', 'type': 'mid-range', 'price': 320, 'rating': 4, 'rooms': 69, 'occupancy': 2},
            {'name': 'Zanzibar Palace Hotel', 'type': 'luxury', 'price': 450, 'rating': 5, 'rooms': 9, 'occupancy': 2},
            {'name': 'Arusha Coffee Lodge', 'type': 'mid-range', 'price': 280, 'rating': 4, 'rooms': 30, 'occupancy': 2},
            {'name': 'Backpacker Safari Camp', 'type': 'budget', 'price': 35, 'rating': 3, 'rooms': 15, 'occupancy': 6}
        ],
        'South Africa': [
            {'name': 'One&Only Cape Town', 'type': 'luxury', 'price': 600, 'rating': 5, 'rooms': 131, 'occupancy': 2},
            {'name': 'Table Bay Hotel', 'type': 'luxury', 'price': 400, 'rating': 5, 'rooms': 329, 'occupancy': 2},
            {'name': 'Protea Hotel Cape Town', 'type': 'mid-range', 'price': 120, 'rating': 4, 'rooms': 112, 'occupancy': 2},
            {'name': 'Kruger Gate Hotel', 'type': 'mid-range', 'price': 180, 'rating': 4, 'rooms': 90, 'occupancy': 3},
            {'name': 'Cape Town Backpackers', 'type': 'budget', 'price': 25, 'rating': 3, 'rooms': 40, 'occupancy': 8}
        ],
        'Rwanda': [
            {'name': 'Bisate Lodge', 'type': 'luxury', 'price': 1200, 'rating': 5, 'rooms': 6, 'occupancy': 2},
            {'name': 'Virunga Lodge', 'type': 'luxury', 'price': 800, 'rating': 5, 'rooms': 8, 'occupancy': 2},
            {'name': 'Lake Kivu Serena Hotel', 'type': 'mid-range', 'price': 200, 'rating': 4, 'rooms': 66, 'occupancy': 2},
            {'name': 'Kigali Serena Hotel', 'type': 'mid-range', 'price': 180, 'rating': 4, 'rooms': 148, 'occupancy': 2}
        ],
        'Dubai': [
            {'name': 'Burj Al Arab Jumeirah', 'type': 'luxury', 'price': 2000, 'rating': 5, 'rooms': 202, 'occupancy': 2},
            {'name': 'Atlantis The Palm', 'type': 'luxury', 'price': 800, 'rating': 5, 'rooms': 1539, 'occupancy': 4},
            {'name': 'Jumeirah Beach Hotel', 'type': 'luxury', 'price': 600, 'rating': 5, 'rooms': 598, 'occupancy': 3},
            {'name': 'Rove Dubai Marina', 'type': 'mid-range', 'price': 150, 'rating': 4, 'rooms': 312, 'occupancy': 2},
            {'name': 'Premier Inn Dubai', 'type': 'budget', 'price': 80, 'rating': 3, 'rooms': 251, 'occupancy': 2}
        ],
        'Malaysia': [
            {'name': 'The Ritz-Carlton Kuala Lumpur', 'type': 'luxury', 'price': 300, 'rating': 5, 'rooms': 365, 'occupancy': 2},
            {'name': 'The Datai Langkawi', 'type': 'luxury', 'price': 500, 'rating': 5, 'rooms': 121, 'occupancy': 2},
            {'name': 'Eastern & Oriental Hotel Penang', 'type': 'luxury', 'price': 250, 'rating': 5, 'rooms': 100, 'occupancy': 2},
            {'name': 'Sunway Resort Hotel', 'type': 'mid-range', 'price': 120, 'rating': 4, 'rooms': 439, 'occupancy': 3},
            {'name': 'Tune Hotel KLIA2', 'type': 'budget', 'price': 40, 'rating': 3, 'rooms': 392, 'occupancy': 2}
        ]
    }
    
    created_accommodations = []
    for destination in destinations:
        if destination.name in accommodations_data:
            for acc_data in accommodations_data[destination.name]:
                # Create slug from name
                slug = acc_data['name'].lower().replace(' ', '-').replace('&', 'and')

                accommodation, created = Accommodation.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': acc_data['name'],
                        'slug': slug,
                        'accommodation_type': Accommodation.HOTEL if acc_data['type'] == 'luxury' else Accommodation.LODGE if acc_data['type'] == 'mid-range' else Accommodation.GUESTHOUSE,
                        'description': f"Experience {acc_data['type']} accommodation in {destination.name}. Perfect for travelers seeking comfort and authentic local experiences.",
                        'destination': destination,
                        'price_per_room_per_night': acc_data['price'],
                        'max_occupancy_per_room': acc_data['occupancy'],
                        'total_rooms': acc_data['rooms'],
                        'amenities': 'WiFi, Restaurant, Room Service, Air Conditioning',
                        'rating': Decimal(str(acc_data['rating'])),
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Created accommodation: {accommodation.name} (${acc_data['price']}/night)")
                else:
                    print(f"🏨 Accommodation exists: {accommodation.name}")
                created_accommodations.append(accommodation)
    
    return created_accommodations

def create_travel_modes():
    """Create various transportation options"""
    travel_modes_data = [
        {'name': 'Road Transport', 'type': 'bus', 'price': 50, 'description': 'Comfortable road transport with experienced drivers and air-conditioned vehicles'},
        {'name': 'Domestic Flight', 'type': 'flight', 'price': 200, 'description': 'Quick and convenient domestic flights to save travel time'},
        {'name': 'International Flight', 'type': 'flight', 'price': 800, 'description': 'International flight connections with major airlines'},
        {'name': 'Cruise Transfer', 'type': 'cruiser', 'price': 150, 'description': 'Scenic water transport and cruise experiences'},
        {'name': 'Self Drive', 'type': 'car', 'price': 0, 'description': 'Use your own vehicle or rental car for maximum flexibility'},
        {'name': 'Luxury Coach', 'type': 'bus', 'price': 80, 'description': 'Premium coach transport with enhanced comfort and amenities'}
    ]
    
    created_travel_modes = []
    for tm_data in travel_modes_data:
        travel_mode, created = TravelMode.objects.get_or_create(
            name=tm_data['name'],
            defaults={
                'transport_type': tm_data['type'],
                'departure_location': 'Various Locations',
                'arrival_location': 'Destination',
                'departure_time': '08:00',
                'arrival_time': '18:00',
                'duration_minutes': 600,
                'price_per_person': tm_data['price'],
                'description': tm_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created travel mode: {travel_mode.name} (${tm_data['price']}/person)")
        else:
            print(f"🚗 Travel mode exists: {travel_mode.name}")
        created_travel_modes.append(travel_mode)
    
    return created_travel_modes

def create_packages(destinations, accommodations, travel_modes):
    """Create 4 packages per destination with varying durations and prices"""
    packages_data = {
        'Kenya': [
            {'name': 'Maasai Mara Safari Adventure', 'duration': 5, 'adult_price': 850, 'child_price': 595, 'type': 'budget'},
            {'name': 'Kenya Highlights Explorer', 'duration': 8, 'adult_price': 1650, 'child_price': 1155, 'type': 'mid-range'},
            {'name': 'Luxury Kenya Safari & Beach', 'duration': 12, 'adult_price': 3200, 'child_price': 2240, 'type': 'luxury'},
            {'name': 'Mombasa Beach Paradise', 'duration': 6, 'adult_price': 1200, 'child_price': 840, 'type': 'mid-range'}
        ],
        'Tanzania': [
            {'name': 'Serengeti Migration Safari', 'duration': 7, 'adult_price': 1800, 'child_price': 1260, 'type': 'mid-range'},
            {'name': 'Kilimanjaro & Safari Combo', 'duration': 14, 'adult_price': 4500, 'child_price': 3150, 'type': 'luxury'},
            {'name': 'Zanzibar Island Escape', 'duration': 5, 'adult_price': 950, 'child_price': 665, 'type': 'budget'},
            {'name': 'Tanzania Grand Circuit', 'duration': 10, 'adult_price': 2800, 'child_price': 1960, 'type': 'luxury'}
        ],
        'South Africa': [
            {'name': 'Cape Town & Wine Country', 'duration': 6, 'adult_price': 1400, 'child_price': 980, 'type': 'mid-range'},
            {'name': 'Garden Route Adventure', 'duration': 9, 'adult_price': 2100, 'child_price': 1470, 'type': 'mid-range'},
            {'name': 'Luxury South Africa Explorer', 'duration': 12, 'adult_price': 4800, 'child_price': 3360, 'type': 'luxury'},
            {'name': 'Kruger Safari Budget', 'duration': 4, 'adult_price': 650, 'child_price': 455, 'type': 'budget'}
        ],
        'Rwanda': [
            {'name': 'Gorilla Trekking Experience', 'duration': 4, 'adult_price': 2200, 'child_price': 1540, 'type': 'luxury'},
            {'name': 'Rwanda Cultural Discovery', 'duration': 6, 'adult_price': 1600, 'child_price': 1120, 'type': 'mid-range'},
            {'name': 'Lake Kivu Relaxation', 'duration': 5, 'adult_price': 900, 'child_price': 630, 'type': 'budget'},
            {'name': 'Complete Rwanda Adventure', 'duration': 8, 'adult_price': 2800, 'child_price': 1960, 'type': 'luxury'}
        ],
        'Dubai': [
            {'name': 'Dubai City Explorer', 'duration': 4, 'adult_price': 1200, 'child_price': 840, 'type': 'mid-range'},
            {'name': 'Luxury Dubai Experience', 'duration': 6, 'adult_price': 3500, 'child_price': 2450, 'type': 'luxury'},
            {'name': 'Dubai Budget Adventure', 'duration': 3, 'adult_price': 650, 'child_price': 455, 'type': 'budget'},
            {'name': 'Dubai & Abu Dhabi Combo', 'duration': 7, 'adult_price': 2200, 'child_price': 1540, 'type': 'mid-range'}
        ],
        'Malaysia': [
            {'name': 'Kuala Lumpur & Langkawi', 'duration': 7, 'adult_price': 1100, 'child_price': 770, 'type': 'mid-range'},
            {'name': 'Malaysia Grand Tour', 'duration': 10, 'adult_price': 1800, 'child_price': 1260, 'type': 'mid-range'},
            {'name': 'Luxury Malaysia Experience', 'duration': 8, 'adult_price': 2800, 'child_price': 1960, 'type': 'luxury'},
            {'name': 'Backpacker Malaysia', 'duration': 12, 'adult_price': 800, 'child_price': 560, 'type': 'budget'}
        ]
    }

    created_packages = []
    for destination in destinations:
        if destination.name in packages_data:
            for pkg_data in packages_data[destination.name]:
                # Create slug from name
                slug = pkg_data['name'].lower().replace(' ', '-').replace('&', 'and')

                package, created = Package.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': pkg_data['name'],
                        'description': f"Experience the best of {destination.name} with our carefully crafted {pkg_data['type']} package. This {pkg_data['duration']}-day adventure includes accommodation, meals, and guided activities.",
                        'main_destination': destination,
                        'duration_days': pkg_data['duration'],
                        'duration_nights': pkg_data['duration'] - 1,
                        'adult_price': pkg_data['adult_price'],
                        'child_price': pkg_data['child_price'],
                        'inclusions': f"Accommodation, meals, guided tours, transportation, and all activities mentioned in the itinerary for this {pkg_data['duration']}-day {destination.name} adventure.",
                        'exclusions': "International flights, travel insurance, personal expenses, tips, and items not mentioned in inclusions.",
                        'status': Package.PUBLISHED
                    }
                )

                if created:
                    # Link accommodations (2-3 per package)
                    dest_accommodations = [acc for acc in accommodations if acc.destination == destination]
                    if dest_accommodations:
                        package.available_accommodations.set(dest_accommodations[:3])

                    # Link travel modes (3-4 per package)
                    package.available_travel_modes.set(travel_modes[:4])

                    print(f"✅ Created package: {package.name} (${pkg_data['adult_price']}) - {pkg_data['type']}")
                else:
                    print(f"📦 Package exists: {package.name}")

                created_packages.append(package)

    return created_packages

def create_itineraries(packages):
    """Create detailed itineraries for packages"""
    sample_activities = {
        'Kenya': [
            "Arrival and transfer to hotel",
            "Game drive in Maasai Mara National Reserve",
            "Visit to Maasai cultural village",
            "Hot air balloon safari over the savanna",
            "Transfer to Nairobi and city tour",
            "Visit to David Sheldrick Elephant Orphanage",
            "Departure transfer to airport"
        ],
        'Tanzania': [
            "Arrival in Arusha and briefing",
            "Serengeti National Park game drive",
            "Ngorongoro Crater exploration",
            "Cultural tour with local tribes",
            "Transfer to Zanzibar",
            "Stone Town historical tour",
            "Beach relaxation and water activities",
            "Spice plantation tour",
            "Departure from Zanzibar"
        ],
        'South Africa': [
            "Arrival in Cape Town",
            "Table Mountain cable car experience",
            "Cape Peninsula tour including Cape Point",
            "Wine tasting in Stellenbosch",
            "Transfer to Kruger National Park",
            "Big Five game drives",
            "Bush walk with experienced guide",
            "Departure from Johannesburg"
        ],
        'Rwanda': [
            "Arrival in Kigali and city tour",
            "Transfer to Volcanoes National Park",
            "Mountain gorilla trekking experience",
            "Golden monkey tracking",
            "Transfer to Lake Kivu",
            "Boat cruise and relaxation",
            "Return to Kigali for departure"
        ],
        'Dubai': [
            "Arrival and Dubai city tour",
            "Burj Khalifa and Dubai Mall visit",
            "Desert safari with BBQ dinner",
            "Dubai Marina and JBR beach",
            "Traditional souk shopping",
            "Luxury spa experience",
            "Departure transfer"
        ],
        'Malaysia': [
            "Arrival in Kuala Lumpur",
            "City tour including Petronas Towers",
            "Batu Caves and cultural sites",
            "Transfer to Langkawi",
            "Island hopping tour",
            "Mangrove and eagle watching",
            "Beach relaxation",
            "Return to KL for departure"
        ]
    }

    created_itineraries = []
    for package in packages:
        destination_name = package.main_destination.name
        if destination_name in sample_activities:
            activities = sample_activities[destination_name]

            # Create or get the main itinerary for the package
            itinerary, itinerary_created = Itinerary.objects.get_or_create(
                package=package,
                defaults={
                    'title': f"{package.name} Itinerary",
                    'overview': f"Detailed day-by-day itinerary for {package.name}"
                }
            )

            for day in range(1, min(package.duration_days + 1, len(activities) + 1)):
                activity_index = (day - 1) % len(activities)

                itinerary_day, created = ItineraryDay.objects.get_or_create(
                    itinerary=itinerary,
                    day_number=day,
                    defaults={
                        'title': f"Day {day}: {activities[activity_index].split(' and ')[0]}",
                        'description': activities[activity_index],
                        'breakfast': day > 1,
                        'lunch': True,
                        'dinner': True
                    }
                )

                if created:
                    created_itineraries.append(itinerary_day)

    print(f"✅ Created {len(created_itineraries)} itinerary items")
    return created_itineraries

def populate_database():
    """Main function to populate the entire database"""
    print("🌍 NOVUSTELL TRAVEL DATABASE POPULATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Create destinations
    print("\n📍 Creating Destinations...")
    destinations = create_destinations()

    # Create cities
    print("\n🏙️ Creating Cities...")
    cities = create_cities(destinations)

    # Create places
    print("\n📍 Creating Tourist Attractions...")
    places = create_places(cities)

    # Create accommodations
    print("\n🏨 Creating Accommodations...")
    accommodations = create_accommodations(destinations)

    # Create travel modes
    print("\n🚗 Creating Travel Modes...")
    travel_modes = create_travel_modes()

    # Create packages
    print("\n📦 Creating Travel Packages...")
    packages = create_packages(destinations, accommodations, travel_modes)

    # Create itineraries
    print("\n📋 Creating Package Itineraries...")
    itineraries = create_itineraries(packages)

    print("\n" + "=" * 60)
    print("✅ DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Destinations: {len(destinations)}")
    print(f"   Cities: {len(cities)}")
    print(f"   Places: {len(places)}")
    print(f"   Accommodations: {len(accommodations)}")
    print(f"   Travel Modes: {len(travel_modes)}")
    print(f"   Packages: {len(packages)}")
    print(f"   Itinerary Items: {len(itineraries)}")
    print("=" * 60)

    return {
        'destinations': destinations,
        'cities': cities,
        'places': places,
        'accommodations': accommodations,
        'travel_modes': travel_modes,
        'packages': packages,
        'itineraries': itineraries
    }

if __name__ == "__main__":
    populate_database()
