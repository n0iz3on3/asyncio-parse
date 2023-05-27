import datetime
import aiohttp
import asyncio

from model import Base, Session, SwapiPeople, engine


async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()


async def paste_to_db(**people_data):
    async with Session() as session:
        session.add(SwapiPeople(**people_data))
        await session.commit()


async def parse_characters(url, session):
    response = await fetch_data(session, url)
    total_characters = response['count']
    characters = response['results']

    while len(characters) < total_characters:
        next_page = response['next']
        response = await fetch_data(session, next_page)
        characters.extend(response['results'])

    for character in characters:
        character_id = character['url'].split('/')[-2]

        # Обработка поля films
        films = []
        for film_url in character['films']:
            film_response = await fetch_data(session, film_url)
            films.append(film_response['title'])
        character_films = ', '.join(films)

        # Обработка поля species
        species = []
        for species_url in character['species']:
            species_response = await fetch_data(session, species_url)
            species.append(species_response['name'])
        character_species = ', '.join(species)

        # Обработка поля starships
        starships = []
        for starship_url in character['starships']:
            starship_response = await fetch_data(session, starship_url)
            starships.append(starship_response['name'])
        character_starships = ', '.join(starships)

        # Обработка поля vehicles
        vehicles = []
        for vehicle_url in character['vehicles']:
            vehicle_response = await fetch_data(session, vehicle_url)
            vehicles.append(vehicle_response['name'])
        character_vehicles = ', '.join(vehicles)

        # Загрузка данных в базу данных
        character_obj = dict(
            birth_year=character['birth_year'],
            eye_color=character['eye_color'],
            films=character_films,
            gender=character['gender'],
            hair_color=character['hair_color'],
            height=character['height'],
            homeworld=character['homeworld'],
            mass=character['mass'],
            name=character['name'],
            skin_color=character['skin_color'],
            species=character_species,
            starships=character_starships,
            vehicles=character_vehicles,
            url=character['url']
        )
        asyncio.create_task(paste_to_db(**character_obj))

    tasks = asyncio.all_tasks() - {asyncio.current_task(), }
    for task in tasks:
        await task


async def main():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)
        
    url = 'https://swapi.dev/api/people/'
    async with aiohttp.ClientSession() as aio_session:
        await parse_characters(url, aio_session)


if __name__ == '__main__':
    start = datetime.datetime.now()
    print('Start process')
    asyncio.run(main())
    print(f'Process finished at: {datetime.datetime.now() - start}')
