import os
import gzip
import shutil
import sqlite3
import logging
from typing import Optional, List, Dict, Any

try:
    import importlib.resources as resources

except ImportError:
    raise ImportError(
        "Python 3.8+ is required to run this library. Please upgrade your Python version."
    )

logging.basicConfig(level=logging.INFO)


class Atlas:
    def __init__(self):
        # Path to the compressed database
        if hasattr(resources, "files"):
            # Python 3.9+ with enhanced importlib.resources
            self._db_compressed_path = str(
                resources.files("pyworldatlas").joinpath("worldatlas.sqlite3.gz")
            )
        else:
            # Python 3.8 with basic importlib.resources
            with resources.path("pyworldatlas", "worldatlas.sqlite3.gz") as db_path:
                self._db_compressed_path = str(db_path)

        self._db_compressed_path = os.path.join(
            os.path.dirname(__file__), "worldatlas.sqlite3.gz"
        )
        self._db_decompressed_path = os.path.join(
            os.path.dirname(__file__), "worldatlas.sqlite3"
        )

        # Ensure the database is decompressed if it's not already there
        self._ensure_decompressed()

    def _ensure_decompressed(self):
        """Check if the decompressed database exists, if not, decompress it."""
        if not os.path.exists(self._db_decompressed_path):
            logging.info("Database not found, decompressing...")
            with gzip.open(self._db_compressed_path, "rb") as f_in:
                with open(self._db_decompressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logging.info("Database decompressed and stored in the package directory.")
        else:
            logging.debug(
                "Decompressed database already exists, skipping decompression."
            )

    def _connect(self):
        """Open the decompressed database in read-only mode."""
        return sqlite3.connect(f"file:{self._db_decompressed_path}?mode=ro", uri=True)

    def get_progress(self) -> Optional[float]:
        """
        Returns the percentage of data that the library is aimed to contain.

        Returns:
            - float: The percentage of data currently available in the library.
        """
        query = "SELECT COUNT(id) FROM base_country"
        total_data_size = 285  # Total entries that somewhat should exist in the table

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                current_data_size = cursor.fetchone()[0]

            progress_percentage = round((current_data_size / total_data_size) * 100, 1)
            logging.info(
                f"Current data size: {current_data_size}, Total data size: {total_data_size}, Progress: {progress_percentage}%"
            )
            return progress_percentage

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return None

    def get_countries(
        self,
        continents: Optional[List[str]] = None,
        # TODO Refine this method
        # min_population: Optional[float] = None,
        # max_population: Optional[float] = None,
        # min_gdp: Optional[float] = None,
        # max_gdp: Optional[float] = None,
    ) -> Optional[List[str]]:
        """
        Fetches a list of countries filtered by continents.

        Parameters:
            - continents (list of str, optional): The names of the continents to filter countries by.
            If specified, it must contain at least one of the following:
            ["Asia", "Africa", "North America", "South America",
            "Antarctica", "Europe", "Oceania"].

        Returns:
            - list: A list of country names (str) from the specified continent(s).
        """

        query = """
        SELECT c.name
        FROM base_country c
        JOIN base_country_continents cc ON c.id = cc.country_id
        JOIN base_continent co ON cc.continent_id = co.id
        """
        params = ()

        try:
            if continents:
                placeholders = ", ".join("?" for _ in continents)
                query += f" WHERE co.name IN ({placeholders})"
                params = tuple(continent.strip() for continent in continents)

            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                countries = cursor.fetchall()

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return None

        else:
            return [country[0] for country in countries]

    def _get_languages(
        self,
        name: Optional[str] = None,
        iname: Optional[str] = None,
        countries: Optional[List[str]] = None,
        continents: Optional[List[str]] = None,
        in_official: Optional[bool] = False,
        in_recognized: Optional[bool] = False,
    ) -> Optional[List[str]]:
        """ """

        return []

    def get_country_profile(self, name: str = None) -> Dict[str, Any]:
        """
        Fetches the profile of the specified country, including government, population, GDP, ethnic groups, religion, etc.

        Parameters:
            name (str): The name of the country to fetch the profile for.
                        Example: "Japan" or "JP" (ISO 3166 Alpha-2 code).

        Returns:
            dict: A dictionary containing various information about the country, including government details, population, GDP, ethnic groups, religion, etc.
        """
        
        if name is None:
            raise self.CountryNotFoundError("Country name is required.")

        name = name.strip().lower()

        # Determine whether to query by ISO code or name
        field = "iso_3166_code" if len(name) == 2 else "name"

        # SQL query string
        query = f"""
            SELECT base_country.*, 
                base_area.total_km2_including_disputed_territories, 
                base_area.total_km2_internationally_recognized, 
                base_area.water_percentage, 
                base_government.*, 
                base_governmenttype.name AS government_type_name,
                base_population.total_population, base_population.density_per_km2, base_population.year as population_year,
                base_gdp.*, 
                base_giniindex.value as gini_value, base_giniindex.year as gini_year
            FROM base_country
            JOIN base_area ON base_country.area_id = base_area.id
            JOIN base_government ON base_country.government_id = base_government.id
            JOIN base_governmenttype ON base_government.government_type_id = base_governmenttype.id
            LEFT JOIN base_population ON base_country.id = base_population.country_id
            LEFT JOIN base_gdp ON base_country.id = base_gdp.country_id
            LEFT JOIN base_giniindex ON base_country.id = base_giniindex.country_id
            WHERE LOWER(base_country.{field}) = ?;
        """

        profile = {}

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Execute the query with the provided parameter
            cursor.execute(query, (name,))
            base_country = cursor.fetchone()

            if not base_country:
                raise self.CountryNotFoundError(f"No data found for country: {name}")

            # Building the profile
            profile["capital"] = self._extract_capital_data(base_country)
            profile["area"] = self._extract_area_data(base_country)

            if not profile["capital"]["is_largest_city"]:
                profile["largest_city"] = self._extract_largest_city_data(base_country)

            profile.update(
                {
                    "driving_side": base_country["driving_side"],
                    "calling_code": base_country["calling_code"],
                    "iso_3166_code": base_country["iso_3166_code"],
                    "internet_tld": base_country["internet_tld"],
                    "population": {
                        "total": base_country["total_population"],
                        "density_km2": base_country["density_per_km2"],
                        "date_year": base_country["population_year"],
                    },
                    "gini_index": {
                        "value": base_country["gini_value"],
                        "year": base_country["gini_year"],
                    },
                    "gdp": {
                        "ppp_trillions": base_country["ppp_total_trillions"],
                        "ppp_per_capita": base_country["ppp_per_capita"],
                        "nominal_total_trillions": base_country[
                            "nominal_total_trillions"
                        ],
                        "nominal_per_capita": base_country["nominal_per_capita"],
                        "ppp_gdp_year": base_country["gdp_year"],
                        "nominal_gdp_year": base_country["gdp_year_nominal"],
                    },
                    "government": self._extract_government_data(base_country),
                }
            )

            # Fetch additional country details: official names, religions, ethnic groups, languages, etc.
            profile["official_names"] = self._fetch_official_names(
                cursor, base_country["id"]
            )
            profile["anthem"] = self._fetch_anthem(cursor, base_country["id"])
            profile["motto"] = self._fetch_motto(cursor, base_country["id"])
            profile["religion"] = self._fetch_religions(cursor, base_country["id"])
            profile["ethnic_groups"] = self._fetch_ethnic_groups(
                cursor, base_country["id"]
            )
            profile["languages"] = self._fetch_languages(cursor, base_country["id"])
            profile["currency"] = self._fetch_currency(cursor, base_country["id"])
            profile["continent"] = self._fetch_continent(cursor, base_country["id"])
            profile["timezones"] = self._fetch_timezones(cursor, base_country["id"])

        return profile

    def _extract_capital_data(self, base_country: sqlite3.Row) -> dict:
        return {
            "name": base_country["capital"],
            "coordinates_degree_east": base_country["capital_coordinates_degree_east"],
            "coordinates_degree_north": base_country[
                "capital_coordinates_degree_north"
            ],
            "is_largest_city": base_country["capital"] == base_country["largest_city"],
        }

    def _extract_area_data(self, base_country: sqlite3.Row) -> dict:
        return {
            "total_km2_including_disputed_territories": base_country[
                "total_km2_including_disputed_territories"
            ],
            "total_km2_internationally_recognized": base_country[
                "total_km2_internationally_recognized"
            ],
            "water_percentage": base_country["water_percentage"],
        }

    def _extract_largest_city_data(self, base_country: sqlite3.Row) -> dict:
        return {
            "name": base_country["largest_city"],
            "coordinates_degree_east": base_country[
                "largest_city_coordinates_degree_east"
            ],
            "coordinates_degree_north": base_country[
                "largest_city_coordinates_degree_north"
            ],
        }

    def _extract_government_data(self, base_country: sqlite3.Row) -> dict:
        return {
            "president": base_country["president"],
            "prime_minister": base_country["prime_minister"],
            "declaration_of_state_sovereignty": base_country[
                "declaration_of_state_sovereignty"
            ],
            "other_leader_title": base_country["other_leader_title"],
            "other_leader": base_country["other_leader"],
            "government_type": base_country["government_type_name"],
            "president_assumed_office": base_country["president_assumed_office"],
            "prime_minister_assumed_office": base_country[
                "prime_minister_assumed_office"
            ],
            "other_leader_assumed_office": base_country["other_leader_assumed_office"],
        }

    def _fetch_official_names(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_officialname.name AS official_name, base_language.name AS language_name
            FROM base_officialname 
            JOIN base_language ON base_officialname.language_id = base_language.id
            WHERE base_officialname.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        official_names = cursor.fetchall()

        # Map the language name to the official name
        official_names_dict = {
            row["language_name"]: row["official_name"] for row in official_names
        }
        return official_names_dict

    def _fetch_motto(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_motto.text, base_language.name 
            FROM base_motto 
            JOIN base_language ON base_motto.language_id = base_language.id
            WHERE base_motto.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        motto_rows = cursor.fetchall()

        motto_dict = {row["name"]: row["text"] for row in motto_rows}
        return motto_dict

    def _fetch_anthem(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_anthem.name as anthem_name, base_language.name as anthem_language
            FROM base_anthem 
            JOIN base_language ON base_anthem.language_id = base_language.id
            WHERE base_anthem.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        anthem_dict = cursor.fetchall()

        anthem_dict = {
            row["anthem_language"]: row["anthem_name"] for row in anthem_dict
        }
        return anthem_dict

    def _fetch_religions(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_religion.name, base_religion.percentage 
            FROM base_religion
            WHERE base_religion.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        religions = cursor.fetchall()

        religion_dict = {row["name"]: row["percentage"] for row in religions}
        return religion_dict

    def _fetch_ethnic_groups(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_ethnicgroup.name, base_ethnicgroup.percentage 
            FROM base_ethnicgroup
            WHERE base_ethnicgroup.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        ethnic_groups = cursor.fetchall()

        ethnic_groups_dict = {row["name"]: row["percentage"] for row in ethnic_groups}
        return ethnic_groups_dict

    def _fetch_languages(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query_official = """
            SELECT base_language.name 
            FROM base_language
            JOIN base_country_official_languages ON base_country_official_languages.language_id = base_language.id
            WHERE base_country_official_languages.country_id = ?;
        """
        query_recognized = """
            SELECT base_language.name 
            FROM base_language
            JOIN base_country_recognized_languages ON base_country_recognized_languages.language_id = base_language.id
            WHERE base_country_recognized_languages.country_id = ?;
        """
        cursor.execute(query_official, (country_id,))
        official_languages = [row["name"] for row in cursor.fetchall()]

        cursor.execute(query_recognized, (country_id,))
        recognized_languages = [row["name"] for row in cursor.fetchall()]

        return {
            "official_languages": official_languages,
            "recognized_languages": recognized_languages,
        }

    def _fetch_currency(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_currency.name, base_currency.symbol, base_currency.iso_code 
            FROM base_currency
            WHERE base_currency.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        currency = cursor.fetchone()

        if currency:
            return {
                "name": currency["name"],
                "symbol": currency["symbol"],
                "iso_code": currency["iso_code"],
            }
        return {}

    def _fetch_continent(self, cursor: sqlite3.Cursor, country_id: int) -> list:
        query = """
            SELECT base_continent.name 
            FROM base_continent
            JOIN base_country_continents ON base_country_continents.continent_id = base_continent.id
            WHERE base_country_continents.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        continents = [row["name"] for row in cursor.fetchall()]

        return continents

    def _fetch_timezones(self, cursor: sqlite3.Cursor, country_id: int) -> dict:
        query = """
            SELECT base_timezone.name, base_timezone.dst 
            FROM base_timezone
            JOIN base_timezone_countries ON base_timezone_countries.timezone_id = base_timezone.id
            WHERE base_timezone_countries.country_id = ?;
        """
        cursor.execute(query, (country_id,))
        timezones = {row["name"]: {"DST": row["dst"]} for row in cursor.fetchall()}

        return timezones
    
atlas = Atlas()

print(atlas.get_country_profile("Andorra"))