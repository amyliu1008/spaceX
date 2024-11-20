import requests
import pandas as pd


class SpaceX:
    def __init__(
        self,
        launchpads_url="https://api.spacexdata.com/v4/launchpads",
        launches_url="https://api.spacexdata.com/v4/launches",
    ):
        self.launchpads = self.get_data(launchpads_url)
        self.launches = self.get_data(launches_url)
        self.launches["date_utc"] = pd.to_datetime(self.launches["date_utc"])

    def get_data(self, url: str):
        try:
            response = requests.request("GET", url, verify=False)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        data = response.json()
        df = pd.DataFrame(data)
        return df

    def get_launch_for_year(self, years: list) -> dict:
        if not all(isinstance(year, int) for year in years):
            raise ValueError("All years must be integer.")
        valid_years = [y for y in years if 2006 <= y <= 2024]
        invalid_years = list(set(years) - set(valid_years))
        if invalid_years:
            print(f"Warning: The following years are invalid: {invalid_years}")
        counts = {}
        launches = self.launches
        for year in valid_years:
            counts[year] = launches[
                launches["date_utc"].dt.year == year
            ].shape[0]
        return counts

    def get_launch_for_site(self, sites: list) -> dict:
        if not all(isinstance(site, str) for site in sites):
            raise ValueError("All sites must be string.")

        launchpads_filtered = self.launchpads[
            ["full_name", "launch_attempts", "launch_successes"]
        ]
        valid_sites = [
            s for s in sites if s in set(launchpads_filtered["full_name"])
        ]
        invalid_sites = [
            s for s in sites if s not in set(launchpads_filtered["full_name"])
        ]
        if invalid_sites:
            print(f"Warning: Cannot find the following sites: {invalid_sites}")

        counts = {}
        for site in valid_sites:
            launchpad = (
                launchpads_filtered[launchpads_filtered["full_name"] == site]
                .set_index("full_name")
                .T.to_dict()
            )
            counts.update(launchpad)
        return counts
