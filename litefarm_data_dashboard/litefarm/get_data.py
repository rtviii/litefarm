from pathlib import Path
import pandas as pd
import json
from .exceptions import NoDatabaseError
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine, text
import paramiko
import io
import logging
import sys
import psycopg2

logging.basicConfig(level=logging.INFO, stream=sys.stderr)


class DataGetter:
    def __init__(
        self,
        config={},
        location_spg_data=Path(__file__).parent.parent
        / "data"
        / "spg_organizations.csv",
    ):
        self._litefarm_db_engine = None
        required_config = [
            "LITEFARM_DB_HOST",
            "LITEFARM_DB_USER",
            "LITEFARM_DB_PASSWORD",
            "LITEFARM_DB_NAME",
            "LITEFARM_DB_SSH_KEY",
        ]
        for key in required_config:
            # Check that all the required config keys are present
            if key not in config:
                raise ValueError(f"Missing config key {key}")
        self.config = config
        self._server = None  # Init the server variable
        if Path(location_spg_data).exists():
            self.spg_data_path = Path(location_spg_data)
        else:
            self.spg_data_path = None

    def __del__(self):
        """
        Destructor, stops the ssh tunnel if it was started when the data getter is deleted
        """
        if self._server is not None:
            try:
                self._server.stop()
            except:
                pass

    @property
    def engine(self):
        """
        Returns the SQLAlchemy engine for the litefarm database
        Can be used this way with pandas : litefarm("SELECT * FROM farm")
        """
        if self._litefarm_db_engine is None:
            # key = paramiko.Ed25519Key.from_private_key( io.StringIO(self.config["LITEFARM_DB_SSH_KEY"]) )
            key = paramiko.RSAKey.from_private_key_file(
                self.config["LITEFARM_DB_SSH_KEY"]
            )

            self._server = SSHTunnelForwarder(
                ("app.litefarm.org", 22),
                ssh_username="litefarm",
                ssh_pkey=key,
                remote_bind_address=("localhost", 5433),
                local_bind_address=("localhost", 5433),
            )
            self._server.start()
            self._litefarm_db_engine = create_engine(
                "postgresql://{}:{}@localhost:{}/{}".format(
                    "readonly",
                    self.config["LITEFARM_DB_PASSWORD"],
                    self._server.local_bind_port,
                    self.config["LITEFARM_DB_NAME"],
                ),
                pool_pre_ping=True,
            )
        return self._litefarm_db_engine

    def litefarm(self, query):
        """
        Returns a pandas dataframe from a query on the litefarm database
        """
        try:
            with self.engine.connect() as conn:
                x = pd.read_sql(text(query), conn)
                print("receieved", x)
                return x
        except psycopg2.OperationalError:
            try:
                self._server.stop()
            except:
                pass
            self._litefarm_db_engine = None

    def get_cleaned_farms(self):
        """
        Returns a pandas dataframe with the 'cleaned farms'
        """
        farm = self.litefarm("SELECT * FROM farm")
        location = self.litefarm("SELECT * FROM location")
        # We first remove "test farms"
        bad_farms = farm[
            farm.farm_name.str.contains(
                "(?:fake|prueba|test|abc|123|hola|sample|demo|delete|none|dummy|wrong)",
                case=False,
            )
            | (farm["farm_name"].str.len() < 4)
            | farm.sandbox_farm
            | farm.deleted
        ][["farm_id"]]
        # Then we remove farms with no location
        bad_farms2 = farm[~farm.farm_id.isin(location.farm_id.unique())]

        bad_farms = pd.concat([bad_farms, bad_farms2])
        cleaned_farms = farm[~farm.farm_id.isin(bad_farms.farm_id)]

        # Then we correct the wrong "created_at" dates
        cleaned_farms.loc[cleaned_farms.created_at.dt.year < 2021, "created_at"] = (
            pd.to_datetime("2021-01-01", utc=True)
        )

        return cleaned_farms

    def get_active_farms(self, date_range=(None, None)):
        """
        Not used anymore, but stays here for reference
        """
        # Set the empty date range to the min and max possible dates
        if date_range[0] is None:
            date_range = (pd.Timestamp.min, date_range[1])
        if date_range[1] is None:
            date_range = (date_range[0], pd.Timestamp.max)
        date_range = (
            pd.Timestamp(date_range[0]).timestamp(),
            pd.Timestamp(date_range[1]).timestamp(),
        )
        logs = self.litefarm("SELECT * FROM userLog WHERE farm_id IS NOT NULL")
        logs = logs[logs.created_at >= date_range[0]][logs.created_at <= date_range[1]]
        farms = self.get_cleaned_farms()
        return farms[farms.farm_id.isin(logs.farm_id.unique())]

    def all_countries(self):
        """
        Returns a list of all countries in the database with more than 10 farms
        """
        try:
            countries = self.litefarm("SELECT * FROM countries")
            farms = self.get_cleaned_farms()
            countries = (
                pd.merge(
                    countries, farms, left_on="id", right_on="country_id", how="inner"
                )
                .groupby("country_name")
                .agg({"farm_id": "count"})
                .reset_index()
            )
            countries = countries[countries.farm_id >= 10]

            return countries.sort_values(
                by=["country_name"]
            ).country_name.values.tolist()
        except NoDatabaseError:
            return []

    def all_organizations(self, year=None):
        """
        Returns a list of all organizations in the spg csv file
        """
        if self.spg_data_path is None:
            return []
        spg_data = pd.read_csv(self.spg_data_path)
        if year is not None:
            spg_data = spg_data[spg_data.year == year]
        return spg_data.organization.unique().tolist()

    def spg_available_years(self):
        """
        Returns a list of all years in the spg csv file
        """
        if self.spg_data_path is None:
            return []
        spg_data = pd.read_csv(self.spg_data_path).sort_values("year", ascending=False)
        return spg_data.year.unique().tolist()


def expand_grid_points_coordinates(data, col="grid_points", expand=False):
    """
    Turns the 'grid_points' column of the dataframe into a dataframe with lat and lon columns
    """
    data["parsed_json"] = data[col].apply(json.loads)
    json_struct = json.loads(data.to_json(orient="records"))
    if expand:
        # Might be useful later for areas or lines with a list of points instead of a single point
        raise NotImplementedError("Todo")
    else:
        return pd.json_normalize(json_struct).rename( columns={"parsed_json.lat": "lat", "parsed_json.lng": "lon"} )


if __name__ == "__main__":
    dg = DataGetter()
    print(expand_grid_points_coordinates(dg.get_cleaned_farms().head()))
