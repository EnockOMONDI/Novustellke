#!/usr/bin/env python
"""
Data population script for Novustell Travel adminside app
Creates comprehensive sample data for testing
"""

import os
import sys
import django
from datetime import datetime, time
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from adminside.models import (
    Destination, Accommodation, TravelMode, Package, 
    Itinerary, ItineraryDay, PackageBooking
)
from django.contrib.auth.models import User

def create_destinations():
    """Create hierarchical destination structure"""
    print("Creating destinations...")
    
    # Countries
    kenya = Destination.objects.create(
        name="Kenya",
        slug="kenya",
        destination_type=Destination.COUNTRY,
        description="Experience the magic of Kenya with its stunning wildlife, beautiful beaches, and rich cultural heritage. From the Great Migration in Maasai Mara to the pristine beaches of the coast.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789012/",
        meta_title="Kenya Travel Packages - Novustell Travel",
        meta_description="Discover Kenya's wildlife, beaches, and culture with our expertly crafted travel packages.",
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    tanzania = Destination.objects.create(
        name="Tanzania",
        slug="tanzania",
        destination_type=Destination.COUNTRY,
        description="Discover Tanzania's incredible wildlife, Mount Kilimanjaro, and the exotic spice islands of Zanzibar. Home to the Serengeti and Ngorongoro Crater.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789013/",
        meta_title="Tanzania Safari Packages - Novustell Travel",
        meta_description="Experience Tanzania's wildlife and natural wonders with our comprehensive travel packages.",
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Cities in Kenya
    nairobi = Destination.objects.create(
        name="Nairobi",
        slug="nairobi",
        destination_type=Destination.CITY,
        description="Kenya's vibrant capital city, known as the 'Green City in the Sun'. Gateway to safari adventures and home to unique attractions like Nairobi National Park.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789014/",
        parent=kenya,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    mombasa = Destination.objects.create(
        name="Mombasa",
        slug="mombasa",
        destination_type=Destination.CITY,
        description="Kenya's coastal gem with pristine beaches, rich Swahili culture, and historic attractions. Perfect for beach holidays and cultural exploration.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789015/",
        parent=kenya,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    nakuru = Destination.objects.create(
        name="Nakuru",
        slug="nakuru",
        destination_type=Destination.CITY,
        description="Home to the famous Lake Nakuru National Park, known for its flamingos and rhino sanctuary. A perfect stop on the safari circuit.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789016/",
        parent=kenya,
        display_order=3,
        is_featured=True,
        is_active=True
    )
    
    # Cities in Tanzania
    dar_es_salaam = Destination.objects.create(
        name="Dar es Salaam",
        slug="dar-es-salaam",
        destination_type=Destination.CITY,
        description="Tanzania's largest city and economic hub, featuring beautiful beaches, vibrant markets, and rich cultural heritage.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789017/",
        parent=tanzania,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    arusha = Destination.objects.create(
        name="Arusha",
        slug="arusha",
        destination_type=Destination.CITY,
        description="Gateway to Tanzania's northern safari circuit, including Serengeti, Ngorongoro Crater, and Mount Kilimanjaro.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789018/",
        parent=tanzania,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    zanzibar = Destination.objects.create(
        name="Zanzibar",
        slug="zanzibar",
        destination_type=Destination.CITY,
        description="The spice island paradise with pristine beaches, historic Stone Town, and rich cultural heritage.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789019/",
        parent=tanzania,
        display_order=3,
        is_featured=True,
        is_active=True
    )
    
    # Places in Nairobi
    Destination.objects.create(
        name="Nairobi National Park",
        slug="nairobi-national-park",
        destination_type=Destination.PLACE,
        description="Unique wildlife park on the edge of a capital city, home to lions, rhinos, and giraffes with Nairobi skyline backdrop.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789020/",
        parent=nairobi,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="Karen Blixen Museum",
        slug="karen-blixen-museum",
        destination_type=Destination.PLACE,
        description="Historic house museum of the famous author of 'Out of Africa', showcasing colonial history and beautiful gardens.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789021/",
        parent=nairobi,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Places in Mombasa
    Destination.objects.create(
        name="Diani Beach",
        slug="diani-beach",
        destination_type=Destination.PLACE,
        description="One of Africa's finest beaches with white sand, crystal clear waters, and excellent water sports facilities.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789022/",
        parent=mombasa,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="Fort Jesus",
        slug="fort-jesus",
        destination_type=Destination.PLACE,
        description="UNESCO World Heritage Site, a 16th-century Portuguese fort showcasing the region's rich maritime history.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789023/",
        parent=mombasa,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Places in Nakuru
    Destination.objects.create(
        name="Lake Nakuru National Park",
        slug="lake-nakuru-national-park",
        destination_type=Destination.PLACE,
        description="Famous for its flamingo populations and rhino sanctuary, offering excellent wildlife viewing opportunities.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789024/",
        parent=nakuru,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="Menengai Crater",
        slug="menengai-crater",
        destination_type=Destination.PLACE,
        description="One of the largest volcanic calderas in the world, offering spectacular views and hiking opportunities.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789025/",
        parent=nakuru,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Places in Dar es Salaam
    Destination.objects.create(
        name="Coco Beach",
        slug="coco-beach",
        destination_type=Destination.PLACE,
        description="Popular beach destination with restaurants, bars, and beautiful sunset views over the Indian Ocean.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789026/",
        parent=dar_es_salaam,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="National Museum",
        slug="national-museum-dar",
        destination_type=Destination.PLACE,
        description="Tanzania's premier museum showcasing the country's history, culture, and archaeological discoveries.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789027/",
        parent=dar_es_salaam,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Places in Arusha
    Destination.objects.create(
        name="Mount Meru",
        slug="mount-meru",
        destination_type=Destination.PLACE,
        description="Tanzania's second highest mountain, offering excellent acclimatization for Kilimanjaro climbers and stunning views.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789028/",
        parent=arusha,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="Arusha National Park",
        slug="arusha-national-park",
        destination_type=Destination.PLACE,
        description="Diverse park featuring Mount Meru, Momella Lakes, and excellent wildlife viewing including giraffes and colobus monkeys.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789029/",
        parent=arusha,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    # Places in Zanzibar
    Destination.objects.create(
        name="Stone Town",
        slug="stone-town",
        destination_type=Destination.PLACE,
        description="UNESCO World Heritage Site, historic heart of Zanzibar with narrow streets, spice markets, and Swahili architecture.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789030/",
        parent=zanzibar,
        display_order=1,
        is_featured=True,
        is_active=True
    )
    
    Destination.objects.create(
        name="Nungwi Beach",
        slug="nungwi-beach",
        destination_type=Destination.PLACE,
        description="Pristine white sand beach on the northern tip of Zanzibar, perfect for swimming, snorkeling, and sunset views.",
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789031/",
        parent=zanzibar,
        display_order=2,
        is_featured=True,
        is_active=True
    )
    
    print("✓ Created destinations with hierarchical structure")
    return {
        'kenya': kenya, 'tanzania': tanzania,
        'nairobi': nairobi, 'mombasa': mombasa, 'nakuru': nakuru,
        'dar_es_salaam': dar_es_salaam, 'arusha': arusha, 'zanzibar': zanzibar
    }

def create_accommodations(destinations):
    """Create diverse accommodations across destinations"""
    print("Creating accommodations...")

    accommodations = []

    # Nairobi accommodations
    accommodations.append(Accommodation.objects.create(
        name="Sarova Stanley Hotel",
        slug="sarova-stanley-hotel",
        accommodation_type=Accommodation.HOTEL,
        description="Historic luxury hotel in the heart of Nairobi, offering elegant rooms, fine dining, and excellent service. Perfect for business and leisure travelers.",
        destination=destinations['nairobi'],
        address="Corner of Kimathi Street and Kenyatta Avenue, Nairobi",
        price_per_room_per_night=180,
        max_occupancy_per_room=2,
        total_rooms=217,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789032/",
        amenities="WiFi, Restaurant, Bar, Gym, Spa, Conference Rooms, Airport Transfer",
        is_active=True,
        is_featured=True,
        rating=Decimal('4.5'),
        total_reviews=324
    ))

    accommodations.append(Accommodation.objects.create(
        name="Nairobi Tented Camp",
        slug="nairobi-tented-camp",
        accommodation_type=Accommodation.LODGE,
        description="Unique tented accommodation near Nairobi National Park, offering an authentic safari experience just minutes from the city center.",
        destination=destinations['nairobi'],
        address="Near Nairobi National Park, Karen",
        price_per_room_per_night=120,
        max_occupancy_per_room=3,
        total_rooms=24,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789033/",
        amenities="Game Drives, Restaurant, Bar, WiFi, Airport Transfer, Guided Tours",
        is_active=True,
        is_featured=True,
        rating=Decimal('4.2'),
        total_reviews=156
    ))

    # Mombasa accommodations
    accommodations.append(Accommodation.objects.create(
        name="Serena Beach Resort & Spa",
        slug="serena-beach-resort-spa",
        accommodation_type=Accommodation.RESORT,
        description="Luxury beachfront resort with pristine white sand beaches, world-class spa, and multiple dining options. Perfect for romantic getaways.",
        destination=destinations['mombasa'],
        address="Shanzu Beach, North Coast, Mombasa",
        price_per_room_per_night=280,
        max_occupancy_per_room=4,
        total_rooms=164,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789034/",
        amenities="Private Beach, Spa, Multiple Restaurants, Pool, Water Sports, Kids Club, WiFi",
        is_active=True,
        is_featured=True,
        rating=Decimal('4.7'),
        total_reviews=892
    ))

    accommodations.append(Accommodation.objects.create(
        name="Diani Beach Airbnb Villa",
        slug="diani-beach-airbnb-villa",
        accommodation_type=Accommodation.AIRBNB,
        description="Beautiful beachfront villa with private pool and direct beach access. Perfect for families and groups seeking privacy and luxury.",
        destination=destinations['mombasa'],
        address="Diani Beach Road, South Coast",
        price_per_room_per_night=95,
        max_occupancy_per_room=6,
        total_rooms=3,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789035/",
        amenities="Private Pool, Beach Access, Kitchen, WiFi, Garden, Parking, Security",
        is_active=True,
        is_featured=False,
        rating=Decimal('4.8'),
        total_reviews=67
    ))

    # Zanzibar accommodations
    accommodations.append(Accommodation.objects.create(
        name="Emerson Zanzibar",
        slug="emerson-zanzibar",
        accommodation_type=Accommodation.GUESTHOUSE,
        description="Boutique hotel in the heart of Stone Town, featuring traditional Zanzibari architecture and rooftop dining with ocean views.",
        destination=destinations['zanzibar'],
        address="236 Hurumzi Street, Stone Town, Zanzibar",
        price_per_room_per_night=150,
        max_occupancy_per_room=2,
        total_rooms=17,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789036/",
        amenities="Rooftop Restaurant, WiFi, Cultural Tours, Airport Transfer, Traditional Decor",
        is_active=True,
        is_featured=True,
        rating=Decimal('4.4'),
        total_reviews=203
    ))

    accommodations.append(Accommodation.objects.create(
        name="Nungwi Beach Airbnb",
        slug="nungwi-beach-airbnb",
        accommodation_type=Accommodation.AIRBNB,
        description="Charming beachfront apartment with stunning sunset views and easy access to Nungwi's pristine beaches and local restaurants.",
        destination=destinations['zanzibar'],
        address="Nungwi Village, Northern Zanzibar",
        price_per_room_per_night=75,
        max_occupancy_per_room=4,
        total_rooms=2,
        image="https://ucarecdn.com/12345678-1234-1234-1234-123456789037/",
        amenities="Beach Access, Kitchen, WiFi, Balcony, Snorkeling Gear, Local Guide",
        is_active=True,
        is_featured=False,
        rating=Decimal('4.6'),
        total_reviews=89
    ))

    print("✓ Created 6 accommodations across destinations")
    return accommodations

def create_travel_modes():
    """Create diverse travel options"""
    print("Creating travel modes...")

    travel_modes = []

    # Flights
    travel_modes.append(TravelMode.objects.create(
        name="Kenya Airways Morning Flight",
        transport_type=TravelMode.FLIGHT,
        departure_location="Jomo Kenyatta International Airport (NBO)",
        arrival_location="Julius Nyerere International Airport (DAR)",
        departure_time=time(8, 30),
        arrival_time=time(10, 45),
        duration_minutes=135,
        price_per_person=320,
        child_discount_percentage=25,
        description="Comfortable morning flight with excellent service and on-time performance. Includes meal and beverage service.",
        terms_and_conditions="Baggage allowance: 23kg checked, 7kg carry-on. Check-in closes 2 hours before departure.",
        total_capacity=180,
        is_active=True
    ))

    travel_modes.append(TravelMode.objects.create(
        name="Precision Air Afternoon Service",
        transport_type=TravelMode.FLIGHT,
        departure_location="Kilimanjaro International Airport (JRO)",
        arrival_location="Abeid Amani Karume International Airport (ZNZ)",
        departure_time=time(14, 15),
        arrival_time=time(15, 30),
        duration_minutes=75,
        price_per_person=180,
        child_discount_percentage=20,
        description="Quick and efficient flight to Zanzibar with stunning aerial views of the coast.",
        terms_and_conditions="Light refreshments included. Advance booking recommended during peak season.",
        total_capacity=50,
        is_active=True
    ))

    # Ground transport
    travel_modes.append(TravelMode.objects.create(
        name="Luxury Safari Vehicle",
        transport_type=TravelMode.CAR,
        departure_location="Nairobi City Center",
        arrival_location="Maasai Mara National Reserve",
        departure_time=time(7, 0),
        arrival_time=time(12, 0),
        duration_minutes=300,
        price_per_person=85,
        child_discount_percentage=15,
        description="Comfortable 4WD safari vehicle with pop-up roof for game viewing. Professional driver-guide included.",
        terms_and_conditions="Includes bottled water and snacks. Maximum 6 passengers per vehicle.",
        total_capacity=6,
        is_active=True
    ))

    travel_modes.append(TravelMode.objects.create(
        name="SGR Express Train",
        transport_type=TravelMode.TRAIN,
        departure_location="Nairobi Terminus",
        arrival_location="Mombasa Terminus",
        departure_time=time(8, 0),
        arrival_time=time(13, 30),
        duration_minutes=330,
        price_per_person=45,
        child_discount_percentage=30,
        description="Modern standard gauge railway with comfortable seating and scenic views of the Kenyan landscape.",
        terms_and_conditions="Economy class seating. Food and beverages available for purchase onboard.",
        total_capacity=1260,
        is_active=True
    ))

    # Water transport
    travel_modes.append(TravelMode.objects.create(
        name="Zanzibar Ferry Service",
        transport_type=TravelMode.BOAT,
        departure_location="Dar es Salaam Ferry Terminal",
        arrival_location="Stone Town Ferry Terminal",
        departure_time=time(9, 30),
        arrival_time=time(11, 30),
        duration_minutes=120,
        price_per_person=35,
        child_discount_percentage=50,
        description="Fast ferry service with air conditioning and comfortable seating. Enjoy ocean views during the journey.",
        terms_and_conditions="Life jackets provided. Rough seas may cause delays. Advance booking recommended.",
        total_capacity=300,
        is_active=True
    ))

    # Cruiser
    travel_modes.append(TravelMode.objects.create(
        name="Indian Ocean Luxury Cruiser",
        transport_type=TravelMode.CRUISER,
        departure_location="Mombasa Port",
        arrival_location="Zanzibar Port",
        departure_time=time(18, 0),
        arrival_time=time(8, 0),
        duration_minutes=840,
        price_per_person=450,
        child_discount_percentage=35,
        description="Overnight luxury cruise with dinner, entertainment, and comfortable cabins. Wake up in paradise!",
        terms_and_conditions="All meals included. Formal dress code for dinner. Sea sickness medication recommended.",
        total_capacity=200,
        is_active=True
    ))

    print("✓ Created 6 travel modes covering all transport types")
    return travel_modes

def create_packages(destinations, accommodations, travel_modes):
    """Create comprehensive travel packages"""
    print("Creating travel packages...")

    packages = []

    # Kenya Safari Package
    kenya_safari = Package.objects.create(
        name="Ultimate Kenya Safari Adventure",
        slug="ultimate-kenya-safari-adventure",
        main_destination=destinations['kenya'],
        description="Experience the best of Kenya's wildlife with visits to Maasai Mara, Lake Nakuru, and Nairobi National Park. Witness the Great Migration and see the Big Five in their natural habitat.",
        duration_days=7,
        duration_nights=6,
        adult_price=1850,
        child_price=1295,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789038/",
        inclusions="Accommodation, All meals, Game drives, Park fees, Professional guide, Airport transfers",
        exclusions="International flights, Visa fees, Personal expenses, Tips, Travel insurance",
        meta_title="Kenya Safari Package - 7 Days Ultimate Adventure",
        meta_description="Join our 7-day Kenya safari adventure featuring Maasai Mara, Lake Nakuru, and more.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('4.8'),
        total_reviews=156
    )

    # Add accommodations and travel modes to Kenya Safari
    kenya_safari.available_accommodations.add(accommodations[0], accommodations[1])  # Nairobi hotels
    kenya_safari.available_travel_modes.add(travel_modes[2])  # Safari vehicle
    packages.append(kenya_safari)

    # Mombasa Beach Package
    mombasa_beach = Package.objects.create(
        name="Mombasa Beach Paradise",
        slug="mombasa-beach-paradise",
        main_destination=destinations['mombasa'],
        description="Relax on pristine white sand beaches, explore historic Fort Jesus, and enjoy water sports in the crystal-clear waters of the Indian Ocean.",
        duration_days=5,
        duration_nights=4,
        adult_price=980,
        child_price=686,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789039/",
        inclusions="Beach resort accommodation, Breakfast and dinner, Airport transfers, Cultural tour, Water sports",
        exclusions="Lunch, International flights, Visa fees, Personal expenses, Spa treatments",
        meta_title="Mombasa Beach Holiday - 5 Days Paradise Package",
        meta_description="Enjoy 5 days of beach bliss in Mombasa with luxury accommodation and activities.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('4.6'),
        total_reviews=203
    )

    mombasa_beach.available_accommodations.add(accommodations[2], accommodations[3])  # Mombasa accommodations
    mombasa_beach.available_travel_modes.add(travel_modes[3])  # Train
    packages.append(mombasa_beach)

    # Tanzania Explorer Package
    tanzania_explorer = Package.objects.create(
        name="Tanzania Wildlife & Culture Explorer",
        slug="tanzania-wildlife-culture-explorer",
        main_destination=destinations['tanzania'],
        description="Discover Tanzania's incredible wildlife in Serengeti and Ngorongoro, then unwind on the spice island of Zanzibar with its pristine beaches and rich culture.",
        duration_days=10,
        duration_nights=9,
        adult_price=2750,
        child_price=1925,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789040/",
        inclusions="All accommodation, All meals, Game drives, Cultural tours, Internal flights, Professional guide",
        exclusions="International flights, Visa fees, Personal expenses, Tips, Optional activities",
        meta_title="Tanzania Safari & Zanzibar - 10 Days Explorer Package",
        meta_description="Experience Tanzania's wildlife and Zanzibar's beaches in this comprehensive 10-day package.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('4.9'),
        total_reviews=89
    )

    tanzania_explorer.available_accommodations.add(accommodations[4], accommodations[5])  # Zanzibar accommodations
    tanzania_explorer.available_travel_modes.add(travel_modes[0], travel_modes[1])  # Flights
    packages.append(tanzania_explorer)

    # Zanzibar Spice Island Package
    zanzibar_spice = Package.objects.create(
        name="Zanzibar Spice Island Getaway",
        slug="zanzibar-spice-island-getaway",
        main_destination=destinations['zanzibar'],
        description="Immerse yourself in the exotic culture of Zanzibar with spice tours, historic Stone Town exploration, and relaxation on world-class beaches.",
        duration_days=6,
        duration_nights=5,
        adult_price=1350,
        child_price=945,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789041/",
        inclusions="Boutique accommodation, Breakfast, Spice tour, Stone Town tour, Airport transfers, Sunset dhow cruise",
        exclusions="Lunch and dinner, International flights, Visa fees, Personal expenses, Water sports",
        meta_title="Zanzibar Holiday - 6 Days Spice Island Experience",
        meta_description="Explore Zanzibar's culture, spices, and beaches in this 6-day island getaway.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('4.7'),
        total_reviews=134
    )

    zanzibar_spice.available_accommodations.add(accommodations[4], accommodations[5])  # Zanzibar accommodations
    zanzibar_spice.available_travel_modes.add(travel_modes[4])  # Ferry
    packages.append(zanzibar_spice)

    # Luxury East Africa Package
    luxury_east_africa = Package.objects.create(
        name="Luxury East Africa Grand Tour",
        slug="luxury-east-africa-grand-tour",
        main_destination=destinations['kenya'],
        description="The ultimate luxury experience combining Kenya's wildlife, Tanzania's Serengeti, and Zanzibar's beaches. Travel in style with premium accommodations and exclusive experiences.",
        duration_days=14,
        duration_nights=13,
        adult_price=4850,
        child_price=3395,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789042/",
        inclusions="Luxury accommodation, All meals, Private game drives, Cultural experiences, All flights, Butler service",
        exclusions="International flights, Visa fees, Personal shopping, Spa treatments, Alcoholic beverages",
        meta_title="Luxury East Africa Tour - 14 Days Grand Experience",
        meta_description="Experience the ultimate luxury in East Africa with our 14-day grand tour package.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('5.0'),
        total_reviews=45
    )

    luxury_east_africa.available_accommodations.add(*accommodations[:4])  # Multiple accommodations
    luxury_east_africa.available_travel_modes.add(travel_modes[0], travel_modes[5])  # Flights and cruiser
    packages.append(luxury_east_africa)

    # Budget Backpacker Package
    budget_backpacker = Package.objects.create(
        name="East Africa Budget Backpacker Adventure",
        slug="east-africa-budget-backpacker-adventure",
        main_destination=destinations['kenya'],
        description="Perfect for budget-conscious travelers wanting to experience East Africa's highlights. Includes basic accommodation, group tours, and authentic local experiences.",
        duration_days=12,
        duration_nights=11,
        adult_price=1250,
        child_price=875,
        featured_image="https://ucarecdn.com/12345678-1234-1234-1234-123456789043/",
        inclusions="Budget accommodation, Some meals, Group tours, Local transport, Cultural experiences, Basic guide",
        exclusions="International flights, Visa fees, Most meals, Personal expenses, Tips, Luxury activities",
        meta_title="Budget East Africa Adventure - 12 Days Backpacker Package",
        meta_description="Explore East Africa on a budget with our 12-day backpacker adventure package.",
        status=Package.PUBLISHED,
        is_featured=True,
        published_at=datetime.now(),
        rating=Decimal('4.3'),
        total_reviews=267
    )

    budget_backpacker.available_accommodations.add(accommodations[3], accommodations[5])  # Airbnb options
    budget_backpacker.available_travel_modes.add(travel_modes[3], travel_modes[4])  # Train and ferry
    packages.append(budget_backpacker)

    print("✓ Created 6 diverse travel packages")
    return packages

def create_itineraries(packages, destinations, accommodations):
    """Create detailed itineraries for packages"""
    print("Creating itineraries...")

    # Kenya Safari Itinerary
    kenya_safari_itinerary = Itinerary.objects.create(
        package=packages[0],  # Kenya Safari
        title="Ultimate Kenya Safari Adventure Itinerary",
        overview="A comprehensive 7-day safari experience showcasing Kenya's most famous wildlife destinations and cultural experiences."
    )

    # Day 1
    ItineraryDay.objects.create(
        itinerary=kenya_safari_itinerary,
        day_number=1,
        title="Arrival in Nairobi",
        destination=destinations['nairobi'],
        accommodation=accommodations[0],  # Sarova Stanley
        description="Arrive at Jomo Kenyatta International Airport. Meet and greet by our representative. Transfer to hotel for check-in and rest. Evening briefing about the safari adventure ahead. Welcome dinner at the hotel.",
        breakfast=False,
        lunch=False,
        dinner=True
    )

    # Day 2
    ItineraryDay.objects.create(
        itinerary=kenya_safari_itinerary,
        day_number=2,
        title="Nairobi National Park & Karen Blixen Museum",
        destination=destinations['nairobi'],
        accommodation=accommodations[0],
        description="Early morning game drive in Nairobi National Park - unique opportunity to see wildlife against the city skyline. Afternoon visit to Karen Blixen Museum and Giraffe Centre. Return to hotel for dinner.",
        breakfast=True,
        lunch=True,
        dinner=True
    )

    # Day 3
    ItineraryDay.objects.create(
        itinerary=kenya_safari_itinerary,
        day_number=3,
        title="Travel to Maasai Mara",
        destination=destinations['kenya'],  # General Kenya for travel day
        accommodation=accommodations[1],  # Tented camp
        description="Depart Nairobi after breakfast for Maasai Mara National Reserve. Scenic drive through the Great Rift Valley with stops for photos. Arrive at camp for lunch and check-in. Afternoon game drive in the reserve.",
        breakfast=True,
        lunch=True,
        dinner=True
    )

    # Mombasa Beach Itinerary
    mombasa_itinerary = Itinerary.objects.create(
        package=packages[1],  # Mombasa Beach
        title="Mombasa Beach Paradise Itinerary",
        overview="A relaxing 5-day beach holiday combining relaxation with cultural exploration on Kenya's beautiful coast."
    )

    # Day 1
    ItineraryDay.objects.create(
        itinerary=mombasa_itinerary,
        day_number=1,
        title="Arrival & Beach Relaxation",
        destination=destinations['mombasa'],
        accommodation=accommodations[2],  # Serena Beach Resort
        description="Arrive at Moi International Airport. Transfer to beachfront resort. Check-in and welcome drink. Afternoon at leisure on the pristine beach. Sunset dinner at the resort.",
        breakfast=False,
        lunch=False,
        dinner=True
    )

    # Day 2
    ItineraryDay.objects.create(
        itinerary=mombasa_itinerary,
        day_number=2,
        title="Fort Jesus & Old Town Tour",
        destination=destinations['mombasa'],
        accommodation=accommodations[2],
        description="Morning visit to historic Fort Jesus and guided tour of Mombasa Old Town. Explore local markets and Swahili architecture. Afternoon return to resort for beach activities and water sports.",
        breakfast=True,
        lunch=False,
        dinner=True
    )

    # Zanzibar Spice Island Itinerary
    zanzibar_itinerary = Itinerary.objects.create(
        package=packages[3],  # Zanzibar Spice
        title="Zanzibar Spice Island Experience",
        overview="A cultural and relaxing 6-day journey through Zanzibar's spice heritage, historic Stone Town, and beautiful beaches."
    )

    # Day 1
    ItineraryDay.objects.create(
        itinerary=zanzibar_itinerary,
        day_number=1,
        title="Arrival & Stone Town Exploration",
        destination=destinations['zanzibar'],
        accommodation=accommodations[4],  # Emerson Zanzibar
        description="Arrive at Abeid Amani Karume International Airport. Transfer to Stone Town boutique hotel. Afternoon walking tour of UNESCO World Heritage Stone Town, including spice markets and historic buildings.",
        breakfast=False,
        lunch=False,
        dinner=True
    )

    # Day 2
    ItineraryDay.objects.create(
        itinerary=zanzibar_itinerary,
        day_number=2,
        title="Spice Tour & Cultural Experience",
        destination=destinations['zanzibar'],
        accommodation=accommodations[4],
        description="Full day spice tour visiting local farms to see, smell, and taste various spices. Learn about traditional uses and cultivation methods. Visit local village for cultural interaction. Evening sunset dhow cruise.",
        breakfast=True,
        lunch=True,
        dinner=False
    )

    print("✓ Created sample itineraries for packages")

def create_sample_bookings(packages):
    """Create sample bookings for testing"""
    print("Creating sample bookings...")

    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@novustelltravel.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )

    # Create sample bookings
    PackageBooking.objects.create(
        package=packages[0],  # Kenya Safari
        user=test_user,
        selected_accommodation=packages[0].available_accommodations.first(),
        selected_travel_mode=packages[0].available_travel_modes.first(),
        travel_date=datetime(2024, 3, 15).date(),
        adults_count=2,
        children_count=1,
        total_amount=Decimal('4995.00'),
        status=PackageBooking.CONFIRMED,
        special_requests="Vegetarian meals preferred. Celebrating anniversary."
    )

    PackageBooking.objects.create(
        package=packages[1],  # Mombasa Beach
        user=test_user,
        selected_accommodation=packages[1].available_accommodations.first(),
        selected_travel_mode=packages[1].available_travel_modes.first(),
        travel_date=datetime(2024, 4, 20).date(),
        adults_count=2,
        children_count=0,
        total_amount=Decimal('1960.00'),
        status=PackageBooking.PENDING,
        special_requests="Honeymoon package. Sea view room preferred."
    )

    print("✓ Created sample bookings")

if __name__ == "__main__":
    print("🚀 Starting Novustell Travel data population...")
    destinations = create_destinations()
    accommodations = create_accommodations(destinations)
    travel_modes = create_travel_modes()
    packages = create_packages(destinations, accommodations, travel_modes)
    create_itineraries(packages, destinations, accommodations)
    create_sample_bookings(packages)
    print("✅ Data population completed successfully!")
    print("\n📊 Summary:")
    print(f"   • {Destination.objects.count()} destinations created")
    print(f"   • {Accommodation.objects.count()} accommodations created")
    print(f"   • {TravelMode.objects.count()} travel modes created")
    print(f"   • {Package.objects.count()} packages created")
    print(f"   • {Itinerary.objects.count()} itineraries created")
    print(f"   • {ItineraryDay.objects.count()} itinerary days created")
    print(f"   • {PackageBooking.objects.count()} sample bookings created")
    print("\n🎉 Ready for testing! Login to admin with:")
    print("   Username: technical")
    print("   Password: technicalpassword")
