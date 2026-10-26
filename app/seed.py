from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, Artist, Song, Playlist, Review

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database(db: Session):
    if db.query(User).first():
        return

    admin_user = User(
        username="admin",
        password_hash=pwd_context.hash("admin123"),
        role="admin",
    )
    normal_user = User(
        username="adam",
        password_hash=pwd_context.hash("user123"),
        role="user",
    )
    db.add_all([admin_user, normal_user])
    db.commit()
    db.refresh(admin_user)
    db.refresh(normal_user)

    artists_map = {
        "Avenoir": Artist(name="Avenoir", bio="Artysta R&B / Soul z Kanady.", country="Canada"),
        "Brent Faiyaz": Artist(name="Brent Faiyaz", bio="Wokalista i producent R&B, założyciel Sonder.", country="USA"),
        "PARTYNEXTDOOR": Artist(name="PARTYNEXTDOOR", bio="Kanadyjski wokalista i producent R&B (OVO Sound).", country="Canada"),
        "Don Toliver": Artist(name="Don Toliver", bio="Raper i wokalista z Houston (Cactus Jack).", country="USA"),
        "Migos": Artist(name="Migos", bio="Trio hip-hopowe z Atlanty (Quavo, Offset, Takeoff).", country="USA"),
        "Calvin Harris": Artist(name="Calvin Harris", bio="Szkocki DJ, producent muzyki EDM i pop.", country="UK"),
        "Route 94": Artist(name="Route 94", bio="Brytyjski producent muzyki deep house i EDM.", country="UK"),
        "Galantis": Artist(name="Galantis", bio="Szwedzki duet producentów muzyki elektronicznej (EDM).", country="Sweden"),
        "Bad Bunny & Jhayco": Artist(name="Bad Bunny & Jhayco", bio="Gwiazdy muzyki latino trap i reggaeton z Puerto Rico.", country="Puerto Rico"),
        "Sky Rompiendo, Feid, Myke Towers": Artist(name="Sky Rompiendo, Feid, Myke Towers", bio="Kolumbijsko-portorykańska supergrupa latino.", country="Colombia / PR"),
    }

    db.add_all(artists_map.values())
    db.commit()
    for artist in artists_map.values():
        db.refresh(artist)

    songs = [
        Song(
            title="TMW",
            genre="RNB/SOUL",
            album="Single",
            duration_sec=164,
            youtube_url="https://www.youtube.com/watch?v=kR5N7O7eb3I",
            artist_id=artists_map["Avenoir"].id,
            plays_count=15,
        ),
        Song(
            title="Gang Over Luv",
            genre="RNB",
            album="Sonder Son",
            duration_sec=206,
            youtube_url="https://www.youtube.com/watch?v=F_dK2f4A5fQ",
            artist_id=artists_map["Brent Faiyaz"].id,
            plays_count=22,
        ),
        Song(
            title="Recognize (feat. Drake)",
            genre="RNB",
            album="PARTYNEXTDOOR TWO",
            duration_sec=315,
            youtube_url="https://www.youtube.com/watch?v=6gRj2G1w3E0",
            artist_id=artists_map["PARTYNEXTDOOR"].id,
            plays_count=19,
        ),
        Song(
            title="Secondhand (feat. Rema)",
            genre="RAP",
            album="OCTANE",
            duration_sec=210,
            youtube_url="https://www.youtube.com/watch?v=yY7iM7_1w7A",
            artist_id=artists_map["Don Toliver"].id,
            plays_count=12,
        ),
        Song(
            title="T-Shirt",
            genre="RAP",
            album="Culture",
            duration_sec=242,
            youtube_url="https://www.youtube.com/watch?v=1VUa99-tJqs",
            artist_id=artists_map["Migos"].id,
            plays_count=31,
        ),
        Song(
            title="Thinking About You (feat. Ayah Marar)",
            genre="EDM",
            album="18 Months",
            duration_sec=247,
            youtube_url="https://www.youtube.com/watch?v=cl3b7dDBLpo",
            artist_id=artists_map["Calvin Harris"].id,
            plays_count=27,
        ),
        Song(
            title="My Love (feat. Jess Glynne)",
            genre="EDM",
            album="Single",
            duration_sec=259,
            youtube_url="https://www.youtube.com/watch?v=BS46C2z5lVE",
            artist_id=artists_map["Route 94"].id,
            plays_count=18,
        ),
        Song(
            title="Runaway (U & I)",
            genre="EDM",
            album="Pharmacy",
            duration_sec=227,
            youtube_url="https://www.youtube.com/watch?v=5XR7naZ_zZA",
            artist_id=artists_map["Galantis"].id,
            plays_count=34,
        ),
        Song(
            title="DÁKITI",
            genre="LATINO",
            album="El Último Tour Del Mundo",
            duration_sec=205,
            youtube_url="https://www.youtube.com/watch?v=TmKh7lAwnBI",
            artist_id=artists_map["Bad Bunny & Jhayco"].id,
            plays_count=40,
        ),
        Song(
            title="El Cielo",
            genre="LATINO",
            album="Single",
            duration_sec=192,
            youtube_url="https://www.youtube.com/watch?v=kM9W5F8G5vA",
            artist_id=artists_map["Sky Rompiendo, Feid, Myke Towers"].id,
            plays_count=25,
        ),
    ]

    db.add_all(songs)
    db.commit()
    for s in songs:
        db.refresh(s)

    fav_playlist = Playlist(
        name="Late Night Vibes & Bangers",
        description="Mieszanka R&B, Rapu, EDM i Latino",
        owner_id=normal_user.id,
        songs=[songs[0], songs[1], songs[4], songs[7], songs[8]],
    )
    db.add(fav_playlist)

    reviews = [
        Review(
            rating=5,
            comment="Sonder Son to absolutny klasyk R&B, ten bit nigdy się nie starzeje.",
            user_id=normal_user.id,
            song_id=songs[1].id,
        ),
        Review(
            rating=5,
            comment="Thinking About You z 18 Months to szczyt złotej ery EDM!",
            user_id=admin_user.id,
            song_id=songs[5].id,
        ),
    ]
    db.add_all(reviews)
    db.commit()