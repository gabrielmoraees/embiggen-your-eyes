"""
Data catalog initialization with all available datasets
"""
from datetime import date, timedelta
from app.models.enums import Category, Subject, SourceId
from app.models.schemas import Source, Dataset, Variant
from .storage import SOURCES, DATASETS


def initialize_catalog():
    """Initialize the catalog with all available datasets, sources, and layers"""
    
    # Calculate default date for time-series datasets (2 days ago)
    default_time_series_date = date.today() - timedelta(days=2)
    
    # ========== DATA SOURCES ==========
    SOURCES[SourceId.NASA_GIBS] = Source(
        id=SourceId.NASA_GIBS,
        name="NASA GIBS",
        description="NASA Global Imagery Browse Services - Near real-time satellite imagery",
        attribution="NASA EOSDIS",
        url="https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs",
        terms_of_use="Public domain"
    )
    
    SOURCES[SourceId.NASA_TREK] = Source(
        id=SourceId.NASA_TREK,
        name="NASA Trek",
        description="NASA Solar System Trek - Planetary mapping portal",
        attribution="NASA/JPL-Caltech",
        url="https://trek.nasa.gov",
        terms_of_use="Public domain"
    )
    
    
    SOURCES[SourceId.OPENPLANETARYMAP] = Source(
        id=SourceId.OPENPLANETARYMAP,
        name="OpenPlanetaryMap",
        description="Open planetary mapping project",
        attribution="OpenPlanetaryMap Contributors",
        url="https://www.openplanetary.org/opm",
        terms_of_use="CC BY-SA 4.0"
    )
    
    SOURCES[SourceId.USGS] = Source(
        id=SourceId.USGS,
        name="USGS Astrogeology",
        description="United States Geological Survey Astrogeology Science Center",
        attribution="USGS Astrogeology Science Center",
        url="https://astrogeology.usgs.gov",
        terms_of_use="Public domain"
    )
    
    SOURCES[SourceId.CUSTOM] = Source(
        id=SourceId.CUSTOM,
        name="Zoomers Community",
        description="User-uploaded imagery shared publicly on the Zoomers platform",
        attribution="Zoomers Community Contributors",
        terms_of_use="Publicly available - uploaded via Zoomers"
    )
    
    # ========== EARTH DATASETS ==========
    
    # VIIRS SNPP Dataset
    DATASETS["viirs_snpp"] = Dataset(
        id="viirs_snpp",
        name="VIIRS SNPP",
        description="Visible Infrared Imaging Radiometer Suite on Suomi NPP satellite",
        source_id=SourceId.NASA_GIBS,
        category=Category.PLANETS,
        subject=Subject.EARTH,
        supports_time_series=True,
        date_range_start=date(2015, 11, 24),
        date_range_end=date.today(),
        default_date=default_time_series_date,
        variants=[
            Variant(
                id="true_color",
                name="True Color",
                description="Natural color composite",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            ),
            Variant(
                id="false_color",
                name="False Color",
                description="False color composite (Bands M11-I2-I1)",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9
            )
        ]
    )
    
    # MODIS Terra Dataset
    DATASETS["modis_terra"] = Dataset(
        id="modis_terra",
        name="MODIS Terra",
        description="Moderate Resolution Imaging Spectroradiometer on Terra satellite",
        source_id=SourceId.NASA_GIBS,
        category=Category.PLANETS,
        subject=Subject.EARTH,
        supports_time_series=True,
        date_range_start=date(2000, 2, 24),
        date_range_end=date.today(),
        default_date=default_time_series_date,
        variants=[
            Variant(
                id="true_color",
                name="True Color",
                description="Natural color composite",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            ),
            Variant(
                id="false_color",
                name="False Color (Bands 7-2-1)",
                description="False color composite emphasizing vegetation",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_Bands721/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_Bands721/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9
            )
        ]
    )
    
    # ========== MARS DATASETS ==========
    
    # Viking Mosaic
    DATASETS["mars_viking"] = Dataset(
        id="mars_viking",
        name="Mars Viking Mosaic",
        description="Viking Orbiter colorized mosaic (232m/pixel)",
        source_id=SourceId.NASA_TREK,
        category=Category.PLANETS,
        subject=Subject.MARS,
        supports_time_series=False,
        variants=[
            Variant(
                id="colorized",
                name="Colorized",
                description="Colorized global mosaic",
                tile_url_template="https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg",
                thumbnail_url="https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            )
        ]
    )
    
    # Mars OPM Basemap
    DATASETS["mars_opm_basemap"] = Dataset(
        id="mars_opm_basemap",
        name="Mars Basemap",
        description="OpenPlanetaryMap Mars basemap",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.PLANETS,
        subject=Subject.MARS,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="Standard basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # ========== MOON DATASETS ==========
    
    # Moon OPM Basemap
    DATASETS["moon_opm_basemap"] = Dataset(
        id="moon_opm_basemap",
        name="Lunar Basemap",
        description="OpenPlanetaryMap lunar basemap",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.SATELLITES,
        subject=Subject.MOON,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="Standard lunar basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # Moon USGS Geologic Dataset
    DATASETS["moon_usgs_geologic"] = Dataset(
        id="moon_usgs_geologic",
        name="Unified Geologic Map",
        description="USGS Unified Geologic Map of the Moon",
        source_id=SourceId.USGS,
        category=Category.SATELLITES,
        subject=Subject.MOON,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Geologic",
                description="Unified geologic map showing 49 lunar units",
                tile_url_template="https://bm2ms.rsl.wustl.edu/arcgis/rest/services/moon_c0/moon_bm_usgs_Unified_Geologic_Map_p2_c0/MapServer/tile/{z}/{y}/{x}",
                thumbnail_url="https://bm2ms.rsl.wustl.edu/arcgis/rest/services/moon_c0/moon_bm_usgs_Unified_Geologic_Map_p2_c0/MapServer/tile/0/0/0",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # ========== MERCURY DATASETS ==========
    
    # Mercury OPM Basemap
    DATASETS["mercury_opm_basemap"] = Dataset(
        id="mercury_opm_basemap",
        name="Mercury Basemap",
        description="OpenPlanetaryMap Mercury basemap (MESSENGER)",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.PLANETS,
        subject=Subject.MERCURY,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="MESSENGER basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # ========== GALAXY DATASETS ==========
    
    # No pre-loaded galaxy datasets
    # Users can import their own gigapixel images using the Import feature
