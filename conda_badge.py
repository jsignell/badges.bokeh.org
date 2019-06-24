import requests
import datetime
import intake


CATALOG_URL = 'https://raw.githubusercontent.com/ContinuumIO/anaconda-package-data/master/catalog/anaconda_package_data.yaml'
BADGE_URL = 'https://img.shields.io/badge/conda-{downloads}/month-{color}.svg'

def conda_badge():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)

    cat = intake.Catalog(CATALOG_URL)
    try:
        monthly = cat.anaconda_package_data_by_month(year=last_month.year, month=last_month.month,
                                                     columns=['pkg_name', 'counts']).to_dask()
    except:
        # get the month before
        month = last_month.replace(day=1) - datetime.timedelta(days=1)
        monthly = cat.anaconda_package_data_by_month(year=month.year, month=month.month,
                                                     columns=['pkg_name', 'counts']).to_dask()

    downloads = monthly[monthly.pkg_name == 'bokeh'].counts.sum().compute()
    if downloads > 1e6:
        downloads = '{}M'.format(int(downloads/1e6))
    elif downloads > 1e3:
        downloads = '{}k'.format(int(downloads/1e3))
    else:
        downloads = int(downloads)

    badge_url = BADGE_URL.format(downloads=downloads, color='brightgreen')
    badge_request = requests.get(badge_url, stream=True)
    badge_request.raw.read(decode_content=True).decode('utf-8')
