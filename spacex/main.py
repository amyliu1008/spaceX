from space import SpaceX
import pandas as pd

spacex = SpaceX()

years = spacex.launches["date_utc"].dt.year.unique().tolist()

launch_for_year = spacex.get_launch_for_year(years)
launch_for_year_df = pd.DataFrame(
    launch_for_year.items(), columns=["Year", "Number of Launches"]
)

print(launch_for_year_df)

sites = spacex.launchpads["full_name"].tolist()
launch_for_site = spacex.get_launch_for_site(sites)
launch_for_site_df = pd.DataFrame.from_dict(launch_for_site, orient="index")
print(launch_for_site_df)
