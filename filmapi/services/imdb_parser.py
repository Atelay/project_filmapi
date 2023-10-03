import asyncio

from bs4 import BeautifulSoup
import concurrent.futures
import json
from flask import current_app as app
from aiohttp import ClientSession


class IMDbParser:
    def __init__(self, headers):
        self.headers = headers
        self.base_url = "https://www.imdb.com"
        self.top_chart_url = f"{self.base_url}/chart/top/"
        self.movie_links = []

    async def get_movie_links(self, session):
        async with session.get(self.top_chart_url, headers=self.headers) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, "lxml")
            movie_containers = soup.find_all(
                "li", class_="ipc-metadata-list-summary-item"
            )
            self.movie_links = [
                f"{self.base_url}{movie.a.attrs['href']}" for movie in movie_containers
            ]

    async def get_response_from_link(self, session: ClientSession, link: str):
        async with session.get(link, headers=self.headers) as response:
            return await response.text()

    def get_data_from_response(self, response) -> dict:
        soup = BeautifulSoup(response, "lxml")
        data = soup.find("script", id="__NEXT_DATA__")
        if data:
            json_data = json.loads(data.string)
        film_info_1: dict = json_data["props"]["pageProps"]["aboveTheFoldData"]
        film_info_2: dict = json_data["props"]["pageProps"]["mainColumnData"]

        title = film_info_2.get("titleText", {}).get("text", "")
        rating = film_info_1.get("ratingsSummary", {}).get("aggregateRating", "")
        description = (
            film_info_1.get("plot", {}).get("plotText", {}).get("plainText", "")
        )

        year = film_info_1["releaseDate"]["year"] or 1900
        month = film_info_1["releaseDate"]["month"] or 1
        day = film_info_1["releaseDate"]["day"] or 1
        release_date = f"{year}-{month}-{day}"

        length = int(int(film_info_1.get("runtime", {}).get("seconds", 0)) / 60)
        distributed_by = (
            film_info_2.get("production", {})
            .get("edges", [{}])[0]
            .get("node", {})
            .get("company", {})
            .get("companyText", {})
            .get("text", "")
        )
        genres = [
            genre["text"] for genre in film_info_1.get("genres", {}).get("genres", [])
        ]
        actors = [
            actor["node"]["name"]["nameText"]["text"]
            for actor in film_info_2.get("cast", {}).get("edges", [])
        ]
        title_original = film_info_2.get("originalTitleText", {}).get("text", "")
        try:
            budget_amount = (
                film_info_2.get("productionBudget", {})
                .get("budget", {})
                .get("amount", "")
            )
            budget_currency = (
                film_info_2.get("productionBudget", {})
                .get("budget", {})
                .get("currency", "")
            )
            budget = f"{budget_amount} {budget_currency}"
        except (KeyError, AttributeError):
            budget = ""
        poster = film_info_1.get("primaryImage", {}).get("url", "")
        try:
            trailer = (
                film_info_1.get("primaryVideos", {})
                .get("edges", [{}])[0]
                .get("node", {})
                .get("playbackURLs", [{}])[0]
                .get("url", "")
            )
        except (IndexError, KeyError, AttributeError):
            trailer = ""

        return {
            "title": title,
            "rating": rating,
            "description": description,
            "release_date": release_date,
            "length": length,
            "distributed_by": distributed_by,
            "genres": genres,
            "actors": actors,
            "title_original": title_original,
            "budget": budget,
            "poster": poster,
            "trailer": trailer,
        }

    async def parse_movies(self, link=None):
        async with ClientSession(headers=app.config.get("HEADERS", {})) as session:
            if link:
                self.movie_links.append(link)
            else:
                await self.get_movie_links(session)
            responses = await asyncio.gather(
                *(
                    self.get_response_from_link(session, link)
                    for link in self.movie_links
                )
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                return list(executor.map(self.get_data_from_response, responses))
