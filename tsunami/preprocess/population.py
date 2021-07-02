import sys

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd

from tsunami.config import PLACE, CRS

ox.config(use_cache=True, log_console=True)


def get_osm_node(points, name):
    results = points[points["name"] == name]

    if len(results) > 0:
        return results[["name", "geometry"]]

    return None


def to_osm_name(name):
    numbers = {
        "一": "１",
        "二": "２",
        "三": "３",
        "四": "４",
        "五": "５",
        "六": "６",
        "七": "７",
        "八": "８",
        "九": "９",
    }

    for key in numbers.keys():
        name = name.replace(numbers[key], key)

    return name


def main():
    data = pd.read_excel(
        "./data/population.xlsx", sheet_name="若林区（合計）", engine="openpyxl", skiprows=1
    )

    points = ox.geometries_from_place(PLACE, {"place": ["quarter", "neighbourhood"]})

    print("OpenStreetMap points:")
    print(points["name"].values)

    population = []
    total = 0

    for i in range(len(data)):
        if "合計" in data["町名"][i] or "大字計" in data["町名"][i]:
            continue

        name = to_osm_name(data["町名"][i])
        node = get_osm_node(points, name)

        if node is not None:
            node["population"] = data["人口総数"][i]
            population.append(node)

            total += data["人口総数"][i]
        else:
            # print(f"{name} not found")
            pass

    print(f"\n{total} / 137142 ({round(total / 137142 * 100)}%) found")

    population = gpd.GeoDataFrame(pd.concat(population, ignore_index=True))
    population = population.to_crs(CRS)

    ax = population.plot(column="population", legend=True, figsize=(14, 10), edgecolor="k")
    ctx.add_basemap(ax, zoom=15, source=ctx.providers.Esri.WorldImagery)
    ax.set_axis_off()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    sys.exit(main())
